from __future__ import annotations

import argparse
import json
from typing import Any

try:
    from .chrono_leg_model import (
        ChronoTripodLegModel,
        ChronoUnavailableError,
        apply_thies_digitized_buffer_law,
        chrono_environment_report,
        leg_positions_from_config,
        tripod_rigid_body_link_model_config,
    )
    from .chrono_one_way_recovery import deck_motion_from_wang, load_wang_response
    from .chrono_stage3_recovery import build_validation, compact_simulation, ensure_dirs
    from .common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json
except ImportError:
    from chrono_leg_model import (
        ChronoTripodLegModel,
        ChronoUnavailableError,
        apply_thies_digitized_buffer_law,
        chrono_environment_report,
        leg_positions_from_config,
        tripod_rigid_body_link_model_config,
    )
    from chrono_one_way_recovery import deck_motion_from_wang, load_wang_response
    from chrono_stage3_recovery import build_validation, compact_simulation, ensure_dirs
    from common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
REPORT_JS = VISUALIZATION_DIR / "chrono-stage3c-rigid-body-link-data.js"
STAGE3C_CASES = ["calm_center", "wave_center", "wave_bow_15m", "wave_port_15m"]


def write_report_js(report: dict[str, Any]) -> None:
    REPORT_JS.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JS.write_text(
        "window.CHRONO_STAGE3C_RIGID_BODY_LINK_DATA = " + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {REPORT_JS}")


def build_report(cases: list[str]) -> dict[str, Any]:
    ensure_dirs()
    config = tripod_rigid_body_link_model_config()
    apply_thies_digitized_buffer_law(config, required=True)
    env = chrono_environment_report()
    if not env["available"]:
        write_json(CASE_ROOT / "validation" / "chrono-stage3c-rigid-body-link-env-check.json", env)
        raise ChronoUnavailableError(json.dumps(env, ensure_ascii=False, indent=2))
    wang = load_wang_response()
    simulations: dict[str, Any] = {}
    for case_id in cases:
        print(f"Running Stage 3C rigid-body-link Chrono case: {case_id}", flush=True)
        motion = deck_motion_from_wang(wang, case_id, config)
        simulations[case_id] = ChronoTripodLegModel(config, motion).run()
    report = {
        "case_id": "Chrono_LeggedRecovery_Stage3C_RigidBodyLinkDiagnostic",
        "title": "Stage 3C Chrono finite-mass rigid-body support-link diagnostic",
        "status": "simulated",
        "environment": env,
        "coupling": {
            "mode": "one_way_stage3c_rigid_body_link_diagnostic",
            "platform_source": "Wang 2023 HAMS/Cummins deck motion",
            "platform_solver": "HAMS/Cummins; not modified",
            "leg_solver": "Project Chrono / PyChrono",
            "buffer_law": "compression_only_table from Thies 2022 Figures 4 and 5 digitized curves",
            "fallback_to_handwritten_contact": False,
        },
        "config": config,
        "leg_positions": leg_positions_from_config(config),
        "simulations": {case_id: compact_simulation(sim) for case_id, sim in simulations.items()},
        "validation": build_validation(config, simulations),
        "acceptance_scope": {
            "stage_3c_done": [
                "Two published PT/KP support members per leg are represented as finite-mass cylinder bodies.",
                "Each support member is connected by spherical mates at the rocket attachment and footpad P point.",
                "The main B-to-foot member remains a nonlinear compression-only TSDA using Thies digitized absorber curves.",
                "Per-leg contact, stroke, slip, support margin, nozzle clearance, and stability diagnostics are recorded.",
            ],
            "not_claimed": [
                "CAD-exact hinge coordinates",
                "published rod radius, rod mass, inertia tensor, and material layup",
                "published telescopic absorber multibody topology",
                "Adams-equivalent joint set or locking mechanism",
                "validated structural load in each CFRP/Ti rod",
                "two-way Cummins feedback from the Stage 3C diagnostic branch",
            ],
        },
    }
    write_json(CASE_ROOT / "Input" / "leg_model_config_stage3c_rigid_body_link.json", config)
    write_json(CASE_ROOT / "chrono-stage3c-rigid-body-link-report-data.json", report)
    write_json(CASE_ROOT / "Output" / "RocketRecovery" / "chrono-stage3c-rigid-body-link-response.json", report)
    write_report_js(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Stage 3C Chrono finite-mass rigid-body support-link diagnostic cases.")
    parser.add_argument("command", choices=["check", "run", "report"], nargs="?", default="check")
    parser.add_argument("--case", action="append", choices=STAGE3C_CASES, help="Run one case. Can be repeated.")
    args = parser.parse_args()
    ensure_dirs()
    if args.command == "check":
        env = chrono_environment_report()
        config = tripod_rigid_body_link_model_config()
        has_curve = apply_thies_digitized_buffer_law(config, required=False)
        write_json(
            CASE_ROOT / "validation" / "chrono-stage3c-rigid-body-link-env-check.json",
            {"environment": env, "thies_digitized_buffer_available": has_curve},
        )
        print(f"Chrono available: {env['available']}")
        print(f"Thies digitized buffer available: {has_curve}")
        print(f"Report: {CASE_ROOT / 'validation' / 'chrono-stage3c-rigid-body-link-env-check.json'}")
        return
    try:
        report = build_report(args.case or STAGE3C_CASES)
    except ChronoUnavailableError as exc:
        print(exc)
        raise SystemExit(2)
    print(f"Status: {report['status']}")
    print(f"Report: {CASE_ROOT / 'chrono-stage3c-rigid-body-link-report-data.json'}")


if __name__ == "__main__":
    main()
