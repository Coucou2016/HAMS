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
NARGOLKAR_REPORT = ROCKET_CASES_DIR / "Paper_Nargolkar_2025" / "nargolkar-2025-report-data.json"
WANG_REPORT = ROCKET_CASES_DIR / "Paper_WangZhi_2023" / "wang-2023-report-data.json"
STAGE3_LOCK_TWO_WAY_REPORT = CASE_ROOT / "chrono-stage3-lock-two-way-report-data.json"
STAGE3_THIES_BUFFER_REPORT = CASE_ROOT / "chrono-stage3-thies-buffer-report-data.json"
LEG_VALIDATION_REPORT = CASE_ROOT / "leg-mechanism-data-validation.json"
REAL_BUILDER_REPORT = CASE_ROOT / "real-leg-mechanism-builder-gate.json"
REAL_RUNTIME_REPORT = CASE_ROOT / "chrono-real-leg-mechanism-report-data.json"
LITERATURE_REGISTRY = CASE_ROOT / "literature-comparison-registry.json"
THIES_BUFFER_CURVES = CASE_ROOT / "validation" / "thies_absorber_curves" / "thies-buffer-curves.json"
HAMS_BENCHMARK = ROCKET_CASES_DIR / "Barge_120x50" / "validation" / "benchmark-regression.json"

AUDIT_JSON = CASE_ROOT / "model-realism-audit.json"
AUDIT_MD = ROOT / "docs" / "model-realism-audit.md"
AUDIT_JS = VISUALIZATION_DIR / "model-realism-audit-data.js"

STATUS_RANK = {"PASS": 0, "PARTIAL": 1, "CHECK": 2, "MISSING": 3}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def optional_json(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {}


def status_worst(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "MISSING"
    return max((row["status"] for row in rows), key=lambda value: STATUS_RANK.get(value, 99))


def check(
    rows: list[dict[str, Any]],
    check_id: str,
    status: str,
    finding: str,
    evidence: str,
    impact: str,
    action: str,
    *,
    source: str,
) -> None:
    rows.append(
        {
            "id": check_id,
            "status": status,
            "finding": finding,
            "evidence": evidence,
            "impact": impact,
            "recommended_action": action,
            "source": source,
        }
    )


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
        "pass": result.returncode == 0 and result.stdout.strip() == "",
        "diff_bytes": len(result.stdout.encode("utf-8")),
        "stderr": result.stderr.strip(),
    }


def max_wang_reference_error(wang: dict[str, Any]) -> dict[str, Any]:
    rows = wang.get("comparison", []) if isinstance(wang, dict) else []
    numeric = [row for row in rows if isinstance(row.get("relative_error"), (int, float))]
    if not numeric:
        return {"available": False, "count": 0}
    worst = max(numeric, key=lambda row: abs(float(row["relative_error"])))
    return {
        "available": True,
        "count": len(numeric),
        "max_relative_error": float(abs(worst["relative_error"])),
        "worst_id": worst.get("id"),
        "worst_computed_value": worst.get("computed_value"),
        "worst_paper_value": worst.get("paper_value"),
        "statuses": sorted({str(row.get("status")) for row in rows}),
    }


def max_nargolkar_curve_error(nargolkar: dict[str, Any]) -> dict[str, Any]:
    comp = nargolkar.get("paper_time_comparison", {}) if isinstance(nargolkar, dict) else {}
    compared: list[dict[str, Any]] = []
    for case_id, velocities in comp.get("cases", {}).items():
        for velocity, responses in velocities.items():
            for response_id, row in responses.items():
                if row.get("status") == "compared" and isinstance(row.get("normalized_rmse_vs_paper_peak"), (int, float)):
                    compared.append(
                        {
                            "case_id": case_id,
                            "velocity_m_s": velocity,
                            "response_id": response_id,
                            "normalized_rmse_vs_paper_peak": float(row["normalized_rmse_vs_paper_peak"]),
                            "correlation": row.get("correlation"),
                        }
                    )
    audit = nargolkar.get("paper_audit", {}) if isinstance(nargolkar, dict) else {}
    if not compared:
        return {
            "available": False,
            "count": 0,
            "all_printed_values_matched": audit.get("all_printed_values_matched"),
            "all_internal_consistency_matched": audit.get("all_internal_consistency_matched"),
        }
    worst = max(compared, key=lambda row: row["normalized_rmse_vs_paper_peak"])
    return {
        "available": True,
        "count": len(compared),
        "max_normalized_rmse_vs_paper_peak": worst["normalized_rmse_vs_paper_peak"],
        "worst_case": worst,
        "all_printed_values_matched": audit.get("all_printed_values_matched"),
        "all_internal_consistency_matched": audit.get("all_internal_consistency_matched"),
    }


def coupling_limitations(report: dict[str, Any]) -> str:
    return json.dumps(report.get("coupling", {}).get("limitations", []), ensure_ascii=False).lower()


def max_omitted_horizontal_force(stage_report: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for case_id, sim in stage_report.get("simulations", {}).items():
        iteration = (sim.get("iterations") or [{}])[-1]
        audit = iteration.get("force_audit", {})
        summary = iteration.get("leg_force_summary", {})
        horizontal = float(audit.get("max_omitted_horizontal_contact_force_n") or 0.0)
        fed_back = float(audit.get("max_horizontal_contact_force_fed_back_n") or 0.0)
        vertical = float(summary.get("max_downward_platform_force_mn") or 0.0) * 1.0e6
        ratio = horizontal / max(abs(vertical), 1.0e-12)
        rows.append(
            {
                "case_id": case_id,
                "horizontal_n": horizontal,
                "fed_back_horizontal_n": fed_back,
                "feedback_included": bool(audit.get("horizontal_force_feedback_included")),
                "vertical_reference_n": vertical,
                "ratio_to_vertical": ratio,
            }
        )
    if not rows:
        return {"available": False, "case_count": 0}
    worst = max(rows, key=lambda row: row["horizontal_n"])
    return {
        "available": True,
        "case_count": len(rows),
        "max_omitted_horizontal_force_n": worst["horizontal_n"],
        "all_cases_feedback_included": all(row["feedback_included"] for row in rows),
        "max_horizontal_force_fed_back_n": max(row["fed_back_horizontal_n"] for row in rows),
        "worst_case": worst,
        "cases": rows,
    }


def build_audit() -> dict[str, Any]:
    nargolkar = optional_json(NARGOLKAR_REPORT)
    wang = optional_json(WANG_REPORT)
    stage = optional_json(STAGE3_LOCK_TWO_WAY_REPORT)
    stage_thies = optional_json(STAGE3_THIES_BUFFER_REPORT)
    leg_validation = optional_json(LEG_VALIDATION_REPORT)
    real_builder = optional_json(REAL_BUILDER_REPORT)
    real_runtime = optional_json(REAL_RUNTIME_REPORT)
    registry = optional_json(LITERATURE_REGISTRY)
    thies_curves = optional_json(THIES_BUFFER_CURVES)
    hams_benchmark = optional_json(HAMS_BENCHMARK)

    rows: list[dict[str, Any]] = []
    source_clean = git_sourcecode_clean()
    check(
        rows,
        "hams_core_boundary",
        "PASS" if source_clean.get("pass") else "CHECK",
        "HAMS SourceCode remains a hydrodynamic kernel and has not been modified by the rocket-leg work.",
        f"git diff -- SourceCode diff_bytes={source_clean.get('diff_bytes')}",
        "This preserves the project boundary: HAMS replaces AQWA-like potential-flow hydrodynamics, not Adams-like leg dynamics.",
        "Keep rocket recovery logic in external analysis modules.",
        source="git",
    )
    check(
        rows,
        "hams_certtest_regression",
        "PASS" if hams_benchmark.get("passed") is True else "PARTIAL",
        "The locally compiled HAMS executable is checked against all four official CertTest output sets.",
        f"passed={hams_benchmark.get('passed')}, cases={len(hams_benchmark.get('cases', []))}, max_relative_error={hams_benchmark.get('max_relative_error')}",
        "A failed hydrodynamic regression limits downstream confidence even when the external Chrono chain runs.",
        "See docs/hams-certtest-toolchain-diagnosis.md; resolve the Intel/MKL versus GNU toolchain provenance without relaxing the registered tolerances.",
        source=rel(HAMS_BENCHMARK),
    )

    wang_error = max_wang_reference_error(wang)
    if not wang_error.get("available"):
        wang_status = "MISSING"
    elif float(wang_error["max_relative_error"]) <= 0.10:
        wang_status = "PASS"
    else:
        wang_status = "PARTIAL"
    check(
        rows,
        "wang_2023_reference_error",
        wang_status,
        "Wang 2023 is currently a transparent HAMS/Cummins surrogate, not a pointwise AQWA/STAR-CCM+ reproduction.",
        json.dumps(wang_error, ensure_ascii=False),
        "The largest text-indicator error is too high to claim that the Wang paper result has been reproduced exactly.",
        "Digitize Wang Figures 6 and 8-10 or obtain original CFD/AQWA time histories; then recalibrate only with an explicit calibrated-source label.",
        source=rel(WANG_REPORT),
    )

    narg_error = max_nargolkar_curve_error(nargolkar)
    if not narg_error.get("available"):
        narg_status = "MISSING"
    elif (
        narg_error.get("all_internal_consistency_matched") is True
        and float(narg_error["max_normalized_rmse_vs_paper_peak"]) <= 0.25
    ):
        narg_status = "PASS"
    else:
        narg_status = "PARTIAL"
    check(
        rows,
        "nargolkar_2025_curve_quality",
        narg_status,
        "Nargolkar table values are tracked, but figure-level time-history reproduction is not yet quantitatively tight.",
        json.dumps(narg_error, ensure_ascii=False),
        "The current comparison is useful for debugging and trend checks; it should not be cited as exact reproduction of Figures 9/10.",
        "Review Table 2 frequency/mass inconsistency, improve figure digitization, and add a strict error threshold per plotted response.",
        source=rel(NARGOLKAR_REPORT),
    )

    coupling = stage.get("coupling", {})
    feedback_dofs = coupling.get("feedback_dofs", [])
    feedback_validation = stage.get("validation", {}).get("six_dof_leg_increment", {})
    six_dof_increment_pass = len(feedback_dofs) == 6 and feedback_validation.get("pass") is True
    check(
        rows,
        "leg_reaction_feedback_dof",
        "PASS" if six_dof_increment_pass else "PARTIAL",
        "Chrono contact and lock reactions are mapped into a full 6DOF HAMS/Cummins incremental correction.",
        f"feedback_dofs={feedback_dofs}, validation_pass={feedback_validation.get('pass')}",
        "This closes the previous omission of surge, sway and yaw leg-reaction increments.",
        "Keep six-component force reciprocity and response-channel checks in every coupled run.",
        source=rel(STAGE3_LOCK_TWO_WAY_REPORT),
    )

    baseline_dofs = coupling.get("baseline_dofs", [])
    baseline_full = len(baseline_dofs) == 6
    check(
        rows,
        "wang_wave_plume_baseline_dof",
        "PASS" if baseline_full else "PARTIAL",
        "The Wang wave/plume baseline remains limited to heave, roll and pitch; zero surge/sway/yaw baselines are explicit placeholders, not reproduced paper data.",
        f"baseline_dofs={baseline_dofs}, increment_model={coupling.get('hydrodynamic_increment_model', {})}",
        "The resulting six-channel response is a 3DOF environmental baseline plus a 6DOF leg-reaction increment, not a full 6DOF Wang reproduction.",
        "Obtain or independently validate horizontal wave, mooring and DP inputs before promoting the environmental baseline to 6DOF.",
        source=rel(STAGE3_LOCK_TWO_WAY_REPORT),
    )

    horizontal = max_omitted_horizontal_force(stage)
    horizontal_status = (
        "MISSING"
        if not horizontal.get("available")
        else "PASS"
        if horizontal.get("all_cases_feedback_included") and horizontal.get("max_omitted_horizontal_force_n", 0.0) <= 1.0e-6
        else "PARTIAL"
    )
    check(
        rows,
        "horizontal_contact_force_not_fed_back",
        horizontal_status,
        "Chrono horizontal contact/friction forces are now injected into surge/sway and all associated moments.",
        json.dumps(horizontal, ensure_ascii=False),
        "A PASS here covers force transfer only; it does not supply missing horizontal wave, mooring or DP physics.",
        "Retain this check and separately validate horizontal environmental/restoring inputs when source data become available.",
        source=rel(STAGE3_LOCK_TWO_WAY_REPORT),
    )

    animation_replay = stage.get("validation", {}).get("animation_feedback_deck_replay", {})
    check(
        rows,
        "animation_feedback_deck_consistency",
        "PASS" if animation_replay.get("pass") is True else "PARTIAL",
        "The displayed Chrono rocket and four-leg animation is replayed on the same 6DOF feedback deck history plotted by the report.",
        json.dumps(animation_replay, ensure_ascii=False),
        "This removes the previous one-stagger mismatch between the plotted corrected deck and the animated Chrono pass.",
        "Keep exact deck-history replay checks for all four cases.",
        source=rel(STAGE3_LOCK_TWO_WAY_REPORT),
    )

    chrono_time_grid = stage.get("validation", {}).get("chrono_time_grid", {})
    check(
        rows,
        "chrono_time_semantics",
        "PASS" if chrono_time_grid.get("pass") is True else "PARTIAL",
        "Chrono states use an exact, strictly increasing physical time axis that includes both configured endpoints.",
        json.dumps(chrono_time_grid, ensure_ascii=False),
        "Post-step states must not be labelled with the pre-step time, especially around first contact and lock events.",
        "Keep the endpoint/sample-count gate enabled for every final replay.",
        source=rel(STAGE3_LOCK_TWO_WAY_REPORT),
    )

    time_step = stage.get("validation", {}).get("time_step_convergence", {})
    six_dof_time_step = stage.get("validation", {}).get("six_dof_time_step_convergence", {})
    time_step_pass = time_step.get("pass") is True and six_dof_time_step.get("pass") is True
    check(
        rows,
        "chrono_time_step_convergence",
        "PASS" if time_step_pass else "PARTIAL",
        "The contact, lock, and full 6DOF platform outputs satisfy the registered coarse-versus-half-step convergence gate.",
        json.dumps({"contact_and_platform": time_step, "six_dof": six_dof_time_step}, ensure_ascii=False),
        "Surge and sway remain event-sensitive without published horizontal mooring or DP restoring data; failed checks are numerical limitations, not paper-validated responses.",
        "Add contact/lock event localization and compare force and moment impulses before reconsidering the time-step gate.",
        source=rel(STAGE3_LOCK_TWO_WAY_REPORT),
    )

    closure_rows = {
        case_id: sim.get("validation", {}).get("loose_coupling_closure_diagnostic", {})
        for case_id, sim in stage.get("simulations", {}).items()
    }
    closure_pass = bool(closure_rows) and all(row.get("pass") is True for row in closure_rows.values())
    check(
        rows,
        "loose_coupling_fixed_point",
        "PASS" if closure_pass else "PARTIAL",
        "The final replay exposes the next-pass reaction/deck closure residual; fixed-point convergence is not yet claimed.",
        json.dumps(closure_rows, ensure_ascii=False),
        "Non-negligible closure residual means the one-pass or finitely iterated platform and leg reactions remain a loose partitioned approximation.",
        "Use documented under-relaxation and an explicit residual gate before claiming converged two-way coupling.",
        source=rel(STAGE3_LOCK_TWO_WAY_REPORT),
    )

    pre_contact = (
        stage.get("config", {})
        .get("solver", {})
        .get("pre_contact_gravity")
    )
    check(
        rows,
        "touchdown_not_full_descent_gnc",
        "PARTIAL" if pre_contact else "CHECK",
        "The Chrono landing animation starts near touchdown with prescribed velocity; it is not a full rocket descent/GNC/engine-throttle simulation.",
        f"pre_contact_gravity={pre_contact!r}",
        "The animation is physically computed for contact and post-touchdown response, but not for the earlier guided descent trajectory.",
        "Keep the current animation label as touchdown/contact simulation; add a separate GNC/engine descent module only after propulsion and guidance data exist.",
        source=rel(STAGE3_LOCK_TWO_WAY_REPORT),
    )

    leg_ready = bool(leg_validation.get("ready"))
    blocking_fields = leg_validation.get("summary", {}).get("blocking_field_count")
    check(
        rows,
        "real_leg_geometry_data_gate",
        "PASS" if leg_ready else "PARTIAL",
        "The Adams-equivalent geometric leg mechanism remains blocked by missing real CAD/Adams/topology data.",
        f"ready={leg_ready}, blocking_fields={blocking_fields}, builder={real_builder.get('overall_status')}, runtime={real_runtime.get('overall_status')}",
        "Stage 3A/3B/3C are proxies/diagnostics. They are not a full Adams-equivalent landing-leg replica.",
        "Fill the request-pack CSVs from CAD, Adams export, author data, or measured engineering data; then rerun importer, validator, builder and real runtime gate.",
        source=rel(LEG_VALIDATION_REPORT),
    )

    buffer_status = thies_curves.get("status")
    curve_boundary = thies_curves.get("claim_boundary")
    buffer_law = stage_thies.get("coupling", {}).get("buffer_law")
    check(
        rows,
        "buffer_curve_source",
        "PARTIAL" if buffer_status == "digitized" else "MISSING" if not buffer_status else "PASS",
        "The nonlinear buffer branch uses Thies figure digitization, not original author tables or measured hydropneumatic data.",
        f"curve_status={buffer_status}, buffer_law={buffer_law}, claim_boundary={curve_boundary}",
        "This is traceable to the supplied paper, but the curve accuracy is limited by raster extraction and a numerical hard-stop guard.",
        "Replace the digitized Figure 4/5 curves with author tables or measured absorber curves when available.",
        source=rel(THIES_BUFFER_CURVES),
    )

    lock_limits = json.dumps(stage.get("coupling", {}).get("limitations", []), ensure_ascii=False)
    check(
        rows,
        "lock_hardware_proxy",
        "PARTIAL" if "proxy" in lock_limits.lower() or "ChLinkMateFix" in json.dumps(stage, ensure_ascii=False) else "PASS",
        "The post-touchdown lock is a Chrono fixed-link proxy, not a published clamp or seafastening mechanism.",
        lock_limits,
        "It is useful for stabilizing and feeding back reactions, but it is not validated hardware.",
        "Replace with real lock geometry, timing, stiffness and actuator data if the recovery-after-touchdown phase becomes a target result.",
        source=rel(STAGE3_LOCK_TWO_WAY_REPORT),
    )

    reg_summary = registry.get("summary", {})
    missing_curves = int(reg_summary.get("missing_curve_count") or 0)
    metadata_complete = bool(reg_summary.get("metadata_complete_for_current_entries"))
    check(
        rows,
        "literature_curve_coverage",
        "PASS" if metadata_complete and missing_curves == 0 else "PARTIAL" if metadata_complete else "CHECK",
        "The literature registry is explicit, but several paper curves are still missing for point-by-point validation.",
        f"metadata_complete={metadata_complete}, missing_curve_count={missing_curves}",
        "The reports should be read as traceable reproduction attempts plus registered gaps, not as complete paper replication.",
        "Digitize or obtain the listed Wang, Thies, Yue and Li curves before using them as strict validation plots.",
        source=rel(LITERATURE_REGISTRY),
    )

    assumption_count = (
        stage.get("config", {})
        .get("parameter_audit", {})
        .get("explicit_assumptions", [])
    )
    not_claimed = stage.get("acceptance_scope", {}).get("not_claimed", [])
    check(
        rows,
        "assumption_boundary_visible",
        "PASS" if assumption_count and not_claimed else "CHECK",
        "Assumptions and non-claims are machine-readable in the active coupled report.",
        f"explicit_assumptions={len(assumption_count)}, not_claimed={len(not_claimed)}",
        "This prevents proxy parameters from being silently promoted into reproduced paper data.",
        "Keep every new parameter tagged as paper/computed/calibrated/assumption/to_verify.",
        source=rel(STAGE3_LOCK_TWO_WAY_REPORT),
    )

    summary = {status: sum(1 for row in rows if row["status"] == status) for status in STATUS_RANK}
    gaps = [row for row in rows if row["status"] != "PASS"]
    priority_actions = [row["recommended_action"] for row in gaps]
    return {
        "audit_id": "HAMS_Chrono_RocketRecovery_ModelRealismAudit",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overall_status": "strictly_reproduced" if not gaps else "needs_hardening",
        "summary": summary,
        "checks": rows,
        "gaps": gaps,
        "priority_actions": priority_actions,
        "claim_boundary": {
            "safe_to_claim": [
                "HAMS core remains an external potential-flow hydrodynamic kernel.",
                "The current chain is executable with open tooling and local PyChrono.",
                "Stage 3 contact/lock animations are calculated from time histories.",
                "Chrono leg and lock reactions drive a full 6DOF HAMS/Cummins incremental response.",
                "Limitations are explicit and machine-readable.",
            ],
            "not_safe_to_claim_yet": [
                "Exact Wang AQWA/STAR-CCM+ pointwise reproduction.",
                "Exact Nargolkar MATLAB/Cummins time-history reproduction.",
                "Full 6DOF Wang wave/plume/mooring/DP baseline.",
                "Strong monolithic platform and leg co-simulation.",
                "Adams-equivalent real landing-leg mechanism.",
                "Real lock/seafastening hardware response.",
            ],
        },
    }


def write_markdown(audit: dict[str, Any]) -> None:
    lines = [
        "# HAMS/Chrono Model Realism Audit",
        "",
        f"- Overall status: `{audit['overall_status']}`",
        f"- Generated UTC: `{audit['generated_utc']}`",
        f"- Summary: PASS `{audit['summary']['PASS']}`, PARTIAL `{audit['summary']['PARTIAL']}`, CHECK `{audit['summary']['CHECK']}`, MISSING `{audit['summary']['MISSING']}`",
        "",
        "## Findings",
        "",
        "| ID | Status | Finding | Evidence | Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in audit["checks"]:
        lines.append(
            "| `{id}` | **{status}** | {finding} | {evidence} | {action} |".format(
                id=row["id"],
                status=row["status"],
                finding=str(row["finding"]).replace("|", "\\|"),
                evidence=str(row["evidence"]).replace("|", "\\|"),
                action=str(row["recommended_action"]).replace("|", "\\|"),
            )
        )
    lines.extend(["", "## Claim Boundary", "", "### Safe To Claim", ""])
    for item in audit["claim_boundary"]["safe_to_claim"]:
        lines.append(f"- {item}")
    lines.extend(["", "### Not Safe To Claim Yet", ""])
    for item in audit["claim_boundary"]["not_safe_to_claim_yet"]:
        lines.append(f"- {item}")
    AUDIT_MD.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_js(audit: dict[str, Any]) -> None:
    AUDIT_JS.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_JS.write_text(
        "window.MODEL_REALISM_AUDIT = "
        + json.dumps(audit, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit whether current HAMS/Cummins + Chrono rocket-recovery claims are realistic.")
    parser.add_argument("command", choices=["audit", "report"], nargs="?", default="audit")
    args = parser.parse_args()
    audit = build_audit()
    write_json(AUDIT_JSON, audit)
    write_markdown(audit)
    write_js(audit)
    print(f"Overall: {audit['overall_status']}")
    print(f"Summary: {audit['summary']}")
    print(f"Audit JSON: {AUDIT_JSON}")
    print(f"Audit MD: {AUDIT_MD}")
    print(f"Audit JS: {AUDIT_JS}")
    if args.command == "report":
        print("Open: http://127.0.0.1:8765/model-realism-audit.html")


if __name__ == "__main__":
    main()
