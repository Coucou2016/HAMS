from __future__ import annotations

try:
    from .review_integrity import thies_total_inertia_z_up, allocate_central_body, retain_full_history
except ImportError:
    from review_integrity import thies_total_inertia_z_up, allocate_central_body, retain_full_history


import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .chrono_leg_model import (
        ChronoTripodLegModel,
        apply_thies_digitized_buffer_law,
        explicit_smc_contact_audit,
        multibody_mass_audit,
        tripod_leg_model_config,
    )
    from .chrono_revision_study import (
        ACTIVE_DOF_INDICES,
        build_wave_components,
        default_study_config,
        load_platform_operator,
        make_time_grid,
        solve_platform,
        trajectory_difference,
    )
    from .chrono_stage3_recovery import compact_simulation
    from .chrono_two_way_recovery import deck_motion_from_arrays, generalized_leg_force_from_chrono_6dof
    from .common import ROCKET_CASES_DIR, read_json, write_json
except ImportError:
    from chrono_leg_model import ChronoTripodLegModel, apply_thies_digitized_buffer_law, explicit_smc_contact_audit, multibody_mass_audit, tripod_leg_model_config
    from chrono_revision_study import ACTIVE_DOF_INDICES, build_wave_components, default_study_config, load_platform_operator, make_time_grid, solve_platform, trajectory_difference
    from chrono_stage3_recovery import compact_simulation
    from chrono_two_way_recovery import deck_motion_from_arrays, generalized_leg_force_from_chrono_6dof
    from common import ROCKET_CASES_DIR, read_json, write_json


ROOT = Path(__file__).resolve().parents[2]
CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery_Review20260926"
WANG_CONFIG_PATH = ROCKET_CASES_DIR / "Paper_WangZhi_2023" / "platform_config.json"
REPORT_PATH = CASE_ROOT / "chrono-same-platform-multibody-report.json"
RESPONSE_PATH = CASE_ROOT / "Output" / "RocketRecovery" / "chrono-same-platform-multibody-response.json"
RESUME = False


def landing_config(
    contact_dt_s: float,
    output_dt_s: float | None = None,
    end_s: float = 526.0,
    contact_stiffness_n_m: float | None = None,
) -> dict[str, Any]:
    config = tripod_leg_model_config()
    config["solver"]["start_s"] = 506.0
    config["solver"]["end_s"] = float(end_s)
    config["solver"]["time_step_s"] = float(contact_dt_s)
    config["solver"]["output_step_s"] = float(output_dt_s if output_dt_s is not None else contact_dt_s)
    if contact_stiffness_n_m is not None:
        config["contact"]["normal_stiffness_n_m"] = float(contact_stiffness_n_m)
    platform = read_json(ROCKET_CASES_DIR / "Barge_120x50" / "platform_config.json")["platform"]
    config["solver"]["deck_geometry_m"] = {"length": platform["length_m"], "beam": platform["beam_m"], "height": platform["deck_z_m"]}
    M = float(config["rocket"]["landing_mass_kg"])
    target_cg = np.array([0.0, 0.0, config["rocket"]["cog_from_base_m"]])
    radius = float(config["legs"]["footpad_radius_m"])
    foot_mass = float(config["legs"]["footpad_mass_kg"])
    az = np.radians(config["legs"]["azimuths_deg"])
    r = float(config["legs"]["footprint_radius_m"])
    foot_cg = np.column_stack([r*np.cos(az), r*np.sin(az), np.full(len(az), radius)])
    child_I = np.array([np.eye(3)*0.4*foot_mass*radius**2 for _ in az])
    core_mass, core_cg, core_I = allocate_central_body(M, target_cg, thies_total_inertia_z_up(),
                                                   np.full(len(az), foot_mass), foot_cg, child_I)
    if np.max(np.abs(core_I-np.diag(np.diag(core_I)))) > 1e-6:
        raise ValueError("Current symmetric proxy requires diagonal central inertia")
    config["rocket"]["cog_from_base_m"] = float(core_cg[2])
    config["rocket"]["inertia_kg_m2"] = dict(zip(("roll_x","pitch_y","yaw_z"), np.diag(core_I).tolist()))
    config["rocket"]["review_reference_allocation"] = {
        "total_cg_m":target_cg.tolist(), "total_inertia_z_up":thies_total_inertia_z_up().tolist(),
        "central_mass_kg":core_mass, "central_cg_m":core_cg.tolist(), "central_inertia":core_I.tolist(),
        "scope":"reference configuration closure of the assumed four-sphere-foot proxy, not recovered CAD"}
    if not apply_thies_digitized_buffer_law(config, required=True):
        raise RuntimeError("The digitized Thies absorber law was not applied")
    return config


def coupling_work_audit(sim: dict[str, Any], force6: dict[str, Any]) -> dict[str, Any]:
    # A net wrench about the platform origin cannot be dotted with rocket-CG
    # velocity. Contact forces act on articulated foot bodies, not one rigid core.
    return {"available": False, "reason": "Independent contact-pair work requires actual contact-point forces, torques and velocities on both sides; the former origin/CG mixed proxy has been disabled.", "contact_pair_work_j": None, "contact_pair_dissipation_proxy_j": None}


def absorber_work_audit(sim: dict[str, Any]) -> dict[str, Any]:
    per_leg: dict[str, Any] = {}
    total_positive = 0.0
    total_net = 0.0
    for leg_id, force_values in sim["forces"]["leg_tsda_force_n"].items():
        force = np.asarray(force_values, dtype=float)
        stroke = np.asarray(sim["contact"]["leg_stroke_m"][leg_id], dtype=float)
        increments = 0.5 * (force[1:] + force[:-1]) * np.diff(stroke)
        positive = float(np.sum(np.maximum(increments, 0.0)))
        net = float(np.sum(increments))
        total_positive += positive
        total_net += net
        per_leg[leg_id] = {"positive_compression_work_j": positive, "net_force_stroke_work_j": net}
    return {
        "per_leg": per_leg,
        "positive_compression_work_j": total_positive,
        "net_force_stroke_work_j": total_net,
        "definition": "Trapezoidal integral of the recorded TSDA force with respect to recorded compression stroke; it includes recoverable and dissipative terms and is not relabelled as pure damping loss.",
    }


def contact_impulse_audit(sim: dict[str, Any]) -> dict[str, Any]:
    time = np.asarray(sim["time_s"], dtype=float)
    per_leg: dict[str, float] = {}
    total_force = np.zeros_like(time)
    for leg_id, values in sim["forces"]["leg_contact_force_n"].items():
        force = np.asarray(values, dtype=float)
        impulse = float(np.trapezoid(force, time))
        per_leg[leg_id] = impulse
        total_force += force
    return {
        "projected_normal_impulse_ns": float(sum(np.trapezoid(np.asarray(v),time) for v in sim["forces"].get("leg_contact_normal_force_n", {}).values())) if "leg_contact_normal_force_n" in sim["forces"] else None,
        "per_leg_normal_impulse_ns": per_leg,
        "total_normal_impulse_ns": float(np.trapezoid(total_force, time)),
        "definition": "Legacy key retained for compatibility: time integral of max(world Fz,0), NOT deck-normal impulse; see projected_normal_impulse_ns for the new quantity.",
    }


def rocket_energy_audit(sim: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    return {"available": False, "reason": "Previous proxy mixed total vehicle mass with central-body velocity/inertia and omitted articulated-foot kinetic energy. No closed whole-vehicle energy claim is made."}


def run_passes(
    pass_count: int,
    contact_dt_s: float,
    retain_response: bool,
    end_s: float = 526.0,
    contact_stiffness_n_m: float | None = None,
    adaptive: bool = False,
) -> dict[str, Any]:
    study = default_study_config()
    study["time_domain"]["end_s"] = float(end_s)
    study["platform"]["deck_reference_z_m"] = 3.0
    study["plume"]["vehicle_platform_consistency"] = "pre_touchdown_only"
    study["plume"]["cutoff_time_s"] = float(study["time_domain"]["touchdown_reference_s"])
    operator = load_platform_operator(study)
    wang_config = read_json(WANG_CONFIG_PATH)
    wave = build_wave_components(operator, study)
    platform_time = make_time_grid(
        float(study["time_domain"]["start_s"]),
        float(study["time_domain"]["end_s"]),
        float(study["time_domain"]["platform_dt_s"]),
    )
    baseline = solve_platform(operator, study, wang_config, wave, platform_time, np.zeros((len(platform_time), 3)))
    current = baseline
    config = landing_config(contact_dt_s, end_s=end_s, contact_stiffness_n_m=contact_stiffness_n_m)
    run_directory = CASE_ROOT / 'raw' / f"end{end_s:g}_dt{contact_dt_s:g}_kn{config['contact']['normal_stiffness_n_m']:g}"
    config_path = run_directory / 'run-config.json'
    if config_path.exists():
        if read_json(config_path) != config:
            raise ValueError(f'Checkpoint configuration differs: {config_path}')
    else:
        if run_directory.exists() and list(run_directory.glob('pass*.json')):
            raise ValueError('Cannot resume histories without their recorded configuration')
        write_json(config_path, config)
    offset = {"x": 0.0, "y": 15.0}
    rows: list[dict[str, Any]] = []
    final_sim: dict[str, Any] | None = None
    final_force6: dict[str, Any] | None = None
    for pass_index in range(1, pass_count + 1):
        print(f"Running end={end_s:g}, dt={contact_dt_s:g}, pass={pass_index}", flush=True)
        motion = deck_motion_from_arrays(platform_time, current["q_active"], current["qd_active"], offset)
        motion.reference_height_m = float(config["solver"]["deck_geometry_m"]["height"])
        raw_path = CASE_ROOT / "raw" / f"end{end_s:g}_dt{contact_dt_s:g}_kn{config['contact']['normal_stiffness_n_m']:g}" / f"pass{pass_index:02d}.json"
        if raw_path.exists() and RESUME:
            previous = read_json(raw_path.with_suffix('.audit.json'))
            raw = previous['raw_history']
            if hashlib.sha256(raw_path.read_bytes()).hexdigest() != raw['sha256']:
                raise ValueError(f'Checkpoint hash mismatch: {raw_path}')
            sim = read_json(raw_path)
            expected = round((end_s - config['solver']['start_s']) / contact_dt_s) + 1
            if len(sim['time_s']) != expected:
                raise ValueError('Checkpoint does not contain every contact-grid node')
            # Reconstruct the applied trajectory before accepting an old pass.
            samples = [motion.sample(t) for t in sim['time_s']]
            for key in ('heave_m', 'roll_rad', 'pitch_rad', 'heave_m_s', 'roll_rad_s', 'pitch_rad_s'):
                if not np.allclose(sim['deck'][key], [s[key] for s in samples], rtol=1e-12, atol=1e-12):
                    raise ValueError(f'Checkpoint deck trajectory differs: {key}')
            print(f'Verified and replayed checkpoint pass {pass_index}', flush=True)
        else:
            sim = ChronoTripodLegModel(config, motion).run()
            raw = retain_full_history(raw_path, sim)
        force6 = generalized_leg_force_from_chrono_6dof(
            sim,
            platform_time,
            footpad_radius_m=float(config["legs"]["footpad_radius_m"]),
        )
        feedback = np.asarray(force6["values_6dof"], dtype=float)[:, ACTIVE_DOF_INDICES]
        updated = solve_platform(operator, study, wang_config, wave, platform_time, feedback)
        rows.append(
            {
                "pass": pass_index,
                "raw_history": raw,
                "trajectory_change": trajectory_difference(current, updated),
                "contact_summary": sim["summary"],
                "wrench_summary": force6["summary"],
                "wrench_action_reaction": force6["force_audit"],
                "coupling_work": coupling_work_audit(sim, force6),
                "absorber_work": absorber_work_audit(sim),
                "contact_impulse": contact_impulse_audit(sim),
                "rocket_energy": rocket_energy_audit(sim, config),
                "platform_summary": updated["summary"],
                "platform_energy": updated["energy"],
            }
        )
        current = updated
        final_sim = sim
        final_force6 = force6
        write_json(raw_path.with_suffix('.audit.json'), rows[-1])
        print(f"Completed pass {pass_index}: peak Fz={sim['summary']['max_leg_contact_force_kn']:.6g} kN", flush=True)
        if adaptive and pass_index >= 2 and coupling_iteration_summary(rows)["comparisons"][-1]["pass_2_percent"]:
            break
    if final_sim is None or final_force6 is None:
        raise RuntimeError("No coupling pass was executed")
    result: dict[str, Any] = {
        "qualification_status": "computed_corrected_proxy_requires_numerical_and_physical_qualification",
        "run_config": config,
        "contact_dt_s": contact_dt_s,
        "platform_dt_s": float(study["time_domain"]["platform_dt_s"]),
        "passes": rows,
        "baseline_platform_summary": baseline["summary"],
        "final_platform_summary": current["summary"],
        "final_contact_summary": final_sim["summary"],
        "contact_model": explicit_smc_contact_audit(config),
        "mass_model": multibody_mass_audit(config),
        "plume_policy": study["plume"],
        "deck_interpolation": {
            "method": "piecewise cubic Hermite interpolation",
            "state_consistency": "position and supplied velocity are interpolated as one Hermite state pair",
            "platform_sample_step_s": float(study["time_domain"]["platform_dt_s"]),
            "contact_step_s": float(contact_dt_s),
        },
        "operator": operator.audit(),
        "ignored_platform_feedback": {
            "dofs": ["surge", "sway", "yaw"],
            "reason": "No mooring/DP horizontal restoring data are available for the generated barge; their contact-wrench components are calculated and audited but not injected.",
            "peak_wrench": {
                key: value
                for key, value in final_force6["summary"].items()
                if key in {"max_surge_platform_force_mn", "max_sway_platform_force_mn", "max_yaw_moment_mnm"}
            },
        },
    }
    if retain_response:
        compact = compact_simulation(final_sim, max_points=4000)
        compact["contact_model"] = final_sim.get("contact_model")
        compact["mass_model"] = final_sim.get("mass_model")
        result["response"] = {
            "platform_time_s": platform_time.tolist(),
            "baseline_q_active": np.asarray(baseline["q_active"]).tolist(),
            "final_q_active": np.asarray(current["q_active"]).tolist(),
            "final_qd_active": np.asarray(current["qd_active"]).tolist(),
            "multibody": compact,
            "platform_wrench_6dof": np.asarray(final_force6["values_6dof"]).tolist(),
        }
    write_json(raw_path.parent / 'run-result.json', result)
    return result


def convergence_summary(runs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    metrics = {
        "max_leg_contact_force_kn": lambda row: float(row["final_contact_summary"]["max_leg_contact_force_kn"]),
        "max_leg_stroke_m": lambda row: float(row["final_contact_summary"]["max_leg_stroke_m"]),
        "max_contact_penetration_m": lambda row: float(row["final_contact_summary"]["max_contact_penetration_m"]),
        "platform_roll_peak_deg": lambda row: float(row["final_platform_summary"]["roll_peak_deg"]),
        "touchdown_span_s": lambda row: float(row["final_contact_summary"]["contact_state"]["touchdown_span_s"]),
        "total_normal_impulse_ns": lambda row: float(row["passes"][-1]["contact_impulse"]["total_normal_impulse_ns"]),
    }
    values = {name: {metric: getter(row) for metric, getter in metrics.items()} for name, row in runs.items()}
    pairs = []
    for coarse, fine in (("dt", "dt_over_2"), ("dt_over_2", "dt_over_4")):
        checks = {}
        for metric in metrics:
            a = values[coarse][metric]
            b = values[fine][metric]
            checks[metric] = abs(a - b) / max(abs(b), 1.0e-12)
        pairs.append({"coarse": coarse, "fine": fine, "relative_changes": checks, "pass_5_percent": all(v <= 0.05 for v in checks.values())})
    return {
        "values": values,
        "pairwise": pairs,
        "criterion": "successive refinements must change peak force, stroke, penetration, touchdown span, contact impulse and platform roll by no more than 5%",
        "pass": all(row["pass_5_percent"] for row in pairs),
    }


def coupling_iteration_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    comparisons: list[dict[str, Any]] = []
    for previous, current in zip(rows[:-1], rows[1:]):
        previous_summary = previous["contact_summary"]
        current_summary = current["contact_summary"]
        metrics = {
            "peak_contact_force": (
                float(previous_summary["max_leg_contact_force_kn"]),
                float(current_summary["max_leg_contact_force_kn"]),
            ),
            "peak_buffer_stroke": (
                float(previous_summary["max_leg_stroke_m"]),
                float(current_summary["max_leg_stroke_m"]),
            ),
            "touchdown_span": (
                float(previous_summary["contact_state"]["touchdown_span_s"]),
                float(current_summary["contact_state"]["touchdown_span_s"]),
            ),
            "normal_contact_impulse": (
                float(previous["contact_impulse"]["total_normal_impulse_ns"]),
                float(current["contact_impulse"]["total_normal_impulse_ns"]),
            ),
        }
        relative_changes = {
            name: abs(after - before) / max(abs(after), 1.0e-12)
            for name, (before, after) in metrics.items()
        }
        comparisons.append(
            {
                "from_pass": int(previous["pass"]),
                "to_pass": int(current["pass"]),
                "relative_changes": relative_changes,
                "platform_fixed_point_metric": float(current["trajectory_change"]["fixed_point_metric"]),
                "pass_2_percent": bool(
                    max(relative_changes.values()) <= 0.02
                    and float(current["trajectory_change"]["fixed_point_metric"]) <= 0.02
                ),
            }
        )
    return {
        "criterion": "last interface update changes platform trajectory and peak force/stroke/touchdown-span/contact-impulse metrics by at most 2%",
        "comparisons": comparisons,
        "pass": bool(comparisons and comparisons[-1]["pass_2_percent"]),
    }


def contact_regularization_summary(runs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for label, run in runs.items():
        summary = run["final_contact_summary"]
        rows.append(
            {
                "label": label,
                "normal_stiffness_n_m": float(run["contact_model"]["normal_stiffness_kn_n_m"]),
                "contact_dt_s": float(run["contact_dt_s"]),
                "peak_contact_force_kn": float(summary["max_leg_contact_force_kn"]),
                "maximum_penetration_m": float(summary["max_contact_penetration_m"]),
                "maximum_buffer_stroke_m": float(summary["max_leg_stroke_m"]),
                "total_normal_impulse_ns": float(run["passes"][-1]["contact_impulse"]["total_normal_impulse_ns"]),
            }
        )
    rows.sort(key=lambda row: row["normal_stiffness_n_m"])
    reference = rows[-1]
    for row in rows:
        for metric in ("peak_contact_force_kn", "maximum_buffer_stroke_m", "total_normal_impulse_ns"):
            row[f"{metric}_relative_to_stiffest"] = abs(float(row[metric]) - float(reference[metric])) / max(
                abs(float(reference[metric])), 1.0e-12
            )
    return {
        "rows": rows,
        "interpretation": "Penalty stiffness is a numerical regularization sensitivity because no measured footpad-deck contact law is public; convergence of impulse/stroke is more meaningful than convergence of penalty penetration itself.",
        "load_prediction_qualified": False,
    }


def build_report(skip_convergence: bool = False) -> dict[str, Any]:
    iterative = run_passes(8, 0.0005, retain_response=True, end_s=526.0, adaptive=True)
    algorithm_rows = {
        "prescribed_deck": iterative["passes"][0]["contact_summary"],
        "one_pass_platform_update": iterative["passes"][0],
        "two_pass_platform_update": iterative["passes"][1],
        "last_platform_update": iterative["passes"][-1],
    }
    convergence_runs: dict[str, dict[str, Any]] = {}
    regularization_runs: dict[str, dict[str, Any]] = {}
    if not skip_convergence:
        convergence_runs["dt"] = run_passes(8, 0.0005, retain_response=False, end_s=516.0, adaptive=True)
        convergence_runs["dt_over_2"] = run_passes(8, 0.00025, retain_response=False, end_s=516.0, adaptive=True)
        convergence_runs["dt_over_4"] = run_passes(8, 0.000125, retain_response=False, end_s=516.0, adaptive=True)
        for stiffness_mn_m in (100.0, 250.0, 500.0):
            if stiffness_mn_m == 100.0:
                regularization_runs["kn_100_MN_m"] = convergence_runs["dt_over_4"]
                continue
            regularization_runs[f"kn_{stiffness_mn_m:g}_MN_m"] = run_passes(
                8,
                0.000125,
                retain_response=False,
                end_s=516.0,
                contact_stiffness_n_m=stiffness_mn_m * 1.0e6,
                adaptive=True,
            )
    report = {
        "case_id": "Barge120x50_ThiesProxy_ChronoExplicitContact",
        "status": "corrected_coupled_computation_completed_not_load_qualified",
        "correction_scope": "inertia frame/reference allocation, deck datum/pose, conservative transfer, raw retention, matched interface tolerance",
        "all_interface_runs_closed": all(coupling_iteration_summary(x["passes"])["pass"] for x in [iterative,*convergence_runs.values(),*regularization_runs.values()]),
        "same_platform_chain": "120x50x7 HAMS operator + deterministic JONSWAP wave force + Wang plume-force profile truncated at touchdown + four-leg multibody contact",
        "algorithms": algorithm_rows,
        "iterative_run": {key: value for key, value in iterative.items() if key != "response"},
        "coupling_iteration_convergence": coupling_iteration_summary(iterative["passes"]),
        "time_step_convergence": convergence_summary(convergence_runs) if convergence_runs else {"enabled": False},
        "contact_regularization_sensitivity": (
            contact_regularization_summary(regularization_runs) if regularization_runs else {"enabled": False}
        ),
        "validation_hierarchy": {
            "level_1_code_verification": ["algebraic wrench assembly identity, not independent reaction verification", "reference-configuration mass closure", "contact coefficient-mode audit", "time-step refinement including failures"],
            "level_2_submodel_validation": ["limited Yang reduced-model comparison only; HAMS benchmark unresolved and digitized Thies law is an input, not validation"],
            "level_3_literature_trend_cross_check": ["eccentric touchdown excites roll/pitch", "Wang plume force used only as labelled forcing profile"],
            "level_4_full_coupled_validation": "not available in the supplied evidence; no matched full-scale sea-touchdown experiment has been verified for this configuration",
        },
        "limitations": [
            "Only heave, roll and pitch are returned to the platform because no mooring/DP horizontal restoring matrix is available.",
            "The four-leg geometry and digitized absorber curves are literature-based proxies, not vehicle CAD or qualification data.",
            "The 120x50 barge uses generated homogeneous mass/inertia properties, not as-built inclining-test data.",
            "Coupling is partitioned replay with adaptive fixed-point stopping; it is not a monolithic solve and remains unqualified if closure or refinement gates fail.",
            "The production response is continued to 526 s to assess post-touchdown settling; time-step refinement uses the shorter 516 s impact window because its acceptance metrics are impact-local.",
        ],
        "output_response": str(RESPONSE_PATH.relative_to(ROOT).as_posix()),
    }
    write_json(REPORT_PATH, report)
    write_json(RESPONSE_PATH, iterative["response"])
    return report


def main() -> None:
    global CASE_ROOT, REPORT_PATH, RESPONSE_PATH, RESUME
    parser = argparse.ArgumentParser(description="Run the actual four-leg multibody model on the same 120x50 HAMS platform operator.")
    parser.add_argument("--skip-convergence", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=CASE_ROOT)
    parser.add_argument("--resume", action="store_true", help="Verify retained histories and rebuild their platform feedback before continuing")
    args = parser.parse_args()
    CASE_ROOT = args.output_dir.resolve()
    REPORT_PATH = CASE_ROOT / 'chrono-same-platform-multibody-report.json'
    RESPONSE_PATH = CASE_ROOT / 'Output' / 'RocketRecovery' / 'chrono-same-platform-multibody-response.json'
    RESUME = args.resume
    report = build_report(skip_convergence=args.skip_convergence)
    print(f"Report: {REPORT_PATH}")
    print(f"Response: {RESPONSE_PATH}")
    print(f"Time-step convergence: {report['time_step_convergence'].get('pass')}")


if __name__ == "__main__":
    main()
