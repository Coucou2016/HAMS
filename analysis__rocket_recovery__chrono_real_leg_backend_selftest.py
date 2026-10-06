from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .chrono_real_leg_backend import smoke_assemble_chrono_system
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
except ImportError:
    from chrono_real_leg_backend import smoke_assemble_chrono_system
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
SYNTHETIC_CONFIG = CASE_ROOT / "validation" / "synthetic_leg_import" / "chrono_real_leg_mechanism_config.synthetic.json"
SELFTEST_JSON = CASE_ROOT / "chrono-real-leg-backend-selftest-report.json"
SELFTEST_MD = ROOT / "docs" / "chrono-real-leg-backend-selftest.md"
SELFTEST_JS = VISUALIZATION_DIR / "chrono-real-leg-backend-selftest-data.js"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def build_selftest(config_path: Path = SYNTHETIC_CONFIG) -> dict[str, Any]:
    if not config_path.exists():
        return {
            "selftest_id": "ChronoRealLegBackendSyntheticSelfTest",
            "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "FAIL",
            "config_path": rel(config_path.resolve()),
            "synthetic_only": True,
            "not_literature_reproduction": True,
            "backend_result": None,
            "error": "Synthetic real-leg config does not exist. Run leg_mechanism_import_selftest.py report first.",
        }
    config = read_json(config_path)
    result = smoke_assemble_chrono_system(config, allow_synthetic=True)
    return {
        "selftest_id": "ChronoRealLegBackendSyntheticSelfTest",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS" if result.get("pass") else "FAIL",
        "config_path": rel(config_path.resolve()),
        "synthetic_only": True,
        "not_literature_reproduction": True,
        "not_production_data": True,
        "backend_result": result,
        "warning": "This smoke test proves that the real-config schema can instantiate PyChrono bodies, spherical mates and absorber links. It does not solve a landing trajectory and does not validate Adams equivalence.",
    }


def write_markdown(report: dict[str, Any]) -> None:
    result = report.get("backend_result") or {}
    manifest = result.get("manifest") or {}
    lines = [
        "# Chrono Real-Leg Backend Synthetic Self-Test",
        "",
        f"- Status: `{report['status']}`",
        f"- Config: `{report['config_path']}`",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Synthetic only: `{report.get('synthetic_only')}`",
        "",
        report.get("warning", report.get("error", "")),
        "",
        "## Backend Result",
        "",
        f"- Pass: `{result.get('pass')}`",
        f"- Stage: `{result.get('stage')}`",
        f"- Created bodies: `{result.get('created_body_count')}`",
        f"- Created links: `{result.get('created_link_count')}`",
        f"- Unsupported items: `{len(result.get('unsupported', []))}`",
        "",
        "## Manifest",
        "",
        f"- Legs: `{manifest.get('leg_count')}`",
        f"- Bodies: `{manifest.get('body_count')}`",
        f"- Joints: `{manifest.get('joint_count')}`",
        f"- Force elements: `{manifest.get('force_element_count')}`",
    ]
    SELFTEST_MD.parent.mkdir(parents=True, exist_ok=True)
    SELFTEST_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_js(report: dict[str, Any]) -> None:
    SELFTEST_JS.parent.mkdir(parents=True, exist_ok=True)
    SELFTEST_JS.write_text(
        "window.CHRONO_REAL_LEG_BACKEND_SELFTEST = "
        + json.dumps(report, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a synthetic smoke test for the real-config-to-PyChrono backend adapter.")
    parser.add_argument("command", choices=["run", "report"], nargs="?", default="run")
    parser.add_argument("--config", type=Path, default=SYNTHETIC_CONFIG)
    args = parser.parse_args()

    report = build_selftest(args.config.resolve())
    write_json(SELFTEST_JSON, report)
    write_markdown(report)
    write_js(report)

    result = report.get("backend_result") or {}
    print(f"Status: {report['status']}")
    print(f"Backend pass: {result.get('pass')}")
    print(f"Created bodies: {result.get('created_body_count')}")
    print(f"Created links: {result.get('created_link_count')}")
    print(f"Self-test JSON: {SELFTEST_JSON}")
    print(f"Self-test MD: {SELFTEST_MD}")
    print(f"Self-test JS: {SELFTEST_JS}")
    if args.command == "report":
        print("Open: http://127.0.0.1:8765/chrono-real-leg-backend-selftest.html")


if __name__ == "__main__":
    main()
