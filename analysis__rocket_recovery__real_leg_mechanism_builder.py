from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from .leg_mechanism_data_contract import TEMPLATE_JSON
    from .leg_mechanism_data_validator import build_validation, is_value_record, marker_xyz, raw_value
except ImportError:
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from leg_mechanism_data_contract import TEMPLATE_JSON
    from leg_mechanism_data_validator import build_validation, is_value_record, marker_xyz, raw_value


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
BUILDER_JSON = CASE_ROOT / "real-leg-mechanism-builder-gate.json"
BUILDER_MD = ROOT / "docs" / "real-leg-mechanism-builder.md"
BUILDER_JS = VISUALIZATION_DIR / "real-leg-mechanism-builder-data.js"
REAL_CONFIG_JSON = CASE_ROOT / "Input" / "chrono_real_leg_mechanism_config.json"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def unwrap(node: Any) -> Any:
    if is_value_record(node):
        return node.get("value")
    if isinstance(node, dict):
        return {key: unwrap(value) for key, value in node.items()}
    if isinstance(node, list):
        return [unwrap(value) for value in node]
    return node


def source_map(node: Any, path: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if is_value_record(node):
        rows.append(
            {
                "path": path,
                "source_category": node.get("source_category"),
                "source_detail": node.get("source_detail"),
                "unit": node.get("unit"),
                "required_for": node.get("required_for", []),
            }
        )
    elif isinstance(node, dict):
        for key, value in node.items():
            rows.extend(source_map(value, f"{path}.{key}" if path else str(key)))
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            rows.extend(source_map(value, f"{path}[{idx}]"))
    return rows


def build_real_config(
    template: dict[str, Any],
    validation: dict[str, Any],
    source_template_path: Path,
    validation_source_path: Path,
) -> dict[str, Any]:
    legs: list[dict[str, Any]] = []
    for leg in template.get("legs", []):
        markers = {name: marker_xyz(leg, name) for name in ("B", "T", "K", "P")}
        topology = leg.get("constraint_topology", {})
        legs.append(
            {
                "id": leg.get("id"),
                "azimuth_deg": raw_value(leg.get("azimuth_deg")),
                "markers_body_frame_m": {
                    key: list(value) if value is not None else None
                    for key, value in markers.items()
                },
                "published_plane_dimensions": unwrap(leg.get("published_plane_dimensions", {})),
                "joint_topology": unwrap(topology),
                "body_properties": unwrap(leg.get("body_properties", {})),
            }
        )

    return {
        "schema_id": "ChronoRealLegMechanismConfig/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_template": rel(source_template_path.resolve()),
        "validation_source": rel(validation_source_path.resolve()),
        "builder_policy": {
            "requires_validator_ready": True,
            "source_categories_preserved": True,
            "no_proxy_fallback": True,
            "synthetic_fixture_allowed_only_for_selftest": validation.get("validation_mode") == "synthetic_selftest",
        },
        "coordinate_system": unwrap(template.get("coordinate_system", {})),
        "rocket": unwrap(template.get("rocket", {})),
        "landing_conditions": unwrap(template.get("landing_conditions", {})),
        "legs": legs,
        "buffer_law": unwrap(template.get("buffer_law", {})),
        "lock_hardware": unwrap(template.get("lock_hardware", {})),
        "source_map": source_map(template),
        "validation_summary": validation.get("summary", {}),
    }


def build_gate(
    input_path: Path = TEMPLATE_JSON,
    output_path: Path = REAL_CONFIG_JSON,
    write_config: bool = True,
    allow_synthetic: bool = False,
    validation_source_path: Path = BUILDER_JSON,
) -> dict[str, Any]:
    template = read_json(input_path)
    validation = build_validation(input_path, allow_synthetic=allow_synthetic)
    ready = bool(validation.get("ready"))
    config = build_real_config(template, validation, input_path, validation_source_path) if ready else None
    resolved_output = output_path.resolve()
    production_output = REAL_CONFIG_JSON.resolve()
    synthetic_production_block = allow_synthetic and resolved_output == production_output

    config_written = False
    if ready and write_config and config and not synthetic_production_block:
        write_json(resolved_output, config)
        config_written = True
    if ready and synthetic_production_block:
        overall_status = "blocked_by_synthetic_output_policy"
    elif config_written:
        overall_status = "ready_config_written"
    else:
        overall_status = "blocked_by_data_validation"

    return {
        "builder_id": "ChronoRealLegMechanismBuilderGate",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "builder_mode": "synthetic_selftest" if allow_synthetic else "strict_real_data",
        "input_path": rel(input_path.resolve()),
        "overall_status": overall_status,
        "ready": ready,
        "config_path": rel(resolved_output),
        "config_written": config_written,
        "validation_summary": validation.get("summary", {}),
        "blocking_checks": validation.get("blocking_checks", []),
        "blocking_fields": validation.get("blocking_fields", [])[:120],
        "policy": {
            "default_behavior": "Do not generate a runnable real-leg Chrono config unless validator.ready is true.",
            "synthetic_output_policy": "Synthetic fixtures may be built only to explicit non-production output paths.",
            "current_fallback": "Continue using Stage 3A proxy and Stage 3B/3C diagnostic branches.",
            "not_a_solver": "This builder only assembles validated real mechanism data; it does not run Chrono by itself.",
        },
        "would_build_sections_when_ready": [
            "coordinate_system",
            "rocket",
            "landing_conditions",
            "legs[].markers_body_frame_m",
            "legs[].joint_topology",
            "legs[].body_properties",
            "buffer_law",
            "lock_hardware",
            "source_map",
        ],
    }


def write_builder_markdown(gate: dict[str, Any]) -> None:
    lines = [
        "# Chrono Real Leg Mechanism Builder Gate",
        "",
        f"- Overall status: `{gate['overall_status']}`",
        f"- Ready: `{gate['ready']}`",
        f"- Builder mode: `{gate.get('builder_mode', 'strict_real_data')}`",
        f"- Input: `{gate['input_path']}`",
        f"- Target config: `{gate['config_path']}`",
        f"- Config written: `{gate['config_written']}`",
        f"- Generated UTC: `{gate['generated_utc']}`",
        "",
        "## Policy",
        "",
        gate["policy"]["default_behavior"],
        "",
        "## Blocking Checks",
        "",
        "| ID | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for row in gate["blocking_checks"]:
        lines.append(
            "| {id} | **{status}** | {evidence} |".format(
                id=row.get("id"),
                status=row.get("status"),
                evidence=str(row.get("evidence", "")).replace("|", "\\|"),
            )
        )
    lines.extend(["", "## Output Sections When Ready", ""])
    for section in gate["would_build_sections_when_ready"]:
        lines.append(f"- `{section}`")
    BUILDER_MD.parent.mkdir(parents=True, exist_ok=True)
    BUILDER_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_builder_js(gate: dict[str, Any]) -> None:
    BUILDER_JS.parent.mkdir(parents=True, exist_ok=True)
    BUILDER_JS.write_text(
        "window.REAL_LEG_MECHANISM_BUILDER_GATE = "
        + json.dumps(gate, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Gate generation of a real Chrono landing-leg mechanism config on validated CAD/Adams-quality data.")
    parser.add_argument("command", choices=["gate", "report"], nargs="?", default="gate")
    parser.add_argument("--input", type=Path, default=TEMPLATE_JSON)
    parser.add_argument("--output", type=Path, default=REAL_CONFIG_JSON)
    parser.add_argument("--no-write-config", action="store_true", help="Do not write the real config even if validation is ready.")
    parser.add_argument("--allow-synthetic", action="store_true", help="Accept synthetic_test_fixture source tags for importer/builder self-tests only.")
    args = parser.parse_args()

    gate = build_gate(
        args.input.resolve(),
        output_path=args.output.resolve(),
        write_config=not args.no_write_config,
        allow_synthetic=args.allow_synthetic,
    )
    write_json(BUILDER_JSON, gate)
    write_builder_markdown(gate)
    write_builder_js(gate)

    print(f"Ready: {gate['ready']}")
    print(f"Overall: {gate['overall_status']}")
    print(f"Config written: {gate['config_written']}")
    print(f"Builder JSON: {BUILDER_JSON}")
    print(f"Builder MD: {BUILDER_MD}")
    print(f"Builder JS: {BUILDER_JS}")
    if args.command == "report":
        print("Open: http://127.0.0.1:8765/real-leg-mechanism-builder.html")


if __name__ == "__main__":
    main()
