from __future__ import annotations

import argparse
import json
from typing import Any

try:
    from .chrono_leg_model import (
        ChronoTripodLegModel,
        ChronoUnavailableError,
        chrono_environment_report,
        leg_positions_from_config,
        tripod_rigid_brace_model_config,
    )
    from .chrono_one_way_recovery import deck_motion_from_wang, load_wang_response
    from .chrono_stage3_recovery import build_validation, compact_simulation, ensure_dirs
    from .common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json
except ImportError:
    from chrono_leg_model import (
        ChronoTripodLegModel,
        ChronoUnavailableError,
        chrono_environment_report,
        leg_positions_from_config,
        tripod_rigid_brace_model_config,
    )
    from chrono_one_way_recovery import deck_motion_from_wang, load_wang_response
    from chrono_stage3_recovery import build_validation, compact_simulation, ensure_dirs
    from common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
REPORT_JS = VISUALIZATION_DIR / "chrono-stage3b-rigid-data.js"
STAGE3B_CASES = ["calm_center", "wave_center", "wave_bow_15m", "wave_port_15m"]


def write_report_js(report: dict[str, Any]) -> None:
    REPORT_JS.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JS.write_text(
        "window.CHRONO_STAGE3B_RIGID_DATA = " + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {REPORT_JS}")


def build_report(cases: list[str]) -> dict[str, Any]:
    ensure_dirs()
    config = tripod_rigid_brace_model_config()
    env = chrono_environment_report()
    if not env["available"]:
        write_json(CASE_ROOT / "validation" / "chrono-stage3b-rigid-env-check.json", env)
        raise ChronoUnavailableError(json.dumps(env, ensure_ascii=False, indent=2))
    wang = load_wang_response()
    simulations: dict[str, Any] = {}
    for case_id in cases:
        print(f"Running Stage 3B rigid-brace Chrono case: {case_id}", flush=True)
        motion = deck_motion_from_wang(wang, case_id, config)
        simulations[case_id] = ChronoTripodLegModel(config, motion).run()
    report = {
        "case_id": "Chrono_LeggedRecovery_Stage3B_RigidBrace",
        "title": "Stage 3B Chrono rigid-brace landing-leg proxy",
        "status": "simulated",
        "environment": env,
        "coupling": {
            "mode": "one_way_stage3b_rigid_brace_proxy",
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
            "stage_3b_done": [
                "Two diagonal braces per leg are represented by fixed-length ChLinkDistance constraints.",
                "The main B-to-foot member remains a nonlinear compression-only TSDA buffer.",
                "The Stage 3A inclined prismatic guide is disabled to avoid over-constraining the simplified tripod proxy.",
                "Per-leg contact state, stroke, slip, support margin, nozzle clearance, and stable-standing diagnostics are recorded.",
            ],
            "not_claimed": [
                "CAD-exact hinge coordinates",
                "rigid brace bodies with published mass/inertia",
                "measured hydropneumatic buffer force-stroke or force-velocity curve",
                "actuated mechanical lock",
                "two-way Cummins feedback from the Stage 3B rigid-brace proxy",
            ],
        },
    }
    write_json(CASE_ROOT / "Input" / "leg_model_config_stage3b_rigid.json", config)
    write_json(CASE_ROOT / "chrono-stage3b-rigid-report-data.json", report)
    write_json(CASE_ROOT / "Output" / "RocketRecovery" / "chrono-stage3b-rigid-response.json", report)
    write_report_js(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Stage 3B Chrono rigid-brace landing-leg proxy cases.")
    parser.add_argument("command", choices=["check", "run", "report"], nargs="?", default="check")
    parser.add_argument("--case", action="append", choices=STAGE3B_CASES, help="Run one case. Can be repeated.")
    args = parser.parse_args()
    ensure_dirs()
    if args.command == "check":
        env = chrono_environment_report()
        write_json(CASE_ROOT / "validation" / "chrono-stage3b-rigid-env-check.json", env)
        print(f"Chrono available: {env['available']}")
        print(f"Report: {CASE_ROOT / 'validation' / 'chrono-stage3b-rigid-env-check.json'}")
        return
    try:
        report = build_report(args.case or STAGE3B_CASES)
    except ChronoUnavailableError as exc:
        print(exc)
        raise SystemExit(2)
    print(f"Status: {report['status']}")
    print(f"Report: {CASE_ROOT / 'chrono-stage3b-rigid-report-data.json'}")


if __name__ == "__main__":
    main()
