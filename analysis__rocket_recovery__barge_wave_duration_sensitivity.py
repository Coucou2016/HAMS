from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import numpy as np

from .barge_wave_revision import (
    CASE_DIR,
    DEFAULT_BATCH_SIZE,
    DEFAULT_BOOTSTRAP_RESAMPLES,
    DEFAULT_MAX_DELTA_OMEGA_RAD_S,
    LEG_LAYOUT_PATH,
    LINEAR_TILT_SCREENING_DEG,
    MIN_REALIZATIONS,
    RAO_PATH,
    SUPPORTED_DURATIONS_S,
    _case_linear_validity,
    _relative_spectrum_m0,
    build_revision_deck_points,
    build_revision_transfer_matrix,
    build_synthesis_frequency_grid,
    load_existing_leg_layout,
    periodicity_diagnostics,
    response_metrics_batch,
    spectrum_component_amplitudes,
    summarize_samples,
    synthesize_response_batch,
)
from .common import ROOT, read_json, write_json


REPORT_PATH = CASE_DIR / "Output" / "RocketRecovery" / "wave-duration-sensitivity.json"
CSV_PATH = CASE_DIR / "Output" / "RocketRecovery" / "wave-duration-sensitivity.csv"
DEFAULT_SEA_STATE_IDS = ("Hs3_Tp8", "Hs3_Tp10")


def compute_nested_duration_cases(
    config: dict[str, Any],
    deck_rao: dict[str, Any],
    deck_points: list[dict[str, Any]],
    physical_leg_ids: list[str],
    sea_state: dict[str, Any],
    heading_deg: float,
    durations_s: tuple[float, ...],
    seed_count: int,
    seed_start: int,
    dt_s: float,
    delta_omega: float,
    bootstrap_resamples: int,
    batch_size: int,
    tilt_threshold_deg: float,
) -> list[dict[str, Any]]:
    """Evaluate record-length sensitivity from nested prefixes of one process.

    A single frequency grid, phase vector and maximum-duration realization are
    used for every requested duration.  This prevents frequency discretization
    or a changed random process from being misidentified as a record-length
    effect.
    """

    ordered_durations = tuple(sorted(float(value) for value in durations_s))
    if not ordered_durations or ordered_durations[0] <= 0.0:
        raise ValueError("durations_s must contain positive values")
    maximum_duration_s = ordered_durations[-1]
    bem_omega = np.asarray(deck_rao["frequencies_rad_s"], dtype=float)
    grid = build_synthesis_frequency_grid(bem_omega, maximum_duration_s, delta_omega)
    omega = np.asarray(grid["omega_rad_s"], dtype=float)
    duration_sample_counts = {duration: int(round(duration / dt_s)) for duration in ordered_durations}
    for duration, sample_count in duration_sample_counts.items():
        if sample_count < 2 or not math.isclose(sample_count * dt_s, duration, rel_tol=0.0, abs_tol=1.0e-8):
            raise ValueError(f"duration {duration:g} s must contain an integer number of dt_s samples")
    time_s = np.arange(duration_sample_counts[maximum_duration_s], dtype=float) * dt_s
    signal_names, transfer = build_revision_transfer_matrix(deck_rao, heading_deg, omega, deck_points)
    density, amplitudes = spectrum_component_amplitudes(
        omega,
        float(sea_state["hs_m"]),
        float(sea_state["tp_s"]),
        float(sea_state.get("gamma", 3.3)),
    )
    seed_ids = list(range(seed_start, seed_start + seed_count))
    point_ids = [str(point["id"]) for point in deck_points]
    samples_by_duration: dict[float, list[dict[str, float]]] = {duration: [] for duration in ordered_durations}
    representative: np.ndarray | None = None
    for start in range(0, seed_count, batch_size):
        batch_seeds = seed_ids[start : start + batch_size]
        phases = np.asarray(
            [np.random.default_rng(seed).uniform(0.0, 2.0 * math.pi, omega.size) for seed in batch_seeds]
        )
        response = synthesize_response_batch(transfer, amplitudes, phases, omega, time_s)
        if representative is None:
            representative = response[0].copy()
        for duration in ordered_durations:
            metric_arrays = response_metrics_batch(
                signal_names,
                response[:, :, : duration_sample_counts[duration]],
                physical_leg_ids,
                point_ids,
                config["platform"],
            )
            for index, seed in enumerate(batch_seeds):
                samples_by_duration[duration].append(
                    {"seed": int(seed), **{name: float(values[index]) for name, values in metric_arrays.items()}}
                )
    if representative is None:
        raise RuntimeError("No duration-sensitivity realization was generated")
    cases: list[dict[str, Any]] = []
    representative_center_velocity = representative[signal_names.index("landing_center.vz_m_s")]
    for duration in ordered_durations:
        samples = samples_by_duration[duration]
        statistics = summarize_samples(
            samples,
            bootstrap_resamples=bootstrap_resamples,
            bootstrap_seed=seed_start + int(duration) * 37 + int(round(float(sea_state["tp_s"]) * 100.0)),
        )
        case_grid = {key: value for key, value in grid.items() if key != "omega_rad_s"}
        case_grid.update(
            {
                "designed_for_maximum_duration_s": maximum_duration_s,
                "evaluated_prefix_duration_s": duration,
                "common_grid_across_durations": True,
            }
        )
        sample_count = duration_sample_counts[duration]
        cases.append(
            {
                "sea_state_id": str(sea_state["id"]),
                "hs_m": float(sea_state["hs_m"]),
                "tp_s": float(sea_state["tp_s"]),
                "gamma": float(sea_state.get("gamma", 3.3)),
                "heading_deg": float(heading_deg),
                "duration_s": duration,
                "frequency_grid": case_grid,
                "spectrum_m0_relative_error": _relative_spectrum_m0(density, omega, float(sea_state["hs_m"])),
                "statistics": statistics,
                "periodicity": periodicity_diagnostics(
                    representative_center_velocity[:sample_count],
                    dt_s,
                    float(grid["implied_repeat_period_s"]),
                    duration,
                ),
                "linear_validity": _case_linear_validity(statistics, samples, tilt_threshold_deg),
            }
        )
    return cases


def build_report(
    seed_count: int = MIN_REALIZATIONS,
    seed_start: int = 202600,
    dt_s: float = 0.1,
    delta_omega: float = DEFAULT_MAX_DELTA_OMEGA_RAD_S,
    bootstrap_resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
    batch_size: int = DEFAULT_BATCH_SIZE,
    sea_state_ids: tuple[str, ...] = DEFAULT_SEA_STATE_IDS,
    heading_deg: float = 90.0,
) -> dict[str, Any]:
    if seed_count < MIN_REALIZATIONS:
        raise ValueError(f"At least {MIN_REALIZATIONS} realizations are required")
    config = read_json(CASE_DIR / "platform_config.json")
    deck_rao = read_json(RAO_PATH)
    layout = load_existing_leg_layout(LEG_LAYOUT_PATH)
    point_sets = build_revision_deck_points(config, layout)
    deck_points = [point_sets["all"][0], *point_sets["physical_legs"]]
    physical_leg_ids = [str(point["id"]) for point in point_sets["physical_legs"]]
    states = {str(state["id"]): state for state in config["sea_states"]}
    missing = set(sea_state_ids) - set(states)
    if missing:
        raise ValueError(f"Unknown sea states: {sorted(missing)}")
    tilt_threshold = LINEAR_TILT_SCREENING_DEG
    cases: list[dict[str, Any]] = []
    for state_id in sea_state_ids:
        cases.extend(
            compute_nested_duration_cases(
                config,
                deck_rao,
                deck_points,
                physical_leg_ids,
                states[state_id],
                heading_deg,
                SUPPORTED_DURATIONS_S,
                seed_count,
                seed_start,
                dt_s,
                delta_omega,
                bootstrap_resamples,
                batch_size,
                tilt_threshold,
            )
        )
    by_state: dict[str, Any] = {}
    for state_id in sea_state_ids:
        rows = [row for row in cases if row["sea_state_id"] == state_id]
        reference = next(row for row in rows if row["duration_s"] == max(SUPPORTED_DURATIONS_S))
        metrics = {}
        for metric, reference_values in reference["statistics"].items():
            reference_p95 = float(reference_values["p95"])
            metrics[metric] = [
                {
                    "duration_s": row["duration_s"],
                    "p95": float(row["statistics"][metric]["p95"]),
                    "p95_bootstrap_95ci": row["statistics"][metric]["p95_bootstrap_95ci"],
                    "relative_difference_from_1800s": abs(float(row["statistics"][metric]["p95"]) - reference_p95)
                    / max(abs(reference_p95), 1.0e-12),
                }
                for row in rows
            ]
        by_state[state_id] = metrics
    return {
        "case_id": "Barge_120x50_random_wave_duration_sensitivity",
        "status": "computed_duration_sensitivity_not_operational_probability",
        "method": {
            "durations_s": list(SUPPORTED_DURATIONS_S),
            "seed_count_per_duration": seed_count,
            "same_seed_ids_across_durations": True,
            "same_frequency_grid_across_durations": True,
            "same_phase_vectors_across_durations": True,
            "nested_record_prefixes": True,
            "record_definition": "600 s and 1200 s records are exact prefixes of each 1800 s realization; only observation duration changes.",
            "bootstrap_resamples": bootstrap_resamples,
            "dt_s": dt_s,
            "maximum_delta_omega_rad_s": delta_omega,
            "heading_deg": heading_deg,
            "sea_state_ids": list(sea_state_ids),
            "foot_layout": "Thies-derived 6.926 m footprint radius with explicitly assumed symmetric azimuths",
        },
        "cases": cases,
        "duration_comparison": by_state,
        "acceptance": {
            "status": "PASS"
            if all(not row["periodicity"]["record_covers_repeat_period"] for row in cases)
            and all(row["spectrum_m0_relative_error"] <= 1.0e-12 for row in cases)
            else "FAIL",
            "claim": "record-duration sensitivity and sampling uncertainty are reported; numerical equality across durations is not required",
        },
    }


def write_csv(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["sea_state_id", "duration_s", "metric", "p95", "p95_ci_lower", "p95_ci_upper"])
        for row in report["cases"]:
            for metric, values in row["statistics"].items():
                ci = values["p95_bootstrap_95ci"]
                writer.writerow([row["sea_state_id"], row["duration_s"], metric, values["p95"], ci["lower"], ci["upper"]])


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate 600/1200/1800 s sensitivity for the critical barge sea states.")
    parser.add_argument("--seeds", type=int, default=MIN_REALIZATIONS)
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--out", type=Path, default=REPORT_PATH)
    parser.add_argument("--csv-out", type=Path, default=CSV_PATH)
    args = parser.parse_args()
    report = build_report(
        seed_count=args.seeds,
        bootstrap_resamples=args.bootstrap_resamples,
        batch_size=args.batch_size,
    )
    write_json(args.out, report)
    write_csv(report, args.csv_out)
    print(f"Duration report: {args.out}")
    print(f"Duration CSV: {args.csv_out}")
    print(f"Cases: {len(report['cases'])}; acceptance: {report['acceptance']['status']}")


if __name__ == "__main__":
    main()
