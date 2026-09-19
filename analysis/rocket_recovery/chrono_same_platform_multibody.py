from __future__ import annotations

import argparse
import copy
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
CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
WANG_CONFIG_PATH = ROCKET_CASES_DIR / "Paper_WangZhi_2023" / "platform_config.json"
REPORT_PATH = CASE_ROOT / "chrono-same-platform-multibody-report.json"
RESPONSE_PATH = CASE_ROOT / "Output" / "RocketRecovery" / "chrono-same-platform-multibody-response.json"


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
    if not apply_thies_digitized_buffer_law(config, required=True):
        raise RuntimeError("The digitized Thies absorber law was not applied")
    return config


def coupling_work_audit(sim: dict[str, Any], force6: dict[str, Any]) -> dict[str, Any]:
    time = np.asarray(sim["time_s"], dtype=float)
    platform_wrench = np.asarray(force6["samples_6dof"], dtype=float)
    rocket_wrench = -platform_wrench
    deck = sim["deck"]
    rocket = sim["rocket"]
    platform_velocity = np.column_stack(
        [
            np.asarray(deck["surge_m_s"], dtype=float),
            np.asarray(deck["sway_m_s"], dtype=float),
            np.asarray(deck["heave_m_s"], dtype=float),
            np.asarray(deck["roll_rad_s"], dtype=float),
            np.asarray(deck["pitch_rad_s"], dtype=float),
            np.asarray(deck["yaw_rad_s"], dtype=float),
        ]
    )
    rocket_velocity = np.column_stack(
        [
            np.gradient(np.asarray(rocket["cg_x_m"], dtype=float), time),
            np.gradient(np.asarray(rocket["cg_y_m"], dtype=float), time),
            np.asarray(rocket["vertical_velocity_m_s"], dtype=float),
            np.asarray(rocket["roll_rate_rad_s"], dtype=float),
            np.asarray(rocket["pitch_rate_rad_s"], dtype=float),
            np.asarray(rocket["yaw_rate_rad_s"], dtype=float),
        ]
    )
    platform_work = float(np.trapezoid(np.einsum("ni,ni->n", platform_wrench, platform_velocity), time))
    rocket_work = float(np.trapezoid(np.einsum("ni,ni->n", rocket_wrench, rocket_velocity), time))
    pair_work = platform_work + rocket_work
    return {
        "platform_contact_work_j": platform_work,
        "rocket_contact_work_j": rocket_work,
        "contact_pair_work_j": pair_work,
        "contact_pair_dissipation_proxy_j": max(0.0, -pair_work),
        "definition": "Generalized equal-and-opposite contact wrench dotted with recorded platform and rocket generalized velocities; unresolved contact elastic energy is not hidden.",
    }


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
        "per_leg_normal_impulse_ns": per_leg,
        "total_normal_impulse_ns": float(np.trapezoid(total_force, time)),
        "definition": "Time integral of the recorded non-negative footpad contact-force magnitudes; this is a convergence metric, not a net six-DOF impulse.",
    }


def rocket_energy_audit(sim: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    time = np.asarray(sim["time_s"], dtype=float)
    contact_count = np.sum(np.asarray(list(sim["contact"]["leg_contact"].values()), dtype=int), axis=0)
    contact_indices = np.flatnonzero(contact_count > 0)
    first = int(contact_indices[0]) if len(contact_indices) else 0
    mass = float(config["rocket"]["landing_mass_kg"])
    inertia = config["rocket"]["inertia_kg_m2"]
    vz = np.asarray(sim["rocket"]["vertical_velocity_m_s"], dtype=float)
    rates = np.column_stack(
        [
            np.asarray(sim["rocket"]["roll_rate_rad_s"], dtype=float),
            np.asarray(sim["rocket"]["pitch_rate_rad_s"], dtype=float),
            np.asarray(sim["rocket"]["yaw_rate_rad_s"], dtype=float),
        ]
    )
    inertia_values = np.asarray([inertia["roll_x"], inertia["pitch_y"], inertia["yaw_z"]], dtype=float)
    kinetic = 0.5 * mass * vz**2 + 0.5 * np.sum(inertia_values[None, :] * rates**2, axis=1)
    z = np.asarray(sim["rocket"]["cg_z_m"], dtype=float)
    gravity_work = mass * float(config["solver"]["gravity_m_s2"]) * float(z[first] - z[-1])
    return {
        "first_contact_sample_time_s": float(time[first]),
        "kinetic_energy_at_first_contact_j": float(kinetic[first]),
        "final_kinetic_energy_j": float(kinetic[-1]),
        "kinetic_energy_change_j": float(kinetic[-1] - kinetic[first]),
        "gravity_work_after_first_contact_j": gravity_work,
        "nominal_precontact_translational_energy_j": 0.5
        * mass
        * float(config["rocket"]["touchdown_vertical_velocity_m_s"]) ** 2,
        "scope": "Translational vertical plus published rotational inertias; horizontal kinetic energy is omitted and reported through this scope statement.",
    }


def run_passes(
    pass_count: int,
    contact_dt_s: float,
    retain_response: bool,
    end_s: float = 526.0,
    contact_stiffness_n_m: float | None = None,
) -> dict[str, Any]:
    study = default_study_config()
    study["time_domain"]["end_s"] = float(end_s)
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
    offset = {"x": 0.0, "y": 15.0}
    rows: list[dict[str, Any]] = []
    final_sim: dict[str, Any] | None = None
    final_force6: dict[str, Any] | None = None
    for pass_index in range(1, pass_count + 1):
        motion = deck_motion_from_arrays(platform_time, current["q_active"], current["qd_active"], offset)
        sim = ChronoTripodLegModel(config, motion).run()
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
    if final_sim is None or final_force6 is None:
        raise RuntimeError("No coupling pass was executed")
    result: dict[str, Any] = {
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
    iterative = run_passes(4, 0.0005, retain_response=True, end_s=526.0)
    algorithm_rows = {
        "prescribed_deck": iterative["passes"][0]["contact_summary"],
        "one_pass_platform_update": iterative["passes"][0],
        "two_pass_platform_update": iterative["passes"][1],
        "four_pass_platform_update": iterative["passes"][3],
    }
    convergence_runs: dict[str, dict[str, Any]] = {}
    regularization_runs: dict[str, dict[str, Any]] = {}
    if not skip_convergence:
        convergence_runs["dt"] = run_passes(2, 0.0005, retain_response=False, end_s=516.0)
        convergence_runs["dt_over_2"] = run_passes(2, 0.00025, retain_response=False, end_s=516.0)
        convergence_runs["dt_over_4"] = run_passes(2, 0.000125, retain_response=False, end_s=516.0)
        for stiffness_mn_m in (100.0, 250.0, 500.0):
            regularization_runs[f"kn_{stiffness_mn_m:g}_MN_m"] = run_passes(
                1,
                0.000125,
                retain_response=False,
                end_s=516.0,
                contact_stiffness_n_m=stiffness_mn_m * 1.0e6,
            )
    report = {
        "case_id": "Barge120x50_ThiesProxy_ChronoExplicitContact",
        "status": "computed_multibody_partitioned_case_study_not_full_scale_validation",
        "same_platform_chain": "120x50x7 HAMS operator + deterministic JONSWAP wave force + Wang plume-force profile truncated at touchdown + four-leg multibody contact",
        "algorithms": algorithm_rows,
        "iterative_run": {key: value for key, value in iterative.items() if key != "response"},
        "coupling_iteration_convergence": coupling_iteration_summary(iterative["passes"]),
        "time_step_convergence": convergence_summary(convergence_runs) if convergence_runs else {"enabled": False},
        "contact_regularization_sensitivity": (
            contact_regularization_summary(regularization_runs) if regularization_runs else {"enabled": False}
        ),
        "validation_hierarchy": {
            "level_1_code_verification": ["action-reaction wrench residual", "mass closure", "contact coefficient-mode audit", "time-step refinement"],
            "level_2_submodel_validation": ["HAMS benchmark", "digitized Thies absorber law", "Yang reduced-model comparison"],
            "level_3_literature_trend_cross_check": ["eccentric touchdown excites roll/pitch", "Wang plume force used only as labelled forcing profile"],
            "level_4_full_coupled_validation": "not available; no public full-scale sea-touchdown experiment exists for this configuration",
        },
        "limitations": [
            "Only heave, roll and pitch are returned to the platform because no mooring/DP horizontal restoring matrix is available.",
            "The four-leg geometry and digitized absorber curves are literature-based proxies, not vehicle CAD or qualification data.",
            "The 120x50 barge uses generated homogeneous mass/inertia properties, not as-built inclining-test data.",
            "Coupling is partitioned replay; four passes diagnose fixed-point sensitivity but do not constitute a monolithic solve.",
            "The production response is continued to 526 s to assess post-touchdown settling; time-step refinement uses the shorter 516 s impact window because its acceptance metrics are impact-local.",
        ],
        "output_response": str(RESPONSE_PATH.relative_to(ROOT).as_posix()),
    }
    write_json(REPORT_PATH, report)
    write_json(RESPONSE_PATH, iterative["response"])
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the actual four-leg multibody model on the same 120x50 HAMS platform operator.")
    parser.add_argument("--skip-convergence", action="store_true")
    args = parser.parse_args()
    report = build_report(skip_convergence=args.skip_convergence)
    print(f"Report: {REPORT_PATH}")
    print(f"Response: {RESPONSE_PATH}")
    print(f"Time-step convergence: {report['time_step_convergence'].get('pass')}")


if __name__ == "__main__":
    main()
