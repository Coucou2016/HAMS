from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .chrono_leg_model import chrono_environment_report
    from .chrono_real_leg_backend import backend_manifest, smoke_assemble_chrono_system
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from .leg_mechanism_data_validator import BLOCKING_SOURCE_CATEGORIES, SYNTHETIC_SOURCE_CATEGORY
    from .real_leg_mechanism_builder import REAL_CONFIG_JSON
except ImportError:
    from chrono_leg_model import chrono_environment_report
    from chrono_real_leg_backend import backend_manifest, smoke_assemble_chrono_system
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from leg_mechanism_data_validator import BLOCKING_SOURCE_CATEGORIES, SYNTHETIC_SOURCE_CATEGORY
    from real_leg_mechanism_builder import REAL_CONFIG_JSON


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
RUNNER_JSON = CASE_ROOT / "chrono-real-leg-mechanism-report-data.json"
RUNNER_MD = ROOT / "docs" / "chrono-real-leg-mechanism.md"
RUNNER_JS = VISUALIZATION_DIR / "chrono-real-leg-mechanism-data.js"

REQUIRED_SECTIONS = [
    "coordinate_system",
    "rocket",
    "landing_conditions",
    "legs",
    "buffer_law",
    "lock_hardware",
    "source_map",
    "validation_summary",
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def source_category_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        category = str(row.get("source_category", "missing_required"))
        counts[category] = counts.get(category, 0) + 1
    return counts


def validate_real_config(config_path: Path, run_backend_smoke: bool = True) -> dict[str, Any]:
    env = chrono_environment_report()
    resolved = config_path.resolve()
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if not resolved.exists():
        blockers.append(
            {
                "id": "missing_real_config",
                "status": "MISSING",
                "evidence": f"{rel(resolved)} does not exist.",
                "next_action": "Fill real CAD/Adams/author CSV data, validate in strict mode, then run real_leg_mechanism_builder.py report.",
            }
        )
        return {
            "case_id": "Chrono_LeggedRecovery_RealLegMechanism",
            "title": "Chrono real landing-leg mechanism runtime gate",
            "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "blocked",
            "overall_status": "blocked_missing_real_config",
            "ready_for_chrono_runtime": False,
            "config_path": rel(resolved),
            "environment": env,
            "blockers": blockers,
            "warnings": warnings,
            "assembly_plan": None,
            "backend_smoke": None,
            "policy": runtime_policy(),
        }

    config = read_json(resolved)
    for section in REQUIRED_SECTIONS:
        if section not in config:
            blockers.append({"id": f"missing_section_{section}", "status": "MISSING", "evidence": f"Config section {section} is missing."})

    if config.get("schema_id") != "ChronoRealLegMechanismConfig/v1":
        blockers.append({"id": "schema_id", "status": "CHECK", "evidence": f"schema_id={config.get('schema_id')}"})

    source_map = config.get("source_map") if isinstance(config.get("source_map"), list) else []
    counts = source_category_counts(source_map)
    synthetic_rows = [row for row in source_map if row.get("source_category") == SYNTHETIC_SOURCE_CATEGORY]
    blocking_rows = [
        row
        for row in source_map
        if row.get("source_category") in BLOCKING_SOURCE_CATEGORIES
        or row.get("source_category") == SYNTHETIC_SOURCE_CATEGORY
        or not str(row.get("source_detail", "")).strip()
    ]
    if synthetic_rows:
        blockers.append(
            {
                "id": "synthetic_sources_rejected",
                "status": "CHECK",
                "evidence": f"{len(synthetic_rows)} source_map rows are synthetic_test_fixture.",
                "next_action": "Use synthetic fixtures only for importer self-tests; replace them with CAD/Adams/author/measured/calibrated data.",
            }
        )
    if blocking_rows:
        blockers.append(
            {
                "id": "blocking_source_rows",
                "status": "CHECK",
                "evidence": f"{len(blocking_rows)} source_map rows are blocked or missing source_detail.",
                "sample_paths": [row.get("path") for row in blocking_rows[:20]],
            }
        )

    validation_summary = config.get("validation_summary") if isinstance(config.get("validation_summary"), dict) else {}
    if validation_summary.get("blocking_check_count", 0) != 0 or validation_summary.get("blocking_field_count", 0) != 0:
        blockers.append(
            {
                "id": "validator_summary_not_clean",
                "status": "CHECK",
                "evidence": f"blocking_check_count={validation_summary.get('blocking_check_count')}, blocking_field_count={validation_summary.get('blocking_field_count')}",
            }
        )

    if not env.get("available"):
        blockers.append({"id": "chrono_unavailable", "status": "MISSING", "evidence": env.get("error", "Project Chrono is not available.")})

    if not config.get("builder_policy", {}).get("no_proxy_fallback"):
        blockers.append({"id": "proxy_fallback_policy", "status": "CHECK", "evidence": "builder_policy.no_proxy_fallback must be true."})

    plan = backend_manifest(config) if not any(row["id"].startswith("missing_section") for row in blockers) else None
    data_ready = len(blockers) == 0
    backend_smoke = None
    if data_ready and run_backend_smoke:
        backend_smoke = smoke_assemble_chrono_system(config, allow_synthetic=False)
        if not backend_smoke.get("pass"):
            blockers.append(
                {
                    "id": "backend_smoke_failed",
                    "status": "CHECK",
                    "evidence": backend_smoke.get("error") or f"unsupported={backend_smoke.get('unsupported')}",
                }
            )
    if not data_ready:
        warnings.append(
            {
                "id": "runtime_backend_waiting_for_real_data",
                "status": "PARTIAL",
                "evidence": "The backend adapter exists, but formal runtime stays blocked until strict real data builds chrono_real_leg_mechanism_config.json.",
            }
        )
    final_ready = data_ready and (backend_smoke is None or bool(backend_smoke.get("pass")))
    return {
        "case_id": "Chrono_LeggedRecovery_RealLegMechanism",
        "title": "Chrono real landing-leg mechanism runtime gate",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "ready_for_chrono_runtime" if final_ready else "blocked",
        "overall_status": "ready_for_real_chrono_backend" if final_ready else "blocked_by_real_config_gate",
        "ready_for_chrono_runtime": final_ready,
        "strict_real_data_ready": data_ready,
        "config_path": rel(resolved),
        "environment": env,
        "source_category_counts": counts,
        "blockers": blockers,
        "warnings": warnings,
        "assembly_plan": plan,
        "backend_smoke": backend_smoke,
        "policy": runtime_policy(),
    }


def runtime_policy() -> dict[str, Any]:
    return {
        "formal_entrypoint": "chrono_real_leg_mechanism_recovery.py",
        "accepted_config": rel(REAL_CONFIG_JSON),
        "rejects_synthetic_fixture": True,
        "rejects_proxy_fallback": True,
        "requires_project_chrono": True,
        "backend_adapter": "chrono_real_leg_backend.py assembles config-defined bodies, spherical mates and absorber links in PyChrono when strict real data exists.",
        "hams_core_policy": "HAMS remains a hydrodynamic/Cummins input provider only; this runner does not modify HAMS SourceCode.",
        "not_claimed": [
            "Do not claim an Adams-equivalent mechanism when this report is blocked.",
            "Do not use synthetic_leg_import outputs as production landing-leg data.",
            "Do not fall back to old hand-written contact_forces.",
        ],
    }


def write_runner_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Chrono Real Landing-Leg Mechanism Runtime Gate",
        "",
        f"- Overall status: `{report['overall_status']}`",
        f"- Status: `{report['status']}`",
        f"- Ready for Chrono runtime: `{report['ready_for_chrono_runtime']}`",
        f"- Config: `{report['config_path']}`",
        f"- Generated UTC: `{report['generated_utc']}`",
        "",
        "## Policy",
        "",
        "- Reject synthetic fixtures.",
        "- Reject proxy fallback.",
        "- Require Project Chrono.",
        "- Keep HAMS as the hydrodynamic/Cummins provider only.",
        "- Use chrono_real_leg_backend.py for config-defined body/joint/link assembly when strict real data exists.",
        "",
        "## Blockers",
        "",
        "| ID | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for row in report.get("blockers", []):
        lines.append(f"| `{row.get('id')}` | **{row.get('status')}** | {str(row.get('evidence', '')).replace('|', '\\|')} |")
    if not report.get("blockers"):
        lines.append("| none | PASS | No data gate blockers. Runtime backend still requires CAD/topology-specific assembly implementation. |")
    lines.extend(["", "## Assembly Plan", ""])
    plan = report.get("assembly_plan")
    if plan:
        lines.extend(
            [
                f"- Leg count: `{plan['leg_count']}`",
                f"- Bodies: `{plan['body_count']}`",
                f"- Joints: `{plan['joint_count']}`",
                f"- Force elements: `{plan['force_element_count']}`",
                f"- Force rows: `{plan['force_element_count']}`",
            ]
        )
    else:
        lines.append("No assembly plan is emitted until a real config exists and passes the strict source gate.")
    if report.get("backend_smoke"):
        smoke = report["backend_smoke"]
        lines.extend(
            [
                "",
                "## Backend Smoke Assembly",
                "",
                f"- Pass: `{smoke.get('pass')}`",
                f"- Created bodies: `{smoke.get('created_body_count')}`",
                f"- Created links: `{smoke.get('created_link_count')}`",
            ]
        )
    RUNNER_MD.parent.mkdir(parents=True, exist_ok=True)
    RUNNER_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_runner_js(report: dict[str, Any]) -> None:
    RUNNER_JS.parent.mkdir(parents=True, exist_ok=True)
    RUNNER_JS.write_text(
        "window.CHRONO_REAL_LEG_MECHANISM_DATA = "
        + json.dumps(report, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Gate the formal Chrono real landing-leg mechanism runtime on strict real CAD/Adams-quality config data.")
    parser.add_argument("command", choices=["check", "report"], nargs="?", default="check")
    parser.add_argument("--config", type=Path, default=REAL_CONFIG_JSON)
    args = parser.parse_args()

    report = validate_real_config(args.config)
    write_json(RUNNER_JSON, report)
    write_runner_markdown(report)
    write_runner_js(report)

    print(f"Overall: {report['overall_status']}")
    print(f"Status: {report['status']}")
    print(f"Ready for Chrono runtime: {report['ready_for_chrono_runtime']}")
    print(f"Blockers: {len(report.get('blockers', []))}")
    print(f"Report JSON: {RUNNER_JSON}")
    print(f"Report MD: {RUNNER_MD}")
    print(f"Report JS: {RUNNER_JS}")
    if args.command == "report":
        print("Open: http://127.0.0.1:8765/chrono-real-leg-mechanism.html")


if __name__ == "__main__":
    main()
