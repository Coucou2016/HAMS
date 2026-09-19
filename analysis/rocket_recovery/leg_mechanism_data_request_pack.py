from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from .leg_mechanism_data_contract import TEMPLATE_JSON
    from .leg_mechanism_gap_tracker import GAP_JSON
except ImportError:
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from leg_mechanism_data_contract import TEMPLATE_JSON
    from leg_mechanism_gap_tracker import GAP_JSON


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
REQUEST_DIR = CASE_ROOT / "Input" / "leg_mechanism_data_request_pack"
REQUEST_JSON = CASE_ROOT / "leg-mechanism-data-request-pack.json"
REQUEST_MD = ROOT / "docs" / "leg-mechanism-data-request-pack.md"
REQUEST_JS = VISUALIZATION_DIR / "leg-mechanism-data-request-pack-data.js"

LEG_RE = re.compile(r"legs\[(\d+)\]")
MARKER_RE = re.compile(r"\.adams_equivalent_geometry\.([BTKP])_")
BODY_RE = re.compile(r"\.body_properties\.([^.]+)\.([^.]+)$")
TOPO_RE = re.compile(r"\.constraint_topology\.([^.]+)$")

ACCEPTABLE_SOURCE_CATEGORIES = [
    "cad_export",
    "adams_export",
    "author_data",
    "measured",
    "calibrated",
    "paper",
    "computed_from_source",
    "engineering_data",
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def leg_id_from_path(path: str) -> str:
    match = LEG_RE.search(path)
    if not match:
        return ""
    return f"leg_{int(match.group(1)) + 1}"


def value_record_value(node: Any) -> Any:
    if isinstance(node, dict) and "value" in node:
        return node.get("value")
    return node


def get_nested(node: Any, parts: list[str]) -> Any:
    value = node
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


def marker_template_row(template: dict[str, Any], leg_id: str, marker: str) -> dict[str, Any]:
    leg_index = int(leg_id.split("_")[-1]) - 1
    marker_key = {
        "B": "B_rocket_marker_xyz_m",
        "T": "T_rocket_marker_xyz_m",
        "K": "K_rocket_marker_xyz_m",
        "P": "P_footpad_marker_xyz_m",
    }[marker]
    node = template["legs"][leg_index]["adams_equivalent_geometry"][marker_key]
    current = {axis: value_record_value(node.get(axis)) for axis in ("x", "y", "z")}
    return {
        "leg_id": leg_id,
        "marker": marker,
        "x_m": "",
        "y_m": "",
        "z_m": "",
        "source_category": "",
        "source_detail": "",
        "current_template_x_m": current["x"],
        "current_template_y_m": current["y"],
        "current_template_z_m": current["z"],
        "required_source": "CAD/Adams marker export for B/T/K/P in a declared rocket body frame",
        "note": "Fill all x/y/z from the same coordinate frame. Do not reuse proxy footprint coordinates.",
    }


def source_detail_for(field_class: str) -> str:
    return {
        "coordinate_system": "CAD/Adams frame export or author frame metadata",
        "azimuths": "CAD/Adams leg layout export or published four-leg azimuth table",
        "marker_coordinates": "CAD/Adams marker export for B/T/K/P in a declared rocket body frame",
        "constraint_topology": "Adams constraint graph, CAD mate definitions, or author topology table",
        "body_properties": "CAD mass-property export or validated component mass budget",
        "buffer_lock": "absorber hardware specification and lock hardware data",
    }.get(field_class, "manual review")


def write_csv(path: Path, rows: list[dict[str, Any]], headers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def build_request_pack() -> dict[str, Any]:
    gap = read_json(GAP_JSON)
    template = read_json(TEMPLATE_JSON)
    blockers = gap.get("blocking_fields", [])

    field_tasks: list[dict[str, Any]] = []
    for idx, row in enumerate(blockers, start=1):
        field_tasks.append(
            {
                "task_id": f"LEGDATA-{idx:03d}",
                "priority": row.get("priority", "P2"),
                "field_class": row.get("field_class"),
                "path": row.get("path"),
                "target_csv": row.get("csv_file"),
                "current_source_category": row.get("source_category"),
                "current_value": row.get("value"),
                "required_source": row.get("needed_source"),
                "acceptable_source_categories": ";".join(ACCEPTABLE_SOURCE_CATEGORIES),
                "current_papers_can_fill": row.get("current_papers_can_fill_without_new_assumption"),
                "note": "Use a traceable non-synthetic source. Leave blank until real source data are available.",
            }
        )

    coordinate_rows = []
    azimuth_rows = []
    marker_group_keys: set[tuple[str, str]] = set()
    topology_rows = []
    body_rows = []
    buffer_lock_rows = []

    for row in blockers:
        path = str(row["path"])
        field_class = row.get("field_class")
        if field_class == "coordinate_system":
            coordinate_rows.append(
                {
                    "field": path.split(".")[-1],
                    "value_json": "",
                    "source_category": "",
                    "source_detail": "",
                    "required_source": source_detail_for("coordinate_system"),
                    "note": row.get("source_detail", ""),
                }
            )
        elif field_class == "azimuths":
            azimuth_rows.append(
                {
                    "leg_id": leg_id_from_path(path),
                    "azimuth_deg": "",
                    "source_category": "",
                    "source_detail": "",
                    "current_template_azimuth_deg": row.get("value"),
                    "required_source": source_detail_for("azimuths"),
                    "note": "Replace symmetric proxy azimuth with source data.",
                }
            )
        elif field_class == "marker_coordinates":
            leg_id = leg_id_from_path(path)
            marker_match = MARKER_RE.search(path)
            if leg_id and marker_match:
                marker_group_keys.add((leg_id, marker_match.group(1)))
        elif field_class == "constraint_topology":
            topo_match = TOPO_RE.search(path)
            topology_rows.append(
                {
                    "leg_id": leg_id_from_path(path),
                    "field": topo_match.group(1) if topo_match else "",
                    "value_json": "",
                    "source_category": "",
                    "source_detail": "",
                    "required_source": source_detail_for("constraint_topology"),
                    "note": row.get("source_detail", ""),
                }
            )
        elif field_class == "body_properties":
            body_match = BODY_RE.search(path)
            body = body_match.group(1) if body_match else ""
            field = body_match.group(2) if body_match else ""
            body_rows.append(
                {
                    "leg_id": leg_id_from_path(path),
                    "body": body,
                    "field": field,
                    "value_json": "",
                    "unit": row.get("unit") or "",
                    "source_category": "",
                    "source_detail": "",
                    "required_source": source_detail_for("body_properties"),
                    "note": row.get("source_detail", ""),
                }
            )
        elif field_class == "buffer_lock":
            section, field = path.split(".", 1)
            buffer_lock_rows.append(
                {
                    "section": section,
                    "field": field,
                    "value_json": "",
                    "unit": row.get("unit") or "",
                    "source_category": "",
                    "source_detail": "",
                    "required_source": source_detail_for("buffer_lock"),
                    "note": row.get("source_detail", ""),
                }
            )

    marker_rows = [
        marker_template_row(template, leg_id, marker)
        for leg_id, marker in sorted(marker_group_keys, key=lambda item: (item[0], item[1]))
    ]

    files = [
        {
            "name": "field_tasks.csv",
            "path": REQUEST_DIR / "field_tasks.csv",
            "rows": field_tasks,
            "headers": [
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
            "purpose": "Master task list for every strict blocking field.",
        },
        {
            "name": "coordinate_system.todo.csv",
            "path": REQUEST_DIR / "coordinate_system.todo.csv",
            "rows": coordinate_rows,
            "headers": ["field", "value_json", "source_category", "source_detail", "required_source", "note"],
            "purpose": "Fill with rocket/deck frame metadata, then copy validated rows into coordinate_system.csv.",
        },
        {
            "name": "leg_azimuths.todo.csv",
            "path": REQUEST_DIR / "leg_azimuths.todo.csv",
            "rows": azimuth_rows,
            "headers": ["leg_id", "azimuth_deg", "source_category", "source_detail", "current_template_azimuth_deg", "required_source", "note"],
            "purpose": "Fill with real four-leg azimuths.",
        },
        {
            "name": "marker_coordinates.todo.csv",
            "path": REQUEST_DIR / "marker_coordinates.todo.csv",
            "rows": marker_rows,
            "headers": [
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
            "purpose": "Fill with B/T/K/P marker coordinates from one declared frame.",
        },
        {
            "name": "constraint_topology.todo.csv",
            "path": REQUEST_DIR / "constraint_topology.todo.csv",
            "rows": topology_rows,
            "headers": ["leg_id", "field", "value_json", "source_category", "source_detail", "required_source", "note"],
            "purpose": "Fill with joint types, axes, limits, and slider definitions.",
        },
        {
            "name": "body_properties.todo.csv",
            "path": REQUEST_DIR / "body_properties.todo.csv",
            "rows": body_rows,
            "headers": ["leg_id", "body", "field", "value_json", "unit", "source_category", "source_detail", "required_source", "note"],
            "purpose": "Fill with CAD mass, COM, and inertia tensors.",
        },
        {
            "name": "buffer_lock.todo.csv",
            "path": REQUEST_DIR / "buffer_lock.todo.csv",
            "rows": buffer_lock_rows,
            "headers": ["section", "field", "value_json", "unit", "source_category", "source_detail", "required_source", "note"],
            "purpose": "Fill with absorber stroke/rebound behavior and lock hardware data.",
        },
    ]

    for spec in files:
        write_csv(spec["path"], spec["rows"], spec["headers"])
    write_jsonl(REQUEST_DIR / "field_tasks.jsonl", field_tasks)

    readme_lines = [
        "# Chrono Real Leg Mechanism Data Request Pack",
        "",
        "These files are a data-acquisition checklist. They are not imported automatically.",
        "Copy completed and source-tagged rows into `Input/leg_mechanism_import_schema/*.csv` only after the source data are available.",
        "",
        "Accepted source categories:",
        ", ".join(f"`{item}`" for item in ACCEPTABLE_SOURCE_CATEGORIES),
        "",
        "Do not use `synthetic_test_fixture`, `engineering_assumption`, `implementation_proxy`, or blank source tags for strict validation.",
    ]
    for spec in files:
        readme_lines.append(f"- `{spec['name']}`: {spec['purpose']} rows={len(spec['rows'])}")
    (REQUEST_DIR / "README.md").write_text("\n".join(readme_lines) + "\n", encoding="utf-8")

    counts_by_file = {spec["name"]: len(spec["rows"]) for spec in files}
    counts_by_class: dict[str, int] = defaultdict(int)
    for task in field_tasks:
        counts_by_class[str(task["field_class"])] += 1

    return {
        "request_pack_id": "ChronoRealLegMechanismDataRequestPack",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overall_status": "todo_pack_written_no_model_data_changed",
        "request_dir": rel(REQUEST_DIR),
        "source_gap_report": rel(GAP_JSON),
        "source_template": rel(TEMPLATE_JSON),
        "strict_blocking_field_count": len(field_tasks),
        "todo_file_count": len(files),
        "counts_by_file": counts_by_file,
        "counts_by_field_class": dict(sorted(counts_by_class.items())),
        "acceptable_source_categories": ACCEPTABLE_SOURCE_CATEGORIES,
        "files": [
            {
                "name": spec["name"],
                "path": rel(spec["path"]),
                "row_count": len(spec["rows"]),
                "purpose": spec["purpose"],
            }
            for spec in files
        ]
        + [
            {
                "name": "field_tasks.jsonl",
                "path": rel(REQUEST_DIR / "field_tasks.jsonl"),
                "row_count": len(field_tasks),
                "purpose": "Line-delimited machine-readable copy of the master task list.",
            },
            {
                "name": "README.md",
                "path": rel(REQUEST_DIR / "README.md"),
                "row_count": None,
                "purpose": "Human instructions for using the request pack.",
            },
        ],
        "next_commands_after_filling": [
            r".\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_importer.py import --source-dir .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_import_schema",
            r".\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_validator.py report --input .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_data_imported.json",
            r".\.tools\chrono-env\python.exe .\analysis\rocket_recovery\real_leg_mechanism_builder.py report --input .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_data_imported.json",
        ],
        "guardrails": [
            "The .todo.csv files are intentionally not named like importer inputs.",
            "Blank or synthetic source tags must not pass strict validation.",
            "Current papers provide scale checks, not source-ready CAD/Adams hinge and mass-property data.",
        ],
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Chrono Real Leg Mechanism Data Request Pack",
        "",
        f"- Overall status: `{report['overall_status']}`",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Request dir: `{report['request_dir']}`",
        f"- Strict blocking fields covered: `{report['strict_blocking_field_count']}`",
        "",
        "## Files",
        "",
        "| File | Rows | Purpose |",
        "| --- | ---: | --- |",
    ]
    for row in report["files"]:
        purpose = str(row["purpose"]).replace("|", "\\|")
        row_count = row["row_count"] if row["row_count"] is not None else ""
        lines.append(f"| `{row['path']}` | {row_count} | {purpose} |")
    lines.extend(["", "## Field Classes", "", "| Class | Count |", "| --- | ---: |"])
    for key, count in report["counts_by_field_class"].items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(["", "## Guardrails", ""])
    for row in report["guardrails"]:
        lines.append(f"- {row}")
    lines.extend(["", "## Commands After Filling Real Data", "", "```powershell"])
    lines.extend(report["next_commands_after_filling"])
    lines.append("```")
    REQUEST_MD.parent.mkdir(parents=True, exist_ok=True)
    REQUEST_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_js(report: dict[str, Any]) -> None:
    REQUEST_JS.parent.mkdir(parents=True, exist_ok=True)
    REQUEST_JS.write_text(
        "window.LEG_MECHANISM_DATA_REQUEST_PACK = "
        + json.dumps(report, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a fillable request pack for real CAD/Adams landing-leg data.")
    parser.add_argument("command", choices=["report", "pack"], nargs="?", default="report")
    args = parser.parse_args()

    report = build_request_pack()
    write_json(REQUEST_JSON, report)
    write_markdown(report)
    write_js(report)
    print(f"Overall: {report['overall_status']}")
    print(f"Request dir: {REQUEST_DIR}")
    print(f"Blocking fields covered: {report['strict_blocking_field_count']}")
    print(f"Request JSON: {REQUEST_JSON}")
    print(f"Request MD: {REQUEST_MD}")
    print(f"Request JS: {REQUEST_JS}")
    if args.command == "report":
        print("Open: http://127.0.0.1:8765/leg-mechanism-data-request-pack.html")


if __name__ == "__main__":
    main()
