from __future__ import annotations

import argparse
import json
import math
from typing import Any

import numpy as np

try:
    from .chrono_leg_model import (
        ChronoTripodLegModel,
        ChronoUnavailableError,
        chrono_environment_report,
        leg_positions_from_config,
        tripod_actuated_lock_model_config,
    )
    from .chrono_stage3_recovery import compact_simulation
    from .chrono_stage3_two_way_recovery import build_validation as build_stage3a_two_way_validation
    from .chrono_two_way_recovery import (
        baseline_arrays_6dof,
        compare_time_step_series_6dof,
        compare_peak_change,
        deck_motion_from_arrays_6dof,
        deck_motion_from_wang_raw,
        generalized_leg_force_from_chrono_6dof,
        leg_force_series_for_json_6dof,
        load_cummins_matrices_6dof,
        load_wang_response,
        make_time_grid,
        peak_summary_6dof,
        rocket_energy_diagnostic,
        solve_cummins_leg_correction,
        values_to_named_series_6dof,
    )
    from .common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json
except ImportError:
    from chrono_leg_model import (
        ChronoTripodLegModel,
        ChronoUnavailableError,
        chrono_environment_report,
        leg_positions_from_config,
        tripod_actuated_lock_model_config,
    )
    from chrono_stage3_recovery import compact_simulation
    from chrono_stage3_two_way_recovery import build_validation as build_stage3a_two_way_validation
    from chrono_two_way_recovery import (
        baseline_arrays_6dof,
        compare_time_step_series_6dof,
        compare_peak_change,
        deck_motion_from_arrays_6dof,
        deck_motion_from_wang_raw,
        generalized_leg_force_from_chrono_6dof,
        leg_force_series_for_json_6dof,
        load_cummins_matrices_6dof,
        load_wang_response,
        make_time_grid,
        peak_summary_6dof,
        rocket_energy_diagnostic,
        solve_cummins_leg_correction,
        values_to_named_series_6dof,
    )
    from common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
REPORT_JS = VISUALIZATION_DIR / "chrono-stage3-lock-two-way-data.js"
PROGRESS_LOG = CASE_ROOT / "validation" / "chrono-stage3-lock-two-way-progress.log"
STAGE3_LOCK_TWO_WAY_CASES = ["calm_center", "wave_center", "wave_bow_15m", "wave_port_15m"]
COUPLING_CLOSURE_TOLERANCE = {
    "translation_peak_m": 1.0e-3,
    "rotation_peak_deg": 1.0e-3,
    "translation_velocity_peak_m_s": 1.0e-3,
    "rotation_rate_peak_deg_s": 1.0e-3,
}


def ensure_dirs() -> None:
    for path in [
        CASE_ROOT,
        CASE_ROOT / "Input",
        CASE_ROOT / "Output" / "RocketRecovery",
        CASE_ROOT / "validation",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def log_progress(message: str) -> None:
    PROGRESS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with PROGRESS_LOG.open("a", encoding="utf-8") as handle:
        handle.write(message + "\n")
    print(message, flush=True)


def run_lock_chrono(config: dict[str, Any], motion: Any, label: str) -> dict[str, Any]:
    log_progress(f"Running Stage 3 lock two-way source case: {label}")
    return ChronoTripodLegModel(config, motion).run()


def animation_deck_consistency(chrono_sim: dict[str, Any], time_s: np.ndarray, q: np.ndarray) -> dict[str, Any]:
    chrono_time = np.asarray(chrono_sim["time_s"], dtype=float)
    deck = chrono_sim["deck"]
    keys = ["surge_m", "sway_m", "heave_m", "roll_rad", "pitch_rad", "yaw_rad"]
    max_errors = {}
    for column, key in enumerate(keys):
        expected = np.interp(chrono_time, time_s, q[:, column])
        actual = np.asarray(deck[key], dtype=float)
        max_errors[key] = float(np.max(np.abs(actual - expected))) if len(actual) else 0.0
    max_error = max(max_errors.values(), default=0.0)
    return {
        "source": "final Chrono replay driven by the reported with_leg_feedback 6DOF deck history",
        "max_abs_error_by_dof": max_errors,
        "tolerance": 1.0e-10,
        "pass": max_error <= 1.0e-10,
    }


def coupling_closure_check(summary: dict[str, float]) -> dict[str, Any]:
    checks = {
        "surge_peak_m": summary["surge_peak_m"] <= COUPLING_CLOSURE_TOLERANCE["translation_peak_m"],
        "sway_peak_m": summary["sway_peak_m"] <= COUPLING_CLOSURE_TOLERANCE["translation_peak_m"],
        "heave_peak_m": summary["heave_peak_m"] <= COUPLING_CLOSURE_TOLERANCE["translation_peak_m"],
        "roll_peak_deg": summary["roll_peak_deg"] <= COUPLING_CLOSURE_TOLERANCE["rotation_peak_deg"],
        "pitch_peak_deg": summary["pitch_peak_deg"] <= COUPLING_CLOSURE_TOLERANCE["rotation_peak_deg"],
        "yaw_peak_deg": summary["yaw_peak_deg"] <= COUPLING_CLOSURE_TOLERANCE["rotation_peak_deg"],
        "surge_velocity_peak_m_s": summary["surge_velocity_peak_m_s"] <= COUPLING_CLOSURE_TOLERANCE["translation_velocity_peak_m_s"],
        "sway_velocity_peak_m_s": summary["sway_velocity_peak_m_s"] <= COUPLING_CLOSURE_TOLERANCE["translation_velocity_peak_m_s"],
        "heave_velocity_peak_m_s": summary["heave_velocity_peak_m_s"] <= COUPLING_CLOSURE_TOLERANCE["translation_velocity_peak_m_s"],
        "roll_rate_peak_deg_s": summary["roll_rate_peak_deg_s"] <= COUPLING_CLOSURE_TOLERANCE["rotation_rate_peak_deg_s"],
        "pitch_rate_peak_deg_s": summary["pitch_rate_peak_deg_s"] <= COUPLING_CLOSURE_TOLERANCE["rotation_rate_peak_deg_s"],
        "yaw_rate_peak_deg_s": summary["yaw_rate_peak_deg_s"] <= COUPLING_CLOSURE_TOLERANCE["rotation_rate_peak_deg_s"],
    }
    return {
        "tolerances": COUPLING_CLOSURE_TOLERANCE,
        "checks": checks,
        "pass": all(checks.values()),
    }


def run_feedback_case(
    case_id: str,
    config: dict[str, Any],
    wang: dict[str, Any],
    matrices: dict[str, Any],
    iterations: int,
    coupling_dt_s: float,
    relaxation: float,
) -> dict[str, Any]:
    start = float(config["solver"]["start_s"])
    end = float(config["solver"]["end_s"])
    time_s = make_time_grid(start, end, coupling_dt_s)
    baseline_sim, q_base, qd_base = baseline_arrays_6dof(wang, case_id, time_s)
    offset = baseline_sim["offset"]
    current_q = q_base.copy()
    current_qd = qd_base.copy()
    current_motion = deck_motion_from_wang_raw(wang, case_id)
    zero_force = np.zeros((len(time_s), 6), dtype=float)
    zero_correction = solve_cummins_leg_correction(matrices, time_s, zero_force, coupling_dt_s)
    iteration_rows: list[dict[str, Any]] = []
    final_chrono: dict[str, Any] | None = None
    final_force = zero_force
    final_replay_force: dict[str, Any] | None = None

    for iteration in range(1, iterations + 1):
        input_q = current_q.copy()
        input_qd = current_qd.copy()
        chrono_sim = run_lock_chrono(config, current_motion, f"{case_id} iteration {iteration}/{iterations}")
        log_progress(f"Chrono completed: {case_id} iteration {iteration}/{iterations}")
        force = generalized_leg_force_from_chrono_6dof(
            chrono_sim,
            time_s,
            include_lock_reaction=True,
            footpad_radius_m=float(config["legs"]["footpad_radius_m"]),
        )
        log_progress(f"6DOF reaction mapping completed: {case_id} iteration {iteration}/{iterations}")
        correction = solve_cummins_leg_correction(matrices, time_s, force["values_6dof"], coupling_dt_s)
        log_progress(f"6DOF Cummins correction completed: {case_id} iteration {iteration}/{iterations}")
        raw_target_q = q_base + correction["q"]
        raw_target_qd = qd_base + correction["qd"]
        current_q = input_q + relaxation * (raw_target_q - input_q)
        current_qd = input_qd + relaxation * (raw_target_qd - input_qd)
        current_motion = deck_motion_from_arrays_6dof(time_s, current_q, current_qd, offset)
        final_chrono = chrono_sim
        final_force = force["values_6dof"]
        iteration_rows.append(
            {
                "iteration": iteration,
                "chrono_summary": chrono_sim["summary"],
                "leg_force_summary": force["summary"],
                "force_audit": force["force_audit"],
                "platform_delta_summary": peak_summary_6dof(correction["q"], correction["qd"]),
                "raw_target_delta_summary": peak_summary_6dof(raw_target_q - q_base, raw_target_qd - qd_base),
                "relaxed_update_summary": peak_summary_6dof(current_q - input_q, current_qd - input_qd),
                "relaxation": relaxation,
                "rocket_energy": rocket_energy_diagnostic(config, chrono_sim),
            }
        )

    assert final_chrono is not None
    log_progress(f"Running final Chrono replay on the reported 6DOF feedback deck: {case_id}")
    final_chrono = run_lock_chrono(config, current_motion, f"{case_id} final feedback-deck replay")
    final_replay_force = generalized_leg_force_from_chrono_6dof(
        final_chrono,
        time_s,
        include_lock_reaction=True,
        footpad_radius_m=float(config["legs"]["footpad_radius_m"]),
    )
    replay_correction = solve_cummins_leg_correction(matrices, time_s, final_replay_force["values_6dof"], coupling_dt_s)
    replay_raw_target_q = q_base + replay_correction["q"]
    replay_raw_target_qd = qd_base + replay_correction["qd"]
    replay_next_q = current_q + relaxation * (replay_raw_target_q - current_q)
    replay_next_qd = current_qd + relaxation * (replay_raw_target_qd - current_qd)
    replay_consistency = animation_deck_consistency(final_chrono, time_s, current_q)
    closure_summary = peak_summary_6dof(replay_next_q - current_q, replay_next_qd - current_qd)
    closure_gate = coupling_closure_check(closure_summary)
    replay_time = np.asarray(final_chrono["time_s"], dtype=float)
    output_dt = float(config["solver"]["output_step_s"])
    expected_output_count = int(round((end - start) / output_dt)) + 1
    chrono_time_grid = {
        "start_s": float(replay_time[0]) if len(replay_time) else None,
        "end_s": float(replay_time[-1]) if len(replay_time) else None,
        "sample_count": int(len(replay_time)),
        "expected_sample_count": expected_output_count,
        "strictly_increasing": bool(len(replay_time) > 0 and np.all(np.diff(replay_time) > 0.0)),
    }
    chrono_time_grid["pass"] = bool(
        len(replay_time) == expected_output_count
        and math.isclose(float(replay_time[0]), start, rel_tol=0.0, abs_tol=1.0e-12)
        and math.isclose(float(replay_time[-1]), end, rel_tol=0.0, abs_tol=1.0e-12)
        and chrono_time_grid["strictly_increasing"]
    )
    log_progress(f"Final Chrono feedback-deck replay completed: {case_id}")
    no_leg_max = float(np.max(np.abs(zero_correction["q"])))
    return {
        "id": case_id,
        "environment": baseline_sim["environment"],
        "offset": offset,
        "with_wave": baseline_sim["with_wave"],
        "with_plume": baseline_sim["with_plume"],
        "iterations_requested": iterations,
        "coupling_relaxation": relaxation,
        "coupling_dt_s": coupling_dt_s,
        "baseline": {**values_to_named_series_6dof(time_s, q_base, qd_base), "summary": peak_summary_6dof(q_base, qd_base)},
        "with_leg_feedback": {**values_to_named_series_6dof(time_s, current_q, current_qd), "summary": peak_summary_6dof(current_q, current_qd)},
        "leg_induced_delta": {**values_to_named_series_6dof(time_s, current_q - q_base, current_qd - qd_base), "summary": peak_summary_6dof(current_q - q_base, current_qd - qd_base)},
        "leg_generalized_force": leg_force_series_for_json_6dof(time_s, final_replay_force["values_6dof"]),
        "final_replay_force_summary": final_replay_force["summary"],
        "final_replay_force_audit": final_replay_force["force_audit"],
        "final_iteration_chrono": final_chrono,
        "iterations": iteration_rows,
        "validation": {
            "no_leg_degeneracy": {
                "max_abs_zero_force_correction": no_leg_max,
                "pass": no_leg_max < 1.0e-12,
            },
            "force_reciprocity": final_replay_force["force_audit"],
            "final_replay_force_reciprocity": final_replay_force["force_audit"],
            "rocket_energy": rocket_energy_diagnostic(config, final_chrono),
            "animation_deck_consistency": replay_consistency,
            "chrono_time_grid": chrono_time_grid,
            "loose_coupling_closure_diagnostic": {
                "meaning": "Difference between the reported feedback deck and the next Cummins correction implied by the final replay reactions. Diagnostic only; no strong-coupling convergence claim.",
                "relaxation": relaxation,
                "next_minus_reported_summary": closure_summary,
                "raw_target_minus_reported_summary": peak_summary_6dof(replay_raw_target_q - current_q, replay_raw_target_qd - current_qd),
                "tolerances": closure_gate["tolerances"],
                "checks": closure_gate["checks"],
                "pass": closure_gate["pass"],
            },
        },
    }


def run_time_step_convergence(
    case_id: str,
    base_config: dict[str, Any],
    wang: dict[str, Any],
    matrices: dict[str, Any],
    coupling_dt_s: float,
    relaxation: float,
    iterations: int,
    reference_series: dict[str, Any],
) -> dict[str, Any]:
    fine_config = json.loads(json.dumps(base_config))
    fine_config["solver"]["time_step_s"] = float(base_config["solver"]["time_step_s"]) * 0.5
    fine_config["solver"]["output_step_s"] = min(
        float(base_config["solver"]["output_step_s"]),
        float(coupling_dt_s) * 0.5,
    )
    fine_time_s = make_time_grid(
        float(fine_config["solver"]["start_s"]),
        float(fine_config["solver"]["end_s"]),
        coupling_dt_s * 0.5,
    )
    baseline_sim, q_base, qd_base = baseline_arrays_6dof(wang, case_id, fine_time_s)
    fine_q = q_base.copy()
    fine_qd = qd_base.copy()
    motion = deck_motion_from_wang_raw(wang, case_id)
    fine_force: dict[str, Any] | None = None
    for iteration in range(1, iterations + 1):
        fine_chrono = run_lock_chrono(fine_config, motion, f"{case_id} convergence iteration {iteration}/{iterations}")
        fine_force = generalized_leg_force_from_chrono_6dof(
            fine_chrono,
            fine_time_s,
            include_lock_reaction=True,
            footpad_radius_m=float(fine_config["legs"]["footpad_radius_m"]),
        )
        fine_correction = solve_cummins_leg_correction(matrices, fine_time_s, fine_force["values_6dof"], coupling_dt_s * 0.5)
        raw_q = q_base + fine_correction["q"]
        raw_qd = qd_base + fine_correction["qd"]
        fine_q = fine_q + relaxation * (raw_q - fine_q)
        fine_qd = fine_qd + relaxation * (raw_qd - fine_qd)
        motion = deck_motion_from_arrays_6dof(fine_time_s, fine_q, fine_qd, baseline_sim["offset"])
    assert fine_force is not None
    fine_feedback_motion = deck_motion_from_arrays_6dof(fine_time_s, fine_q, fine_qd, baseline_sim["offset"])
    fine_replay = run_lock_chrono(fine_config, fine_feedback_motion, f"{case_id} convergence feedback-deck replay")
    fine_series = values_to_named_series_6dof(fine_time_s, fine_q, fine_qd)
    common_grid_comparison = compare_time_step_series_6dof(reference_series, fine_series)
    return {
        "case_id": case_id,
        "half_chrono_time_step_s": fine_config["solver"]["time_step_s"],
        "half_cummins_time_step_s": coupling_dt_s * 0.5,
        "fine_output_step_s": fine_config["solver"]["output_step_s"],
        "coupling_relaxation": relaxation,
        "iterations": iterations,
        "chrono_summary": fine_replay["summary"],
        "leg_force_summary": fine_force["summary"],
        "platform_summary": peak_summary_6dof(fine_q, fine_qd),
        "common_grid_comparison": common_grid_comparison,
        "animation_deck_consistency": animation_deck_consistency(fine_replay, fine_time_s, fine_q),
    }


def lock_feedback_validation(simulations: dict[str, Any]) -> dict[str, Any]:
    cases = {}
    all_pass = True
    for case_id, sim in simulations.items():
        force_summary = sim["final_replay_force_summary"]
        lock = sim["final_iteration_chrono"]["summary"]["post_touchdown_lock"]
        force_audit = sim["final_replay_force_audit"]
        row = {
            "actual_lock_actuated_time_s": lock["actual_lock_actuated_time_s"],
            "lock_reaction_included": force_audit["lock_reaction_included"],
            "max_lock_vertical_platform_force_mn": force_summary["max_lock_vertical_platform_force_mn"],
            "max_lock_roll_platform_moment_mnm": force_summary["max_lock_roll_platform_moment_mnm"],
            "max_lock_pitch_platform_moment_mnm": force_summary["max_lock_pitch_platform_moment_mnm"],
            "max_lock_yaw_platform_moment_mnm": force_summary["max_lock_yaw_platform_moment_mnm"],
            "pass": bool(lock["actual_lock_actuated_time_s"] is not None and force_audit["lock_reaction_included"]),
        }
        cases[case_id] = row
        all_pass = all_pass and row["pass"]
    return {"cases": cases, "pass": all_pass if cases else False}


def six_dof_feedback_validation(simulations: dict[str, Any]) -> dict[str, Any]:
    cases = {}
    all_pass = True
    force_residual_keys = [
        "max_surge_action_reaction_residual_n",
        "max_sway_action_reaction_residual_n",
        "max_vertical_action_reaction_residual_n",
    ]
    moment_residual_keys = [
        "max_roll_moment_residual_nm",
        "max_pitch_moment_residual_nm",
        "max_yaw_moment_residual_nm",
    ]
    for case_id, sim in simulations.items():
        audit = sim["final_replay_force_audit"]
        response_keys = set(sim["with_leg_feedback"]["responses"])
        force_pass = all(float(audit.get(key, float("inf"))) < 1.0e-6 for key in force_residual_keys)
        moment_pass = all(float(audit.get(key, float("inf"))) < 1.0e-4 for key in moment_residual_keys)
        response_pass = set(["surge_m", "sway_m", "heave_m", "roll_rad", "pitch_rad", "yaw_rad"]).issubset(response_keys)
        row = {
            "horizontal_force_feedback_included": bool(audit.get("horizontal_force_feedback_included")),
            "max_horizontal_contact_force_fed_back_n": audit.get("max_horizontal_contact_force_fed_back_n"),
            "force_reciprocity_pass": force_pass,
            "moment_reciprocity_pass": moment_pass,
            "six_response_channels_present": response_pass,
        }
        row["pass"] = bool(row["horizontal_force_feedback_included"] and force_pass and moment_pass and response_pass)
        cases[case_id] = row
        all_pass = all_pass and row["pass"]
    return {
        "dof_order": ["surge", "sway", "heave", "roll", "pitch", "yaw"],
        "cases": cases,
        "pass": all_pass if cases else False,
    }


def animation_replay_validation(simulations: dict[str, Any]) -> dict[str, Any]:
    cases = {case_id: sim["validation"]["animation_deck_consistency"] for case_id, sim in simulations.items()}
    return {"cases": cases, "pass": bool(cases) and all(row.get("pass") is True for row in cases.values())}


def chrono_time_grid_validation(simulations: dict[str, Any]) -> dict[str, Any]:
    cases = {case_id: sim["validation"]["chrono_time_grid"] for case_id, sim in simulations.items()}
    return {"cases": cases, "pass": bool(cases) and all(row.get("pass") is True for row in cases.values())}


def loose_coupling_closure_validation(simulations: dict[str, Any]) -> dict[str, Any]:
    cases = {
        case_id: sim["validation"]["loose_coupling_closure_diagnostic"]
        for case_id, sim in simulations.items()
    }
    return {
        "cases": cases,
        "pass": bool(cases) and all(row.get("pass") is True for row in cases.values()),
        "claim_boundary": "Numerical fixed-point closure of the loose partitioned iteration only; not monolithic strong co-simulation.",
    }


def six_dof_time_step_convergence_validation(reference: dict[str, Any], fine: dict[str, Any] | None) -> dict[str, Any]:
    if fine is None:
        return {"enabled": False, "pass": None}
    coarse = reference["with_leg_feedback"]["summary"]
    fine_summary = fine["platform_summary"]
    metric_names = [
        "surge_peak_m",
        "sway_peak_m",
        "heave_peak_m",
        "roll_peak_deg",
        "pitch_peak_deg",
        "yaw_peak_deg",
    ]
    native_checks = []
    native_passed = True
    for name in metric_names:
        coarse_value = float(coarse[name])
        fine_value = float(fine_summary[name])
        relative = abs(fine_value - coarse_value) / max(abs(fine_value), abs(coarse_value), 1.0e-12)
        row_pass = relative <= 0.10
        native_checks.append(
            {
                "metric": name,
                "coarse": coarse_value,
                "fine": fine_value,
                "relative_difference": relative,
                "pass": row_pass,
            }
        )
        native_passed = native_passed and row_pass
    common_grid = fine.get("common_grid_comparison")
    checks = common_grid["checks"] if common_grid is not None else native_checks
    passed = bool(common_grid["pass"]) if common_grid is not None else native_passed
    replay_pass = fine.get("animation_deck_consistency", {}).get("pass") is True
    return {
        "enabled": True,
        "case_id": fine["case_id"],
        "tolerance": 0.10,
        "checks": checks,
        "native_peak_checks": native_checks,
        "native_peak_pass": native_passed,
        "comparison_grid": common_grid,
        "fine_animation_deck_consistency_pass": replay_pass,
        "pass": passed and replay_pass,
    }


def compact_case(case_result: dict[str, Any]) -> dict[str, Any]:
    compact = dict(case_result)
    compact["final_iteration_chrono"] = compact_simulation(case_result["final_iteration_chrono"])
    return compact


def write_report_js(report: dict[str, Any]) -> None:
    REPORT_JS.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JS.write_text(
        "window.CHRONO_STAGE3_LOCK_TWO_WAY_DATA = " + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {REPORT_JS}")


def build_report(
    cases: list[str],
    iterations: int,
    coupling_dt_s: float,
    run_convergence: bool,
    convergence_case: str,
    relaxation: float,
) -> dict[str, Any]:
    ensure_dirs()
    PROGRESS_LOG.write_text("", encoding="utf-8")
    config = tripod_actuated_lock_model_config()
    env = chrono_environment_report()
    if not env["available"]:
        write_json(CASE_ROOT / "validation" / "chrono-stage3-lock-two-way-env-check.json", env)
        raise ChronoUnavailableError(json.dumps(env, ensure_ascii=False, indent=2))
    log_progress("Loading Wang 2023 HAMS/Cummins baseline...")
    wang = load_wang_response()
    log_progress("Loading full 6x6 HAMS added-mass and radiation-damping matrices...")
    matrices = load_cummins_matrices_6dof(wang)
    simulations = {}
    for case_id in cases:
        log_progress(f"Building Stage 3 lock two-way loose-coupling case: {case_id}")
        simulations[case_id] = run_feedback_case(case_id, config, wang, matrices, iterations, coupling_dt_s, relaxation)
    convergence = None
    if run_convergence and convergence_case in simulations:
        log_progress(f"Running Stage 3 lock two-way time-step convergence check: {convergence_case}")
        convergence = run_time_step_convergence(
            convergence_case,
            config,
            wang,
            matrices,
            coupling_dt_s,
            relaxation,
            iterations,
            simulations[convergence_case]["with_leg_feedback"],
        )
    validation = build_stage3a_two_way_validation(simulations, convergence)
    validation["lock_feedback"] = lock_feedback_validation(simulations)
    validation["six_dof_leg_increment"] = six_dof_feedback_validation(simulations)
    validation["animation_feedback_deck_replay"] = animation_replay_validation(simulations)
    validation["chrono_time_grid"] = chrono_time_grid_validation(simulations)
    validation["loose_coupling_fixed_point"] = loose_coupling_closure_validation(simulations)
    validation["six_dof_time_step_convergence"] = six_dof_time_step_convergence_validation(
        simulations[convergence["case_id"]] if convergence and convergence.get("case_id") in simulations else {},
        convergence,
    )
    report = {
        "case_id": "Chrono_LeggedRecovery_Stage3_Lock_TwoWay",
        "title": "Stage 3 lock two-way loose coupling: full 6DOF HAMS/Cummins leg-reaction increment with Chrono contact and lock feedback",
        "status": "simulated",
        "environment": env,
        "coupling": {
            "mode": "stage3_lock_two_way_loose_6dof_leg_increment",
            "platform_source": "Wang 2023 heave/roll/pitch baseline plus local HAMS full 6x6 hydrodynamic matrices",
            "platform_solver": "Wang 2023 three-DOF baseline plus full 6DOF Cummins F_contact+F_lock incremental correction",
            "leg_solver": "Project Chrono / PyChrono ChronoTripodLegModel with actuated lock proxy",
            "fallback_to_handwritten_contact": False,
            "rhs": "F_wave + F_plume in heave/roll/pitch from Wang baseline; full [Fx,Fy,Fz,Mx,My,Mz] contact plus lock reactions from Chrono mapped into the 6DOF Cummins correction.",
            "hydrodynamic_increment_model": matrices["model_boundary"],
            "feedback_dofs": ["surge", "sway", "heave", "roll", "pitch", "yaw"],
            "baseline_dofs": ["heave", "roll", "pitch"],
            "animation_source": "final Chrono replay prescribed by the reported with_leg_feedback 6DOF deck history",
            "loose_coupling_relaxation": relaxation,
            "fixed_point_closure_status": "closed" if validation["loose_coupling_fixed_point"]["pass"] else "not_closed",
            "limitations": [
                "This is loose linear correction, not monolithic strong co-simulation.",
                "The final replay synchronizes animation and deck history, but its returned reactions are only reported as the next-pass closure diagnostic; fixed-point convergence is not claimed.",
                "Wang 2023 supplies only the heave/roll/pitch wave-plume baseline; surge/sway/yaw baseline values are zero, not paper-reproduced responses.",
                "No unpublished mooring or DP horizontal restoring data are synthesized; surge/sway/yaw increments are unmoored diagnostics driven by Chrono reactions and HAMS radiation.",
                "The lock is a ChLinkMateFix proxy, not a published clamp hardware model.",
            ],
        },
        "config": config,
        "leg_positions": leg_positions_from_config(config),
        "simulations": {case_id: compact_case(sim) for case_id, sim in simulations.items()},
        "validation": validation,
        "acceptance_scope": {
            "stage_3_lock_two_way_done": [
                "Chrono foot contact forces and post-touchdown lock constraint reactions are mapped to platform generalized loads.",
                "The 6DOF Cummins correction equation includes [Fx,Fy,Fz,Mx,My,Mz] from Chrono contact and lock reactions.",
                "Full HAMS 6x6 added-mass and radiation-damping matrices are used for the leg-induced incremental response.",
                "The animation Chrono state is replayed on the same reported with_leg_feedback 6DOF deck history.",
                "No fallback to integrated_recovery_model.contact_forces.",
            ],
            "not_claimed": [
                "strong monolithic Chrono/Cummins co-simulation",
                "fixed-point convergence of the loose-coupling reaction/deck iteration",
                "full six-DOF Wang wave/plume baseline",
                "validated mooring or dynamic-positioning response in surge/sway/yaw",
                "published clamp geometry or actuator dynamics",
                "validated hardware seafastening loads",
            ],
        },
    }
    write_json(CASE_ROOT / "chrono-stage3-lock-two-way-report-data.json", report)
    write_json(CASE_ROOT / "Output" / "RocketRecovery" / "chrono-stage3-lock-two-way-response.json", report)
    write_report_js(report)
    log_progress("Stage 3 lock two-way report artifacts completed.")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 3 lock Chrono to HAMS/Cummins two-way loose coupling.")
    parser.add_argument("command", choices=["check", "run", "report"], nargs="?", default="check")
    parser.add_argument("--case", action="append", choices=STAGE3_LOCK_TWO_WAY_CASES, help="Run/check one case. Can be repeated.")
    parser.add_argument("--iterations", type=int, default=1, help="Loose-coupling iterations per case.")
    parser.add_argument("--coupling-dt", type=float, default=0.01, help="Cummins correction and report grid time step.")
    parser.add_argument("--relaxation", type=float, default=1.0, help="Picard relaxation in (0,1]; use values below 1 only for explicit multi-iteration studies.")
    parser.add_argument("--skip-convergence", action="store_true", help="Skip the half-time-step convergence rerun.")
    parser.add_argument("--convergence-case", choices=STAGE3_LOCK_TWO_WAY_CASES, default="wave_port_15m")
    args = parser.parse_args()
    ensure_dirs()
    if args.command == "check":
        env = chrono_environment_report()
        write_json(CASE_ROOT / "validation" / "chrono-stage3-lock-two-way-env-check.json", env)
        print(f"Chrono available: {env['available']}")
        print(f"Report: {CASE_ROOT / 'validation' / 'chrono-stage3-lock-two-way-env-check.json'}")
        return
    try:
        if not 0.0 < args.relaxation <= 1.0:
            parser.error("--relaxation must be in (0, 1].")
        report = build_report(
            args.case or STAGE3_LOCK_TWO_WAY_CASES,
            max(1, args.iterations),
            args.coupling_dt,
            not args.skip_convergence,
            args.convergence_case,
            args.relaxation,
        )
    except ChronoUnavailableError as exc:
        print(exc)
        raise SystemExit(2)
    print(f"Status: {report['status']}")
    print(f"Report: {CASE_ROOT / 'chrono-stage3-lock-two-way-report-data.json'}")


if __name__ == "__main__":
    main()
