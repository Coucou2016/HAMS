from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import least_squares

try:
    from .common import G, ROOT, ROCKET_CASES_DIR, read_json, write_json
except ImportError:
    from common import G, ROOT, ROCKET_CASES_DIR, read_json, write_json


CASE_DIR = ROCKET_CASES_DIR / "Paper_Yang_2026"
DIGITIZED_DIR = CASE_DIR / "reference" / "digitized"
DIGITIZED_META = DIGITIZED_DIR / "yang-2026-fig09-11-digitization.json"
OUTPUT_DIR = CASE_DIR / "identified_landing_model"
REPORT_PATH = OUTPUT_DIR / "yang-2026-identified-landing-report.json"


CONDITIONS = {
    "Y0_simultaneous": {"figure": "fig09", "pitch_deg": 0.0, "tilt_axis_deg": 0.0, "role": "calibration"},
    "Y1_1-2-1": {"figure": "fig10", "pitch_deg": 3.0, "tilt_axis_deg": 0.0, "role": "frozen_parameter_validation"},
    "Y2_2-2": {"figure": "fig11", "pitch_deg": 3.0, "tilt_axis_deg": 45.0, "role": "frozen_parameter_validation"},
}


@dataclass(frozen=True)
class IdentifiedParameters:
    force_observation_ratio: float
    stroke_observation_ratio: float
    vertical_stiffness_n_m: float
    quadratic_vertical_stiffness_n_m2: float
    compression_vertical_damping_ns_m: float
    rebound_vertical_damping_ns_m: float

    @classmethod
    def from_scaled(cls, values: np.ndarray) -> "IdentifiedParameters":
        return cls(
            force_observation_ratio=float(values[0]),
            stroke_observation_ratio=float(values[1]),
            vertical_stiffness_n_m=float(values[2]) * 1.0e5,
            quadratic_vertical_stiffness_n_m2=float(values[3]) * 1.0e6,
            compression_vertical_damping_ns_m=float(values[4]) * 1.0e4,
            rebound_vertical_damping_ns_m=float(values[5]) * 1.0e4,
        )

    def to_scaled(self) -> np.ndarray:
        return np.asarray(
            [
                self.force_observation_ratio,
                self.stroke_observation_ratio,
                self.vertical_stiffness_n_m / 1.0e5,
                self.quadratic_vertical_stiffness_n_m2 / 1.0e6,
                self.compression_vertical_damping_ns_m / 1.0e4,
                self.rebound_vertical_damping_ns_m / 1.0e4,
            ],
            dtype=float,
        )

    def as_dict(self) -> dict[str, float]:
        return {
            "force_observation_ratio": self.force_observation_ratio,
            "stroke_observation_ratio": self.stroke_observation_ratio,
            "vertical_stiffness_n_m": self.vertical_stiffness_n_m,
            "quadratic_vertical_stiffness_n_m2": self.quadratic_vertical_stiffness_n_m2,
            "compression_vertical_damping_ns_m": self.compression_vertical_damping_ns_m,
            "rebound_vertical_damping_ns_m": self.rebound_vertical_damping_ns_m,
        }


def read_curve(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    time_s = np.asarray([float(row["time_s"]) for row in rows], dtype=float)
    values = np.asarray([float(row["value"]) for row in rows], dtype=float)
    order = np.argsort(time_s)
    return time_s[order], values[order]


def baseline_corrected_reference(figure: str) -> dict[str, Any]:
    file_map = {
        "acceleration": DIGITIZED_DIR / f"{figure}_acceleration_test.csv",
        "force": DIGITIZED_DIR / f"{figure}_main_strut_load_test.csv",
        "stroke": DIGITIZED_DIR / f"{figure}_buffer_stroke_test.csv",
    }
    acceleration_time, acceleration = read_curve(file_map["acceleration"])
    force_time, force = read_curve(file_map["force"])
    stroke_time, stroke = read_curve(file_map["stroke"])

    pre_limit = float(np.quantile(force_time, 0.13))
    force_baseline = float(np.median(force[force_time <= pre_limit]))
    force_corrected = np.maximum(0.0, force - force_baseline)
    threshold = 0.08 * max(float(np.max(force_corrected)), 1.0)
    contact_candidates = np.where(force_corrected >= threshold)[0]
    if not len(contact_candidates):
        raise ValueError(f"Could not detect contact in {figure}")
    contact_time = float(force_time[int(contact_candidates[0])])

    stroke_pre = stroke[stroke_time <= contact_time]
    stroke_baseline_mm = float(np.median(stroke_pre)) if len(stroke_pre) else float(stroke[0])
    stroke_corrected_m = np.maximum(0.0, (stroke - stroke_baseline_mm) * 1.0e-3)
    return {
        "contact_time_s": contact_time,
        "acceleration": {
            "time_from_contact_s": acceleration_time - contact_time,
            "value_m_s2": acceleration * 1.0e-3,
            "raw_unit": "mm/s^2",
        },
        "force": {
            "time_from_contact_s": force_time - contact_time,
            "value_n": force_corrected,
            "baseline_removed_n": force_baseline,
        },
        "stroke": {
            "time_from_contact_s": stroke_time - contact_time,
            "value_m": stroke_corrected_m,
            "baseline_removed_mm": stroke_baseline_mm,
        },
    }


def leg_projected_coordinates(radius_m: float, tilt_axis_deg: float) -> np.ndarray:
    azimuths = np.radians(np.asarray([0.0, 90.0, 180.0, 270.0]))
    axis = math.radians(float(tilt_axis_deg))
    return float(radius_m) * np.cos(azimuths - axis)


def observed_stroke_from_vertical_compression(delta_m: np.ndarray, parameters: IdentifiedParameters) -> np.ndarray:
    delta = np.maximum(0.0, np.asarray(delta_m, dtype=float))
    return np.clip(delta / parameters.stroke_observation_ratio, 0.0, 0.25)


def leg_forces(
    vertical_compression_m: np.ndarray,
    vertical_compression_rate_m_s: np.ndarray,
    parameters: IdentifiedParameters,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    compression = np.maximum(0.0, np.asarray(vertical_compression_m, dtype=float))
    compression_rate = np.asarray(vertical_compression_rate_m_s, dtype=float)
    spring = parameters.vertical_stiffness_n_m * compression
    spring += parameters.quadratic_vertical_stiffness_n_m2 * compression**2
    damping = parameters.compression_vertical_damping_ns_m * np.maximum(compression_rate, 0.0)
    damping += parameters.rebound_vertical_damping_ns_m * np.minimum(compression_rate, 0.0)
    active = np.asarray(vertical_compression_m, dtype=float) > 0.0
    vertical_force = np.where(active, np.maximum(0.0, spring + damping), 0.0)
    observed_strut_force = vertical_force / parameters.force_observation_ratio
    observed_stroke = observed_stroke_from_vertical_compression(compression, parameters)
    return observed_strut_force, vertical_force, observed_stroke


def simulate_condition(
    condition_id: str,
    parameters: IdentifiedParameters,
    *,
    dt_s: float = 0.001,
    duration_s: float = 1.6,
    mass_kg: float = 5200.0,
    touchdown_velocity_m_s: float = 2.0,
    support_margin_m: float = 2.65,
    pitch_inertia_kg_m2: float | None = None,
) -> dict[str, Any]:
    condition = CONDITIONS[condition_id]
    footprint_radius = float(support_margin_m) * math.sqrt(2.0)
    projected = leg_projected_coordinates(footprint_radius, condition["tilt_axis_deg"])
    pitch0 = math.radians(float(condition["pitch_deg"]))
    initial_offsets = pitch0 * projected
    gaps = np.max(initial_offsets) - initial_offsets
    inertia = float(pitch_inertia_kg_m2 if pitch_inertia_kg_m2 is not None else mass_kg * footprint_radius**2)

    count = int(round(duration_s / dt_s)) + 1
    time_s = np.arange(count, dtype=float) * dt_s
    state = np.zeros(4, dtype=float)
    state[1] = float(touchdown_velocity_m_s)
    state[2] = pitch0

    states = np.zeros((count, 4), dtype=float)
    acceleration_up = np.zeros(count, dtype=float)
    strut_history = np.zeros((count, 4), dtype=float)
    vertical_force_history = np.zeros((count, 4), dtype=float)
    stroke_history = np.zeros((count, 4), dtype=float)
    contact_history = np.zeros((count, 4), dtype=int)

    def rhs(current: np.ndarray) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
        down, down_rate, pitch, pitch_rate = current
        compression = down + (pitch - pitch0) * projected - gaps
        compression_rate = down_rate + pitch_rate * projected
        strut_force, vertical_force, stroke = leg_forces(compression, compression_rate, parameters)
        down_acceleration = G - float(np.sum(vertical_force)) / mass_kg
        pitch_acceleration = -float(np.dot(vertical_force, projected)) / inertia
        return np.asarray([down_rate, down_acceleration, pitch_rate, pitch_acceleration]), (strut_force, vertical_force, stroke)

    for index in range(count):
        states[index] = state
        derivative, values = rhs(state)
        strut_force, vertical_force, stroke = values
        acceleration_up[index] = -derivative[1]
        strut_history[index] = strut_force
        vertical_force_history[index] = vertical_force
        stroke_history[index] = stroke
        contact_history[index] = (strut_force > 1.0).astype(int)
        if index == count - 1:
            break
        k1 = derivative
        k2 = rhs(state + 0.5 * dt_s * k1)[0]
        k3 = rhs(state + 0.5 * dt_s * k2)[0]
        k4 = rhs(state + dt_s * k3)[0]
        state = state + dt_s / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    first_contact_index = []
    for leg in range(4):
        indices = np.where(contact_history[:, leg] > 0)[0]
        first_contact_index.append(int(indices[0]) if len(indices) else None)
    contact_order = sorted(
        [
            {"leg_id": f"leg_{leg + 1}", "first_contact_time_s": float(time_s[index])}
            for leg, index in enumerate(first_contact_index)
            if index is not None
        ],
        key=lambda item: item["first_contact_time_s"],
    )
    return {
        "condition_id": condition_id,
        "role": condition["role"],
        "time_s": time_s,
        "states": states,
        "acceleration_up_m_s2": acceleration_up,
        "strut_force_n": strut_history,
        "vertical_force_n": vertical_force_history,
        "stroke_m": stroke_history,
        "contact": contact_history,
        "touchdown_sequence": contact_order,
        "configuration": {
            "mass_kg": mass_kg,
            "touchdown_velocity_m_s": touchdown_velocity_m_s,
            "initial_pitch_deg": condition["pitch_deg"],
            "tilt_axis_deg": condition["tilt_axis_deg"],
            "support_margin_m": support_margin_m,
            "footprint_radius_m": footprint_radius,
            "pitch_inertia_kg_m2": inertia,
            "pitch_inertia_source": "proxy:m*footprint_radius^2" if pitch_inertia_kg_m2 is None else "caller supplied",
        },
    }


def reference_on_grid(reference: dict[str, Any], time_s: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "acceleration_up_m_s2": np.interp(
            time_s,
            reference["acceleration"]["time_from_contact_s"],
            reference["acceleration"]["value_m_s2"],
        ),
        "strut_force_n": np.interp(
            time_s,
            reference["force"]["time_from_contact_s"],
            reference["force"]["value_n"],
        ),
        "stroke_m": np.interp(
            time_s,
            reference["stroke"]["time_from_contact_s"],
            reference["stroke"]["value_m"],
        ),
    }


def calibration_residual(values: np.ndarray, reference: dict[str, Any], sample_time_s: np.ndarray) -> np.ndarray:
    parameters = IdentifiedParameters.from_scaled(values)
    simulation = simulate_condition("Y0_simultaneous", parameters, dt_s=0.002, duration_s=float(sample_time_s[-1]))
    sim_time = simulation["time_s"]
    target = reference_on_grid(reference, sample_time_s)
    first_leg = 0
    simulated = {
        "acceleration_up_m_s2": np.interp(sample_time_s, sim_time, simulation["acceleration_up_m_s2"]),
        "strut_force_n": np.interp(sample_time_s, sim_time, simulation["strut_force_n"][:, first_leg]),
        "stroke_m": np.interp(sample_time_s, sim_time, simulation["stroke_m"][:, first_leg]),
    }
    weights = {
        "acceleration_up_m_s2": 28.0,
        "strut_force_n": 100000.0,
        "stroke_m": 0.1,
    }
    residuals = []
    for key in ("acceleration_up_m_s2", "strut_force_n", "stroke_m"):
        residuals.append((simulated[key] - target[key]) / weights[key])
    regularization = np.asarray(
        [
            (parameters.force_observation_ratio - 0.5) / 0.25,
            (parameters.stroke_observation_ratio - 1.0) / 0.5,
        ],
        dtype=float,
    )
    return np.concatenate(residuals + [0.03 * regularization])


def identify_parameters(reference: dict[str, Any]) -> tuple[IdentifiedParameters, dict[str, Any]]:
    initial = IdentifiedParameters(
        force_observation_ratio=0.5,
        stroke_observation_ratio=1.0,
        vertical_stiffness_n_m=1.5e5,
        quadratic_vertical_stiffness_n_m2=0.0,
        compression_vertical_damping_ns_m=2.0e4,
        rebound_vertical_damping_ns_m=4.0e4,
    )
    sample_time = np.linspace(0.0, 1.2, 181)
    result = least_squares(
        calibration_residual,
        initial.to_scaled(),
        args=(reference, sample_time),
        bounds=(
            np.asarray([0.2, 0.3, 0.2, 0.0, 0.1, 0.1]),
            np.asarray([0.9, 2.0, 10.0, 20.0, 10.0, 30.0]),
        ),
        max_nfev=100,
        x_scale="jac",
        verbose=0,
    )
    parameters = IdentifiedParameters.from_scaled(result.x)
    return parameters, {
        "success": bool(result.success),
        "status": int(result.status),
        "message": result.message,
        "cost": float(result.cost),
        "optimality": float(result.optimality),
        "function_evaluations": int(result.nfev),
        "active_mask": result.active_mask.tolist(),
        "initial_parameters": initial.as_dict(),
        "identified_parameters": parameters.as_dict(),
    }


def comparison_metrics(time_s: np.ndarray, model: np.ndarray, paper: np.ndarray) -> dict[str, Any]:
    difference = np.asarray(model) - np.asarray(paper)
    rmse = float(np.sqrt(np.mean(difference**2)))
    peak = max(float(np.max(np.abs(paper))), 1.0e-12)
    if np.std(model) > 1.0e-12 and np.std(paper) > 1.0e-12:
        correlation = float(np.corrcoef(model, paper)[0, 1])
    else:
        correlation = None
    model_peak = float(np.max(model))
    paper_peak = float(np.max(paper))
    return {
        "sample_count": int(len(time_s)),
        "time_range_s": [float(time_s[0]), float(time_s[-1])],
        "rmse": rmse,
        "normalized_rmse_vs_paper_peak": rmse / peak,
        "correlation": correlation,
        "model_peak": model_peak,
        "paper_peak": paper_peak,
        "peak_relative_error": abs(model_peak - paper_peak) / max(abs(paper_peak), 1.0e-12),
    }


def compare_condition(condition_id: str, simulation: dict[str, Any], reference: dict[str, Any]) -> dict[str, Any]:
    end_time = min(1.2, float(simulation["time_s"][-1]))
    time_s = np.linspace(0.0, end_time, 241)
    target = reference_on_grid(reference, time_s)
    sim_time = simulation["time_s"]
    first_leg = simulation["touchdown_sequence"][0]["leg_id"] if simulation["touchdown_sequence"] else "leg_1"
    first_leg_index = int(first_leg.split("_")[-1]) - 1
    model = {
        "acceleration_up_m_s2": np.interp(time_s, sim_time, simulation["acceleration_up_m_s2"]),
        "strut_force_n": np.interp(time_s, sim_time, simulation["strut_force_n"][:, first_leg_index]),
        "stroke_m": np.interp(time_s, sim_time, simulation["stroke_m"][:, first_leg_index]),
    }
    return {
        "condition_id": condition_id,
        "role": CONDITIONS[condition_id]["role"],
        "first_touchdown_leg": first_leg,
        "touchdown_sequence": simulation["touchdown_sequence"],
        "metrics": {key: comparison_metrics(time_s, model[key], target[key]) for key in model},
        "time_s": time_s.tolist(),
        "paper": {key: value.tolist() for key, value in target.items()},
        "model": {key: value.tolist() for key, value in model.items()},
    }


def write_condition_csv(comparison: dict[str, Any]) -> Path:
    path = OUTPUT_DIR / f"{comparison['condition_id']}-comparison.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = ["acceleration_up_m_s2", "strut_force_n", "stroke_m"]
    with path.open("w", encoding="utf-8", newline="") as stream:
        fieldnames = ["time_s"] + [f"paper_{key}" for key in keys] + [f"model_{key}" for key in keys]
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for index, time_value in enumerate(comparison["time_s"]):
            row: dict[str, float] = {"time_s": time_value}
            for key in keys:
                row[f"paper_{key}"] = comparison["paper"][key][index]
                row[f"model_{key}"] = comparison["model"][key][index]
            writer.writerow(row)
    return path


def build_report() -> dict[str, Any]:
    if not DIGITIZED_META.exists():
        raise FileNotFoundError("Run yang_2026_digitize.py before landing identification.")
    references = {
        condition_id: baseline_corrected_reference(config["figure"])
        for condition_id, config in CONDITIONS.items()
    }
    parameters, optimizer = identify_parameters(references["Y0_simultaneous"])
    comparisons = {}
    configurations = {}
    for condition_id in CONDITIONS:
        simulation = simulate_condition(condition_id, parameters)
        comparison = compare_condition(condition_id, simulation, references[condition_id])
        comparison["csv"] = str(write_condition_csv(comparison).relative_to(ROOT).as_posix())
        comparisons[condition_id] = comparison
        configurations[condition_id] = simulation["configuration"]

    thresholds = {"normalized_rmse_vs_paper_peak": 0.2, "correlation": 0.85, "peak_relative_error": 0.1}
    calibration_metric_status = {}
    calibration_metrics = comparisons["Y0_simultaneous"]["metrics"]
    for metric_name, values in calibration_metrics.items():
        checks = {
            "normalized_rmse": values["normalized_rmse_vs_paper_peak"] <= thresholds["normalized_rmse_vs_paper_peak"],
            "correlation": values["correlation"] is not None and values["correlation"] >= thresholds["correlation"],
            "peak_relative_error": values["peak_relative_error"] <= thresholds["peak_relative_error"],
        }
        calibration_metric_status[metric_name] = {"pass": all(checks.values()), "checks": checks}
    strict_calibration_pass = all(item["pass"] for item in calibration_metric_status.values())

    report = {
        "model_id": "Yang2026_OpenReducedFourLeg_Identification_v2",
        "model_status": "identified_reduced_order_model_not_adams_abaqus_replica",
        "source_data": str(DIGITIZED_META.relative_to(ROOT).as_posix()),
        "identification_policy": {
            "calibration_case": "Y0_simultaneous only",
            "validation_cases": ["Y1_1-2-1", "Y2_2-2"],
            "validation_recalibration_allowed": False,
            "claim_boundary": "A transparent open reduced-order landing model. It is not a reconstruction of unpublished Yang ADAMS/Abaqus parameters.",
        },
        "parameter_provenance": {
            "mass_kg": {"value": 5200.0, "class": "published", "source": "Yang Table 1"},
            "touchdown_velocity_m_s": {"value": 2.0, "class": "published", "source": "Yang Table 1"},
            "pitch_angles_deg": {"value": [0.0, 3.0, 3.0], "class": "published", "source": "Yang Table 1"},
            "support_margin_m": {"value": 2.65, "class": "digitized", "source": "Yang Figure 16 final plateau"},
            "footprint_radius_m": {"value": 2.65 * math.sqrt(2.0), "class": "derived", "source": "square support polygon circumradius from digitized inradius"},
            "pitch_inertia": {"value": "m*footprint_radius^2", "class": "proxy", "source": "not published; frozen before validation"},
            "generalized_contact_and_observation_parameters": {
                "value": parameters.as_dict(),
                "class": "identified",
                "source": "least-squares fit to Y0 Figure 9 only",
                "interpretation": "The vertical contact law drives rigid-body dynamics. Separate constant ratios map that generalized response to published main-strut load and buffer stroke because the linkage geometry and auxiliary-strut load split are not published.",
            },
        },
        "optimizer": optimizer,
        "configurations": configurations,
        "comparisons": comparisons,
        "acceptance": {
            "calibration_targets": thresholds,
            "calibration_metric_status": calibration_metric_status,
            "strict_calibration_pass": strict_calibration_pass,
            "overall_status": "PASS" if strict_calibration_pass else "PARTIAL",
            "validation_is_diagnostic": True,
            "reason": "Pitch inertia and exact geometry are not published, so asymmetric cases cannot yet be strict validation cases.",
        },
        "known_limits": [
            "Small-angle two-degree-of-freedom rigid-body model, not a flexible multibody mechanism.",
            "Footpads are massless unilateral contacts and horizontal friction is omitted.",
            "Published main-strut load and buffer stroke are observation mappings from generalized vertical contact; they are not reconstructed linkage forces or coordinates.",
            "Raster curves are baseline-corrected before identification; raw CSV files remain unchanged.",
            "No validation-case parameter is re-optimized.",
        ],
    }
    write_json(REPORT_PATH, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Identify a transparent reduced four-leg model from Yang Figure 9 and freeze it for Figures 10-11.")
    parser.add_argument("command", choices=["identify", "report"], nargs="?", default="report")
    args = parser.parse_args()
    report = build_report()
    print(f"Model status: {report['model_status']}")
    print(f"Optimizer success: {report['optimizer']['success']}")
    for condition_id, comparison in report["comparisons"].items():
        metrics = comparison["metrics"]
        print(
            f"{condition_id}: nRMSE acc={metrics['acceleration_up_m_s2']['normalized_rmse_vs_paper_peak']:.3f}, "
            f"force={metrics['strut_force_n']['normalized_rmse_vs_paper_peak']:.3f}, "
            f"stroke={metrics['stroke_m']['normalized_rmse_vs_paper_peak']:.3f}"
        )
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
