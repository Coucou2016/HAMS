from __future__ import annotations

import argparse
import csv
import math
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import least_squares
from scipy.stats import qmc

try:
    from .common import ROOT, write_json
    from .yang_2026_landing_identification import (
        CONDITIONS,
        DIGITIZED_META,
        IdentifiedParameters,
        baseline_corrected_reference,
        calibration_residual,
        compare_condition,
        simulate_condition,
    )
except ImportError:
    from common import ROOT, write_json
    from yang_2026_landing_identification import (
        CONDITIONS,
        DIGITIZED_META,
        IdentifiedParameters,
        baseline_corrected_reference,
        calibration_residual,
        compare_condition,
        simulate_condition,
    )


OUTPUT_DIR = ROOT / "RocketRecoveryCases" / "Paper_Yang_2026" / "identified_landing_model"
REPORT_PATH = OUTPUT_DIR / "yang-2026-identifiability-report.json"
STARTS_CSV_PATH = OUTPUT_DIR / "yang-2026-multistart-solutions.csv"

PARAMETER_NAMES = [
    "force_observation_ratio",
    "stroke_observation_ratio",
    "vertical_stiffness_n_m",
    "quadratic_vertical_stiffness_n_m2",
    "compression_vertical_damping_ns_m",
    "rebound_vertical_damping_ns_m",
]
LOWER_BOUNDS = np.asarray([0.2, 0.3, 0.2, 0.0, 0.1, 0.1], dtype=float)
UPPER_BOUNDS = np.asarray([0.9, 2.0, 10.0, 20.0, 10.0, 30.0], dtype=float)
SAMPLE_TIME_S = np.linspace(0.0, 1.2, 181)


def _reference() -> dict[str, Any]:
    return baseline_corrected_reference(CONDITIONS["Y0_simultaneous"]["figure"])


def _solve_start(task: tuple[int, list[float], int]) -> dict[str, Any]:
    start_index, initial_values, max_nfev = task
    reference = _reference()
    result = least_squares(
        calibration_residual,
        np.asarray(initial_values, dtype=float),
        args=(reference, SAMPLE_TIME_S),
        bounds=(LOWER_BOUNDS, UPPER_BOUNDS),
        max_nfev=max_nfev,
        x_scale="jac",
        verbose=0,
    )
    singular_values = np.linalg.svd(np.asarray(result.jac, dtype=float), compute_uv=False)
    positive = singular_values[singular_values > np.finfo(float).eps * singular_values[0]]
    condition_number = float(positive[0] / positive[-1]) if len(positive) else math.inf
    return {
        "start_index": int(start_index),
        "success": bool(result.success),
        "status": int(result.status),
        "cost": float(result.cost),
        "optimality": float(result.optimality),
        "nfev": int(result.nfev),
        "initial_scaled": [float(value) for value in initial_values],
        "solution_scaled": result.x.tolist(),
        "active_mask": result.active_mask.tolist(),
        "jacobian_singular_values": singular_values.tolist(),
        "jacobian_condition_number": condition_number,
    }


def generate_initial_values(start_count: int, seed: int) -> np.ndarray:
    if start_count < 2:
        raise ValueError("At least two starts are required for an identifiability study")
    sampler = qmc.LatinHypercube(d=len(PARAMETER_NAMES), seed=seed)
    values = qmc.scale(sampler.random(n=start_count), LOWER_BOUNDS, UPPER_BOUNDS)
    published_nominal = IdentifiedParameters(
        force_observation_ratio=0.5,
        stroke_observation_ratio=1.0,
        vertical_stiffness_n_m=1.5e5,
        quadratic_vertical_stiffness_n_m2=0.0,
        compression_vertical_damping_ns_m=2.0e4,
        rebound_vertical_damping_ns_m=4.0e4,
    ).to_scaled()
    values[0] = np.clip(published_nominal, LOWER_BOUNDS, UPPER_BOUNDS)
    return values


def run_multistart(start_count: int, seed: int, max_nfev: int, workers: int) -> list[dict[str, Any]]:
    initial_values = generate_initial_values(start_count, seed)
    tasks = [(index, values.tolist(), max_nfev) for index, values in enumerate(initial_values)]
    results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_solve_start, task): task[0] for task in tasks}
        for future in as_completed(futures):
            results.append(future.result())
            if len(results) % max(1, start_count // 8) == 0:
                print(f"Completed {len(results)}/{start_count} multistart optimizations", flush=True)
    return sorted(results, key=lambda row: (row["cost"], row["start_index"]))


def _physical_matrix(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray(
        [list(IdentifiedParameters.from_scaled(np.asarray(row["solution_scaled"])).as_dict().values()) for row in rows],
        dtype=float,
    )


def _parameter_statistics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    values = _physical_matrix(rows)
    if len(values) > 1:
        correlation = np.corrcoef(values, rowvar=False)
    else:
        correlation = np.full((values.shape[1], values.shape[1]), np.nan)
    statistics = {}
    for index, name in enumerate(PARAMETER_NAMES):
        column = values[:, index]
        statistics[name] = {
            "minimum": float(np.min(column)),
            "p05": float(np.quantile(column, 0.05)),
            "median": float(np.median(column)),
            "p95": float(np.quantile(column, 0.95)),
            "maximum": float(np.max(column)),
            "coefficient_of_variation": float(np.std(column, ddof=1) / abs(np.mean(column)))
            if len(column) > 1 and abs(float(np.mean(column))) > 1.0e-15
            else None,
        }
    return {
        "parameter_order": PARAMETER_NAMES,
        "statistics": statistics,
        "pearson_correlation": correlation.tolist(),
    }


def _prediction_envelopes(rows: list[dict[str, Any]]) -> dict[str, Any]:
    envelope: dict[str, Any] = {}
    for condition_id, condition in CONDITIONS.items():
        reference = baseline_corrected_reference(condition["figure"])
        comparisons = []
        for row in rows:
            parameters = IdentifiedParameters.from_scaled(np.asarray(row["solution_scaled"], dtype=float))
            simulation = simulate_condition(condition_id, parameters)
            comparisons.append(compare_condition(condition_id, simulation, reference))

        time_s = np.asarray(comparisons[0]["time_s"], dtype=float)
        channels: dict[str, Any] = {}
        for channel in ("acceleration_up_m_s2", "strut_force_n", "stroke_m"):
            values = np.asarray([comparison["model"][channel] for comparison in comparisons], dtype=float)
            peak_values = np.max(values, axis=1)
            channels[channel] = {
                "p05": np.quantile(values, 0.05, axis=0).tolist(),
                "median": np.quantile(values, 0.50, axis=0).tolist(),
                "p95": np.quantile(values, 0.95, axis=0).tolist(),
                "peak_p05": float(np.quantile(peak_values, 0.05)),
                "peak_median": float(np.median(peak_values)),
                "peak_p95": float(np.quantile(peak_values, 0.95)),
            }
        envelope[condition_id] = {
            "role": condition["role"],
            "time_s": time_s.tolist(),
            "reference": comparisons[0]["paper"],
            "channels": channels,
        }
    return envelope


def write_solutions_csv(rows: list[dict[str, Any]], near_indices: set[int]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "rank",
        "start_index",
        "success",
        "cost",
        "relative_cost_above_best",
        "optimality",
        "nfev",
        "near_optimal",
    ] + PARAMETER_NAMES
    best_cost = float(rows[0]["cost"])
    with STARTS_CSV_PATH.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for rank, row in enumerate(rows, start=1):
            physical = IdentifiedParameters.from_scaled(np.asarray(row["solution_scaled"])).as_dict()
            writer.writerow(
                {
                    "rank": rank,
                    "start_index": row["start_index"],
                    "success": row["success"],
                    "cost": row["cost"],
                    "relative_cost_above_best": (float(row["cost"]) - best_cost) / max(best_cost, 1.0e-15),
                    "optimality": row["optimality"],
                    "nfev": row["nfev"],
                    "near_optimal": row["start_index"] in near_indices,
                    **physical,
                }
            )


def build_report(start_count: int, seed: int, max_nfev: int, workers: int) -> dict[str, Any]:
    if not DIGITIZED_META.exists():
        raise FileNotFoundError("Run yang_2026_digitize.py before the identifiability study")
    rows = run_multistart(start_count, seed, max_nfev, workers)
    best_cost = float(rows[0]["cost"])
    near_tolerance = 0.01
    near_rows = [row for row in rows if float(row["cost"]) <= best_cost * (1.0 + near_tolerance)]
    if len(near_rows) < min(10, start_count):
        near_rows = rows[: min(10, start_count)]
        selection_rule = "lowest ten solutions because fewer than ten were within 1% of best cost"
    else:
        selection_rule = "cost not greater than 1% above the best solution"

    scaled_best = np.asarray(rows[0]["solution_scaled"], dtype=float)
    lower_distance = (scaled_best - LOWER_BOUNDS) / (UPPER_BOUNDS - LOWER_BOUNDS)
    upper_distance = (UPPER_BOUNDS - scaled_best) / (UPPER_BOUNDS - LOWER_BOUNDS)
    near_bound = np.minimum(lower_distance, upper_distance) <= 1.0e-4
    singular_values = np.asarray(rows[0]["jacobian_singular_values"], dtype=float)
    relative_singular_values = singular_values / max(float(singular_values[0]), 1.0e-30)
    numerical_rank = int(np.sum(relative_singular_values > 1.0e-6))

    report = {
        "study_id": "Yang2026_reduced_model_multistart_identifiability_v1",
        "source_data": str(DIGITIZED_META.relative_to(ROOT).as_posix()),
        "configuration": {
            "start_count": start_count,
            "sampling": "six-dimensional Latin hypercube plus the previous nominal initial value",
            "random_seed": seed,
            "maximum_function_evaluations_per_start": max_nfev,
            "parallel_workers": workers,
            "calibration_case": "Y0_simultaneous only",
            "sample_count_per_channel": int(len(SAMPLE_TIME_S)),
            "nrmse_definition": "sqrt(mean((model-reference)^2)) divided by max(abs(reference)) on the common 0-1.2 s grid",
        },
        "bounds_scaled": {name: [float(LOWER_BOUNDS[i]), float(UPPER_BOUNDS[i])] for i, name in enumerate(PARAMETER_NAMES)},
        "best_solution": {
            **rows[0],
            "physical_parameters": IdentifiedParameters.from_scaled(scaled_best).as_dict(),
            "distance_to_lower_bound_fraction": lower_distance.tolist(),
            "distance_to_upper_bound_fraction": upper_distance.tolist(),
            "near_bound": {name: bool(near_bound[i]) for i, name in enumerate(PARAMETER_NAMES)},
            "jacobian_relative_singular_values": relative_singular_values.tolist(),
            "jacobian_numerical_rank_at_1e-6": numerical_rank,
        },
        "convergence": {
            "successful_starts": int(sum(bool(row["success"]) for row in rows)),
            "total_starts": len(rows),
            "best_cost": best_cost,
            "median_cost": float(np.median([row["cost"] for row in rows])),
            "near_optimal_count": len(near_rows),
            "near_optimal_selection": selection_rule,
        },
        "near_optimal_ensemble": _parameter_statistics(near_rows),
        "prediction_envelopes": _prediction_envelopes(near_rows),
        "interpretation": {
            "structural_identifiability_claimed": False,
            "practical_identifiability_supported": bool(numerical_rank == len(PARAMETER_NAMES) and not np.any(near_bound)),
            "claim_boundary": "The public curves constrain response envelopes and selected peaks, but do not establish a unique physical parameter set for the unpublished flexible mechanism.",
        },
        "all_solutions_csv": str(STARTS_CSV_PATH.relative_to(ROOT).as_posix()),
    }
    near_indices = {int(row["start_index"]) for row in near_rows}
    write_solutions_csv(rows, near_indices)
    write_json(REPORT_PATH, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a reproducible multistart practical-identifiability study for the Yang reduced landing model.")
    parser.add_argument("--starts", type=int, default=128)
    parser.add_argument("--seed", type=int, default=20260829)
    parser.add_argument("--max-nfev", type=int, default=120)
    parser.add_argument("--workers", type=int, default=min(16, max(1, os.cpu_count() or 1)))
    args = parser.parse_args()
    report = build_report(args.starts, args.seed, args.max_nfev, args.workers)
    print(f"Successful starts: {report['convergence']['successful_starts']}/{report['convergence']['total_starts']}")
    print(f"Near-optimal ensemble: {report['convergence']['near_optimal_count']}")
    print(f"Jacobian rank: {report['best_solution']['jacobian_numerical_rank_at_1e-6']}/{len(PARAMETER_NAMES)}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
