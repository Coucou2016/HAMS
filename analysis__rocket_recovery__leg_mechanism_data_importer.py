from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from .leg_mechanism_data_contract import ADAMS_GATE, TEMPLATE_JSON
except ImportError:
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from leg_mechanism_data_contract import ADAMS_GATE, TEMPLATE_JSON


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
SCHEMA_DIR = CASE_ROOT / "Input" / "leg_mechanism_import_schema"
DEFAULT_OUTPUT_TEMPLATE = CASE_ROOT / "Input" / "leg_mechanism_data_imported.json"
IMPORT_REPORT_JSON = CASE_ROOT / "leg-mechanism-data-import-report.json"
IMPORT_REPORT_MD = ROOT / "docs" / "leg-mechanism-data-import.md"
IMPORT_REPORT_JS = VISUALIZATION_DIR / "leg-mechanism-import-data.js"

SCHEMA_FILES = {
    "coordinate_system.csv": ["field", "value_json", "source_category", "source_detail"],
    "leg_azimuths.csv": ["leg_id", "azimuth_deg", "source_category", "source_detail"],
    "marker_coordinates.csv": ["leg_id", "marker", "x_m", "y_m", "z_m", "source_category", "source_detail"],
    "constraint_topology.csv": ["leg_id", "field", "value_json", "source_category", "source_detail"],
    "body_properties.csv": ["leg_id", "body", "field", "value_json", "unit", "source_category", "source_detail"],
    "buffer_lock.csv": ["section", "field", "value_json", "unit", "source_category", "source_detail"],
}

ALLOWED_MARKERS = {"B", "T", "K", "P"}
MARKER_NODE = {
    "B": "B_rocket_marker_xyz_m",
    "T": "T_rocket_marker_xyz_m",
    "K": "K_rocket_marker_xyz_m",
    "P": "P_footpad_marker_xyz_m",
}
ALLOWED_TOPOLOGY_FIELDS = {"B_joint_type", "T_joint_type", "K_joint_type", "P_joint_type", "absorber_slider_axis_xyz", "joint_limit_definitions"}
ALLOWED_BODY_FIELDS = {"mass_kg", "com_xyz_m", "inertia_kg_m2"}
ALLOWED_BUFFER_LOCK_SECTIONS = {"buffer_law", "lock_hardware"}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def parse_value(text: str) -> Any:
    stripped = (text or "").strip()
    if stripped == "":
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    try:
        return float(stripped)
    except ValueError:
        return stripped


def required(row: dict[str, str], key: str) -> str:
    value = (row.get(key) or "").strip()
    if value == "":
        raise ValueError(f"missing required column value: {key}")
    return value


def update_record(record: dict[str, Any], value: Any, source_category: str, source_detail: str, unit: str | None = None) -> None:
    if "required_for" not in record:
        record["required_for"] = [ADAMS_GATE]
    record["value"] = value
    if unit is not None and unit != "":
        record["unit"] = unit
    record["source_category"] = source_category
    record["source_detail"] = source_detail


def write_schema_files(schema_dir: Path = SCHEMA_DIR) -> dict[str, Any]:
    schema_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[dict[str, Any]] = []
    for filename, header in SCHEMA_FILES.items():
        path = schema_dir / filename
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
        outputs.append({"path": rel(path), "columns": header})
    readme = schema_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Leg Mechanism Import Schema",
                "",
                "Fill these CSV files only with CAD, Adams export, author data, calibrated engineering data, or measured data.",
                "Do not use the current proxy assumptions as imported data.",
                "",
                "Accepted source categories for validator-ready fields include:",
                "`paper`, `cad_export`, `adams_export`, `author_data`, `measured`, `calibrated`, `computed_from_source`, `engineering_data`.",
                "",
                "Run:",
                "",
                "```powershell",
                r".\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_importer.py import --source-dir .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_import_schema",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {"schema_dir": rel(schema_dir), "files": outputs, "readme": rel(readme)}


def read_csv_if_exists(source_dir: Path, filename: str) -> list[dict[str, str]]:
    path = source_dir / filename
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def find_leg(template: dict[str, Any], leg_id: str) -> dict[str, Any]:
    for leg in template.get("legs", []):
        if leg.get("id") == leg_id:
            return leg
    raise ValueError(f"unknown leg_id: {leg_id}")


def apply_coordinate_rows(template: dict[str, Any], rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    target = template.get("coordinate_system", {})
    for row in rows:
        field = required(row, "field")
        if field not in target:
            raise ValueError(f"unknown coordinate_system field: {field}")
        update_record(
            target[field],
            parse_value(required(row, "value_json")),
            required(row, "source_category"),
            required(row, "source_detail"),
        )
        changes.append({"file": "coordinate_system.csv", "field": f"coordinate_system.{field}"})
    return changes


def apply_azimuth_rows(template: dict[str, Any], rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for row in rows:
        leg_id = required(row, "leg_id")
        leg = find_leg(template, leg_id)
        update_record(
            leg["azimuth_deg"],
            float(required(row, "azimuth_deg")),
            required(row, "source_category"),
            required(row, "source_detail"),
            "deg",
        )
        changes.append({"file": "leg_azimuths.csv", "field": f"{leg_id}.azimuth_deg"})
    return changes


def apply_marker_rows(template: dict[str, Any], rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for row in rows:
        leg_id = required(row, "leg_id")
        marker = required(row, "marker").upper()
        if marker not in ALLOWED_MARKERS:
            raise ValueError(f"unknown marker {marker}; expected one of {sorted(ALLOWED_MARKERS)}")
        leg = find_leg(template, leg_id)
        node = leg["adams_equivalent_geometry"][MARKER_NODE[marker]]
        source_category = required(row, "source_category")
        source_detail = required(row, "source_detail")
        for axis, column in [("x", "x_m"), ("y", "y_m"), ("z", "z_m")]:
            update_record(node[axis], float(required(row, column)), source_category, source_detail, "m")
        changes.append({"file": "marker_coordinates.csv", "field": f"{leg_id}.{marker}_marker_xyz_m"})
    return changes


def apply_topology_rows(template: dict[str, Any], rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for row in rows:
        leg_id = required(row, "leg_id")
        field = required(row, "field")
        if field not in ALLOWED_TOPOLOGY_FIELDS:
            raise ValueError(f"unknown topology field: {field}")
        leg = find_leg(template, leg_id)
        update_record(
            leg["constraint_topology"][field],
            parse_value(required(row, "value_json")),
            required(row, "source_category"),
            required(row, "source_detail"),
        )
        changes.append({"file": "constraint_topology.csv", "field": f"{leg_id}.constraint_topology.{field}"})
    return changes


def apply_body_rows(template: dict[str, Any], rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for row in rows:
        leg_id = required(row, "leg_id")
        body = required(row, "body")
        field = required(row, "field")
        if field not in ALLOWED_BODY_FIELDS:
            raise ValueError(f"unknown body field: {field}")
        leg = find_leg(template, leg_id)
        body_node = leg.get("body_properties", {}).get(body)
        if not isinstance(body_node, dict):
            raise ValueError(f"unknown body {body} for {leg_id}")
        update_record(
            body_node[field],
            parse_value(required(row, "value_json")),
            required(row, "source_category"),
            required(row, "source_detail"),
            row.get("unit"),
        )
        changes.append({"file": "body_properties.csv", "field": f"{leg_id}.body_properties.{body}.{field}"})
    return changes


def apply_buffer_lock_rows(template: dict[str, Any], rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for row in rows:
        section = required(row, "section")
        field = required(row, "field")
        if section not in ALLOWED_BUFFER_LOCK_SECTIONS:
            raise ValueError(f"unknown section {section}; expected one of {sorted(ALLOWED_BUFFER_LOCK_SECTIONS)}")
        target = template.get(section, {})
        if field not in target:
            raise ValueError(f"unknown field {section}.{field}")
        update_record(
            target[field],
            parse_value(required(row, "value_json")),
            required(row, "source_category"),
            required(row, "source_detail"),
            row.get("unit"),
        )
        changes.append({"file": "buffer_lock.csv", "field": f"{section}.{field}"})
    return changes


def import_from_csv(
    source_dir: Path,
    template_path: Path = TEMPLATE_JSON,
    output_path: Path = DEFAULT_OUTPUT_TEMPLATE,
) -> dict[str, Any]:
    template = read_json(template_path)
    changes: list[dict[str, Any]] = []
    changes.extend(apply_coordinate_rows(template, read_csv_if_exists(source_dir, "coordinate_system.csv")))
    changes.extend(apply_azimuth_rows(template, read_csv_if_exists(source_dir, "leg_azimuths.csv")))
    changes.extend(apply_marker_rows(template, read_csv_if_exists(source_dir, "marker_coordinates.csv")))
    changes.extend(apply_topology_rows(template, read_csv_if_exists(source_dir, "constraint_topology.csv")))
    changes.extend(apply_body_rows(template, read_csv_if_exists(source_dir, "body_properties.csv")))
    changes.extend(apply_buffer_lock_rows(template, read_csv_if_exists(source_dir, "buffer_lock.csv")))
    write_json(output_path, template)
    return {
        "import_id": "ChronoLegMechanismDataImport",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_dir": rel(source_dir.resolve()),
        "template_path": rel(template_path.resolve()),
        "output_path": rel(output_path.resolve()),
        "change_count": len(changes),
        "changes": changes,
        "next_commands": [
            rf".\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_validator.py report --input {rel(output_path.resolve())}",
            rf".\.tools\chrono-env\python.exe .\analysis\rocket_recovery\real_leg_mechanism_builder.py report --input {rel(output_path.resolve())}",
        ],
        "note": "The importer only transfers externally supplied data into the template shape; validator and builder gate remain authoritative.",
    }


def build_schema_report(schema_dir: Path = SCHEMA_DIR) -> dict[str, Any]:
    schema = write_schema_files(schema_dir)
    return {
        "import_id": "ChronoLegMechanismImportSchema",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": "schema_only",
        "schema": schema,
        "change_count": 0,
        "output_path": None,
        "note": "Empty CSV schema files were written. No model template values were changed.",
    }


def write_report_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Chrono Leg Mechanism Data Import",
        "",
        f"- Mode: `{report.get('mode', 'import')}`",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Change count: `{report.get('change_count', 0)}`",
        f"- Output: `{report.get('output_path')}`",
        "",
        report.get("note", ""),
        "",
        "## Schema Files",
        "",
    ]
    for row in report.get("schema", {}).get("files", []):
        lines.append(f"- `{row['path']}`: {', '.join(row['columns'])}")
    if report.get("changes"):
        lines.extend(["", "## Changes", ""])
        for row in report["changes"]:
            lines.append(f"- `{row['file']}` -> `{row['field']}`")
    IMPORT_REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    IMPORT_REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report_js(report: dict[str, Any]) -> None:
    IMPORT_REPORT_JS.parent.mkdir(parents=True, exist_ok=True)
    IMPORT_REPORT_JS.write_text(
        "window.LEG_MECHANISM_IMPORT_REPORT = "
        + json.dumps(report, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Import CAD/Adams leg-mechanism CSV data into the Chrono leg mechanism template.")
    parser.add_argument("command", choices=["schema", "import", "report"], nargs="?", default="schema")
    parser.add_argument("--source-dir", type=Path, default=SCHEMA_DIR)
    parser.add_argument("--template", type=Path, default=TEMPLATE_JSON)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_TEMPLATE)
    args = parser.parse_args()

    if args.command in {"schema", "report"}:
        report = build_schema_report(args.source_dir.resolve())
    else:
        report = import_from_csv(args.source_dir.resolve(), args.template.resolve(), args.output.resolve())
    write_json(IMPORT_REPORT_JSON, report)
    write_report_markdown(report)
    write_report_js(report)

    print(f"Mode: {report.get('mode', 'import')}")
    print(f"Change count: {report.get('change_count', 0)}")
    print(f"Import report JSON: {IMPORT_REPORT_JSON}")
    print(f"Import report MD: {IMPORT_REPORT_MD}")
    print(f"Import report JS: {IMPORT_REPORT_JS}")
    if args.command == "report":
        print("Open: http://127.0.0.1:8765/leg-mechanism-import.html")
    if args.command == "import":
        print(f"Imported template: {report['output_path']}")


if __name__ == "__main__":
    main()
