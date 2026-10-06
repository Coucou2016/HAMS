from __future__ import annotations

import argparse
import json
from typing import Any

try:
    from .chrono_leg_model import (
        ChronoTripodLegModel,
        ChronoUnavailableError,
        apply_thies_digitized_buffer_law,
        attach_parameter_provenance,
        chrono_environment_report,
        leg_positions_from_config,
        tripod_leg_model_config,
    )
    from .chrono_one_way_recovery import deck_motion_from_wang, load_wang_response
    from .chrono_stage3_recovery import STAGE3_CASES, build_validation, compact_simulation, ensure_dirs
    from .common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json
except ImportError:
    from chrono_leg_model import (
        ChronoTripodLegModel,
        ChronoUnavailableError,
        apply_thies_digitized_buffer_law,
        attach_parameter_provenance,
        chrono_environment_report,
        leg_positions_from_config,
        tripod_leg_model_config,
    )
    from chrono_one_way_recovery import deck_motion_from_wang, load_wang_response
    from chrono_stage3_recovery import STAGE3_CASES, build_validation, compact_simulation, ensure_dirs
    from common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
REPORT_JS = VISUALIZATION_DIR / "chrono-stage3-thies-buffer-data.js"


def write_report_js(report: dict[str, Any]) -> None:
    REPORT_JS.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JS.write_text(
        "window.CHRONO_STAGE3_THIES_BUFFER_DATA = " + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {REPORT_JS}")


def build_report(cases: list[str]) -> dict[str, Any]:
    ensure_dirs()
    config = tripod_leg_model_config()
    apply_thies_digitized_buffer_law(config, required=True)
    config["model_id"] = "ChronoLeggedRecovery_Stage3A_TripodProxy_ThiesDigitizedBuffer"
    config["legs"]["stage3_tripod_proxy"]["stage"] = "Stage 3A-thies-digitized-buffer"
    config["legs"]["equivalent_guidance_model"] += " Main buffer law is replaced by Thies 2022 Figure 4/5 digitized table curves."
    attach_parameter_provenance(config)
    env = chrono_environment_report()
    if not env["available"]:
        write_json(CASE_ROOT / "validation" / "chrono-stage3-thies-buffer-env-check.json", env)
        raise ChronoUnavailableError(json.dumps(env, ensure_ascii=False, indent=2))

    wang = load_wang_response()
    simulations: dict[str, Any] = {}
    for case_id in cases:
        print(f"Running Stage 3A Thies digitized-buffer Chrono case: {case_id}", flush=True)
        motion = deck_motion_from_wang(wang, case_id, config)
        simulations[case_id] = ChronoTripodLegModel(config, motion).run()

    report = {
        "case_id": "Chrono_LeggedRecovery_Stage3A_ThiesDigitizedBuffer",
        "title": "Stage 3A Chrono tripod with Thies 2022 digitized absorber curves",
        "status": "simulated",
        "environment": env,
        "coupling": {
            "mode": "one_way_stage3a_tripod_proxy_thies_digitized_buffer",
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
            "done": [
                "The main-buffer TSDA uses table-based spring and damping curves digitized from Thies 2022 Figures 4 and 5.",
                "The force sign convention is converted from Thies negative compression to Chrono positive compression.",
                "The numerical hard stop remains only outside the visible digitized Figure 4 stroke range.",
            ],
            "not_claimed": [
                "Original Adams input tables or author data recovery",
                "Exact hydropneumatic hardware characterization beyond the visible PDF figure curves",
                "CAD-exact tripod hinge coordinates",
            ],
        },
    }
    write_json(CASE_ROOT / "Input" / "leg_model_config_stage3_thies_buffer.json", config)
    write_json(CASE_ROOT / "chrono-stage3-thies-buffer-report-data.json", report)
    write_json(CASE_ROOT / "Output" / "RocketRecovery" / "chrono-stage3-thies-buffer-response.json", report)
    write_report_js(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Stage 3A Chrono tripod cases with Thies 2022 digitized absorber curves.")
    parser.add_argument("command", choices=["check", "run", "report"], nargs="?", default="check")
    parser.add_argument("--case", action="append", choices=STAGE3_CASES, help="Run one case. Can be repeated.")
    args = parser.parse_args()
    ensure_dirs()
    if args.command == "check":
        config = tripod_leg_model_config()
        ok = apply_thies_digitized_buffer_law(config, required=False)
        env = chrono_environment_report()
        check = {"chrono": env, "digitized_buffer_available": ok}
        write_json(CASE_ROOT / "validation" / "chrono-stage3-thies-buffer-env-check.json", check)
        print(f"Chrono available: {env['available']}")
        print(f"Digitized buffer available: {ok}")
        print(f"Report: {CASE_ROOT / 'validation' / 'chrono-stage3-thies-buffer-env-check.json'}")
        return
    try:
        report = build_report(args.case or STAGE3_CASES)
    except (ChronoUnavailableError, FileNotFoundError) as exc:
        print(exc)
        raise SystemExit(2)
    print(f"Status: {report['status']}")
    print(f"Report: {CASE_ROOT / 'chrono-stage3-thies-buffer-report-data.json'}")


if __name__ == "__main__":
    main()
