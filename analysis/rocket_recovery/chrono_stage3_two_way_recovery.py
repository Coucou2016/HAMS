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
    from .chrono_stage3_recovery import compact_simulation
    from .chrono_two_way_recovery import (
        baseline_arrays,
        compare_peak_change,
        convergence_validation,
        deck_motion_from_arrays,
        deck_motion_from_wang_raw,
        generalized_leg_force_from_chrono,
        leg_force_series_for_json,
        load_cummins_matrices,
        load_wang_response,
        make_time_grid,
        peak_summary,
        rocket_energy_diagnostic,
        solve_cummins_leg_correction,
        values_to_named_series,
    )
    from .common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json
except ImportError:
    from chrono_leg_model import (
        ChronoTripodLegModel,
        ChronoUnavailableError,
        chrono_environment_report,
        leg_positions_from_config,
        tripod_leg_model_config,
    )
    from chrono_stage3_recovery import compact_simulation
    from chrono_two_way_recovery import (
        baseline_arrays,
        compare_peak_change,
        convergence_validation,
        deck_motion_from_arrays,
        deck_motion_from_wang_raw,
        generalized_leg_force_from_chrono,
        leg_force_series_for_json,
        load_cummins_matrices,
        load_wang_response,
        make_time_grid,
        peak_summary,
        rocket_energy_diagnostic,
        solve_cummins_leg_correction,
        values_to_named_series,
    )
    from common import ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
REPORT_JS = VISUALIZATION_DIR / "chrono-stage3-two-way-data.js"
PROGRESS_LOG = CASE_ROOT / "validation" / "chrono-stage3-two-way-progress.log"
STAGE3_TWO_WAY_CASES = ["calm_center", "wave_center", "wave_bow_15m", "wave_port_15m"]


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


def run_tripod_chrono(config: dict[str, Any], motion: Any, label: str) -> dict[str, Any]:
    log_progress(f"Running Stage 3A tripod Chrono two-way source case: {label}")
    return ChronoTripodLegModel(config, motion).run()


def run_feedback_case(
    case_id: str,
    config: dict[str, Any],
    wang: dict[str, Any],
    matrices: dict[str, Any],
    iterations: int,
    coupling_dt_s: float,
) -> dict[str, Any]:
    start = float(config["solver"]["start_s"])
    end = float(config["solver"]["end_s"])
    time_s = make_time_grid(start, end, coupling_dt_s)
    baseline_sim, q_base, qd_base = baseline_arrays(wang, case_id, time_s)
    offset = baseline_sim["offset"]
    current_q = q_base.copy()
    current_qd = qd_base.copy()
    current_motion = deck_motion_from_wang_raw(wang, case_id)
    zero_force = np.zeros((len(time_s), 3), dtype=float)
    zero_correction = solve_cummins_leg_correction(matrices, time_s, zero_force, coupling_dt_s)
    iteration_rows: list[dict[str, Any]] = []
    final_chrono: dict[str, Any] | None = None
    final_force = zero_force

    for iteration in range(1, iterations + 1):
        chrono_sim = run_tripod_chrono(config, current_motion, f"{case_id} iteration {iteration}/{iterations}")
        force = generalized_leg_force_from_chrono(chrono_sim, time_s)
        correction = solve_cummins_leg_correction(matrices, time_s, force["values_3dof"], coupling_dt_s)
        current_q = q_base + correction["q"]
        current_qd = qd_base + correction["qd"]
        current_motion = deck_motion_from_arrays(time_s, current_q, current_qd, offset)
        final_chrono = chrono_sim
        final_force = force["values_3dof"]
        iteration_rows.append(
            {
                "iteration": iteration,
                "chrono_summary": chrono_sim["summary"],
                "leg_force_summary": force["summary"],
                "force_audit": force["force_audit"],
                "platform_delta_summary": peak_summary(correction["q"], correction["qd"]),
                "rocket_energy": rocket_energy_diagnostic(config, chrono_sim),
            }
        )

    assert final_chrono is not None
    no_leg_max = float(np.max(np.abs(zero_correction["q"])))
    baseline_summary = peak_summary(q_base, qd_base)
    feedback_summary = peak_summary(current_q, current_qd)
    delta_summary = peak_summary(current_q - q_base, current_qd - qd_base)
    return {
        "id": case_id,
        "environment": baseline_sim["environment"],
        "offset": offset,
        "with_wave": baseline_sim["with_wave"],
        "with_plume": baseline_sim["with_plume"],
        "iterations_requested": iterations,
        "coupling_dt_s": coupling_dt_s,
        "baseline": {**values_to_named_series(time_s, q_base, qd_base), "summary": baseline_summary},
        "with_leg_feedback": {**values_to_named_series(time_s, current_q, current_qd), "summary": feedback_summary},
        "leg_induced_delta": {**values_to_named_series(time_s, current_q - q_base, current_qd - qd_base), "summary": delta_summary},
        "leg_generalized_force": leg_force_series_for_json(time_s, final_force),
        "final_iteration_chrono": final_chrono,
        "iterations": iteration_rows,
        "validation": {
            "no_leg_degeneracy": {
                "max_abs_zero_force_correction": no_leg_max,
                "pass": no_leg_max < 1.0e-12,
            },
            "force_reciprocity": iteration_rows[-1]["force_audit"],
            "rocket_energy": iteration_rows[-1]["rocket_energy"],
        },
    }


def run_time_step_convergence(
    case_id: str,
    base_config: dict[str, Any],
    wang: dict[str, Any],
    matrices: dict[str, Any],
    coupling_dt_s: float,
) -> dict[str, Any]:
    fine_config = json.loads(json.dumps(base_config))
    fine_config["solver"]["time_step_s"] = float(base_config["solver"]["time_step_s"]) * 0.5
    fine_time_s = make_time_grid(
        float(fine_config["solver"]["start_s"]),
        float(fine_config["solver"]["end_s"]),
        coupling_dt_s * 0.5,
    )
    baseline_sim, q_base, qd_base = baseline_arrays(wang, case_id, fine_time_s)
    motion = deck_motion_from_wang_raw(wang, case_id)
    fine_chrono = run_tripod_chrono(fine_config, motion, f"{case_id} convergence half Chrono dt")
    fine_force = generalized_leg_force_from_chrono(fine_chrono, fine_time_s)
    fine_correction = solve_cummins_leg_correction(matrices, fine_time_s, fine_force["values_3dof"], coupling_dt_s * 0.5)
    fine_q = q_base + fine_correction["q"]
    fine_qd = qd_base + fine_correction["qd"]
    return {
        "case_id": case_id,
        "half_chrono_time_step_s": fine_config["solver"]["time_step_s"],
        "half_cummins_time_step_s": coupling_dt_s * 0.5,
        "chrono_summary": fine_chrono["summary"],
        "leg_force_summary": fine_force["summary"],
        "platform_summary": peak_summary(fine_q, fine_qd),
    }


def build_validation(simulations: dict[str, Any], convergence: dict[str, Any] | None) -> dict[str, Any]:
    force_checks = {}
    energy_checks = {}
    no_leg_checks = {}
    peak_changes = {}
    contact_checks = {}
    all_force_pass = True
    all_no_leg_pass = True
    all_contact_pass = True
    for case_id, sim in simulations.items():
        force = sim["validation"]["force_reciprocity"]
        force_pass = (
            force["max_vertical_action_reaction_residual_n"] < 1.0e-6
            and force["max_roll_moment_residual_nm"] < 1.0e-4
            and force["max_pitch_moment_residual_nm"] < 1.0e-4
        )
        no_leg_pass = bool(sim["validation"]["no_leg_degeneracy"]["pass"])
        contact_state = sim["final_iteration_chrono"]["summary"]["contact_state"]
        per_leg = contact_state["per_leg"]
        contact_pass = (
            bool(per_leg)
            and all(row["first_contact_time_s"] is not None for row in per_leg.values())
            and contact_state["all_legs_finally_in_contact"]
            and len(contact_state["all_contact_intervals_s"]) > 0
        )
        force_checks[case_id] = {**force, "pass": force_pass}
        energy_checks[case_id] = {**sim["validation"]["rocket_energy"], "pass": None, "status": "incomplete_energy_budget"}
        no_leg_checks[case_id] = sim["validation"]["no_leg_degeneracy"]
        contact_checks[case_id] = {
            "per_leg_first_contact_times_s": {leg_id: row["first_contact_time_s"] for leg_id, row in per_leg.items()},
            "touchdown_sequence": contact_state["touchdown_sequence"],
            "touchdown_span_s": contact_state["touchdown_span_s"],
            "liftoff_count_total": contact_state["liftoff_count_total"],
            "recontact_count_total": contact_state["recontact_count_total"],
            "final_contact_count": contact_state["final_contact_count"],
            "all_contact_interval_count": len(contact_state["all_contact_intervals_s"]),
            "pass": contact_pass,
        }
        peak_changes[case_id] = compare_peak_change(sim)
        all_force_pass = all_force_pass and force_pass
        all_no_leg_pass = all_no_leg_pass and no_leg_pass
        all_contact_pass = all_contact_pass and contact_pass

    bow_change = abs(peak_changes.get("wave_bow_15m", {}).get("leg_induced_pitch_peak_deg", 0.0))
    port_change = abs(peak_changes.get("wave_port_15m", {}).get("leg_induced_roll_peak_deg", 0.0))
    return {
        "rhs_composition": {
            "form": "q_total = q_Wang(F_wave + F_plume) + delta_q(F_leg_from_stage3a_tripod)",
            "equivalent_linear_equation": "(M + A_inf) qdd + C qd + K q + F_memory = F_wave + F_plume + F_leg",
            "no_leg_degeneracy_pass": all_no_leg_pass,
        },
        "force_reciprocity": {"cases": force_checks, "pass": all_force_pass},
        "energy_diagnostic": {"cases": energy_checks, "pass": None, "status": "incomplete_energy_budget"},
        "contact_state_machine": {"cases": contact_checks, "pass": all_contact_pass if contact_checks else False},
        "eccentric_response": {
            "wave_bow_15m_pitch_peak_delta_deg": bow_change,
            "wave_port_15m_roll_peak_delta_deg": port_change,
            "threshold_deg": 1.0e-3,
            "pass": bow_change > 1.0e-3 and port_change > 1.0e-3,
        },
        "time_step_convergence": convergence_validation(
            simulations[convergence["case_id"]] if convergence and convergence.get("case_id") in simulations else {},
            convergence,
        ),
        "peak_changes": peak_changes,
    }


def compact_case(case_result: dict[str, Any]) -> dict[str, Any]:
    compact = dict(case_result)
    compact["final_iteration_chrono"] = compact_simulation(case_result["final_iteration_chrono"])
    return compact


def write_report_js(report: dict[str, Any]) -> None:
    REPORT_JS.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JS.write_text(
        "window.CHRONO_STAGE3_TWO_WAY_DATA = " + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {REPORT_JS}")


def build_report(
    cases: list[str],
    iterations: int,
    coupling_dt_s: float,
    run_convergence: bool,
    convergence_case: str,
) -> dict[str, Any]:
    ensure_dirs()
    PROGRESS_LOG.write_text("", encoding="utf-8")
    config = tripod_leg_model_config()
    env = chrono_environment_report()
    if not env["available"]:
        write_json(CASE_ROOT / "validation" / "chrono-stage3-two-way-env-check.json", env)
        raise ChronoUnavailableError(json.dumps(env, ensure_ascii=False, indent=2))
    log_progress("Loading Wang 2023 HAMS/Cummins baseline...")
    wang = load_wang_response()
    log_progress("Loading HAMS radiation damping matrices...")
    matrices = load_cummins_matrices(wang)
    simulations = {}
    for case_id in cases:
        log_progress(f"Building Stage 3A tripod two-way loose-coupling case: {case_id}")
        simulations[case_id] = run_feedback_case(case_id, config, wang, matrices, iterations, coupling_dt_s)

    convergence = None
    if run_convergence and convergence_case in simulations:
        log_progress(f"Running Stage 3A tripod time-step convergence check: {convergence_case}")
        convergence = run_time_step_convergence(convergence_case, config, wang, matrices, coupling_dt_s)

    report = {
        "case_id": "Chrono_LeggedRecovery_Stage3A_TwoWay",
        "title": "Stage 3A tripod two-way loose coupling: HAMS/Cummins platform response with Chrono tripod leg feedback",
        "status": "simulated",
        "environment": env,
        "coupling": {
            "mode": "stage3a_tripod_two_way_loose_linear_correction",
            "platform_source": "Wang 2023 HAMS/Cummins baseline",
            "platform_solver": "HAMS/Cummins Wang 2023 surrogate plus Cummins F_leg correction",
            "leg_solver": "Project Chrono / PyChrono ChronoTripodLegModel",
            "fallback_to_handwritten_contact": False,
            "rhs": "F_wave + F_plume from Wang baseline; F_leg from Stage 3A tripod Chrono contact force mapped into Cummins correction.",
            "limitations": [
                "This is still loose linear correction, not a monolithic strong co-simulation.",
                "Only heave/roll/pitch platform DOFs are fed back.",
                "Stage 3A tripod uses elastic TSDA braces and a proxy nozzle reference, not CAD-exact joints.",
            ],
        },
        "config": config,
        "leg_positions": leg_positions_from_config(config),
        "simulations": {case_id: compact_case(sim) for case_id, sim in simulations.items()},
        "validation": build_validation(simulations, convergence),
        "acceptance_scope": {
            "stage_3a_two_way_done": [
                "Stage 3A tripod Chrono contact force is mapped to platform generalized loads.",
                "Cummins correction equation includes F_leg from the tripod proxy.",
                "Final Chrono iteration records per-leg first contact, liftoff, recontact, touchdown span, and stable-standing diagnostics.",
                "Four requested cases are generated when selected.",
                "No fallback to integrated_recovery_model.contact_forces.",
            ],
            "not_claimed": [
                "full six-DOF platform feedback",
                "strong monolithic Chrono/Cummins co-simulation",
                "CAD-exact tripod hinge coordinates",
                "validated hydropneumatic buffer force-stroke or force-velocity curve",
                "actuated mechanical lock",
            ],
        },
    }
    write_json(CASE_ROOT / "chrono-stage3-two-way-report-data.json", report)
    write_json(CASE_ROOT / "Output" / "RocketRecovery" / "chrono-stage3-two-way-response.json", report)
    write_report_js(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 3A tripod Chrono to HAMS/Cummins two-way loose coupling.")
    parser.add_argument("command", choices=["check", "run", "report"], nargs="?", default="check")
    parser.add_argument("--case", action="append", choices=STAGE3_TWO_WAY_CASES, help="Run/check one case. Can be repeated.")
    parser.add_argument("--iterations", type=int, default=1, help="Loose-coupling iterations per case.")
    parser.add_argument("--coupling-dt", type=float, default=0.01, help="Cummins correction and report grid time step.")
    parser.add_argument("--skip-convergence", action="store_true", help="Skip the half-time-step convergence rerun.")
    parser.add_argument("--convergence-case", choices=STAGE3_TWO_WAY_CASES, default="wave_port_15m")
    args = parser.parse_args()
    ensure_dirs()
    if args.command == "check":
        env = chrono_environment_report()
        write_json(CASE_ROOT / "validation" / "chrono-stage3-two-way-env-check.json", env)
        print(f"Chrono available: {env['available']}")
        print(f"Report: {CASE_ROOT / 'validation' / 'chrono-stage3-two-way-env-check.json'}")
        return
    try:
        report = build_report(
            cases=args.case or STAGE3_TWO_WAY_CASES,
            iterations=max(1, args.iterations),
            coupling_dt_s=args.coupling_dt,
            run_convergence=not args.skip_convergence,
            convergence_case=args.convergence_case,
        )
    except ChronoUnavailableError as exc:
        print(exc)
        raise SystemExit(2)
    print(f"Status: {report['status']}")
    print(f"Report: {CASE_ROOT / 'chrono-stage3-two-way-report-data.json'}")


if __name__ == "__main__":
    main()
