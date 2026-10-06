from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy import signal

try:
    from .common import G, ROOT, ROCKET_CASES_DIR, read_json, write_json
except ImportError:
    from common import G, ROOT, ROCKET_CASES_DIR, read_json, write_json


CASE_DIR = ROCKET_CASES_DIR / "Paper_Yang_2026"
REFERENCE_PATH = CASE_DIR / "reference" / "yang-2026-published.json"
REPORT_PATH = CASE_DIR / "yang-2026-evidence-report.json"
REPORT_MD_PATH = CASE_DIR / "yang-2026-evidence-report.md"


def load_reference(path: Path = REFERENCE_PATH) -> dict[str, Any]:
    return read_json(path)


def relative_error_percent(model_value: float, test_value: float) -> float:
    return 100.0 * abs(float(model_value) - float(test_value)) / max(abs(float(test_value)), 1.0e-15)


def audit_table_2(reference: dict[str, Any], tolerance_percentage_points: float = 0.25) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    strict_rows = 0
    strict_consistent = 0
    for source in reference["table_2"]:
        test_value = float(source["test"])
        flexible_error = relative_error_percent(float(source["flexible"]), test_value)
        rigid_error = relative_error_percent(float(source["rigid"]), test_value)
        flexible_delta = abs(flexible_error - float(source["flexible_error_percent_printed"]))
        rigid_delta = abs(rigid_error - float(source["rigid_error_percent_printed"]))
        internally_consistent = flexible_delta <= tolerance_percentage_points and rigid_delta <= tolerance_percentage_points
        if source.get("strict_validation", False):
            strict_rows += 1
            strict_consistent += int(internally_consistent)
        rows.append(
            {
                "condition_id": source["condition_id"],
                "metric": source["metric"],
                "strict_validation": bool(source.get("strict_validation", False)),
                "printed": {
                    "flexible_error_percent": source["flexible_error_percent_printed"],
                    "rigid_error_percent": source["rigid_error_percent_printed"],
                },
                "recomputed": {
                    "flexible_error_percent": flexible_error,
                    "rigid_error_percent": rigid_error,
                },
                "difference_percentage_points": {
                    "flexible": flexible_delta,
                    "rigid": rigid_delta,
                },
                "internally_consistent": internally_consistent,
                "note": source.get("note"),
            }
        )
    return {
        "tolerance_percentage_points": tolerance_percentage_points,
        "row_count": len(rows),
        "strict_row_count": strict_rows,
        "strict_consistent_count": strict_consistent,
        "all_strict_rows_consistent": strict_rows == strict_consistent,
        "rows": rows,
    }


def audit_sea_change_claims(reference: dict[str, Any]) -> dict[str, Any]:
    baseline = next(row for row in reference["table_2"] if row["condition_id"] == "Y1_1-2-1" and row["metric"] == "peak_vertical_acceleration_g")
    baseline_force = next(row for row in reference["table_2"] if row["condition_id"] == "Y1_1-2-1" and row["metric"] == "maximum_main_strut_load_n")
    baseline_stroke = next(row for row in reference["table_2"] if row["condition_id"] == "Y1_1-2-1" and row["metric"] == "maximum_buffer_stroke_m")
    sea = reference["sea_case"]

    def increase(new_value: float, old_value: float) -> float:
        return 100.0 * (new_value - old_value) / old_value

    return {
        "baseline": "Y1_1-2-1 flexible-body values from Table 2",
        "recomputed_increase_percent": {
            "peak_vertical_acceleration": increase(sea["peak_vertical_acceleration_g"], baseline["flexible"]),
            "maximum_main_strut_load": increase(sea["maximum_main_strut_load_n"], baseline_force["flexible"]),
            "maximum_buffer_stroke": increase(sea["maximum_buffer_stroke_m"], baseline_stroke["flexible"]),
        },
        "printed_claims_percent": sea["printed_change_claims_percent"],
        "status": "publication_values_and_percentage_labels_are_not_fully_consistent",
    }


def physics_consistent_drop_height(velocity_m_s: float, gravity_m_s2: float = G) -> float:
    return float(velocity_m_s) ** 2 / (2.0 * float(gravity_m_s2))


def printed_drop_height_equation_value(velocity_m_s: float, gravity_m_s2: float = G) -> float:
    return float(velocity_m_s) / (2.0 * float(gravity_m_s2))


def oil_damping_force(
    stroke_velocity_m_s: float,
    oil_density_kg_m3: float,
    compressed_oil_area_m2: float,
    compression_orifice_area_m2: float,
    rebound_orifice_area_m2: float,
    discharge_coefficient: float,
) -> float:
    velocity = float(stroke_velocity_m_s)
    orifice = float(compression_orifice_area_m2 if velocity >= 0.0 else rebound_orifice_area_m2)
    magnitude = (
        float(oil_density_kg_m3)
        * float(compressed_oil_area_m2) ** 3
        * velocity**2
        / (2.0 * float(discharge_coefficient) ** 2 * orifice**2)
    )
    return magnitude if velocity >= 0.0 else -magnitude


def air_spring_force(
    stroke_m: float,
    initial_air_height_m: float,
    initial_pressure_pa: float,
    atmospheric_pressure_pa: float,
    compressed_air_area_m2: float,
    polytropic_exponent: float,
) -> float:
    compression_ratio = 1.0 - float(stroke_m) / float(initial_air_height_m)
    if compression_ratio <= 0.0:
        raise ValueError("stroke_m must remain below initial_air_height_m")
    pressure = float(initial_pressure_pa) * compression_ratio ** (-float(polytropic_exponent))
    return float(compressed_air_area_m2) * (pressure - float(atmospheric_pressure_pa))


def structural_stop_force(stroke_m: float, initial_stroke_m: float, maximum_stroke_m: float, stiffness_n_m: float) -> float:
    stroke = float(stroke_m)
    if stroke < float(initial_stroke_m):
        return float(stiffness_n_m) * stroke
    if stroke <= float(maximum_stroke_m):
        return 0.0
    return float(stiffness_n_m) * (stroke - float(maximum_stroke_m))


def impact_normal_force(
    penetration_m: float,
    penetration_rate_m_s: float,
    stiffness_n_m_power: float,
    exponent: float,
    maximum_penetration_m: float,
    maximum_damping_ns_m: float,
) -> float:
    penetration = max(0.0, float(penetration_m))
    if penetration <= 0.0:
        return 0.0
    blend = min(1.0, penetration / max(float(maximum_penetration_m), 1.0e-15))
    damping = blend * float(maximum_damping_ns_m) * max(0.0, float(penetration_rate_m_s))
    return float(stiffness_n_m_power) * penetration ** float(exponent) + damping


def _continuous_filter_coefficients(reference: dict[str, Any], motion: str) -> tuple[np.ndarray, np.ndarray]:
    cfg = reference["deck_filters"][motion]
    numerator = np.asarray(cfg["numerator_descending_s"], dtype=float)
    denominator = np.asarray([1.0], dtype=float)
    for factor in cfg["denominator_factors"]:
        denominator = np.polymul(denominator, np.asarray(factor, dtype=float))
    return numerator, denominator


def simulate_unit_white_noise_deck(
    reference: dict[str, Any],
    duration_s: float = 120.0,
    dt_s: float = 0.01,
    seed: int = 2026,
) -> dict[str, Any]:
    if duration_s <= 0.0 or dt_s <= 0.0:
        raise ValueError("duration_s and dt_s must be positive")
    count = int(round(duration_s / dt_s)) + 1
    time_s = np.arange(count, dtype=float) * dt_s
    rng = np.random.default_rng(seed)
    white_noise = rng.normal(0.0, math.sqrt(1.0 / dt_s), size=count)
    output: dict[str, Any] = {
        "normalization": "input samples have variance 1/dt to approximate unit-intensity continuous white noise",
        "seed": int(seed),
        "dt_s": float(dt_s),
        "duration_s": float(time_s[-1]),
        "time_s": time_s.tolist(),
    }
    for motion in ("heave", "pitch"):
        numerator, denominator = _continuous_filter_coefficients(reference, motion)
        discrete_num, discrete_den, _ = signal.cont2discrete((numerator, denominator), dt_s, method="bilinear")
        values = signal.lfilter(np.squeeze(discrete_num), discrete_den, white_noise)
        output[f"{motion}_time_series"] = values.tolist()
        output[f"{motion}_statistics"] = {
            "mean": float(np.mean(values)),
            "rms": float(np.sqrt(np.mean(values**2))),
            "standard_deviation": float(np.std(values)),
            "peak_absolute": float(np.max(np.abs(values))),
        }
    output["claim_limit"] = (
        "The transfer-function shape is reproduced exactly. The paper does not publish white-noise normalization or seed, "
        "so this realization is not a pointwise reproduction of Figures 13 or 17."
    )
    return output


def build_report(reference: dict[str, Any], duration_s: float, dt_s: float, seed: int) -> dict[str, Any]:
    velocity = float(reference["test_conditions"][0]["vertical_touchdown_velocity_m_s"])
    table_audit = audit_table_2(reference)
    sea_audit = audit_sea_change_claims(reference)
    deck = simulate_unit_white_noise_deck(reference, duration_s=duration_s, dt_s=dt_s, seed=seed)
    return {
        "case_id": "Paper_Yang_2026",
        "paper": reference["paper"],
        "evidence_policy": {
            "published": "Directly printed numerical value or equation.",
            "digitized": "Extracted from a plotted curve and never treated as author-provided raw data.",
            "identified": "Estimated from one calibration case and excluded from validation claims for that case.",
            "proxy": "Engineering assumption used only in sensitivity studies.",
        },
        "drop_height_audit": {
            "touchdown_velocity_m_s": velocity,
            "paper_equation_value_m": printed_drop_height_equation_value(velocity),
            "physics_consistent_value_m": physics_consistent_drop_height(velocity),
            "status": "paper_equation_is_dimensionally_inconsistent",
        },
        "table_2_audit": table_audit,
        "sea_change_audit": sea_audit,
        "deck_filter_reproduction": deck,
        "required_but_unpublished_parameters": reference["required_but_unpublished_parameters"],
        "publication_anomalies": reference["publication_anomalies"],
        "reproduction_gate": {
            "scalar_targets_available": True,
            "deck_filter_equations_available": True,
            "full_adams_abaqus_replica_possible_from_publication_alone": False,
            "reason": "The paper does not publish the mechanism geometry, inertial, buffer, contact, modal and random-realization parameters required for a unique reconstruction.",
        },
    }


def write_markdown_report(report: dict[str, Any], path: Path = REPORT_MD_PATH) -> None:
    table = report["table_2_audit"]
    sea = report["sea_change_audit"]["recomputed_increase_percent"]
    deck = report["deck_filter_reproduction"]
    lines = [
        "# Yang et al. 2026 Evidence Audit",
        "",
        f"- DOI: `{report['paper']['doi']}`",
        f"- Table 2 rows: {table['row_count']}",
        f"- Strict rows internally consistent: {table['strict_consistent_count']}/{table['strict_row_count']}",
        f"- Physics-consistent drop height at 2 m/s: {report['drop_height_audit']['physics_consistent_value_m']:.6f} m",
        f"- Value from printed Equation 11: {report['drop_height_audit']['paper_equation_value_m']:.6f} m",
        "",
        "## Sea-case arithmetic",
        "",
        f"- Acceleration increase from published 1-2-1 flexible baseline: {sea['peak_vertical_acceleration']:.3f}%",
        f"- Main-strut load increase: {sea['maximum_main_strut_load']:.3f}%",
        f"- Buffer-stroke increase: {sea['maximum_buffer_stroke']:.3f}%",
        "",
        "## Deterministic deck realization",
        "",
        f"- Seed: {deck['seed']}",
        f"- Duration: {deck['duration_s']:.3f} s",
        f"- Time step: {deck['dt_s']:.6f} s",
        f"- Heave RMS: {deck['heave_statistics']['rms']:.6g} m",
        f"- Pitch RMS: {deck['pitch_statistics']['rms']:.6g} rad",
        "",
        "The filter equations are reproduced, but the time trace is not claimed to match the paper because the white-noise normalization and random seed were not published.",
        "",
        "## Reproduction gate",
        "",
        f"- Full ADAMS/Abaqus replica from publication alone: **{report['reproduction_gate']['full_adams_abaqus_replica_possible_from_publication_alone']}**",
        f"- Reason: {report['reproduction_gate']['reason']}",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit and reproduce the public Yang et al. 2026 equations and scalar targets.")
    parser.add_argument("command", choices=["audit", "deck", "report"], nargs="?", default="report")
    parser.add_argument("--duration", type=float, default=120.0)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    reference = load_reference()
    if args.command == "audit":
        payload = {
            "drop_height": {
                "printed_m": printed_drop_height_equation_value(2.0),
                "physics_consistent_m": physics_consistent_drop_height(2.0),
            },
            "table_2": audit_table_2(reference),
            "sea_change": audit_sea_change_claims(reference),
        }
    elif args.command == "deck":
        payload = simulate_unit_white_noise_deck(reference, duration_s=args.duration, dt_s=args.dt, seed=args.seed)
    else:
        payload = build_report(reference, duration_s=args.duration, dt_s=args.dt, seed=args.seed)
        write_json(REPORT_PATH, payload)
        write_markdown_report(payload)
    print(f"Yang 2026 {args.command}: {REPORT_PATH if args.command == 'report' else 'completed'}")


if __name__ == "__main__":
    main()
