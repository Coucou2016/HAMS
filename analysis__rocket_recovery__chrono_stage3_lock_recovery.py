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
        tripod_actuated_lock_model_config,
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
        tripod_actuated_lock_model_config,
    )
    from chrono_one_way_recovery import deck_motion_from_wang, load_wang_response
    from chrono_stage3_recovery import build_validation, compact_simulation, ensure_dirs
    from common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
REPORT_JS = VISUALIZATION_DIR / "chrono-stage3-lock-data.js"
STAGE3_LOCK_CASES = ["calm_center", "wave_center", "wave_bow_15m", "wave_port_15m"]


def write_report_js(report: dict[str, Any]) -> None:
    REPORT_JS.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JS.write_text(
        "window.CHRONO_STAGE3_LOCK_DATA = " + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {REPORT_JS}")


def lock_validation(simulations: dict[str, Any]) -> dict[str, Any]:
    cases = {}
    for case_id, sim in simulations.items():
        lock = sim["summary"]["post_touchdown_lock"]
        cases[case_id] = {
            "eligible_lock_time_s": lock["eligible_lock_time_s"],
            "actual_lock_actuated_time_s": lock["actual_lock_actuated_time_s"],
            "actual_lock_final_state": lock["actual_lock_final_state"],
            "pass": lock["actual_lock_actuated_time_s"] is not None and bool(lock["actual_lock_final_state"]),
        }
    return {"cases": cases, "pass": all(row["pass"] for row in cases.values()) if cases else False}


def build_report(cases: list[str]) -> dict[str, Any]:
    ensure_dirs()
    config = tripod_actuated_lock_model_config()
    env = chrono_environment_report()
    if not env["available"]:
        write_json(CASE_ROOT / "validation" / "chrono-stage3-lock-env-check.json", env)
        raise ChronoUnavailableError(json.dumps(env, ensure_ascii=False, indent=2))
    wang = load_wang_response()
    simulations: dict[str, Any] = {}
    for case_id in cases:
        print(f"Running Stage 3 lock Chrono case: {case_id}", flush=True)
        motion = deck_motion_from_wang(wang, case_id, config)
        simulations[case_id] = ChronoTripodLegModel(config, motion).run()
    validation = build_validation(config, simulations)
    validation["actuated_lock"] = lock_validation(simulations)
    report = {
        "case_id": "Chrono_LeggedRecovery_Stage3_ActuatedLock",
        "title": "Stage 3 Chrono post-touchdown lock proxy",
        "status": "simulated",
        "environment": env,
        "coupling": {
            "mode": "one_way_stage3_actuated_lock_proxy",
            "platform_source": "Wang 2023 HAMS/Cummins deck motion",
            "platform_solver": "HAMS/Cummins; not modified",
            "leg_solver": "Project Chrono / PyChrono",
            "fallback_to_handwritten_contact": False,
        },
        "config": config,
        "leg_positions": leg_positions_from_config(config),
        "simulations": {case_id: compact_simulation(sim) for case_id, sim in simulations.items()},
        "validation": validation,
        "acceptance_scope": {
            "stage_3_lock_done": [
                "A ChLinkMateFix rocket-to-prescribed-deck constraint is added after all legs remain stable for the configured dwell time.",
                "The report records both the diagnostic eligible lock time and actual Chrono lock actuation time.",
                "The lock state is exported as a time series for animation and charts.",
            ],
            "not_claimed": [
                "published clamp geometry",
                "actuator dynamics",
                "load-rated hold-down hardware model",
                "post-lock transport seafastening model",
            ],
        },
    }
    write_json(CASE_ROOT / "Input" / "leg_model_config_stage3_lock.json", config)
    write_json(CASE_ROOT / "chrono-stage3-lock-report-data.json", report)
    write_json(CASE_ROOT / "Output" / "RocketRecovery" / "chrono-stage3-lock-response.json", report)
    write_report_js(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Stage 3 Chrono post-touchdown lock proxy cases.")
    parser.add_argument("command", choices=["check", "run", "report"], nargs="?", default="check")
    parser.add_argument("--case", action="append", choices=STAGE3_LOCK_CASES, help="Run one case. Can be repeated.")
    args = parser.parse_args()
    ensure_dirs()
    if args.command == "check":
        env = chrono_environment_report()
        write_json(CASE_ROOT / "validation" / "chrono-stage3-lock-env-check.json", env)
        print(f"Chrono available: {env['available']}")
        print(f"Report: {CASE_ROOT / 'validation' / 'chrono-stage3-lock-env-check.json'}")
        return
    try:
        report = build_report(args.case or STAGE3_LOCK_CASES)
    except ChronoUnavailableError as exc:
        print(exc)
        raise SystemExit(2)
    print(f"Status: {report['status']}")
    print(f"Report: {CASE_ROOT / 'chrono-stage3-lock-report-data.json'}")


if __name__ == "__main__":
    main()
