from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .common import ROOT, read_json, write_json
    from .sea_state_response import jonswap_spectrum
    from .barge_wave_revision import (
        DEFAULT_BATCH_SIZE,
        DEFAULT_BOOTSTRAP_RESAMPLES,
        DEFAULT_MAX_DELTA_OMEGA_RAD_S,
        MIN_REALIZATIONS,
        REPORT_PATH as REVISION_REPORT_PATH,
        SUMMARY_CSV_PATH as REVISION_SUMMARY_CSV_PATH,
        SUPPORTED_DURATIONS_S,
        build_report as build_revision_report,
        write_summary_csv as write_revision_summary_csv,
    )
except ImportError:
    from common import ROOT, read_json, write_json
    from sea_state_response import jonswap_spectrum
    from barge_wave_revision import (
        DEFAULT_BATCH_SIZE,
        DEFAULT_BOOTSTRAP_RESAMPLES,
        DEFAULT_MAX_DELTA_OMEGA_RAD_S,
        MIN_REALIZATIONS,
        REPORT_PATH as REVISION_REPORT_PATH,
        SUMMARY_CSV_PATH as REVISION_SUMMARY_CSV_PATH,
        SUPPORTED_DURATIONS_S,
        build_report as build_revision_report,
        write_summary_csv as write_revision_summary_csv,
    )


CASE_DIR = ROOT / "RocketRecoveryCases" / "Barge_120x50"
RAO_PATH = CASE_DIR / "Output" / "RocketRecovery" / "deck-point-rao.json"
REPORT_PATH = CASE_DIR / "Output" / "RocketRecovery" / "wave-sensitivity.json"
SUMMARY_CSV_PATH = CASE_DIR / "Output" / "RocketRecovery" / "wave-sensitivity-summary.csv"


def _complex_value(row: dict[str, Any], group: str, axis: str) -> complex:
    value = row[group][axis]
    return complex(float(value["real"]), float(value["imag"]))


def _point_rows(point: dict[str, Any], heading_deg: float) -> list[dict[str, Any]]:
    return sorted(
        (row for row in point["rows"] if math.isclose(float(row["heading_deg"]), heading_deg, abs_tol=1.0e-9)),
        key=lambda row: float(row["frequency_rad_s"]),
    )


def _interpolate_complex(source_omega: np.ndarray, values: np.ndarray, target_omega: np.ndarray) -> np.ndarray:
    return np.interp(target_omega, source_omega, values.real) + 1j * np.interp(target_omega, source_omega, values.imag)


def build_transfer_matrix(deck_rao: dict[str, Any], heading_deg: float, target_omega: np.ndarray) -> tuple[list[str], np.ndarray]:
    point_order = ["landing_center", "leg_forward_port", "leg_forward_starboard", "leg_aft_port", "leg_aft_starboard"]
    indexed = {point["id"]: point for point in deck_rao["points"]}
    signal_names: list[str] = []
    transfers: list[np.ndarray] = []

    for point_id in point_order:
        rows = _point_rows(indexed[point_id], heading_deg)
        source_omega = np.asarray([float(row["frequency_rad_s"]) for row in rows], dtype=float)
        for group, axis, suffix in (
            ("displacement_m", "z", "z_m"),
            ("velocity_m_s", "z", "vz_m_s"),
        ):
            values = np.asarray([_complex_value(row, group, axis) for row in rows], dtype=complex)
            signal_names.append(f"{point_id}.{suffix}")
            transfers.append(_interpolate_complex(source_omega, values, target_omega))

    center_rows = _point_rows(indexed["landing_center"], heading_deg)
    source_omega = np.asarray([float(row["frequency_rad_s"]) for row in center_rows], dtype=float)
    for group, axis, name in (
        ("angles_rad", "roll", "platform.roll_rad"),
        ("angles_rad", "pitch", "platform.pitch_rad"),
        ("angle_rates_rad_s", "roll", "platform.roll_rate_rad_s"),
        ("angle_rates_rad_s", "pitch", "platform.pitch_rate_rad_s"),
    ):
        values = np.asarray([_complex_value(row, group, axis) for row in center_rows], dtype=complex)
        signal_names.append(name)
        transfers.append(_interpolate_complex(source_omega, values, target_omega))
    return signal_names, np.asarray(transfers, dtype=complex)


def fft_frequency_grid(duration_s: float, dt_s: float, omega_min: float, omega_max: float) -> tuple[int, np.ndarray, np.ndarray]:
    sample_count = int(round(duration_s / dt_s))
    if sample_count < 8 or not math.isclose(sample_count * dt_s, duration_s, rel_tol=0.0, abs_tol=1.0e-9):
        raise ValueError("duration_s must contain an integer number of time steps")
    omega_all = 2.0 * math.pi * np.fft.rfftfreq(sample_count, d=dt_s)
    indices = np.flatnonzero((omega_all >= omega_min) & (omega_all <= omega_max))
    if indices.size < 2:
        raise ValueError("FFT grid does not resolve the registered HAMS frequency band")
    return sample_count, indices, omega_all[indices]


def spectrum_component_amplitudes(omega: np.ndarray, hs_m: float, tp_s: float, gamma: float) -> tuple[np.ndarray, np.ndarray]:
    density = np.asarray(jonswap_spectrum(omega.tolist(), hs_m, tp_s, gamma), dtype=float)
    delta_omega = float(omega[1] - omega[0])
    weights = np.full(omega.size, delta_omega, dtype=float)
    weights[[0, -1]] *= 0.5
    amplitudes = np.sqrt(2.0 * density * weights)
    return density, amplitudes


def synthesize_response(
    transfer: np.ndarray,
    component_amplitudes: np.ndarray,
    phases_rad: np.ndarray,
    fft_indices: np.ndarray,
    sample_count: int,
) -> np.ndarray:
    coefficients = np.zeros((transfer.shape[0], sample_count // 2 + 1), dtype=complex)
    coefficients[:, fft_indices] = (
        0.5
        * sample_count
        * transfer
        * component_amplitudes[None, :]
        * np.exp(1j * phases_rad)[None, :]
    )
    return np.fft.irfft(coefficients, n=sample_count, axis=1)


def response_metrics(signal_names: list[str], response: np.ndarray) -> dict[str, float]:
    series = {name: response[index] for index, name in enumerate(signal_names)}
    point_ids = ["landing_center", "leg_forward_port", "leg_forward_starboard", "leg_aft_port", "leg_aft_starboard"]
    leg_ids = point_ids[1:]
    metrics = {
        f"{point_id}.max_abs_vertical_velocity_m_s": float(np.max(np.abs(series[f"{point_id}.vz_m_s"])))
        for point_id in point_ids
    }
    leg_z = np.asarray([series[f"{point_id}.z_m"] for point_id in leg_ids])
    leg_vz = np.asarray([series[f"{point_id}.vz_m_s"] for point_id in leg_ids])
    tilt = np.hypot(series["platform.roll_rad"], series["platform.pitch_rad"])
    tilt_rate = np.hypot(series["platform.roll_rate_rad_s"], series["platform.pitch_rate_rad_s"])
    metrics.update(
        {
            "four_feet.max_vertical_span_m": float(np.max(np.ptp(leg_z, axis=0))),
            "four_feet.max_vertical_velocity_span_m_s": float(np.max(np.ptp(leg_vz, axis=0))),
            "platform.max_tilt_deg": float(np.degrees(np.max(tilt))),
            "platform.max_tilt_rate_deg_s": float(np.degrees(np.max(tilt_rate))),
        }
    )
    return metrics


def summarize_samples(samples: list[dict[str, float]]) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for metric in samples[0]:
        if metric == "seed":
            continue
        values = np.asarray([row[metric] for row in samples], dtype=float)
        output[metric] = {
            "mean": float(np.mean(values)),
            "standard_deviation": float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
            "p50": float(np.quantile(values, 0.50)),
            "p95": float(np.quantile(values, 0.95)),
            "p99": float(np.quantile(values, 0.99)),
            "maximum": float(np.max(values)),
        }
    return output


def build_report(seed_count: int = 100, seed_start: int = 202600, duration_s: float = 600.0, dt_s: float = 0.1) -> dict[str, Any]:
    if seed_count < 2:
        raise ValueError("seed_count must be at least two for sample statistics")
    config = read_json(CASE_DIR / "platform_config.json")
    deck_rao = read_json(RAO_PATH)
    source_omega = np.asarray(deck_rao["frequencies_rad_s"], dtype=float)
    sample_count, fft_indices, target_omega = fft_frequency_grid(duration_s, dt_s, float(source_omega[0]), float(source_omega[-1]))
    headings = [float(value) for value in config["headings_deg"]]
    seed_ids = list(range(seed_start, seed_start + seed_count))
    cases: list[dict[str, Any]] = []

    for sea_state in config["sea_states"]:
        density, component_amplitudes = spectrum_component_amplitudes(
            target_omega,
            float(sea_state["hs_m"]),
            float(sea_state["tp_s"]),
            float(sea_state.get("gamma", 3.3)),
        )
        for heading_deg in headings:
            signal_names, transfer = build_transfer_matrix(deck_rao, heading_deg, target_omega)
            samples = []
            for seed in seed_ids:
                phases = np.random.default_rng(seed).uniform(0.0, 2.0 * math.pi, target_omega.size)
                response = synthesize_response(transfer, component_amplitudes, phases, fft_indices, sample_count)
                samples.append({"seed": seed, **response_metrics(signal_names, response)})
            cases.append(
                {
                    "sea_state_id": sea_state["id"],
                    "hs_m": float(sea_state["hs_m"]),
                    "tp_s": float(sea_state["tp_s"]),
                    "gamma": float(sea_state.get("gamma", 3.3)),
                    "heading_deg": heading_deg,
                    "spectral_m0_m2": float(np.trapezoid(density, target_omega)),
                    "samples": samples,
                    "statistics": summarize_samples(samples),
                }
            )

    target_m0 = {state["id"]: float(state["hs_m"]) ** 2 / 16.0 for state in config["sea_states"]}
    m0_errors = [
        abs(case["spectral_m0_m2"] - target_m0[case["sea_state_id"]]) / target_m0[case["sea_state_id"]]
        for case in cases
    ]
    metrics = list(cases[0]["statistics"])
    case_index = {(case["sea_state_id"], case["heading_deg"]): case for case in cases}
    linearity_errors = []
    for tp_s in (6, 8, 10):
        for heading_deg in headings:
            baseline = case_index[(f"Hs1_Tp{tp_s}", heading_deg)]
            for hs_m in (2, 3):
                scaled = case_index[(f"Hs{hs_m}_Tp{tp_s}", heading_deg)]
                for metric in metrics:
                    expected = hs_m * baseline["statistics"][metric]["p95"]
                    actual = scaled["statistics"][metric]["p95"]
                    denominator = max(abs(expected), 1.0e-14)
                    linearity_errors.append(abs(actual - expected) / denominator)
    all_finite = all(
        math.isfinite(float(value))
        for case in cases
        for sample in case["samples"]
        for value in sample.values()
    )
    maximum_m0_error = max(m0_errors)
    maximum_linearity_error = max(linearity_errors)
    acceptance_pass = (
        len(cases) == len(config["sea_states"]) * len(headings)
        and all(len(case["samples"]) == seed_count for case in cases)
        and all_finite
        and maximum_m0_error <= 1.0e-12
        and maximum_linearity_error <= 1.0e-12
    )
    return {
        "case_id": config["case_id"],
        "status": "computed_linear_wave_screening_not_coupled_landing_probability",
        "method": {
            "hydrodynamic_source": str(RAO_PATH.relative_to(ROOT).as_posix()),
            "wave_model": "JONSWAP scaled on the synthesis grid to m0=Hs^2/16",
            "synthesis": "random-phase linear superposition using interpolated complex HAMS deck-point RAOs and an inverse real FFT",
            "duration_s": duration_s,
            "dt_s": dt_s,
            "sample_count": sample_count,
            "seed_start": seed_start,
            "seed_count": seed_count,
            "frequency_min_rad_s": float(target_omega[0]),
            "frequency_max_rad_s": float(target_omega[-1]),
            "frequency_step_rad_s": float(target_omega[1] - target_omega[0]),
            "maximum_relative_spectrum_m0_error": maximum_m0_error,
        },
        "scope_boundary": {
            "included": "Correlated linear wave-frequency motion at the landing center and four registered foot points.",
            "excluded": "No touchdown timing policy, landing threshold, plume, GNC, DP controller, Chrono contact, or rocket-platform feedback is included in this screening layer.",
        },
        "acceptance": {
            "status": "PASS" if acceptance_pass else "FAIL",
            "checks": {
                "case_count": {"actual": len(cases), "expected": len(config["sea_states"]) * len(headings)},
                "seeds_per_case": {"actual": min(len(case["samples"]) for case in cases), "expected": seed_count},
                "all_values_finite": all_finite,
                "maximum_relative_spectrum_m0_error": maximum_m0_error,
                "maximum_relative_hs_linearity_error": maximum_linearity_error,
            },
            "claim": "Numerically reproducible linear HAMS/JONSWAP deck-motion screening only.",
            "not_claimed": "Coupled landing success probability or operational sea-state qualification.",
        },
        "cases": cases,
    }


def write_summary_csv(report: dict[str, Any]) -> None:
    SUMMARY_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    metrics = list(report["cases"][0]["statistics"])
    with SUMMARY_CSV_PATH.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["sea_state_id", "hs_m", "tp_s", "heading_deg", "metric", "mean", "standard_deviation", "p50", "p95", "p99", "maximum"])
        for case in report["cases"]:
            for metric in metrics:
                values = case["statistics"][metric]
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
                        values["p99"],
                        values["maximum"],
                    ]
                )


# Keep the historical helpers available while making the public report API use the revision.
legacy_build_report = build_report
legacy_write_summary_csv = write_summary_csv
build_report = build_revision_report
write_summary_csv = write_revision_summary_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute revised random-phase HAMS deck-point wave sensitivity statistics.")
    parser.add_argument("command", nargs="?", default="report", choices=["report"])
    parser.add_argument("--seeds", type=int, default=MIN_REALIZATIONS)
    parser.add_argument("--seed-start", type=int, default=202600)
    parser.add_argument("--duration", type=float, choices=SUPPORTED_DURATIONS_S, default=600.0)
    parser.add_argument("--dt", type=float, default=0.1)
    parser.add_argument("--delta-omega", type=float, default=DEFAULT_MAX_DELTA_OMEGA_RAD_S)
    parser.add_argument("--bootstrap-resamples", type=int, default=DEFAULT_BOOTSTRAP_RESAMPLES)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--out", type=Path, default=REVISION_REPORT_PATH)
    parser.add_argument("--summary-csv", type=Path, default=REVISION_SUMMARY_CSV_PATH)
    args = parser.parse_args()
    report = build_revision_report(
        seed_count=args.seeds,
        seed_start=args.seed_start,
        duration_s=args.duration,
        dt_s=args.dt,
        delta_omega=args.delta_omega,
        bootstrap_resamples=args.bootstrap_resamples,
        batch_size=args.batch_size,
    )
    write_json(args.out, report)
    write_revision_summary_csv(report, args.summary_csv)
    print(f"Wave sensitivity report: {args.out}")
    print(f"Summary CSV: {args.summary_csv}")
    print(f"Cases: {len(report['cases'])}; seeds per case: {report['method']['seed_count']}")


if __name__ == "__main__":
    main()
