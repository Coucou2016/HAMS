from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
except ImportError:
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
AUDIT_JSON = CASE_ROOT / "final-acceptance-audit.json"
AUDIT_MD = ROOT / "docs" / "chrono-final-acceptance-audit.md"
AUDIT_JS = VISUALIZATION_DIR / "chrono-final-acceptance-data.js"

REPORT_PATHS = {
    "hams_benchmark": ROCKET_CASES_DIR / "Barge_120x50" / "validation" / "benchmark-regression.json",
    "nargolkar_2025": ROCKET_CASES_DIR / "Paper_Nargolkar_2025" / "nargolkar-2025-report-data.json",
    "wang_2023": ROCKET_CASES_DIR / "Paper_WangZhi_2023" / "wang-2023-report-data.json",
    "literature_registry": ROCKET_CASES_DIR / "Chrono_LeggedRecovery" / "literature-comparison-registry.json",
    "thies_buffer_curves": ROCKET_CASES_DIR / "Chrono_LeggedRecovery" / "validation" / "thies_absorber_curves" / "thies-buffer-curves.json",
    "chrono_one_way": CASE_ROOT / "chrono-one-way-report-data.json",
    "chrono_two_way": CASE_ROOT / "chrono-two-way-report-data.json",
    "chrono_stage3_tripod": CASE_ROOT / "chrono-stage3-tripod-report-data.json",
    "chrono_stage3_two_way": CASE_ROOT / "chrono-stage3-two-way-report-data.json",
    "chrono_stage3_lock": CASE_ROOT / "chrono-stage3-lock-report-data.json",
    "chrono_stage3_lock_two_way": CASE_ROOT / "chrono-stage3-lock-two-way-report-data.json",
    "chrono_stage3_thies_buffer": CASE_ROOT / "chrono-stage3-thies-buffer-report-data.json",
    "chrono_stage3b_rigid": CASE_ROOT / "chrono-stage3b-rigid-report-data.json",
    "chrono_stage3c_rigid_body_link": CASE_ROOT / "chrono-stage3c-rigid-body-link-report-data.json",
    "leg_mechanism_contract": CASE_ROOT / "leg-mechanism-data-contract.json",
    "leg_mechanism_validation": CASE_ROOT / "leg-mechanism-data-validation.json",
    "leg_mechanism_gap_tracker": CASE_ROOT / "leg-mechanism-gap-tracker.json",
    "leg_mechanism_data_request_pack": CASE_ROOT / "leg-mechanism-data-request-pack.json",
    "leg_mechanism_data_request_lint": CASE_ROOT / "leg-mechanism-data-request-lint.json",
    "leg_mechanism_import": CASE_ROOT / "leg-mechanism-data-import-report.json",
    "leg_mechanism_import_selftest": CASE_ROOT / "leg-mechanism-import-selftest-report.json",
    "chrono_real_leg_backend_selftest": CASE_ROOT / "chrono-real-leg-backend-selftest-report.json",
    "real_leg_mechanism_builder": CASE_ROOT / "real-leg-mechanism-builder-gate.json",
    "chrono_real_leg_mechanism": CASE_ROOT / "chrono-real-leg-mechanism-report-data.json",
    "model_realism_audit": CASE_ROOT / "model-realism-audit.json",
}

HTML_PATHS = {
    "chrono_one_way": VISUALIZATION_DIR / "chrono-recovery.html",
    "chrono_two_way": VISUALIZATION_DIR / "chrono-two-way.html",
    "chrono_stage3_tripod": VISUALIZATION_DIR / "chrono-stage3-tripod.html",
    "chrono_stage3_two_way": VISUALIZATION_DIR / "chrono-stage3-two-way.html",
    "chrono_stage3_lock": VISUALIZATION_DIR / "chrono-stage3-lock.html",
    "chrono_stage3_lock_two_way": VISUALIZATION_DIR / "chrono-stage3-lock-two-way.html",
    "chrono_stage3_thies_buffer": VISUALIZATION_DIR / "chrono-stage3-thies-buffer.html",
    "chrono_stage3c_rigid_body_link": VISUALIZATION_DIR / "chrono-stage3c-rigid-body-link.html",
    "leg_mechanism_contract": VISUALIZATION_DIR / "leg-mechanism-contract.html",
    "leg_mechanism_validation": VISUALIZATION_DIR / "leg-mechanism-validation.html",
    "leg_mechanism_gap_tracker": VISUALIZATION_DIR / "leg-mechanism-gap-tracker.html",
    "leg_mechanism_data_request_pack": VISUALIZATION_DIR / "leg-mechanism-data-request-pack.html",
    "leg_mechanism_data_request_lint": VISUALIZATION_DIR / "leg-mechanism-data-request-lint.html",
    "leg_mechanism_import": VISUALIZATION_DIR / "leg-mechanism-import.html",
    "leg_mechanism_import_selftest": VISUALIZATION_DIR / "leg-mechanism-import-selftest.html",
    "chrono_real_leg_backend_selftest": VISUALIZATION_DIR / "chrono-real-leg-backend-selftest.html",
    "real_leg_mechanism_builder": VISUALIZATION_DIR / "real-leg-mechanism-builder.html",
    "chrono_real_leg_mechanism": VISUALIZATION_DIR / "chrono-real-leg-mechanism.html",
    "model_realism_audit": VISUALIZATION_DIR / "model-realism-audit.html",
    "thies_buffer_curves": VISUALIZATION_DIR / "thies-buffer-curves.html",
    "literature_registry": VISUALIZATION_DIR / "literature-comparison-registry.html",
    "final_acceptance": VISUALIZATION_DIR / "chrono-final-acceptance.html",
    "nargolkar_2025": VISUALIZATION_DIR / "nargolkar-2025.html",
    "wang_2023": VISUALIZATION_DIR / "wang-2023.html",
}

PIPELINE_SCRIPT = ROOT / "local-tools" / "Run-RocketRecoveryPipeline.ps1"

STATUS_RANK = {"PASS": 0, "PARTIAL": 1, "CHECK": 2, "MISSING": 3}


def load_reports() -> dict[str, Any]:
    reports: dict[str, Any] = {}
    for key, path in REPORT_PATHS.items():
        if path.exists():
            reports[key] = read_json(path)
    return reports


def nested_get(row: dict[str, Any], path: list[str], default: Any = None) -> Any:
    value: Any = row
    for item in path:
        if not isinstance(value, dict) or item not in value:
            return default
        value = value[item]
    return value


def bool_status(value: Any) -> str:
    if value is True:
        return "PASS"
    if value is False:
        return "CHECK"
    return "MISSING"


def min_status(*statuses: str) -> str:
    return max(statuses, key=lambda status: STATUS_RANK.get(status, 99))


def report_ok(report: dict[str, Any] | None, expected_cases: int | None = None) -> bool:
    if not report:
        return False
    if report.get("status") not in {None, "simulated"}:
        return False
    if expected_cases is not None:
        cases = report.get("simulations") or report.get("cases") or {}
        if len(cases) < expected_cases:
            return False
    return True


def git_sourcecode_clean() -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["git", "-c", f"safe.directory={ROOT.as_posix()}", "diff", "--", "SourceCode"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return {"checked": False, "pass": None, "note": "git is not available"}
    return {
        "checked": True,
        "returncode": result.returncode,
        "pass": result.returncode == 0 and result.stdout.strip() == "",
        "diff_bytes": len(result.stdout.encode("utf-8")),
        "stderr": result.stderr.strip(),
    }


def chrono_contact_force_scan() -> dict[str, Any]:
    matches: list[str] = []
    for path in (ROOT / "analysis" / "rocket_recovery").glob("chrono*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "contact_forces(" in text:
            matches.append(str(path.relative_to(ROOT)))
    return {"pass": not matches, "matches": matches}


def deck_dof_status(report: dict[str, Any] | None) -> dict[str, Any]:
    if not report or not report.get("simulations"):
        return {"status": "MISSING", "deck_keys": []}
    first = next(iter(report["simulations"].values()))
    chrono = first.get("final_iteration_chrono") or first
    deck_keys = sorted((chrono.get("deck") or {}).keys())
    feedback_dofs = report.get("coupling", {}).get("feedback_dofs", [])
    reduced_feedback = len(feedback_dofs) != 6
    zero_filled_adapter_fields = []
    deck = chrono.get("deck") or {}
    for key in ["surge_m", "sway_m", "yaw_rad", "surge_m_s", "sway_m_s", "yaw_rad_s"]:
        series = deck.get(key)
        if isinstance(series, list) and series and max(abs(float(value)) for value in series) <= 1.0e-14:
            zero_filled_adapter_fields.append(key)
    required_3dof = ["heave_m", "roll_rad", "pitch_rad", "heave_m_s", "roll_rad_s", "pitch_rad_s"]
    required_6dof = [
        "surge_m",
        "sway_m",
        "heave_m",
        "roll_rad",
        "pitch_rad",
        "yaw_rad",
        "surge_m_s",
        "sway_m_s",
        "heave_m_s",
        "roll_rad_s",
        "pitch_rad_s",
        "yaw_rad_s",
    ]
    has_required_3dof = all(key in deck_keys for key in required_3dof)
    has_full_6dof = all(
        key in deck_keys
        for key in required_6dof
    )
    if has_full_6dof and not reduced_feedback:
        status = "PASS"
    elif has_required_3dof:
        status = "PARTIAL"
    else:
        status = "MISSING"
    return {
        "status": status,
        "deck_keys": deck_keys,
        "has_full_6dof": has_full_6dof,
        "reduced_feedback": reduced_feedback,
        "feedback_dofs": feedback_dofs,
        "zero_filled_adapter_fields": zero_filled_adapter_fields,
        "required_6dof_keys": required_6dof,
    }


def parameter_audit_summary(report: dict[str, Any] | None) -> dict[str, Any]:
    audit = nested_get(report or {}, ["config", "parameter_audit"], {})
    provenance = nested_get(report or {}, ["config", "parameter_provenance"], {})
    published = audit.get("published_values", []) if isinstance(audit, dict) else []
    assumptions = audit.get("explicit_assumptions", []) if isinstance(audit, dict) else []
    machine_readable_fields = bool(nested_get(report or {}, ["config", "rocket"])) and bool(nested_get(report or {}, ["config", "legs"]))
    parameters = provenance.get("parameters", []) if isinstance(provenance, dict) else []
    category_counts = provenance.get("category_counts", {}) if isinstance(provenance, dict) else {}
    all_rows_classified = bool(parameters) and all(
        row.get("source_category") in {"paper", "computed", "engineering_assumption", "implementation_assumption", "implementation_setting", "solver_setting", "source_metadata", "to_verify"}
        and row.get("source_detail")
        for row in parameters
    )
    has_assumption_or_to_verify = bool(category_counts.get("engineering_assumption") or category_counts.get("implementation_assumption") or category_counts.get("to_verify"))
    return {
        "published_value_count": len(published),
        "explicit_assumption_count": len(assumptions),
        "machine_readable_config_sections": machine_readable_fields,
        "parameter_provenance_count": len(parameters),
        "parameter_provenance_category_counts": category_counts,
        "status": "PASS" if published and assumptions and machine_readable_fields and all_rows_classified and has_assumption_or_to_verify else "PARTIAL",
        "note": "Config now includes a per-parameter provenance table; rows marked as engineering assumptions or to_verify must not be treated as reproduced paper data.",
    }


def literature_summary(reports: dict[str, Any]) -> dict[str, Any]:
    registry = reports.get("literature_registry", {})
    if registry:
        summary = registry.get("summary", {})
        has_available_data = bool(summary.get("available_comparisons_covered"))
        metadata_complete = bool(summary.get("metadata_complete_for_current_entries"))
        missing_curve_count = int(summary.get("missing_curve_count", 0) or 0)
        status = "PASS" if has_available_data and metadata_complete and missing_curve_count == 0 else "PARTIAL"
        return {
            "registry_path": str(REPORT_PATHS["literature_registry"]),
            "status": status,
            "metadata_complete": metadata_complete,
            "available_comparisons_covered": has_available_data,
            "pointwise_digitized_curve_count": summary.get("pointwise_digitized_curve_count", 0),
            "wang_text_indicator_count": summary.get("wang_text_indicator_count", 0),
            "thies_table_or_scale_count": summary.get("thies_table_or_scale_count", 0),
            "thies_digitized_buffer_curve_count": summary.get("thies_digitized_buffer_curve_count", 0),
            "missing_curve_count": summary.get("missing_curve_count", 0),
            "metadata_gap_count": summary.get("metadata_gap_count", 0),
            "note": (
                "A central registry now records pointwise Nargolkar digitized curves, Wang text indicators, "
                "Thies table/scale checks, units, extraction methods, error metrics and missing-curve gaps. "
                "Missing Wang/Thies/Yue/Li curves remain registered gaps, not reproduced claims."
            ),
        }
    narg = reports.get("nargolkar_2025", {})
    wang = reports.get("wang_2023", {})
    chrono = reports.get("chrono_stage3_lock_two_way", {})
    narg_comp = narg.get("paper_time_comparison", {})
    wang_comp = wang.get("comparison", {})
    thies_energy = nested_get(chrono, ["config", "validation_targets"], {})
    return {
        "nargolkar_digitized_time_comparison": bool(narg_comp),
        "wang_text_indicator_comparison": bool(wang_comp),
        "thies_touchdown_energy_target_kj": thies_energy.get("thies_touchdown_energy_kj"),
        "thies_touchdown_energy_computed_kj": thies_energy.get("computed_touchdown_energy_kj"),
        "status": "PARTIAL" if narg_comp and wang_comp and thies_energy else "MISSING",
        "note": (
            "Nargolkar has digitized time-history comparison fields; Wang and Thies checks are "
            "published-indicator/scale comparisons because source CFD/AQWA/Adams curves are not machine-readable."
        ),
    }


def add_requirement(rows: list[dict[str, Any]], group: str, req_id: str, requirement: str, status: str, evidence: str, note: str = "") -> None:
    rows.append(
        {
            "group": group,
            "id": req_id,
            "requirement": requirement,
            "status": status,
            "evidence": evidence,
            "note": note,
        }
    )


def build_audit() -> dict[str, Any]:
    reports = load_reports()
    source_clean = git_sourcecode_clean()
    contact_scan = chrono_contact_force_scan()
    one_way = reports.get("chrono_one_way")
    two_way = reports.get("chrono_two_way")
    stage3 = reports.get("chrono_stage3_tripod")
    stage3_lock_two = reports.get("chrono_stage3_lock_two_way")
    stage3_thies_buffer = reports.get("chrono_stage3_thies_buffer")
    stage3b = reports.get("chrono_stage3b_rigid")
    stage3c = reports.get("chrono_stage3c_rigid_body_link")
    mechanism_contract = reports.get("leg_mechanism_contract")
    mechanism_validation = reports.get("leg_mechanism_validation")
    mechanism_gap_tracker = reports.get("leg_mechanism_gap_tracker")
    mechanism_request_pack = reports.get("leg_mechanism_data_request_pack")
    mechanism_request_lint = reports.get("leg_mechanism_data_request_lint")
    mechanism_import = reports.get("leg_mechanism_import")
    mechanism_import_selftest = reports.get("leg_mechanism_import_selftest")
    real_backend_selftest = reports.get("chrono_real_leg_backend_selftest")
    real_leg_builder = reports.get("real_leg_mechanism_builder")
    real_leg_runtime = reports.get("chrono_real_leg_mechanism")
    model_realism = reports.get("model_realism_audit")
    hams_benchmark = reports.get("hams_benchmark")
    thies_buffer_curves = reports.get("thies_buffer_curves")
    deck_dof = deck_dof_status(stage3_lock_two or one_way)
    param_audit = parameter_audit_summary(stage3_lock_two or stage3)
    lit = literature_summary(reports)
    buffer_law = nested_get(stage3 or {}, ["config", "legs", "nonlinear_buffer_law"], {})
    buffer_supports_table = isinstance(buffer_law, dict) and "compression_only_table" in buffer_law.get("supported_types", [])
    buffer_interface_pass = bool(nested_get(stage3 or {}, ["validation", "nonlinear_buffer_law", "pass"])) and buffer_supports_table
    thies_buffer_law = nested_get(stage3_thies_buffer or {}, ["config", "legs", "nonlinear_buffer_law"], {})
    real_buffer_available = (
        bool(nested_get(thies_buffer_curves or {}, ["validation", "pass"]))
        and report_ok(stage3_thies_buffer, 1)
        and thies_buffer_law.get("type") == "compression_only_table"
        and bool(thies_buffer_law.get("force_stroke_points"))
        and bool(thies_buffer_law.get("force_velocity_points"))
    )
    animation_replay_pass = bool(nested_get(stage3_lock_two or {}, ["validation", "animation_feedback_deck_replay", "pass"]))
    chrono_time_grid_pass = bool(nested_get(stage3_lock_two or {}, ["validation", "chrono_time_grid", "pass"]))
    time_step_pass = bool(nested_get(stage3_lock_two or {}, ["validation", "time_step_convergence", "pass"]))
    six_dof_time_step_pass = bool(nested_get(stage3_lock_two or {}, ["validation", "six_dof_time_step_convergence", "pass"]))
    closure_rows = [
        sim.get("validation", {}).get("loose_coupling_closure_diagnostic", {})
        for sim in (stage3_lock_two or {}).get("simulations", {}).values()
    ]
    closure_pass = bool(closure_rows) and all(row.get("pass") is True for row in closure_rows)
    rows: list[dict[str, Any]] = []

    add_requirement(
        rows,
        "boundary",
        "hams_core_unchanged",
        "HAMS core source remains unchanged.",
        bool_status(source_clean["pass"]),
        "git diff -- SourceCode",
        "Generated HAMS case outputs may be dirty; this check is limited to SourceCode.",
    )
    add_requirement(
        rows,
        "boundary",
        "hams_official_benchmark",
        "The locally compiled HAMS executable reproduces the four CertTest benchmark output sets within the registered tolerances.",
        "PASS" if bool((hams_benchmark or {}).get("passed")) else "CHECK",
        f"RocketRecoveryCases/Barge_120x50/validation/benchmark-regression.json cases={len((hams_benchmark or {}).get('cases', []))}",
        "The four cases were regenerated with SourceCode/hams.exe. See docs/hams-certtest-toolchain-diagnosis.md; do not relabel the recorded toolchain-sensitive failures as tolerance noise.",
    )
    add_requirement(
        rows,
        "boundary",
        "no_commercial_required_solver",
        "No Adams/AQWA runtime is required for the implemented leg-coupling chain.",
        "PASS" if report_ok(stage3_lock_two, 4) and contact_scan["pass"] else "CHECK",
        "Chrono reports are simulated; chrono*.py has no contact_forces() fallback.",
        "AQWA/Adams/STAR are only mentioned as literature baselines and missing original-model data.",
    )
    add_requirement(
        rows,
        "stage1",
        "deck_motion_input",
        "Chrono reads platform displacement, velocity, attitude and angular-rate time histories.",
        deck_dof["status"],
        f"Deck keys in Chrono report: {', '.join(deck_dof['deck_keys'])}",
        "DeckMotion and the leg-reaction correction are 6DOF. The Wang wave/plume baseline remains heave/roll/pitch only, so zero horizontal baseline channels are audited separately as a model limitation.",
    )
    add_requirement(
        rows,
        "stage1",
        "vertical_rocket_and_leg_outputs",
        "Rocket lands vertically and each leg outputs contact, force, stroke, slip, attitude, velocity and nozzle-clearance diagnostics.",
        "PASS" if report_ok(stage3, 4) and bool(nested_get(stage3 or {}, ["validation", "case_physical_diagnostics", "pass"])) else "CHECK",
        "chrono-stage3-tripod-report-data.json validation.case_physical_diagnostics",
        "This proves the Stage 3A proxy diagnostics, not a hardware-valid Adams replica.",
    )
    add_requirement(
        rows,
        "stage1",
        "calculated_animation",
        "HTML animation is driven by calculated time histories, not hand-made trajectories.",
        "PASS" if HTML_PATHS["chrono_stage3_lock_two_way"].exists() and (VISUALIZATION_DIR / "chrono-stage3-lock-two-way-data.js").exists() and animation_replay_pass and chrono_time_grid_pass else "PARTIAL",
        "visualization/chrono-stage3-lock-two-way.html + data JS + validation.animation_feedback_deck_replay + validation.chrono_time_grid",
        "The final replay must use the plotted feedback deck and an exact endpoint-inclusive time axis; staggered decks or pre-step time labels are not accepted.",
    )
    add_requirement(
        rows,
        "stage1",
        "literature_scale_comparison",
        "Available Thies/Nargolkar/Wang velocity, force and displacement scales are compared.",
        lit["status"],
        lit.get("registry_path") or "Nargolkar, Wang and Chrono reports contain comparison/audit sections.",
        lit["note"],
    )
    add_requirement(
        rows,
        "stage2",
        "generalized_force_mapping",
        "Chrono leg and lock reactions map into platform [Fx,Fy,Fz,Mx,My,Mz] generalized loads.",
        bool_status(nested_get(stage3_lock_two or {}, ["validation", "six_dof_leg_increment", "pass"])),
        "chrono-stage3-lock-two-way validation.six_dof_leg_increment",
        "This validates six-component transfer and reciprocity; it does not imply a full 6DOF Wang wave/mooring/DP baseline.",
    )
    add_requirement(
        rows,
        "stage2",
        "no_force_degeneracy",
        "With no contact force, the platform response degenerates to the HAMS/Cummins baseline.",
        bool_status(nested_get(stage3_lock_two or {}, ["validation", "rhs_composition", "no_leg_degeneracy_pass"])),
        "chrono-stage3-lock-two-way validation.rhs_composition.no_leg_degeneracy_pass",
    )
    add_requirement(
        rows,
        "stage2",
        "eccentric_response",
        "Eccentric landing produces explainable roll/pitch response changes.",
        bool_status(nested_get(stage3_lock_two or {}, ["validation", "eccentric_response", "pass"])),
        "chrono-stage3-lock-two-way validation.eccentric_response",
    )
    add_requirement(
        rows,
        "stage2",
        "baseline_vs_feedback_output",
        "Baseline and feedback time histories are output and plotted together.",
        "PASS" if report_ok(stage3_lock_two, 4) and HTML_PATHS["chrono_stage3_lock_two_way"].exists() else "MISSING",
        "chrono-stage3-lock-two-way report contains baseline/with_leg_feedback/leg_induced_delta; HTML plots them.",
    )
    add_requirement(
        rows,
        "stage2",
        "loose_coupling_declared",
        "The two-way stage is explicitly marked as loose coupling, not strong co-simulation.",
        "PASS" if "loose" in json.dumps(nested_get(stage3_lock_two or {}, ["coupling"], {}), ensure_ascii=False).lower() else "CHECK",
        "chrono-stage3-lock-two-way coupling.limitations",
    )
    add_requirement(
        rows,
        "stage2",
        "loose_coupling_fixed_point",
        "The partitioned Chrono/Cummins iteration publishes and satisfies an explicit reaction/deck closure residual gate.",
        "PASS" if closure_pass else "PARTIAL",
        "chrono-stage3-lock-two-way simulations[*].validation.loose_coupling_closure_diagnostic",
        "The published closure residual is currently pass=false; this remains honest loose coupling and is not fixed-point convergence.",
    )
    add_requirement(
        rows,
        "stage2",
        "time_step_convergence",
        "Contact, lock, and all six platform response channels satisfy the registered coarse-versus-half-step convergence gate.",
        "PASS" if time_step_pass and six_dof_time_step_pass else "PARTIAL",
        "chrono-stage3-lock-two-way validation.time_step_convergence + validation.six_dof_time_step_convergence",
        "The current wave_port_15m half-step study fails in event-sensitive horizontal channels; this must remain visible until event localization and real horizontal restoring inputs are available.",
    )
    add_requirement(
        rows,
        "stage3",
        "geometric_leg_mechanism",
        "Equivalent spring-damper legs are upgraded toward geometric link mechanisms.",
        "PARTIAL" if report_ok(stage3, 4) and stage3b and stage3c and mechanism_contract and mechanism_import and mechanism_import_selftest and real_backend_selftest and mechanism_validation and mechanism_gap_tracker and mechanism_request_pack and bool((mechanism_request_lint or {}).get("pass")) and real_leg_builder and real_leg_runtime else "MISSING",
        "Stage 3A tripod proxy passes; Stage 3B/3C diagnostics exist but fail physical checks; leg mechanism contract/import schema/import self-test/backend self-test/validation/gap tracker/request pack/request lint/builder/runtime gate define, accept, check, and block missing Adams-equivalent input fields.",
        "This is not yet an Adams-equivalent CAD hinge/link mechanism. The request-pack lint passes and proves the .todo.csv data-acquisition package covers all strict blockers without changing model inputs.",
    )
    add_requirement(
        rows,
        "stage3",
        "nonlinear_buffer_interface",
        "Buffers support nonlinear force-stroke and force-velocity curves.",
        "PASS" if buffer_interface_pass else "MISSING",
        "chrono-stage3-tripod validation.nonlinear_buffer_law plus config.legs.nonlinear_buffer_law.supported_types",
        "The table interface exists. The default active law still uses published linear k/c plus explicit hard-stop assumptions; real curve availability is audited separately.",
    )
    add_requirement(
        rows,
        "stage3",
        "contact_state_and_stability",
        "Footpads support friction, slip, liftoff, recontact, stability, toppling risk, lock state and nozzle clearance.",
        "PASS"
        if bool(nested_get(stage3_lock_two or {}, ["validation", "contact_state_machine", "pass"]))
        and bool(nested_get(stage3_lock_two or {}, ["validation", "lock_feedback", "pass"]))
        else "CHECK",
        "chrono-stage3-lock-two-way validation.contact_state_machine + lock_feedback",
    )
    add_requirement(
        rows,
        "stage3",
        "real_buffer_data",
        "Real or literature-given buffer curves can be used instead of arbitrary assumptions.",
        "PARTIAL" if real_buffer_available else "MISSING",
        "thies-buffer-curves.json plus chrono-stage3-thies-buffer-report-data.json",
        (
            "Thies 2022 Figure 4/5 curves are digitized and used in a Chrono compression_only_table buffer-law branch. "
            "The raster digitization is not original author data, and the hard stop beyond the visible curve range remains a numerical guard."
        )
        if real_buffer_available
        else "No simulated Chrono branch using a machine-readable literature buffer curve was found.",
    )
    add_requirement(
        rows,
        "stage3",
        "parameter_sources",
        "All new parameters are in config and marked as paper, computed, assumption or to-verify.",
        param_audit["status"],
        f"published={param_audit['published_value_count']}, assumptions={param_audit['explicit_assumption_count']}, provenance_rows={param_audit['parameter_provenance_count']}",
        param_audit["note"],
    )
    pipeline_text = PIPELINE_SCRIPT.read_text(encoding="utf-8", errors="replace") if PIPELINE_SCRIPT.exists() else ""
    pipeline_has_required_steps = all(
        token in pipeline_text
        for token in [
            "Build-HAMS.ps1",
            "nargolkar_2025.py",
            "wang_2023.py",
            "chrono_stage3_lock_two_way_recovery.py",
            "thies_buffer_digitization.py",
            "chrono_stage3_thies_buffer_recovery.py",
            "chrono_stage3c_rigid_body_link_recovery.py",
            "leg_mechanism_data_contract.py",
            "leg_mechanism_data_importer.py",
            "leg_mechanism_import_selftest.py",
            "chrono_real_leg_backend_selftest.py",
            "leg_mechanism_data_validator.py",
            "leg_mechanism_gap_tracker.py",
            "leg_mechanism_data_request_pack.py",
            "leg_mechanism_data_request_lint.py",
            "real_leg_mechanism_builder.py",
            "chrono_real_leg_mechanism_recovery.py",
            "model_realism_audit.py",
            "literature_comparison_registry.py",
            "final_acceptance_audit.py",
        ]
    )
    case_artifacts_pass = (
        report_ok(stage3_lock_two, 4)
        and report_ok(stage3_thies_buffer, 4)
        and HTML_PATHS["chrono_stage3_lock_two_way"].exists()
        and HTML_PATHS["chrono_stage3_thies_buffer"].exists()
        and HTML_PATHS["chrono_stage3c_rigid_body_link"].exists()
        and HTML_PATHS["leg_mechanism_contract"].exists()
        and HTML_PATHS["leg_mechanism_validation"].exists()
        and HTML_PATHS["leg_mechanism_gap_tracker"].exists()
        and HTML_PATHS["leg_mechanism_data_request_pack"].exists()
        and HTML_PATHS["leg_mechanism_data_request_lint"].exists()
        and HTML_PATHS["leg_mechanism_import"].exists()
        and HTML_PATHS["leg_mechanism_import_selftest"].exists()
        and HTML_PATHS["chrono_real_leg_backend_selftest"].exists()
        and HTML_PATHS["real_leg_mechanism_builder"].exists()
        and HTML_PATHS["chrono_real_leg_mechanism"].exists()
        and HTML_PATHS["model_realism_audit"].exists()
        and HTML_PATHS["thies_buffer_curves"].exists()
        and HTML_PATHS["literature_registry"].exists()
        and HTML_PATHS["final_acceptance"].exists()
    )
    add_requirement(
        rows,
        "final",
        "command_line_chain",
        "Command line can run HAMS hydrodynamics, Cummins response, Chrono landing, two-way feedback and HTML visualization.",
        "PASS" if pipeline_has_required_steps and report_ok(stage3_lock_two, 4) and report_ok(stage3_thies_buffer, 4) and Path(ROOT / "LOCAL_USAGE.md").exists() else "PARTIAL",
        "local-tools/Run-RocketRecoveryPipeline.ps1 plus existing generated reports and LOCAL_USAGE.md.",
        "The audit validates the command entrypoint and artifacts; use -DryRun to inspect the full sequence without rerunning expensive simulations.",
    )
    add_requirement(
        rows,
        "final",
        "case_artifacts",
        "Cases output JSON, comparison plots/HTML animation and validation summary.",
        "PASS" if case_artifacts_pass else "MISSING",
        "chrono-stage3-lock-two-way + chrono-stage3-thies-buffer JSON/HTML, Thies curve page, literature registry and final audit page.",
    )
    add_requirement(
        rows,
        "final",
        "model_realism_audit",
        "A machine-readable realism audit separates reproduced data, digitized curves, surrogate models, proxy mechanisms and missing data.",
        "PASS" if model_realism and HTML_PATHS["model_realism_audit"].exists() else "MISSING",
        "model-realism-audit.json plus model-realism-audit.html",
        "This is an honesty gate: it can pass while still reporting PARTIAL model realism findings.",
    )
    add_requirement(
        rows,
        "final",
        "paper_curve_metadata",
        "Paper comparison curves state data source, digitization method, units and error metrics.",
        "PASS" if lit.get("metadata_complete") else "MISSING",
        lit.get("registry_path") or "Nargolkar digitized time comparison plus Wang/Thies text-indicator comparisons.",
        "Current comparison entries include source, extraction method, units and errors; missing full curves are explicit registry gaps.",
    )
    add_requirement(
        rows,
        "final",
        "assumptions_not_claimed_as_reproduced",
        "Unsupported parts are marked as engineering assumptions or to-verify, not as reproduced.",
        "PASS" if param_audit["explicit_assumption_count"] > 0 else "CHECK",
        "config.parameter_audit.explicit_assumptions and report.acceptance_scope.not_claimed",
    )

    summary = {status: sum(1 for row in rows if row["status"] == status) for status in STATUS_RANK}
    complete = summary["MISSING"] == 0 and summary["CHECK"] == 0 and summary["PARTIAL"] == 0
    gaps = [row for row in rows if row["status"] != "PASS"]
    return {
        "audit_id": "HAMS_Chrono_RocketRecovery_FinalAcceptance",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overall_status": "complete" if complete else "incomplete",
        "summary": summary,
        "requirements": rows,
        "gaps": gaps,
        "report_artifacts": {
            key: {
                "path": str(path),
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() else None,
            }
            for key, path in REPORT_PATHS.items()
        },
        "html_artifacts": {
            key: {
                "path": str(path),
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() else None,
            }
            for key, path in HTML_PATHS.items()
        },
        "sourcecode_clean_check": source_clean,
        "chrono_contact_force_scan": contact_scan,
        "deck_dof_status": deck_dof,
        "parameter_audit_summary": param_audit,
        "literature_comparison_summary": lit,
        "next_hardening_steps": [
            "Replace Wang zero-filled surge/sway/yaw adapter fields with full 6DOF HAMS/Cummins platform time histories when available.",
            "Run local-tools/Run-RocketRecoveryPipeline.ps1 end-to-end after major model changes to refresh every artifact from source.",
            "Use leg_mechanism_gap_tracker.py and leg_mechanism_data_request_pack.py as the authoritative real-data punch list; fill the CSV files under RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_import_schema with CAD/Adams hinge coordinates, telescopic absorber topology, joint graph, and rod mass/inertia data, then import, validate, build, and run chrono_real_leg_mechanism_recovery.py in strict mode.",
            "Replace raster-digitized Thies buffer curves with original author tables or measured hydropneumatic hardware data when available.",
            "Use docs/literature-comparison-registry.md as the source-data punch list; digitize or obtain Wang/Thies/Yue/Li curves for point-by-point validation.",
        ],
    }


def write_audit_markdown(audit: dict[str, Any]) -> None:
    lines = [
        "# Chrono/HAMS Final Acceptance Audit",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- Generated UTC: `{audit['generated_utc']}`",
        f"- Summary: PASS `{audit['summary']['PASS']}`, PARTIAL `{audit['summary']['PARTIAL']}`, CHECK `{audit['summary']['CHECK']}`, MISSING `{audit['summary']['MISSING']}`",
        "",
        "## Requirement Results",
        "",
        "| Group | ID | Status | Evidence | Note |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in audit["requirements"]:
        lines.append(
            "| {group} | `{id}` | **{status}** | {evidence} | {note} |".format(
                group=row["group"],
                id=row["id"],
                status=row["status"],
                evidence=str(row["evidence"]).replace("|", "\\|"),
                note=str(row["note"]).replace("|", "\\|"),
            )
        )
    lines.extend(["", "## Remaining Gaps", ""])
    for row in audit["gaps"]:
        lines.append(f"- **{row['status']}** `{row['id']}`: {row['requirement']} {row['note']}")
    lines.extend(["", "## Next Hardening Steps", ""])
    for step in audit["next_hardening_steps"]:
        lines.append(f"- {step}")
    AUDIT_MD.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_js(audit: dict[str, Any]) -> None:
    AUDIT_JS.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_JS.write_text(
        "window.CHRONO_FINAL_ACCEPTANCE_AUDIT = "
        + json.dumps(audit, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build final acceptance audit for the HAMS/Cummins + Chrono rocket recovery workflow.")
    parser.add_argument("command", choices=["audit", "report"], nargs="?", default="audit")
    args = parser.parse_args()
    audit = build_audit()
    write_json(AUDIT_JSON, audit)
    write_audit_markdown(audit)
    write_audit_js(audit)
    print(f"Overall: {audit['overall_status']}")
    print(f"Summary: {audit['summary']}")
    print(f"Audit JSON: {AUDIT_JSON}")
    print(f"Audit MD: {AUDIT_MD}")
    print(f"Audit JS: {AUDIT_JS}")
    if args.command == "report":
        print(f"Open: http://127.0.0.1:8765/chrono-final-acceptance.html")


if __name__ == "__main__":
    main()
