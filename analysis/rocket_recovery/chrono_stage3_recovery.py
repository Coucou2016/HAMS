from __future__ import annotations

import argparse
import json
from typing import Any

import numpy as np

try:
    from .chrono_leg_model import (
        ChronoTripodLegModel,
        ChronoUnavailableError,
        chrono_environment_report,
        leg_positions_from_config,
        tripod_leg_model_config,
    )
    from .chrono_one_way_recovery import deck_motion_from_wang, load_wang_response
    from .common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json
except ImportError:
    from chrono_leg_model import (
        ChronoTripodLegModel,
        ChronoUnavailableError,
        chrono_environment_report,
        leg_positions_from_config,
        tripod_leg_model_config,
    )
    from chrono_one_way_recovery import deck_motion_from_wang, load_wang_response
    from common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
REPORT_JS = VISUALIZATION_DIR / "chrono-stage3-tripod-data.js"
STAGE3_CASES = ["calm_center", "wave_center", "wave_bow_15m", "wave_port_15m"]


def ensure_dirs() -> None:
    for path in [
        CASE_ROOT,
        CASE_ROOT / "Input",
        CASE_ROOT / "Output" / "RocketRecovery",
        CASE_ROOT / "validation",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def thies_energy_validation(config: dict[str, Any]) -> dict[str, Any]:
    target = float(config["validation_targets"]["thies_touchdown_energy_kj"])
    computed = float(config["validation_targets"]["computed_touchdown_energy_kj"])
    rel = abs(computed - target) / target if target else None
    return {
        "target_kj": target,
        "computed_kj": computed,
        "relative_error": rel,
        "pass": rel is not None and rel < 0.01,
    }


def case_validation(config: dict[str, Any], sim: dict[str, Any]) -> dict[str, Any]:
    summary = sim["summary"]
    contact_state = summary["contact_state"]
    penetration_limit = float(config["legs"]["footpad_radius_m"])
    slip_limit = 0.50
    final_v_limit = 0.05
    return {
        "max_contact_penetration_m": summary["max_contact_penetration_m"],
        "penetration_limit_m": penetration_limit,
        "max_footpad_slip_m": summary["max_footpad_slip_m"],
        "diagnostic_slip_limit_m": slip_limit,
        "final_contact_count": summary["final_contact_count"],
        "final_vertical_velocity_m_s": summary["final_vertical_velocity_m_s"],
        "touchdown_span_s": contact_state["touchdown_span_s"],
        "liftoff_count_total": contact_state["liftoff_count_total"],
        "recontact_count_total": contact_state["recontact_count_total"],
        "all_contact_intervals_s": contact_state["all_contact_intervals_s"],
        "stable_standing_diagnostic": summary["stable_standing_diagnostic"],
        "eligible_lock_time_s": summary["post_touchdown_lock"]["eligible_lock_time_s"],
        "max_brace_length_error_m": summary["max_brace_length_error_m"],
        "max_brace_axial_force_kn": summary["max_brace_axial_force_kn"],
        "min_support_polygon_margin_m": summary["min_support_polygon_margin_m"],
        "final_support_polygon_margin_m": summary["final_support_polygon_margin_m"],
        "min_nozzle_clearance_m": summary.get("min_nozzle_clearance_m"),
        "final_nozzle_clearance_m": summary.get("final_nozzle_clearance_m"),
        "nozzle_clearance_required_m": config["rocket"]["nozzle_clearance_required_m"],
        "nozzle_clearance_diagnostic": "reported for traceability only; not used as a Stage 3A pass/fail criterion",
        "pass": (
            summary["max_contact_penetration_m"] <= penetration_limit
            and summary["max_footpad_slip_m"] <= slip_limit
            and summary["final_contact_count"] == int(config["legs"]["count"])
            and abs(summary["final_vertical_velocity_m_s"]) <= final_v_limit
            and summary["post_touchdown_lock"]["eligible_lock_time_s"] is not None
        ),
    }


def build_validation(config: dict[str, Any], simulations: dict[str, Any]) -> dict[str, Any]:
    cases = {case_id: case_validation(config, sim) for case_id, sim in simulations.items()}
    contact_cases = {}
    for case_id, sim in simulations.items():
        state = sim["summary"]["contact_state"]
        per_leg = state["per_leg"]
        contact_cases[case_id] = {
            "per_leg_first_contact_times_s": {leg_id: row["first_contact_time_s"] for leg_id, row in per_leg.items()},
            "touchdown_sequence": state["touchdown_sequence"],
            "touchdown_span_s": state["touchdown_span_s"],
            "liftoff_count_total": state["liftoff_count_total"],
            "recontact_count_total": state["recontact_count_total"],
            "final_contact_count": state["final_contact_count"],
            "all_contact_interval_count": len(state["all_contact_intervals_s"]),
            "pass": (
                len(per_leg) == int(config["legs"]["count"])
                and all(row["first_contact_time_s"] is not None for row in per_leg.values())
                and state["all_legs_finally_in_contact"]
                and len(state["all_contact_intervals_s"]) > 0
            ),
        }
    return {
        "thies_touchdown_energy": thies_energy_validation(config),
        "mechanism_topology": {
            "elements_per_leg": config["legs"]["stage3_tripod_proxy"]["mechanism_elements_per_leg"],
            "pass": all(
                key in config["legs"]["stage3_tripod_proxy"]["mechanism_elements_per_leg"]
                for key in ["main_guide", "main_buffer", "long_brace", "short_brace", "footpad"]
            ),
        },
        "nonlinear_buffer_law": {
            "law": config["legs"]["nonlinear_buffer_law"],
            "pass": config["legs"]["nonlinear_buffer_law"]["type"] in config["legs"]["nonlinear_buffer_law"]["supported_types"]
            and bool(config["legs"]["nonlinear_buffer_law"]["no_tension"]),
        },
        "contact_state_machine": {"cases": contact_cases, "pass": all(row["pass"] for row in contact_cases.values()) if contact_cases else False},
        "case_physical_diagnostics": {"cases": cases, "pass": all(row["pass"] for row in cases.values()) if cases else False},
        "parameter_traceability": {
            "published_value_count": len(config["parameter_audit"]["published_values"]),
            "explicit_assumption_count": len(config["parameter_audit"]["explicit_assumptions"]),
            "pass": len(config["parameter_audit"]["published_values"]) > 0 and len(config["parameter_audit"]["explicit_assumptions"]) > 0,
        },
    }


def compact_simulation(sim: dict[str, Any], max_points: int = 2000) -> dict[str, Any]:
    time = sim["time_s"]
    stride = max(1, int(np.ceil(len(time) / max_points)))
    indices = list(range(0, len(time), stride))
    if indices[-1] != len(time) - 1:
        indices.append(len(time) - 1)

    def take(series: list[float]) -> list[float]:
        return [series[i] for i in indices]

    compact = {
        "time_s": take(time),
        "deck": {key: take(values) for key, values in sim["deck"].items()},
        "rocket": {key: take(values) for key, values in sim["rocket"].items()},
        "forces": {
            "leg_tsda_force_n": {leg: take(values) for leg, values in sim["forces"]["leg_tsda_force_n"].items()},
            "leg_contact_force_n": {leg: take(values) for leg, values in sim["forces"]["leg_contact_force_n"].items()},
            "leg_contact_force_xyz_n": {
                leg: {axis: take(values) for axis, values in axes.items()} for leg, axes in sim["forces"]["leg_contact_force_xyz_n"].items()
            },
            "lock_reaction_force_xyz_n": {
                axis: take(values) for axis, values in sim["forces"].get("lock_reaction_force_xyz_n", {}).items()
            },
            "lock_reaction_torque_xyz_nm": {
                axis: take(values) for axis, values in sim["forces"].get("lock_reaction_torque_xyz_nm", {}).items()
            },
        },
        "feet": {"position_m": {leg: {axis: take(values) for axis, values in axes.items()} for leg, axes in sim["feet"]["position_m"].items()}},
        "contact": {
            "leg_stroke_m": {leg: take(values) for leg, values in sim["contact"]["leg_stroke_m"].items()},
            "leg_contact_penetration_m": {leg: take(values) for leg, values in sim["contact"]["leg_contact_penetration_m"].items()},
            "leg_slip_m": {leg: take(values) for leg, values in sim["contact"]["leg_slip_m"].items()},
            "leg_contact": {leg: [values[i] for i in indices] for leg, values in sim["contact"]["leg_contact"].items()},
        },
        "mechanism": {
            "anchor_position_m": sim["mechanism"]["anchor_position_m"],
            "brace_length_error_m": {
                leg: {brace: take(values) for brace, values in brace_rows.items()}
                for leg, brace_rows in sim["mechanism"]["brace_length_error_m"].items()
            },
            "brace_force_n": {
                leg: {brace: take(values) for brace, values in brace_rows.items()}
                for leg, brace_rows in sim["mechanism"]["brace_force_n"].items()
            },
            "support_polygon_margin_m": take(sim["mechanism"]["support_polygon_margin_m"]),
            "lock_state": [sim["mechanism"].get("lock_state", [0] * len(time))[i] for i in indices],
            "lock_point_position_m": {
                axis: take(values) for axis, values in sim["mechanism"].get("lock_point_position_m", {}).items()
            },
        },
        "summary": sim["summary"],
    }
    return compact


def write_report_js(report: dict[str, Any]) -> None:
    REPORT_JS.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JS.write_text(
        "window.CHRONO_STAGE3_TRIPOD_DATA = " + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {REPORT_JS}")


def build_report(cases: list[str]) -> dict[str, Any]:
    ensure_dirs()
    config = tripod_leg_model_config()
    env = chrono_environment_report()
    if not env["available"]:
        write_json(CASE_ROOT / "validation" / "chrono-stage3-env-check.json", env)
        raise ChronoUnavailableError(json.dumps(env, ensure_ascii=False, indent=2))
    wang = load_wang_response()
    simulations: dict[str, Any] = {}
    for case_id in cases:
        print(f"Running Stage 3A tripod Chrono case: {case_id}", flush=True)
        motion = deck_motion_from_wang(wang, case_id, config)
        simulations[case_id] = ChronoTripodLegModel(config, motion).run()
    report = {
        "case_id": "Chrono_LeggedRecovery_Stage3A_Tripod",
        "title": "Stage 3A Chrono tripod landing-leg proxy",
        "status": "simulated",
        "environment": env,
        "coupling": {
            "mode": "one_way_stage3a_tripod_proxy",
            "platform_source": "Wang 2023 HAMS/Cummins deck motion",
            "platform_solver": "HAMS/Cummins; not modified",
            "leg_solver": "Project Chrono / PyChrono",
            "fallback_to_handwritten_contact": False,
        },
        "config": config,
        "leg_positions": leg_positions_from_config(config),
        "simulations": {case_id: compact_simulation(sim) for case_id, sim in simulations.items()},
        "validation": build_validation(config, simulations),
        "acceptance_scope": {
            "stage_3a_done": [
                "Main leg is an inclined Chrono prismatic guide, not the earlier vertical guide.",
                "Main buffer uses a nonlinear compression-only force functor with a hard-stop region.",
                "Main buffer can be switched to a table-based force-stroke/force-velocity law when measured or digitized data is available.",
                "Two diagonal braces are included as spherical-end axial elastic links and their force/length errors are recorded.",
                "Per-leg first contact, liftoff, recontact, contact intervals, touchdown span, and final contact state are recorded.",
                "Post-touchdown lock is evaluated as a diagnostic stability time.",
            ],
            "not_claimed": [
                "CAD-exact tripod hinge coordinates",
                "rigid brace bodies with published mass/inertia",
                "validated hydropneumatic buffer force-stroke or force-velocity curve",
                "actuated mechanical lock that changes the Chrono constraints after touchdown",
                "two-way feedback from a CAD-exact Stage 3 mechanism; Stage 3A proxy feedback is handled by chrono_stage3_two_way_recovery.py",
            ],
        },
    }
    write_json(CASE_ROOT / "Input" / "leg_model_config_stage3_tripod.json", config)
    write_json(CASE_ROOT / "chrono-stage3-tripod-report-data.json", report)
    write_json(CASE_ROOT / "Output" / "RocketRecovery" / "chrono-stage3-tripod-response.json", report)
    write_report_js(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Stage 3A Chrono tripod landing-leg proxy cases.")
    parser.add_argument("command", choices=["check", "run", "report"], nargs="?", default="check")
    parser.add_argument("--case", action="append", choices=STAGE3_CASES, help="Run one case. Can be repeated.")
    args = parser.parse_args()
    ensure_dirs()
    if args.command == "check":
        env = chrono_environment_report()
        write_json(CASE_ROOT / "validation" / "chrono-stage3-env-check.json", env)
        print(f"Chrono available: {env['available']}")
        print(f"Report: {CASE_ROOT / 'validation' / 'chrono-stage3-env-check.json'}")
        return
    try:
        report = build_report(args.case or STAGE3_CASES)
    except ChronoUnavailableError as exc:
        print(exc)
        raise SystemExit(2)
    print(f"Status: {report['status']}")
    print(f"Report: {CASE_ROOT / 'chrono-stage3-tripod-report-data.json'}")


if __name__ == "__main__":
    main()
