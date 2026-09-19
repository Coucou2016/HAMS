from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from .leg_mechanism_data_importer import SCHEMA_FILES
    from .leg_mechanism_data_request_pack import REQUEST_DIR, REQUEST_JSON
    from .leg_mechanism_gap_tracker import GAP_JSON
except ImportError:
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from leg_mechanism_data_importer import SCHEMA_FILES
    from leg_mechanism_data_request_pack import REQUEST_DIR, REQUEST_JSON
    from leg_mechanism_gap_tracker import GAP_JSON


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
LINT_JSON = CASE_ROOT / "leg-mechanism-data-request-lint.json"
LINT_MD = ROOT / "docs" / "leg-mechanism-data-request-lint.md"
LINT_JS = VISUALIZATION_DIR / "leg-mechanism-data-request-lint-data.js"

LEG_RE = re.compile(r"legs\[(\d+)\]")
MARKER_RE = re.compile(r"\.adams_equivalent_geometry\.([BTKP])_")
BODY_RE = re.compile(r"\.body_properties\.([^.]+)\.([^.]+)$")
TOPO_RE = re.compile(r"\.constraint_topology\.([^.]+)$")


EXPECTED_TODO_HEADERS = {
    "field_tasks.csv": [
        "task_id",
        "priority",
        "field_class",
        "path",
        "target_csv",
        "current_source_category",
        "current_value",
        "required_source",
        "acceptable_source_categories",
        "current_papers_can_fill",
        "note",
    ],
    "coordinate_system.todo.csv": ["field", "value_json", "source_category", "source_detail", "required_source", "note"],
    "leg_azimuths.todo.csv": [
        "leg_id",
        "azimuth_deg",
        "source_category",
        "source_detail",
        "current_template_azimuth_deg",
        "required_source",
        "note",
    ],
    "marker_coordinates.todo.csv": [
        "leg_id",
        "marker",
        "x_m",
        "y_m",
        "z_m",
        "source_category",
        "source_detail",
        "current_template_x_m",
        "current_template_y_m",
        "current_template_z_m",
        "required_source",
        "note",
    ],
    "constraint_topology.todo.csv": ["leg_id", "field", "value_json", "source_category", "source_detail", "required_source", "note"],
    "body_properties.todo.csv": ["leg_id", "body", "field", "value_json", "unit", "source_category", "source_detail", "required_source", "note"],
    "buffer_lock.todo.csv": ["section", "field", "value_json", "unit", "source_category", "source_detail", "required_source", "note"],
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            rows.append(json.loads(stripped))
    return rows


def leg_id_from_path(path: str) -> str:
    match = LEG_RE.search(path)
    if not match:
        return ""
    return f"leg_{int(match.group(1)) + 1}"


def check(status: str, check_id: str, description: str, evidence: str, blockers: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "description": description,
        "evidence": evidence,
        "blockers": blockers or [],
    }


def blocker_key(row: dict[str, Any]) -> str:
    return str(row.get("path", ""))


def marker_group_key(path: str) -> str:
    leg_id = leg_id_from_path(path)
    match = MARKER_RE.search(path)
    return f"{leg_id}.{match.group(1)}" if leg_id and match else path


def topology_key(path: str) -> str:
    leg_id = leg_id_from_path(path)
    match = TOPO_RE.search(path)
    return f"{leg_id}.{match.group(1)}" if leg_id and match else path


def body_key(path: str) -> str:
    leg_id = leg_id_from_path(path)
    match = BODY_RE.search(path)
    return f"{leg_id}.{match.group(1)}.{match.group(2)}" if leg_id and match else path


def build_lint() -> dict[str, Any]:
    request_pack = read_json(REQUEST_JSON)
    gap_report = read_json(GAP_JSON)
    request_dir = (ROOT / request_pack["request_dir"]).resolve()
    blockers = gap_report.get("blocking_fields", [])
    blocker_paths = {blocker_key(row) for row in blockers}

    csv_data: dict[str, dict[str, Any]] = {}
    missing_files: list[str] = []
    header_errors: list[str] = []
    for filename, expected_header in EXPECTED_TODO_HEADERS.items():
        path = request_dir / filename
        if not path.exists():
            missing_files.append(filename)
            continue
        header, rows = read_csv_rows(path)
        csv_data[filename] = {"header": header, "rows": rows, "path": path}
        if header != expected_header:
            header_errors.append(f"{filename}: expected {expected_header}, got {header}")

    jsonl_path = request_dir / "field_tasks.jsonl"
    readme_path = request_dir / "README.md"
    if not jsonl_path.exists():
        missing_files.append("field_tasks.jsonl")
    if not readme_path.exists():
        missing_files.append("README.md")

    checks: list[dict[str, Any]] = []
    checks.append(
        check(
            "PASS" if not missing_files else "MISSING",
            "request_pack_files_exist",
            "All request-pack CSV, JSONL and README files must exist.",
            f"missing={len(missing_files)}, request_dir={rel(request_dir)}",
            missing_files,
        )
    )
    checks.append(
        check(
            "PASS" if not header_errors else "CHECK",
            "todo_headers_match_schema",
            "Todo CSV headers must match the documented request-pack schema.",
            f"header_errors={len(header_errors)}",
            header_errors,
        )
    )

    task_rows = csv_data.get("field_tasks.csv", {}).get("rows", [])
    task_paths = {row.get("path", "") for row in task_rows}
    duplicate_task_paths = sorted(path for path in task_paths if sum(1 for row in task_rows if row.get("path", "") == path) > 1)
    missing_from_tasks = sorted(blocker_paths - task_paths)
    extra_in_tasks = sorted(task_paths - blocker_paths)
    checks.append(
        check(
            "PASS" if not missing_from_tasks and not extra_in_tasks and not duplicate_task_paths else "CHECK",
            "field_tasks_cover_blocking_fields",
            "field_tasks.csv must cover every strict blocking field exactly once.",
            f"tasks={len(task_rows)}, blockers={len(blocker_paths)}, missing={len(missing_from_tasks)}, extra={len(extra_in_tasks)}, duplicates={len(duplicate_task_paths)}",
            (missing_from_tasks + extra_in_tasks + duplicate_task_paths)[:60],
        )
    )

    jsonl_rows = read_jsonl_rows(jsonl_path) if jsonl_path.exists() else []
    jsonl_paths = {row.get("path", "") for row in jsonl_rows}
    checks.append(
        check(
            "PASS" if jsonl_paths == task_paths and len(jsonl_rows) == len(task_rows) else "CHECK",
            "jsonl_matches_field_tasks",
            "field_tasks.jsonl must match field_tasks.csv path coverage.",
            f"jsonl_rows={len(jsonl_rows)}, csv_rows={len(task_rows)}, path_sets_equal={jsonl_paths == task_paths}",
            sorted((jsonl_paths ^ task_paths))[:60],
        )
    )

    official_schema_names = set(SCHEMA_FILES)
    request_files = {path.name for path in request_dir.iterdir() if path.is_file()} if request_dir.exists() else set()
    ambiguous_importer_names = sorted((request_files - {"field_tasks.csv"}) & official_schema_names)
    non_todo_csv = sorted(
        name
        for name in request_files
        if name.endswith(".csv") and not name.endswith(".todo.csv") and name != "field_tasks.csv"
    )
    checks.append(
        check(
            "PASS" if not ambiguous_importer_names and not non_todo_csv else "CHECK",
            "todo_files_cannot_be_imported_accidentally",
            "Request-pack todo files must not share exact names with importer CSV files.",
            f"ambiguous_importer_names={len(ambiguous_importer_names)}, non_todo_csv={len(non_todo_csv)}",
            ambiguous_importer_names + non_todo_csv,
        )
    )

    coordinate_expected = {path.split(".")[-1] for path in blocker_paths if path.startswith("coordinate_system.")}
    coordinate_actual = {row.get("field", "") for row in csv_data.get("coordinate_system.todo.csv", {}).get("rows", [])}
    azimuth_expected = {leg_id_from_path(path) for path in blocker_paths if path.endswith(".azimuth_deg")}
    azimuth_actual = {row.get("leg_id", "") for row in csv_data.get("leg_azimuths.todo.csv", {}).get("rows", [])}
    marker_expected = {marker_group_key(path) for path in blocker_paths if ".adams_equivalent_geometry." in path}
    marker_actual = {
        f"{row.get('leg_id', '')}.{row.get('marker', '')}"
        for row in csv_data.get("marker_coordinates.todo.csv", {}).get("rows", [])
    }
    topology_expected = {topology_key(path) for path in blocker_paths if ".constraint_topology." in path}
    topology_actual = {
        f"{row.get('leg_id', '')}.{row.get('field', '')}"
        for row in csv_data.get("constraint_topology.todo.csv", {}).get("rows", [])
    }
    body_expected = {body_key(path) for path in blocker_paths if ".body_properties." in path}
    body_actual = {
        f"{row.get('leg_id', '')}.{row.get('body', '')}.{row.get('field', '')}"
        for row in csv_data.get("body_properties.todo.csv", {}).get("rows", [])
    }
    buffer_expected = {path for path in blocker_paths if path.startswith("buffer_law.") or path.startswith("lock_hardware.")}
    buffer_actual = {
        f"{row.get('section', '')}.{row.get('field', '')}"
        for row in csv_data.get("buffer_lock.todo.csv", {}).get("rows", [])
    }
    coverage_sets = {
        "coordinate_system": (coordinate_expected, coordinate_actual),
        "azimuths": (azimuth_expected, azimuth_actual),
        "marker_groups": (marker_expected, marker_actual),
        "constraint_topology": (topology_expected, topology_actual),
        "body_properties": (body_expected, body_actual),
        "buffer_lock": (buffer_expected, buffer_actual),
    }
    coverage_blockers: list[str] = []
    coverage_evidence: list[dict[str, Any]] = []
    for name, (expected, actual) in coverage_sets.items():
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        coverage_evidence.append(
            {
                "name": name,
                "expected_count": len(expected),
                "actual_count": len(actual),
                "missing_count": len(missing),
                "extra_count": len(extra),
            }
        )
        coverage_blockers.extend(f"{name}: missing {item}" for item in missing[:20])
        coverage_blockers.extend(f"{name}: extra {item}" for item in extra[:20])
    checks.append(
        check(
            "PASS" if not coverage_blockers else "CHECK",
            "todo_rows_cover_blocking_field_groups",
            "Per-topic todo CSVs must cover all blocking field groups. Marker scalar fields are intentionally grouped as one B/T/K/P row.",
            json.dumps(coverage_evidence, ensure_ascii=False),
            coverage_blockers[:80],
        )
    )

    blank_value_issues: list[str] = []
    for filename in EXPECTED_TODO_HEADERS:
        if filename == "field_tasks.csv" or filename not in csv_data:
            continue
        for row_idx, row in enumerate(csv_data[filename]["rows"], start=2):
            for column in ["source_category", "source_detail"]:
                if row.get(column, "").strip():
                    blank_value_issues.append(f"{filename}:{row_idx}:{column}")
    checks.append(
        check(
            "PASS" if not blank_value_issues else "CHECK",
            "todo_rows_are_unfilled",
            "Generated .todo.csv files must remain blank for user-supplied source tags until real data are copied into importer schema files.",
            f"nonblank_source_cells={len(blank_value_issues)}",
            blank_value_issues[:80],
        )
    )

    acceptable = set(request_pack.get("acceptable_source_categories", []))
    forbidden = {"synthetic_test_fixture", "engineering_assumption", "implementation_proxy", "missing_required", "to_verify"} & acceptable
    checks.append(
        check(
            "PASS" if not forbidden else "CHECK",
            "acceptable_sources_are_strict",
            "Request pack acceptable source categories must exclude synthetic fixtures and assumptions.",
            f"acceptable={sorted(acceptable)}",
            sorted(forbidden),
        )
    )

    current_papers_can_fill_count = sum(1 for row in task_rows if str(row.get("current_papers_can_fill", "")).lower() == "true")
    checks.append(
        check(
            "PASS" if current_papers_can_fill_count == 0 else "CHECK",
            "current_papers_not_used_to_fill_strict_blockers",
            "The request pack must preserve the gap-tracker conclusion that current papers cannot directly fill strict real-mechanism blockers.",
            f"current_papers_can_fill_count={current_papers_can_fill_count}",
            [row.get("path", "") for row in task_rows if str(row.get("current_papers_can_fill", "")).lower() == "true"][:80],
        )
    )

    blocking_checks = [row for row in checks if row["status"] != "PASS"]
    return {
        "lint_id": "ChronoRealLegMechanismDataRequestPackLint",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overall_status": "pass" if not blocking_checks else "check",
        "pass": not blocking_checks,
        "request_pack_json": rel(REQUEST_JSON),
        "gap_tracker_json": rel(GAP_JSON),
        "request_dir": rel(request_dir),
        "summary": {
            "check_count": len(checks),
            "passing_check_count": sum(1 for row in checks if row["status"] == "PASS"),
            "blocking_check_count": len(blocking_checks),
            "blocking_field_count": len(blocker_paths),
            "field_task_count": len(task_rows),
            "todo_file_count": sum(1 for name in EXPECTED_TODO_HEADERS if name.endswith(".todo.csv")),
        },
        "checks": checks,
        "blocking_checks": blocking_checks,
        "coverage_evidence": coverage_evidence,
    }


def write_markdown(lint: dict[str, Any]) -> None:
    lines = [
        "# Chrono Real Leg Mechanism Data Request Pack Lint",
        "",
        f"- Overall status: `{lint['overall_status']}`",
        f"- Pass: `{lint['pass']}`",
        f"- Generated UTC: `{lint['generated_utc']}`",
        f"- Request dir: `{lint['request_dir']}`",
        f"- Checks: `{lint['summary']['passing_check_count']}/{lint['summary']['check_count']}`",
        "",
        "## Checks",
        "",
        "| ID | Status | Evidence | Blockers |",
        "| --- | --- | --- | --- |",
    ]
    for row in lint["checks"]:
        blockers = ", ".join(row.get("blockers", [])[:12])
        if len(row.get("blockers", [])) > 12:
            blockers += f", ... {len(row['blockers']) - 12} more"
        evidence = str(row["evidence"]).replace("|", "\\|")
        blockers = blockers.replace("|", "\\|")
        lines.append(f"| `{row['id']}` | **{row['status']}** | {evidence} | {blockers} |")
    lines.extend(["", "## Coverage", "", "| Group | Expected | Actual | Missing | Extra |", "| --- | ---: | ---: | ---: | ---: |"])
    for row in lint["coverage_evidence"]:
        lines.append(
            f"| `{row['name']}` | {row['expected_count']} | {row['actual_count']} | {row['missing_count']} | {row['extra_count']} |"
        )
    LINT_MD.parent.mkdir(parents=True, exist_ok=True)
    LINT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_js(lint: dict[str, Any]) -> None:
    LINT_JS.parent.mkdir(parents=True, exist_ok=True)
    LINT_JS.write_text(
        "window.LEG_MECHANISM_DATA_REQUEST_LINT = "
        + json.dumps(lint, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint the real landing-leg data request pack before it is used for CAD/Adams data collection.")
    parser.add_argument("command", choices=["lint", "report"], nargs="?", default="lint")
    args = parser.parse_args()

    lint = build_lint()
    write_json(LINT_JSON, lint)
    write_markdown(lint)
    write_js(lint)
    print(f"Overall: {lint['overall_status']}")
    print(f"Pass: {lint['pass']}")
    print(f"Checks: {lint['summary']['passing_check_count']}/{lint['summary']['check_count']}")
    print(f"Lint JSON: {LINT_JSON}")
    print(f"Lint MD: {LINT_MD}")
    print(f"Lint JS: {LINT_JS}")
    if args.command == "report":
        print("Open: http://127.0.0.1:8765/leg-mechanism-data-request-lint.html")


if __name__ == "__main__":
    main()
