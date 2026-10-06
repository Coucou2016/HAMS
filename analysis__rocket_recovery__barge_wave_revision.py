from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

try:
    from .common import ROOT, read_json
    from .sea_state_response import jonswap_spectrum
except ImportError:
    from common import ROOT, read_json
    from sea_state_response import jonswap_spectrum


CASE_DIR = ROOT / "RocketRecoveryCases" / "Barge_120x50"
RAO_PATH = CASE_DIR / "Output" / "RocketRecovery" / "deck-point-rao-medium.json"
LEG_LAYOUT_PATH = ROOT / "RocketRecoveryCases" / "Chrono_LeggedRecovery" / "chrono-stage3b-rigid-report-data.json"
REPORT_PATH = CASE_DIR / "Output" / "RocketRecovery" / "wave-sensitivity-revision.json"
SUMMARY_CSV_PATH = CASE_DIR / "Output" / "RocketRecovery" / "wave-sensitivity-revision-summary.csv"

SUPPORTED_DURATIONS_S = (600.0, 1200.0, 1800.0)
MIN_REALIZATIONS = 1000
DEFAULT_MAX_DELTA_OMEGA_RAD_S = 0.005
DEFAULT_BOOTSTRAP_RESAMPLES = 1000
DEFAULT_BATCH_SIZE = 16
BOOTSTRAP_CONFIDENCE_LEVEL = 0.95
LINEAR_TILT_SCREENING_DEG = 5.0
MINIMUM_BEM_FREQUENCY_COUNT = 19
POINT_ORDER = (
    "landing_center",
    "leg_forward_port",
    "leg_forward_starboard",
    "leg_aft_port",
    "leg_aft_starboard",
)
PHYSICAL_LEG_IDS = ("leg_1", "leg_2", "leg_3", "leg_4")


def _source_label(path: Path) -> str:
    resolved = Path(path).resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(resolved)


def _complex_value(row: dict[str, Any], group: str, axis: str) -> complex:
    value = row[group][axis]
    return complex(float(value["real"]), float(value["imag"]))


def _point_rows(point: dict[str, Any], heading_deg: float) -> list[dict[str, Any]]:
    rows = sorted(
        (row for row in point["rows"] if math.isclose(float(row["heading_deg"]), heading_deg, abs_tol=1.0e-9)),
        key=lambda row: float(row["frequency_rad_s"]),
    )
    if not rows:
        raise ValueError(f"No RAO rows for point {point.get('id')} at heading {heading_deg}")
    return rows


def _validate_frequency_axis(omega: np.ndarray, name: str) -> np.ndarray:
    values = np.asarray(omega, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError(f"{name} must be a one-dimensional array with at least two values")
    if not np.all(np.isfinite(values)) or np.any(np.diff(values) <= 0.0):
        raise ValueError(f"{name} must be finite and strictly increasing")
    return values


def interpolate_complex_rao(
    source_omega: np.ndarray,
    values: np.ndarray,
    target_omega: np.ndarray,
) -> np.ndarray:
    """Interpolate one complex RAO in the complex plane, retaining phase."""

    source = _validate_frequency_axis(source_omega, "source_omega")
    source_values = np.asarray(values, dtype=complex)
    target = np.asarray(target_omega, dtype=float)
    if source_values.ndim != 1 or source_values.size != source.size:
        raise ValueError("values must be one-dimensional and match source_omega")
    if target.ndim != 1 or not np.all(np.isfinite(target)):
        raise ValueError("target_omega must be a finite one-dimensional array")
    tolerance = max(1.0e-12, 1.0e-12 * max(abs(float(source[0])), abs(float(source[-1]))))
    if target.size and (target[0] < source[0] - tolerance or target[-1] > source[-1] + tolerance):
        raise ValueError("target_omega must lie within the BEM frequency range")
    clipped_target = np.clip(target, source[0], source[-1])
    return np.interp(clipped_target, source, source_values.real) + 1j * np.interp(
        clipped_target, source, source_values.imag
    )


def fine_frequency_grid(
    omega_min: float,
    omega_max: float,
    delta_omega: float = DEFAULT_MAX_DELTA_OMEGA_RAD_S,
    duration_s: float | None = None,
) -> np.ndarray:
    """Build an inclusive fine grid with an optional no-repeat record constraint."""

    omega_min = float(omega_min)
    omega_max = float(omega_max)
    delta_omega = float(delta_omega)
    if not math.isfinite(omega_min) or not math.isfinite(omega_max) or omega_max <= omega_min:
        raise ValueError("omega_max must be greater than omega_min")
    if not math.isfinite(delta_omega) or delta_omega <= 0.0:
        raise ValueError("delta_omega must be positive")
    if duration_s is not None:
        duration_s = float(duration_s)
        if duration_s <= 0.0 or not math.isfinite(duration_s):
            raise ValueError("duration_s must be positive and finite")

    bandwidth = omega_max - omega_min
    interval_count = max(1, int(math.ceil(bandwidth / delta_omega - 1.0e-12)))
    while True:
        candidate = np.linspace(omega_min, omega_max, interval_count + 1, dtype=float)
        actual_delta = float(np.max(np.diff(candidate)))
        repeat_period = 2.0 * math.pi / actual_delta
        within_step_limit = actual_delta <= delta_omega
        outside_record = duration_s is None or repeat_period > duration_s + 1.0e-12
        if within_step_limit and outside_record:
            return candidate
        interval_count += 1


def build_synthesis_frequency_grid(
    source_omega: np.ndarray,
    duration_s: float,
    delta_omega: float = DEFAULT_MAX_DELTA_OMEGA_RAD_S,
) -> dict[str, Any]:
    """Separate the 19-point BEM axis from the duration-aware synthesis axis."""

    source = _validate_frequency_axis(source_omega, "source_omega")
    target = fine_frequency_grid(float(source[0]), float(source[-1]), delta_omega, duration_s)
    actual_delta = float(target[1] - target[0])
    repeat_period = 2.0 * math.pi / actual_delta
    return {
        "omega_rad_s": target,
        "frequency_count": int(target.size),
        "omega_min_rad_s": float(target[0]),
        "omega_max_rad_s": float(target[-1]),
        "delta_omega_rad_s": actual_delta,
        "maximum_allowed_delta_omega_rad_s": float(delta_omega),
        "implied_repeat_period_s": repeat_period,
        "record_duration_s": float(duration_s),
        "record_covers_repeat_period": bool(repeat_period <= float(duration_s) + 1.0e-12),
    }


def load_existing_leg_layout(path: Path = LEG_LAYOUT_PATH) -> dict[str, Any]:
    """Read the current four-leg radius and azimuth source without creating fallback geometry."""

    source_path = Path(path).resolve()
    data = read_json(source_path)
    legs = data["config"]["legs"]
    radius = float(legs["footprint_radius_m"])
    azimuths = [float(value) for value in legs["azimuths_deg"]]
    if len(azimuths) != 4:
        raise ValueError(f"Expected four existing leg azimuths, found {len(azimuths)}")
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("Existing footprint radius must be positive and finite")

    positions = []
    source_positions = data.get("leg_positions", [])
    for index, azimuth_deg in enumerate(azimuths, start=1):
        azimuth_rad = math.radians(azimuth_deg)
        x_m = radius * math.cos(azimuth_rad)
        y_m = radius * math.sin(azimuth_rad)
        if index <= len(source_positions):
            source_position = source_positions[index - 1]
            if not math.isclose(float(source_position["x_m"]), x_m, rel_tol=0.0, abs_tol=1.0e-9):
                raise ValueError(f"Existing x position for leg_{index} does not match radius and azimuth")
            if not math.isclose(float(source_position["y_m"]), y_m, rel_tol=0.0, abs_tol=1.0e-9):
                raise ValueError(f"Existing y position for leg_{index} does not match radius and azimuth")
        positions.append(
            {
                "id": f"leg_{index}",
                "azimuth_deg": azimuth_deg,
                "x_m": x_m,
                "y_m": y_m,
            }
        )
    return {
        "source": _source_label(source_path),
        "radius_m": radius,
        "radius_rounded_m": round(radius, 3),
        "azimuths_deg": azimuths,
        "positions": positions,
        "azimuth_source_status": "existing Chrono proxy layout; current record marks these symmetric azimuths as an assumption",
    }


def build_revision_deck_points(config: dict[str, Any], leg_layout: dict[str, Any]) -> dict[str, Any]:
    """Return actual-leg points plus the exact generic points already registered in platform_config.json."""

    deck_z = float(config["platform"]["deck_z_m"])
    generic_points = []
    generic_ids: set[str] = set()
    for raw_point in config["deck_points"]:
        point_id = str(raw_point["id"])
        if point_id in generic_ids:
            raise ValueError(f"Duplicate generic deck point id: {point_id}")
        generic_ids.add(point_id)
        generic_points.append(
            {
                "id": point_id,
                "position_m": [float(value) for value in raw_point["position_m"]],
                "kind": "generic_sampling",
                "source_id": point_id,
                "source": "existing platform_config.json deck_points",
            }
        )

    if "landing_center" not in generic_ids:
        raise ValueError("The existing generic deck points must include landing_center")

    physical_points = []
    for position in leg_layout["positions"]:
        point_id = str(position["id"])
        if point_id in generic_ids:
            raise ValueError(f"Physical leg id collides with generic deck point id: {point_id}")
        physical_points.append(
            {
                "id": point_id,
                "position_m": [float(position["x_m"]), float(position["y_m"]), deck_z],
                "kind": "physical_leg",
                "azimuth_deg": float(position["azimuth_deg"]),
                "source_id": None,
                "source": "existing four-leg radius and azimuth layout",
            }
        )

    center = next(point for point in generic_points if point["id"] == "landing_center")
    non_center_generic = [point for point in generic_points if point["id"] != "landing_center"]
    all_points = [center, *physical_points, *non_center_generic]
    return {
        "all": all_points,
        "physical_legs": physical_points,
        "generic_sampling": generic_points,
    }


def _source_motion_from_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, np.ndarray]]:
    return {
        "displacement_m": {
            axis: np.asarray([_complex_value(row, "displacement_m", axis) for row in rows], dtype=complex)
            for axis in ("x", "y", "z")
        },
        "angles_rad": {
            axis: np.asarray([_complex_value(row, "angles_rad", axis) for row in rows], dtype=complex)
            for axis in ("roll", "pitch", "yaw")
        },
    }


def _transform_motion(
    dofs: dict[str, np.ndarray],
    point: Sequence[float],
) -> dict[str, dict[str, np.ndarray]]:
    x, y, z = (float(value) for value in point)
    surge = dofs["1"]
    sway = dofs["2"]
    heave = dofs["3"]
    roll = dofs["4"]
    pitch = dofs["5"]
    yaw = dofs["6"]
    return {
        "displacement_m": {
            "x": surge + pitch * z - yaw * y,
            "y": sway + yaw * x - roll * z,
            "z": heave + roll * y - pitch * x,
        },
        "angles_rad": {"roll": roll, "pitch": pitch, "yaw": yaw},
    }


def _generalized_motion_from_center(
    center_motion: dict[str, dict[str, np.ndarray]],
    center_position: Sequence[float],
) -> dict[str, np.ndarray]:
    x, y, z = (float(value) for value in center_position)
    displacement = center_motion["displacement_m"]
    angles = center_motion["angles_rad"]
    return {
        "1": displacement["x"] - angles["pitch"] * z + angles["yaw"] * y,
        "2": displacement["y"] - angles["yaw"] * x + angles["roll"] * z,
        "3": displacement["z"] - angles["roll"] * y + angles["pitch"] * x,
        "4": angles["roll"],
        "5": angles["pitch"],
        "6": angles["yaw"],
    }


def build_revision_transfer_matrix(
    deck_rao: dict[str, Any],
    heading_deg: float,
    target_omega: np.ndarray,
    deck_points: Iterable[dict[str, Any]],
) -> tuple[list[str], np.ndarray]:
    """Build point transfers from complex BEM RAOs and the existing rigid-point formula."""

    deck_points = list(deck_points)
    source_omega = _validate_frequency_axis(np.asarray(deck_rao["frequencies_rad_s"], dtype=float), "BEM frequencies")
    target = np.asarray(target_omega, dtype=float)
    if target.size and (target[0] < source_omega[0] or target[-1] > source_omega[-1]):
        raise ValueError("Synthesis frequencies must stay inside the BEM frequency range")
    indexed = {point["id"]: point for point in deck_rao["points"]}
    if "landing_center" not in indexed:
        raise ValueError("deck-point-rao.json must contain landing_center")

    center_rows = _point_rows(indexed["landing_center"], heading_deg)
    center_motion = _source_motion_from_rows(center_rows)
    center_position = next(
        [float(value) for value in point["position_m"]]
        for point in deck_points
        if point["id"] == "landing_center"
    )
    generalized = _generalized_motion_from_center(center_motion, center_position)

    signal_names: list[str] = []
    transfers: list[np.ndarray] = []
    for point in deck_points:
        point_id = str(point["id"])
        source_id = point.get("source_id") or point_id
        if point.get("kind") == "generic_sampling" and source_id in indexed:
            source_motion = _source_motion_from_rows(_point_rows(indexed[source_id], heading_deg))
        else:
            source_motion = _transform_motion(generalized, point["position_m"])

        displacement = {
            axis: interpolate_complex_rao(
                source_omega,
                source_motion["displacement_m"][axis],
                target,
            )
            for axis in ("x", "y", "z")
        }
        signal_names.append(f"{point_id}.z_m")
        transfers.append(displacement["z"])
        signal_names.append(f"{point_id}.vz_m_s")
        transfers.append(1j * target * displacement["z"])

    center_angles = {
        axis: interpolate_complex_rao(source_omega, center_motion["angles_rad"][axis], target)
        for axis in ("roll", "pitch", "yaw")
    }
    for axis, name in (
        ("roll", "platform.roll_rad"),
        ("pitch", "platform.pitch_rad"),
    ):
        signal_names.append(name)
        transfers.append(center_angles[axis])
    for axis, name in (
        ("roll", "platform.roll_rate_rad_s"),
        ("pitch", "platform.pitch_rate_rad_s"),
    ):
        signal_names.append(name)
        transfers.append(1j * target * center_angles[axis])
    return signal_names, np.asarray(transfers, dtype=complex)


def spectrum_component_amplitudes(
    omega: np.ndarray,
    hs_m: float,
    tp_s: float,
    gamma: float,
) -> tuple[np.ndarray, np.ndarray]:
    frequencies = _validate_frequency_axis(np.asarray(omega, dtype=float), "synthesis frequencies")
    if frequencies.size < 2:
        raise ValueError("At least two synthesis frequencies are required")
    delta = np.diff(frequencies)
    if not np.allclose(delta, delta[0], rtol=0.0, atol=1.0e-12):
        raise ValueError("The synthesis frequency grid must be uniform")
    density = np.asarray(jonswap_spectrum(frequencies.tolist(), float(hs_m), float(tp_s), float(gamma)), dtype=float)
    weights = np.full(frequencies.size, float(delta[0]), dtype=float)
    weights[[0, -1]] *= 0.5
    return density, np.sqrt(2.0 * density * weights)


def _synthesis_fft_parameters(omega: np.ndarray, time_s: np.ndarray, n_fft: int | None) -> tuple[int, float]:
    frequencies = _validate_frequency_axis(omega, "synthesis frequencies")
    delta = float(frequencies[1] - frequencies[0])
    repeat_period = 2.0 * math.pi / delta
    time = np.asarray(time_s, dtype=float)
    if time.ndim != 1 or time.size == 0 or not np.all(np.isfinite(time)):
        raise ValueError("time_s must be a finite one-dimensional array")
    if np.any(np.diff(time) <= 0.0):
        raise ValueError("time_s must be strictly increasing")
    if time[-1] >= repeat_period - 1.0e-10:
        raise ValueError("time_s reaches the synthesis grid repeat period")
    if n_fft is None:
        dt = float(np.median(np.diff(time))) if time.size > 1 else repeat_period / 4096.0
        n_fft = int(math.ceil(repeat_period / dt))
    n_fft = int(n_fft)
    minimum_fft_size = 2 * (frequencies.size - 1) + 2
    if n_fft < minimum_fft_size:
        raise ValueError("n_fft is too short for the synthesis frequency grid")
    return n_fft, repeat_period / n_fft


def synthesize_response_batch(
    transfer: np.ndarray,
    component_amplitudes: np.ndarray,
    phases_rad: np.ndarray,
    omega: np.ndarray,
    time_s: np.ndarray,
    n_fft: int | None = None,
) -> np.ndarray:
    """Synthesize arbitrary endpoint-aligned fine-grid frequencies in batches.

    The complex inverse FFT evaluates the harmonic grid in a period longer than each
    requested record; a carrier restores the nonzero BEM lower-frequency endpoint.
    """

    transfers = np.asarray(transfer, dtype=complex)
    amplitudes = np.asarray(component_amplitudes, dtype=float)
    phases = np.asarray(phases_rad, dtype=float)
    frequencies = _validate_frequency_axis(np.asarray(omega, dtype=float), "synthesis frequencies")
    time = np.asarray(time_s, dtype=float)
    if transfers.ndim != 2 or transfers.shape[1] != frequencies.size:
        raise ValueError("transfer must have shape (signals, frequencies)")
    if amplitudes.ndim != 1 or amplitudes.size != frequencies.size:
        raise ValueError("component_amplitudes must match omega")
    if phases.ndim != 2 or phases.shape[1] != frequencies.size:
        raise ValueError("phases_rad must have shape (realizations, frequencies)")
    if not np.all(np.isfinite(phases)):
        raise ValueError("phases_rad must be finite")
    n_fft, base_dt = _synthesis_fft_parameters(frequencies, time, n_fft)
    batch_count = phases.shape[0]
    coefficient = np.zeros((batch_count, transfers.shape[0], n_fft), dtype=complex)
    coefficient[:, :, : frequencies.size] = (
        n_fft
        * transfers[None, :, :]
        * amplitudes[None, None, :]
        * np.exp(1j * phases[:, None, :])
    )
    analytic = np.fft.ifft(coefficient, axis=-1)
    left = np.floor(time / base_dt).astype(int)
    fraction = time / base_dt - left
    right = (left + 1) % n_fft
    interpolated = analytic[:, :, left] * (1.0 - fraction)[None, None, :] + analytic[:, :, right] * fraction[None, None, :]
    carrier = np.exp(1j * frequencies[0] * time)[None, None, :]
    return np.real(interpolated * carrier)


def synthesize_response_on_fine_grid(
    transfer: np.ndarray,
    component_amplitudes: np.ndarray,
    phases_rad: np.ndarray,
    omega: np.ndarray,
    time_s: np.ndarray,
    n_fft: int | None = None,
) -> np.ndarray:
    phases = np.asarray(phases_rad, dtype=float)
    if phases.ndim != 1:
        raise ValueError("phases_rad must be one-dimensional for a single realization")
    return synthesize_response_batch(
        transfer,
        component_amplitudes,
        phases[None, :],
        omega,
        time_s,
        n_fft,
    )[0]


def response_metrics_batch(
    signal_names: list[str],
    response: np.ndarray,
    physical_leg_ids: Sequence[str],
    all_point_ids: Sequence[str],
    platform: dict[str, Any],
    free_surface_z_m: float = 0.0,
) -> dict[str, np.ndarray]:
    values = np.asarray(response, dtype=float)
    if values.ndim != 3 or values.shape[1] != len(signal_names):
        raise ValueError("response must have shape (realizations, signals, time)")
    index = {name: position for position, name in enumerate(signal_names)}

    def series(name: str) -> np.ndarray:
        if name not in index:
            raise KeyError(f"Missing synthesized signal: {name}")
        return values[:, index[name], :]

    metrics: dict[str, np.ndarray] = {}
    for point_id in all_point_ids:
        metrics[f"{point_id}.max_abs_vertical_velocity_m_s"] = np.max(
            np.abs(series(f"{point_id}.vz_m_s")), axis=1
        )

    leg_z = np.stack([series(f"{point_id}.z_m") for point_id in physical_leg_ids], axis=1)
    leg_vz = np.stack([series(f"{point_id}.vz_m_s") for point_id in physical_leg_ids], axis=1)
    roll = series("platform.roll_rad")
    pitch = series("platform.pitch_rad")
    roll_rate = series("platform.roll_rate_rad_s")
    pitch_rate = series("platform.pitch_rate_rad_s")
    metrics["four_feet.max_vertical_span_m"] = np.max(np.ptp(leg_z, axis=1), axis=1)
    metrics["four_feet.max_vertical_velocity_span_m_s"] = np.max(np.ptp(leg_vz, axis=1), axis=1)
    metrics["platform.max_tilt_deg"] = np.degrees(np.max(np.hypot(roll, pitch), axis=1))
    metrics["platform.max_tilt_rate_deg_s"] = np.degrees(np.max(np.hypot(roll_rate, pitch_rate), axis=1))

    edge_x = float(platform["length_m"]) * 0.5
    edge_y = float(platform["beam_m"]) * 0.5
    edge_offsets = np.asarray(
        [
            [-edge_x, -edge_y],
            [-edge_x, edge_y],
            [edge_x, -edge_y],
            [edge_x, edge_y],
        ],
        dtype=float,
    )
    heave = series("landing_center.z_m")
    edge_elevation = (
        float(platform["deck_z_m"])
        + heave[:, None, :]
        + roll[:, None, :] * edge_offsets[None, :, 1, None]
        - pitch[:, None, :] * edge_offsets[None, :, 0, None]
    )
    immersion = np.maximum(float(free_surface_z_m) - edge_elevation, 0.0)
    dynamic_edge_elevation = edge_elevation - float(platform["deck_z_m"])
    metrics["deck_edge.minimum_dynamic_elevation_m"] = np.min(dynamic_edge_elevation, axis=(1, 2))
    metrics["deck_edge.max_immersion_m"] = np.max(immersion, axis=(1, 2))
    return metrics


def bootstrap_quantile_ci(
    values: np.ndarray,
    quantile: float = 0.95,
    confidence_level: float = BOOTSTRAP_CONFIDENCE_LEVEL,
    resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
    seed: int = 0,
) -> dict[str, Any]:
    observations = np.asarray(values, dtype=float)
    if observations.ndim != 1 or observations.size == 0 or not np.all(np.isfinite(observations)):
        raise ValueError("values must be a non-empty finite one-dimensional array")
    if not 0.0 < quantile < 1.0:
        raise ValueError("quantile must lie between zero and one")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must lie between zero and one")
    if int(resamples) < 1:
        raise ValueError("resamples must be positive")
    resample_count = int(resamples)
    if observations.size == 1:
        lower = upper = float(observations[0])
    else:
        rng = np.random.default_rng(int(seed))
        bootstrap_quantiles = np.empty(resample_count, dtype=float)
        batch_size = max(1, min(128, resample_count))
        for start in range(0, resample_count, batch_size):
            stop = min(resample_count, start + batch_size)
            indices = rng.integers(0, observations.size, size=(stop - start, observations.size))
            bootstrap_quantiles[start:stop] = np.quantile(observations[indices], quantile, axis=1)
        tail = 0.5 * (1.0 - confidence_level)
        lower, upper = np.quantile(bootstrap_quantiles, [tail, 1.0 - tail])
        lower = float(lower)
        upper = float(upper)
    return {
        "lower": lower,
        "upper": upper,
        "confidence_level": float(confidence_level),
        "resamples": resample_count,
        "method": "percentile bootstrap over realization-level statistic",
        "seed": int(seed),
    }


def summarize_samples(
    samples: list[dict[str, float]],
    bootstrap_resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = 0,
) -> dict[str, dict[str, Any]]:
    if not samples:
        raise ValueError("samples must not be empty")
    output: dict[str, dict[str, Any]] = {}
    metrics = [metric for metric in samples[0] if metric != "seed"]
    for metric_index, metric in enumerate(metrics):
        values = np.asarray([row[metric] for row in samples], dtype=float)
        if not np.all(np.isfinite(values)):
            raise ValueError(f"Non-finite values in metric {metric}")
        p95_ci = bootstrap_quantile_ci(
            values,
            quantile=0.95,
            confidence_level=BOOTSTRAP_CONFIDENCE_LEVEL,
            resamples=bootstrap_resamples,
            seed=int(bootstrap_seed) + metric_index,
        )
        output[metric] = {
            "mean": float(np.mean(values)),
            "standard_deviation": float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
            "p50": float(np.quantile(values, 0.50)),
            "p95": float(np.quantile(values, 0.95)),
            "p99": float(np.quantile(values, 0.99)),
            "maximum": float(np.max(values)),
            "p95_bootstrap_95ci": p95_ci,
        }
    return output


def scale_linear_statistics(
    statistics: dict[str, dict[str, Any]],
    scale: float,
) -> dict[str, dict[str, Any]]:
    """Scale realization statistics and their bootstrap CI for a linear Hs change."""

    factor = float(scale)
    if factor <= 0.0 or not math.isfinite(factor):
        raise ValueError("Linear statistics scale must be positive and finite")
    output: dict[str, dict[str, Any]] = {}
    for metric, values in statistics.items():
        scaled = {
            key: factor * float(value)
            for key, value in values.items()
            if key != "p95_bootstrap_95ci"
        }
        ci = values["p95_bootstrap_95ci"]
        scaled["p95_bootstrap_95ci"] = {
            **ci,
            "lower": factor * float(ci["lower"]),
            "upper": factor * float(ci["upper"]),
            "scaled_from_reference_hs": True,
            "scale_factor": factor,
        }
        output[metric] = scaled
    return output


def _normalized_autocorrelation(values: np.ndarray) -> np.ndarray:
    signal = np.asarray(values, dtype=float)
    centered = signal - float(np.mean(signal))
    variance = float(np.dot(centered, centered))
    if variance <= 0.0:
        return np.concatenate(([1.0], np.zeros(max(0, signal.size - 1), dtype=float)))
    fft_size = 1
    while fft_size < 2 * signal.size:
        fft_size *= 2
    spectrum = np.fft.rfft(centered, n=fft_size)
    autocorrelation = np.fft.irfft(spectrum * np.conjugate(spectrum), n=fft_size)[: signal.size]
    return autocorrelation / autocorrelation[0]


def periodicity_diagnostics(
    signal: np.ndarray,
    dt_s: float,
    repeat_period_s: float,
    record_duration_s: float | None = None,
) -> dict[str, Any]:
    values = np.asarray(signal, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("signal must have at least two samples")
    dt_s = float(dt_s)
    repeat_period_s = float(repeat_period_s)
    if dt_s <= 0.0 or repeat_period_s <= 0.0:
        raise ValueError("dt_s and repeat_period_s must be positive")
    record_duration = float(record_duration_s) if record_duration_s is not None else values.size * dt_s
    autocorrelation = _normalized_autocorrelation(values)
    repeat_lag = int(round(repeat_period_s / dt_s))
    repeat_in_record = repeat_period_s <= record_duration + 1.0e-12
    autocorrelation_at_repeat = None
    duplicate_error = None

    def segment_correlation(lag: int) -> float | None:
        if not 0 < lag < values.size:
            return None
        first = values[:-lag]
        second = values[lag:]
        first_centered = first - float(np.mean(first))
        second_centered = second - float(np.mean(second))
        denominator = float(np.linalg.norm(first_centered) * np.linalg.norm(second_centered))
        if denominator <= 0.0:
            return None
        return float(np.dot(first_centered, second_centered) / denominator)

    if 0 < repeat_lag < values.size:
        autocorrelation_at_repeat = segment_correlation(repeat_lag)
        scale = max(float(np.sqrt(np.mean(values**2))), 1.0e-14)
        duplicate_error = float(np.sqrt(np.mean((values[repeat_lag:] - values[:-repeat_lag]) ** 2)) / scale)

    probes: dict[str, float | None] = {}
    for fraction in (0.25, 0.5, 0.75, 1.0):
        lag_s = fraction * repeat_period_s
        lag = int(round(lag_s / dt_s))
        probes[f"{fraction:g}_repeat_period"] = segment_correlation(lag)
    before_repeat = autocorrelation[1 : min(values.size, max(2, repeat_lag))]
    return {
        "record_duration_s": record_duration,
        "dt_s": dt_s,
        "repeat_period_s": repeat_period_s,
        "repeat_lag_samples": repeat_lag,
        "record_covers_repeat_period": bool(repeat_in_record),
        "duplicate_period_relative_rms_error": duplicate_error,
        "autocorrelation": {
            "normalization": "demeaned signal autocorrelation divided by lag-zero value",
            "at_repeat_period": autocorrelation_at_repeat,
            "at_fractional_repeat_periods": probes,
            "maximum_absolute_before_repeat": float(np.max(np.abs(before_repeat))) if before_repeat.size else None,
        },
        "pass": not repeat_in_record,
    }


def rao_kinematic_consistency(deck_rao: dict[str, Any]) -> dict[str, Any]:
    max_velocity_error = 0.0
    max_rate_error = 0.0
    for point in deck_rao["points"]:
        for row in point["rows"]:
            omega = float(row["frequency_rad_s"])
            for axis in ("x", "y", "z"):
                displacement = _complex_value(row, "displacement_m", axis)
                velocity = _complex_value(row, "velocity_m_s", axis)
                max_velocity_error = max(max_velocity_error, abs(velocity - 1j * omega * displacement))
            for axis in ("roll", "pitch", "yaw"):
                angle = _complex_value(row, "angles_rad", axis)
                rate = _complex_value(row, "angle_rates_rad_s", axis)
                max_rate_error = max(max_rate_error, abs(rate - 1j * omega * angle))
    return {
        "formula": "velocity = i*omega*displacement; angle_rate = i*omega*angle",
        "maximum_absolute_velocity_error": float(max_velocity_error),
        "maximum_absolute_angle_rate_error": float(max_rate_error),
        "pass": bool(max_velocity_error <= 1.0e-9 and max_rate_error <= 1.0e-9),
    }


def _relative_spectrum_m0(density: np.ndarray, omega: np.ndarray, hs_m: float) -> float:
    target = float(hs_m) ** 2 / 16.0
    actual = float(np.trapezoid(density, omega))
    return abs(actual - target) / max(abs(target), 1.0e-14)


def _case_linear_validity(
    statistics: dict[str, dict[str, Any]],
    samples: list[dict[str, float]],
    tilt_threshold_deg: float,
    edge_tolerance_m: float = 1.0e-12,
) -> dict[str, Any]:
    tilt_metric = statistics["platform.max_tilt_deg"]
    immersion_metric = statistics["deck_edge.max_immersion_m"]
    maximum_tilt = float(tilt_metric["maximum"])
    maximum_immersion = float(immersion_metric["maximum"])
    immersed_count = sum(float(row["deck_edge.max_immersion_m"]) > edge_tolerance_m for row in samples)
    return {
        "tilt_threshold_deg": float(tilt_threshold_deg),
        "maximum_observed_tilt_deg": maximum_tilt,
        "p95_tilt_deg": float(tilt_metric["p95"]),
        "tilt_threshold_pass": bool(maximum_tilt <= float(tilt_threshold_deg)),
        "deck_edge_immersion": {
            "metric": "positive depth below mean free surface at any deck corner",
            "maximum_immersion_m": maximum_immersion,
            "immersed_realization_count": int(immersed_count),
            "realization_count": len(samples),
            "tolerance_m": float(edge_tolerance_m),
            "pass": bool(maximum_immersion <= edge_tolerance_m),
        },
        "pass": bool(maximum_tilt <= float(tilt_threshold_deg) and maximum_immersion <= edge_tolerance_m),
    }


def _sample_finite(samples: list[dict[str, float]]) -> bool:
    return all(math.isfinite(float(value)) for row in samples for value in row.values())


def build_report(
    seed_count: int = MIN_REALIZATIONS,
    seed_start: int = 202600,
    duration_s: float = 600.0,
    dt_s: float = 0.1,
    delta_omega: float = DEFAULT_MAX_DELTA_OMEGA_RAD_S,
    bootstrap_resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
    batch_size: int = DEFAULT_BATCH_SIZE,
    case_dir: Path = CASE_DIR,
    rao_path: Path = RAO_PATH,
    leg_layout_path: Path = LEG_LAYOUT_PATH,
) -> dict[str, Any]:
    seed_count = int(seed_count)
    if seed_count < MIN_REALIZATIONS:
        raise ValueError(f"seed_count must be at least {MIN_REALIZATIONS} realizations")
    duration_s = float(duration_s)
    if duration_s not in SUPPORTED_DURATIONS_S:
        raise ValueError(f"duration_s must be one of {SUPPORTED_DURATIONS_S}")
    dt_s = float(dt_s)
    if dt_s <= 0.0 or not math.isfinite(dt_s):
        raise ValueError("dt_s must be positive and finite")
    if int(batch_size) < 1:
        raise ValueError("batch_size must be positive")
    if int(bootstrap_resamples) < 1:
        raise ValueError("bootstrap_resamples must be positive")
    if float(delta_omega) <= 0.0 or float(delta_omega) > DEFAULT_MAX_DELTA_OMEGA_RAD_S + 1.0e-15:
        raise ValueError(f"delta_omega must be in (0, {DEFAULT_MAX_DELTA_OMEGA_RAD_S}]")

    config = read_json(Path(case_dir) / "platform_config.json")
    deck_rao = read_json(Path(rao_path))
    bem_omega = _validate_frequency_axis(np.asarray(deck_rao["frequencies_rad_s"], dtype=float), "BEM frequencies")
    if bem_omega.size < MINIMUM_BEM_FREQUENCY_COUNT:
        raise ValueError(f"Expected at least {MINIMUM_BEM_FREQUENCY_COUNT} BEM frequencies, found {bem_omega.size}")
    leg_layout = load_existing_leg_layout(Path(leg_layout_path))
    deck_point_sets = build_revision_deck_points(config, leg_layout)
    deck_points = deck_point_sets["all"]
    all_point_ids = [str(point["id"]) for point in deck_points]
    physical_leg_ids = [str(point["id"]) for point in deck_point_sets["physical_legs"]]
    grid = build_synthesis_frequency_grid(bem_omega, duration_s, delta_omega)
    target_omega = np.asarray(grid["omega_rad_s"], dtype=float)
    sample_count = int(round(duration_s / dt_s))
    if sample_count < 2 or not math.isclose(sample_count * dt_s, duration_s, rel_tol=0.0, abs_tol=1.0e-8):
        raise ValueError("duration_s must contain an integer number of dt_s samples")
    time_s = np.arange(sample_count, dtype=float) * dt_s
    tilt_reference = read_json(Path(leg_layout_path))["config"]["validation_targets"]
    thies_incident_envelope_deg = float(tilt_reference["max_incident_angle_deg"])
    tilt_threshold_deg = LINEAR_TILT_SCREENING_DEG
    kinematic_check = rao_kinematic_consistency(deck_rao)
    headings = [float(value) for value in config["headings_deg"]]
    seed_ids = list(range(int(seed_start), int(seed_start) + seed_count))
    transfer_by_heading = {
        heading: build_revision_transfer_matrix(deck_rao, heading, target_omega, deck_points) for heading in headings
    }
    spectrum_reference_hs = {
        (float(state["tp_s"]), float(state.get("gamma", 3.3))): min(
            float(candidate["hs_m"])
            for candidate in config["sea_states"]
            if float(candidate["tp_s"]) == float(state["tp_s"])
            and float(candidate.get("gamma", 3.3)) == float(state.get("gamma", 3.3))
        )
        for state in config["sea_states"]
    }
    synthesis_cache: dict[tuple[float, float, float], dict[str, Any]] = {}
    cases: list[dict[str, Any]] = []
    for sea_state in config["sea_states"]:
        hs_m = float(sea_state["hs_m"])
        tp_s = float(sea_state["tp_s"])
        gamma = float(sea_state.get("gamma", 3.3))
        density, _state_amplitudes = spectrum_component_amplitudes(target_omega, hs_m, tp_s, gamma)
        reference_hs = spectrum_reference_hs[(tp_s, gamma)]
        scale = hs_m / reference_hs
        for heading_index, heading_deg in enumerate(headings):
            cache_key = (tp_s, gamma, heading_deg)
            if cache_key not in synthesis_cache:
                signal_names, transfer = transfer_by_heading[heading_deg]
                _reference_density, reference_amplitudes = spectrum_component_amplitudes(
                    target_omega, reference_hs, tp_s, gamma
                )
                base_samples: list[dict[str, float]] = []
                representative_response: np.ndarray | None = None
                for start in range(0, seed_count, int(batch_size)):
                    batch_seed_ids = seed_ids[start : start + int(batch_size)]
                    phases = np.asarray(
                        [np.random.default_rng(seed).uniform(0.0, 2.0 * math.pi, target_omega.size) for seed in batch_seed_ids],
                        dtype=float,
                    )
                    response = synthesize_response_batch(
                        transfer,
                        reference_amplitudes,
                        phases,
                        target_omega,
                        time_s,
                    )
                    if representative_response is None:
                        representative_response = response[0].copy()
                    metric_arrays = response_metrics_batch(
                        signal_names,
                        response,
                        physical_leg_ids,
                        all_point_ids,
                        config["platform"],
                    )
                    for row_index, seed in enumerate(batch_seed_ids):
                        row: dict[str, float] = {"seed": int(seed)}
                        row.update({metric: float(values[row_index]) for metric, values in metric_arrays.items()})
                        base_samples.append(row)
                if representative_response is None:
                    raise RuntimeError("No representative response was generated")
                bootstrap_seed = int(seed_start) + int(round(tp_s * 100.0)) * 1009 + heading_index * 97
                synthesis_cache[cache_key] = {
                    "signal_names": signal_names,
                    "base_samples": base_samples,
                    "base_statistics": summarize_samples(
                        base_samples,
                        bootstrap_resamples=int(bootstrap_resamples),
                        bootstrap_seed=bootstrap_seed,
                    ),
                    "representative_response": representative_response,
                    "reference_hs_m": reference_hs,
                    "bootstrap_seed": bootstrap_seed,
                }
            cached = synthesis_cache[cache_key]
            signal_names = cached["signal_names"]
            representative_response = cached["representative_response"]
            samples = []
            for base_row in cached["base_samples"]:
                row: dict[str, float] = {"seed": int(base_row["seed"])}
                for metric, value in base_row.items():
                    if metric == "seed" or metric == "deck_edge.max_immersion_m":
                        continue
                    row[metric] = scale * float(value)
                minimum_dynamic = row["deck_edge.minimum_dynamic_elevation_m"]
                row["deck_edge.max_immersion_m"] = max(
                    0.0,
                    -(float(config["platform"]["deck_z_m"]) + minimum_dynamic),
                )
                samples.append(row)
            summary = scale_linear_statistics(cached["base_statistics"], scale)
            if not math.isclose(scale, 1.0, rel_tol=0.0, abs_tol=1.0e-15):
                immersion_summary = summarize_samples(
                    [
                        {"seed": int(row["seed"]), "deck_edge.max_immersion_m": float(row["deck_edge.max_immersion_m"])}
                        for row in samples
                    ],
                    bootstrap_resamples=int(bootstrap_resamples),
                    bootstrap_seed=int(cached["bootstrap_seed"]) + 7919,
                )
                summary["deck_edge.max_immersion_m"] = immersion_summary["deck_edge.max_immersion_m"]
            representative_signal_index = signal_names.index("landing_center.vz_m_s")
            periodicity = periodicity_diagnostics(
                representative_response[representative_signal_index],
                dt_s,
                float(grid["implied_repeat_period_s"]),
                duration_s,
            )
            linear_validity = _case_linear_validity(summary, samples, tilt_threshold_deg)
            cases.append(
                {
                    "sea_state_id": sea_state["id"],
                    "hs_m": hs_m,
                    "tp_s": tp_s,
                    "gamma": gamma,
                    "heading_deg": heading_deg,
                    "spectral_m0_m2": float(np.trapezoid(density, target_omega)),
                    "samples": samples,
                    "statistics": summary,
                    "linear_validity": linear_validity,
                    "periodicity": periodicity,
                }
            )

    target_m0 = {str(state["id"]): float(state["hs_m"]) ** 2 / 16.0 for state in config["sea_states"]}
    m0_errors = [
        abs(float(case["spectral_m0_m2"]) - target_m0[str(case["sea_state_id"])]) / target_m0[str(case["sea_state_id"])]
        for case in cases
    ]
    case_index = {(str(case["sea_state_id"]), float(case["heading_deg"])): case for case in cases}
    metric_names = [
        metric
        for metric in cases[0]["statistics"]
        if metric != "deck_edge.max_immersion_m"
    ]
    linearity_errors: list[float] = []
    tp_values = sorted({float(state["tp_s"]) for state in config["sea_states"]})
    for tp_s in tp_values:
        same_period = [state for state in config["sea_states"] if float(state["tp_s"]) == tp_s]
        baseline_state = min(same_period, key=lambda state: float(state["hs_m"]))
        baseline_hs = float(baseline_state["hs_m"])
        for heading_deg in headings:
            baseline = case_index[(str(baseline_state["id"]), heading_deg)]
            for state in same_period:
                scale = float(state["hs_m"]) / baseline_hs
                scaled = case_index[(str(state["id"]), heading_deg)]
                for metric in metric_names:
                    expected = scale * float(baseline["statistics"][metric]["p95"])
                    actual = float(scaled["statistics"][metric]["p95"])
                    linearity_errors.append(abs(actual - expected) / max(abs(expected), 1.0e-14))

    all_finite = all(_sample_finite(case["samples"]) for case in cases)
    maximum_m0_error = max(m0_errors)
    maximum_linearity_error = max(linearity_errors)
    linearity_validity = {
        "tilt_threshold_deg": tilt_threshold_deg,
        "tilt_threshold_source": "conservative numerical validity-screening convention selected within the reviewer's recommended 3-5 deg range",
        "tilt_threshold_semantics": "A 5 deg flag for the fixed-wetted-surface linear model, not a barge qualification or landing-success limit.",
        "thies_vehicle_incident_angle_envelope_deg_for_context_only": thies_incident_envelope_deg,
        "maximum_observed_tilt_deg": max(float(case["linear_validity"]["maximum_observed_tilt_deg"]) for case in cases),
        "tilt_threshold_pass": all(bool(case["linear_validity"]["tilt_threshold_pass"]) for case in cases),
        "maximum_observed_deck_edge_immersion_m": max(
            float(case["linear_validity"]["deck_edge_immersion"]["maximum_immersion_m"]) for case in cases
        ),
        "deck_edge": {
            "edge_positions_m": [
                [-float(config["platform"]["length_m"]) * 0.5, -float(config["platform"]["beam_m"]) * 0.5],
                [-float(config["platform"]["length_m"]) * 0.5, float(config["platform"]["beam_m"]) * 0.5],
                [float(config["platform"]["length_m"]) * 0.5, -float(config["platform"]["beam_m"]) * 0.5],
                [float(config["platform"]["length_m"]) * 0.5, float(config["platform"]["beam_m"]) * 0.5],
            ],
            "deck_z_m": float(config["platform"]["deck_z_m"]),
            "free_surface_z_m": 0.0,
            "free_surface_source": "existing HAMS barge mesh convention: waterplane z=0",
        },
        "deck_edge_immersion_pass": all(
            bool(case["linear_validity"]["deck_edge_immersion"]["pass"]) for case in cases
        ),
        "interpretation": "This is a platform-only small-angle and mean-free-surface edge check, not a nonlinear slamming or green-water criterion.",
    }
    representative_periodicity = cases[0]["periodicity"]
    numerical_acceptance_pass = bool(
        len(cases) == len(config["sea_states"]) * len(headings)
        and all(len(case["samples"]) >= MIN_REALIZATIONS for case in cases)
        and all_finite
        and maximum_m0_error <= 1.0e-12
        and maximum_linearity_error <= 1.0e-12
        and float(grid["delta_omega_rad_s"]) <= float(delta_omega) + 1.0e-12
        and not bool(grid["record_covers_repeat_period"])
        and bool(kinematic_check["pass"])
    )
    validity_acceptance_pass = bool(
        linearity_validity["tilt_threshold_pass"] and linearity_validity["deck_edge_immersion_pass"]
    )
    overall_acceptance_status = (
        "PASS"
        if numerical_acceptance_pass and validity_acceptance_pass
        else "NUMERICAL_PASS_OUTSIDE_LINEAR_VALIDITY"
        if numerical_acceptance_pass
        else "FAIL"
    )
    return {
        "case_id": config["case_id"],
        "status": "computed_linear_wave_screening_not_coupled_landing_probability",
        "method": {
            "hydrodynamic_source": _source_label(Path(rao_path)),
            "wave_model": "JONSWAP scaled on the random synthesis grid to m0=Hs^2/16",
            "synthesis": "random-phase linear superposition using complex-interpolated HAMS deck-point RAOs and a non-repeating harmonic-grid inverse FFT",
            "linear_hs_reuse": "For identical Tp, gamma, heading and random phases, one reference-Hs realization set is synthesized and all motion metrics are scaled analytically by Hs; deck-edge immersion is recomputed after adding the fixed 3 m freeboard.",
            "duration_s": duration_s,
            "dt_s": dt_s,
            "sample_count": sample_count,
            "seed_start": int(seed_start),
            "seed_count": seed_count,
            "realizations_per_case": seed_count,
            "bootstrap_resamples": int(bootstrap_resamples),
            "bootstrap_confidence_level": BOOTSTRAP_CONFIDENCE_LEVEL,
            "frequency_min_rad_s": float(target_omega[0]),
            "frequency_max_rad_s": float(target_omega[-1]),
            "frequency_step_rad_s": float(grid["delta_omega_rad_s"]),
            "maximum_allowed_frequency_step_rad_s": float(delta_omega),
            "maximum_relative_spectrum_m0_error": maximum_m0_error,
        },
        "frequency_grids": {
            "bem": {
                "role": "HAMS/BEM input frequency axis kept distinct from the stochastic synthesis grid",
                "count": int(bem_omega.size),
                "frequencies_rad_s": [float(value) for value in bem_omega],
            },
            "random_synthesis": {
                "role": "fine random-wave synthesis frequency axis",
                "count": int(grid["frequency_count"]),
                "frequencies_rad_s": [float(value) for value in target_omega],
                "delta_omega_rad_s": float(grid["delta_omega_rad_s"]),
                "maximum_allowed_delta_omega_rad_s": float(delta_omega),
                "implied_repeat_period_s": float(grid["implied_repeat_period_s"]),
                "record_duration_s": duration_s,
                "record_covers_repeat_period": bool(grid["record_covers_repeat_period"]),
            },
        },
        "rao_interpolation": {
            "method": "linear interpolation of real and imaginary parts of each complex RAO",
            "phase_handling": "complex phase is retained; no magnitude-only interpolation is used",
            "velocity_formula_after_interpolation": "velocity = i*omega*displacement",
            "angle_rate_formula_after_interpolation": "angle_rate = i*omega*angle",
        },
        "leg_layout": leg_layout,
        "deck_points": deck_point_sets,
        "scope_boundary": {
            "included": "Correlated linear wave-frequency motion at the landing center, four actual-radius leg points, and the existing generic sampling points.",
            "excluded": "No touchdown timing policy, plume, GNC, DP controller, Chrono contact, rocket-platform feedback, wave-surface phase, slamming, or green-water model is included.",
        },
        "checks": {
            "bem_frequency_count": {
                "actual": int(bem_omega.size),
                "minimum": MINIMUM_BEM_FREQUENCY_COUNT,
                "pass": bool(bem_omega.size >= MINIMUM_BEM_FREQUENCY_COUNT),
            },
            "fine_frequency_step": {
                "actual_rad_s": float(grid["delta_omega_rad_s"]),
                "maximum_allowed_rad_s": float(delta_omega),
                "pass": bool(grid["delta_omega_rad_s"] <= float(delta_omega) + 1.0e-12),
            },
            "rao_kinematic_consistency": kinematic_check,
            "periodicity": representative_periodicity,
            "linear_validity": linearity_validity,
        },
        "acceptance": {
            "status": overall_acceptance_status,
            "numerical_verification_pass": numerical_acceptance_pass,
            "all_cases_within_linear_validity": validity_acceptance_pass,
            "checks": {
                "case_count": {"actual": len(cases), "expected": len(config["sea_states"]) * len(headings)},
                "realizations_per_case": {"actual": min(len(case["samples"]) for case in cases), "minimum": MIN_REALIZATIONS},
                "all_values_finite": all_finite,
                "maximum_relative_spectrum_m0_error": maximum_m0_error,
                "maximum_relative_hs_linearity_error": maximum_linearity_error,
                "frequency_step_within_limit": float(grid["delta_omega_rad_s"]) <= float(delta_omega) + 1.0e-12,
                "no_repeat_period_in_record": not bool(grid["record_covers_repeat_period"]),
                "rao_kinematic_consistency": bool(kinematic_check["pass"]),
                "linear_validity": validity_acceptance_pass,
            },
            "claim": "Numerically reproducible linear HAMS/JONSWAP deck-motion screening with realization-level P95 bootstrap uncertainty.",
            "not_claimed": "Coupled landing success probability, nonlinear deck wetting, or operational sea-state qualification.",
        },
        "cases": cases,
    }


def write_summary_csv(report: dict[str, Any], path: Path = SUMMARY_CSV_PATH) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics = list(report["cases"][0]["statistics"])
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "sea_state_id",
                "hs_m",
                "tp_s",
                "heading_deg",
                "metric",
                "mean",
                "standard_deviation",
                "p50",
                "p95",
                "p95_bootstrap_ci_lower",
                "p95_bootstrap_ci_upper",
                "p99",
                "maximum",
            ]
        )
        for case in report["cases"]:
            for metric in metrics:
                values = case["statistics"][metric]
                ci = values["p95_bootstrap_95ci"]
                writer.writerow(
                    [
                        case["sea_state_id"],
                        case["hs_m"],
                        case["tp_s"],
                        case["heading_deg"],
                        metric,
                        values["mean"],
                        values["standard_deviation"],
                        values["p50"],
                        values["p95"],
                        ci["lower"],
                        ci["upper"],
                        values["p99"],
                        values["maximum"],
                    ]
                )
