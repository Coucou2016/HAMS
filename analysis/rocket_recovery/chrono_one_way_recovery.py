from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .chrono_leg_model import (
        ChronoOneWayLegModel,
        ChronoUnavailableError,
        DeckMotion,
        chrono_environment_report,
        default_leg_model_config,
        leg_positions_from_config,
    )
    from .common import ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
except ImportError:
    from chrono_leg_model import (
        ChronoOneWayLegModel,
        ChronoUnavailableError,
        DeckMotion,
        chrono_environment_report,
        default_leg_model_config,
        leg_positions_from_config,
    )
    from common import ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
REPORT_JS = VISUALIZATION_DIR / "chrono-recovery-data.js"
WANG_RESPONSE = ROCKET_CASES_DIR / "Paper_WangZhi_2023" / "Output" / "RocketRecovery" / "wang-2023-response.json"

STAGE1_CASES = ["calm_center", "wave_center", "wave_bow_15m", "wave_port_15m"]


def ensure_dirs() -> None:
    for path in [
        CASE_ROOT,
        CASE_ROOT / "Input",
        CASE_ROOT / "Output" / "RocketRecovery",
        CASE_ROOT / "validation",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def load_wang_response() -> dict[str, Any]:
    if not WANG_RESPONSE.exists():
        raise FileNotFoundError(f"Missing Wang response file: {WANG_RESPONSE}. Run wang_2023.py report first.")
    return read_json(WANG_RESPONSE)


def deck_motion_from_wang(wang: dict[str, Any], case_id: str, config: dict[str, Any]) -> DeckMotion:
    sim = wang["simulations"][case_id]
    time_s = np.array(sim["time_s"], dtype=float)
    zeros = np.zeros_like(time_s)
    return DeckMotion(
        time_s=time_s,
        heave_m=np.array(sim["responses"]["heave_m"], dtype=float),
        roll_rad=np.array(sim["responses"]["roll_rad"], dtype=float),
        pitch_rad=np.array(sim["responses"]["pitch_rad"], dtype=float),
        heave_m_s=np.array(sim["velocities"]["heave_m_s"], dtype=float),
        roll_rad_s=np.array(sim["velocities"]["roll_rad_s"], dtype=float),
        pitch_rad_s=np.array(sim["velocities"]["pitch_rad_s"], dtype=float),
        surge_m=np.array(sim["responses"].get("surge_m", zeros), dtype=float),
        sway_m=np.array(sim["responses"].get("sway_m", zeros), dtype=float),
        yaw_rad=np.array(sim["responses"].get("yaw_rad", zeros), dtype=float),
        surge_m_s=np.array(sim["velocities"].get("surge_m_s", zeros), dtype=float),
        sway_m_s=np.array(sim["velocities"].get("sway_m_s", zeros), dtype=float),
        yaw_rad_s=np.array(sim["velocities"].get("yaw_rad_s", zeros), dtype=float),
        offset_x_m=float(sim["offset"]["x"]),
        offset_y_m=float(sim["offset"]["y"]),
    )


def compact_deck_inputs(wang: dict[str, Any], cases: list[str]) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for case_id in cases:
        sim = wang["simulations"][case_id]
        time = np.array(sim["time_s"], dtype=float)
        mask = (time >= 506.0) & (time <= 526.0)
        rows[case_id] = {
            "offset": sim["offset"],
            "with_wave": sim["with_wave"],
            "with_plume": sim["with_plume"],
            "time_window_s": [506.0, 526.0],
            "samples": int(mask.sum()),
            "peak_deck_motion": {
                "surge_m": 0.0,
                "sway_m": 0.0,
                "heave_m": float(np.max(np.abs(np.array(sim["responses"]["heave_m"], dtype=float)[mask]))),
                "roll_deg": float(np.max(np.abs(np.array(sim["responses"]["roll_deg"], dtype=float)[mask]))),
                "pitch_deg": float(np.max(np.abs(np.array(sim["responses"]["pitch_deg"], dtype=float)[mask]))),
                "yaw_deg": 0.0,
            },
            "six_dof_adapter_note": "Wang 2023 reduced response supplies heave/roll/pitch; surge/sway/yaw are explicit zero-filled fields in the Chrono DeckMotion adapter.",
        }
    return rows


def build_validation(config: dict[str, Any], simulations: dict[str, Any] | None = None) -> dict[str, Any]:
    target = config["validation_targets"]["thies_touchdown_energy_kj"]
    computed = config["validation_targets"]["computed_touchdown_energy_kj"]
    validation: dict[str, Any] = {
        "thies_touchdown_energy": {
            "target_kj": target,
            "computed_kj": computed,
            "relative_error": abs(computed - target) / target if target else None,
            "pass": abs(computed - target) / target < 0.01 if target else False,
        },
        "chrono_required": "PASS only when environment.available is true and simulations were produced by Chrono.",
    }
    if simulations:
        validation["stage1_case_physical_bounds"] = {}
        for case_id, sim in simulations.items():
            validation["stage1_case_physical_bounds"][case_id] = {
                "max_contact_penetration_m": sim["summary"]["max_contact_penetration_m"],
                "max_footpad_slip_m": sim["summary"]["max_footpad_slip_m"],
                "max_leg_stroke_m": sim["summary"]["max_leg_stroke_m"],
                "max_rocket_roll_deg": sim["summary"]["max_rocket_roll_deg"],
                "max_rocket_pitch_deg": sim["summary"]["max_rocket_pitch_deg"],
                "penetration_limit_m": config["legs"]["footpad_radius_m"],
                "guide_slip_limit_m": 0.25,
                "pass": sim["summary"]["max_contact_penetration_m"] <= config["legs"]["footpad_radius_m"]
                and sim["summary"]["max_footpad_slip_m"] <= 0.25,
            }
        calm = simulations.get("calm_center")
        if calm:
            max_forces = []
            for values in calm["forces"]["leg_contact_force_n"].values():
                max_forces.append(max(values) / 1000.0 if values else 0.0)
            denom = max(max_forces) if max_forces else 0.0
            asym = (max(max_forces) - min(max_forces)) / denom if denom > 0 else 0.0
            validation["calm_center_symmetry"] = {
                "max_leg_contact_forces_kn": max_forces,
                "relative_asymmetry": asym,
                "tolerance": config["validation_targets"]["symmetric_force_tolerance"],
                "pass": asym <= config["validation_targets"]["symmetric_force_tolerance"],
            }
            validation["calm_center_physical_bounds"] = {
                "max_contact_penetration_m": calm["summary"]["max_contact_penetration_m"],
                "max_footpad_slip_m": calm["summary"]["max_footpad_slip_m"],
                "max_leg_stroke_m": calm["summary"]["max_leg_stroke_m"],
                "penetration_limit_m": config["legs"]["footpad_radius_m"],
                "slip_limit_m": 0.25,
                "pass": calm["summary"]["max_contact_penetration_m"] <= config["legs"]["footpad_radius_m"]
                and calm["summary"]["max_footpad_slip_m"] <= 0.25,
            }
        tilted = simulations.get("wave_port_15m") or simulations.get("wave_bow_15m")
        if tilted:
            first_contact = tilted["summary"]["first_contact_time_s"]
            all_contact = tilted["summary"]["all_legs_contact_time_s"]
            validation["tilted_deck_contact_sequence"] = {
                "first_contact_time_s": first_contact,
                "all_legs_contact_time_s": all_contact,
                "pass": first_contact is not None and all_contact is not None and all_contact > first_contact,
            }
    return validation


def build_report(run_chrono: bool, cases: list[str]) -> dict[str, Any]:
    ensure_dirs()
    config = default_leg_model_config()
    wang = load_wang_response()
    env = chrono_environment_report()
    simulations: dict[str, Any] = {}
    if run_chrono:
        if not env["available"]:
            write_json(CASE_ROOT / "validation" / "chrono-env-check.json", env)
            raise ChronoUnavailableError(json.dumps(env, ensure_ascii=False, indent=2))
        for case_id in cases:
            motion = deck_motion_from_wang(wang, case_id, config)
            print(f"Running PyChrono one-way case: {case_id}")
            simulations[case_id] = ChronoOneWayLegModel(config, motion).run()
    report = {
        "case_id": "Chrono_LeggedRecovery_OneWay",
        "title": "One-way HAMS/Cummins deck motion into Project Chrono landing-leg model",
        "status": "simulated" if simulations else "environment_check_only",
        "environment": env,
        "coupling": {
            "mode": "one_way",
            "platform_source": str(WANG_RESPONSE),
            "platform_solver": "HAMS/Cummins Wang 2023 surrogate",
            "leg_solver": "Project Chrono / PyChrono",
            "fallback_to_handwritten_contact": False,
            "deck_input": "prescribed heave/roll/pitch histories from Wang response JSON",
        },
        "config": config,
        "leg_positions": leg_positions_from_config(config),
        "deck_inputs": compact_deck_inputs(wang, cases),
        "simulations": simulations,
        "validation": build_validation(config, simulations if simulations else None),
        "acceptance_scope": {
            "stage_1": [
                "Chrono is required for the landing-leg/contact solver.",
                "The old integrated_recovery_model.contact_forces is not used.",
                "Four named cases are configured: calm_center, wave_center, wave_bow_15m, wave_port_15m.",
                "Generated outputs include leg contact, force, stroke, slip, rocket vertical motion and deck motion when Chrono is available.",
            ],
            "not_claimed": [
                "full Adams-equivalent linkage fidelity",
                "two-way feedback into Cummins equation",
                "validated nonlinear hydropneumatic buffer law",
            ],
        },
    }
    write_json(CASE_ROOT / "Input" / "leg_model_config.json", config)
    write_json(CASE_ROOT / "chrono-one-way-report-data.json", report)
    if simulations:
        write_json(CASE_ROOT / "Output" / "RocketRecovery" / "chrono-one-way-response.json", report)
    write_report_js(report)
    return report


def write_report_js(report: dict[str, Any]) -> None:
    REPORT_JS.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JS.write_text(
        "window.CHRONO_RECOVERY_DATA = " + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {REPORT_JS}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Project Chrono one-way landing-leg coupling from HAMS/Cummins deck motion.")
    parser.add_argument("command", choices=["check", "prepare", "run", "report"], nargs="?", default="check")
    parser.add_argument("--case", action="append", choices=STAGE1_CASES, help="Run/check one case. Can be repeated.")
    args = parser.parse_args()
    cases = args.case or STAGE1_CASES
    run_chrono = args.command in {"run", "report"}
    try:
        report = build_report(run_chrono=run_chrono, cases=cases)
    except ChronoUnavailableError as exc:
        print(exc)
        raise SystemExit(2)
    print(f"Status: {report['status']}")
    print(f"Chrono available: {report['environment']['available']}")
    print(f"Report: {CASE_ROOT / 'chrono-one-way-report-data.json'}")


if __name__ == "__main__":
    main()
