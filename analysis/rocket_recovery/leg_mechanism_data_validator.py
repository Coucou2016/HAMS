from __future__ import annotations

import argparse
import json
import math
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
VALIDATION_JSON = CASE_ROOT / "leg-mechanism-data-validation.json"
VALIDATION_MD = ROOT / "docs" / "leg-mechanism-data-validation.md"
VALIDATION_JS = VISUALIZATION_DIR / "leg-mechanism-validation-data.js"

BLOCKING_SOURCE_CATEGORIES = {
    "missing_required",
    "engineering_assumption",
    "implementation_assumption",
    "implementation_proxy",
    "to_verify",
}

ACCEPTABLE_READY_SOURCE_CATEGORIES = {
    "paper",
    "cad_export",
    "adams_export",
    "author_data",
    "measured",
    "calibrated",
    "computed",
    "computed_from_source",
    "engineering_data",
}
SYNTHETIC_SOURCE_CATEGORY = "synthetic_test_fixture"

GEOMETRY_TOLERANCE_M = 0.05
ANGLE_TOLERANCE_DEG = 1.0


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def is_value_record(node: Any) -> bool:
    return isinstance(node, dict) and {"value", "source_category", "source_detail", "required_for"}.issubset(node.keys())


def flatten_values(node: Any, path: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if is_value_record(node):
        rows.append({"path": path, **node})
    elif isinstance(node, dict):
        for key, child in node.items():
            rows.extend(flatten_values(child, f"{path}.{key}" if path else str(key)))
    elif isinstance(node, list):
        for idx, child in enumerate(node):
            rows.extend(flatten_values(child, f"{path}[{idx}]"))
    return rows


def check(status: str, check_id: str, description: str, evidence: str, blockers: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "description": description,
        "evidence": evidence,
        "blockers": blockers or [],
    }


def is_missing(value: Any) -> bool:
    return value is None or value == ""


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def numeric_value(record: Any) -> float | None:
    if is_value_record(record):
        value = record.get("value")
    else:
        value = record
    if finite_number(value):
        return float(value)
    return None


def raw_value(record: Any) -> Any:
    return record.get("value") if is_value_record(record) else record


def category(record: Any) -> str:
    return str(record.get("source_category", "missing_required")) if is_value_record(record) else "missing_required"


def acceptable_source_categories(allow_synthetic: bool = False) -> set[str]:
    categories = set(ACCEPTABLE_READY_SOURCE_CATEGORIES)
    if allow_synthetic:
        categories.add(SYNTHETIC_SOURCE_CATEGORY)
    return categories


def source_is_ready(record_or_row: Any, allow_synthetic: bool = False) -> bool:
    source_category = (
        str(record_or_row.get("source_category", "missing_required"))
        if isinstance(record_or_row, dict)
        else "missing_required"
    )
    source_detail = str(record_or_row.get("source_detail", "")).strip() if isinstance(record_or_row, dict) else ""
    return (
        source_category not in BLOCKING_SOURCE_CATEGORIES
        and source_category in acceptable_source_categories(allow_synthetic)
        and bool(source_detail)
    )


def marker_xyz(leg: dict[str, Any], marker: str) -> tuple[float, float, float] | None:
    geom = leg.get("adams_equivalent_geometry", {})
    node = geom.get(f"{marker}_rocket_marker_xyz_m") if marker in {"B", "T", "K"} else geom.get("P_footpad_marker_xyz_m")
    if not isinstance(node, dict):
        return None
    coords = [numeric_value(node.get(axis)) for axis in ("x", "y", "z")]
    if any(value is None for value in coords):
        return None
    return coords[0], coords[1], coords[2]  # type: ignore[return-value]


def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((aa - bb) ** 2 for aa, bb in zip(a, b)))


def vector_norm(value: Any) -> float | None:
    if is_value_record(value):
        value = value.get("value")
    if isinstance(value, dict):
        vals = [value.get(axis) for axis in ("x", "y", "z")]
    elif isinstance(value, list | tuple) and len(value) == 3:
        vals = list(value)
    else:
        return None
    if not all(finite_number(v) for v in vals):
        return None
    return math.sqrt(sum(float(v) ** 2 for v in vals))


def validate_required_fields(rows: list[dict[str, Any]], allow_synthetic: bool = False) -> dict[str, Any]:
    required_rows = [row for row in rows if ADAMS_GATE in row.get("required_for", [])]
    missing_rows = [row for row in required_rows if is_missing(row.get("value"))]
    blocking_rows = [
        row
        for row in required_rows
        if not source_is_ready(row, allow_synthetic)
    ]
    status = "PASS" if not missing_rows and not blocking_rows else "CHECK"
    mode_note = " Synthetic fixture source tags are accepted only for importer/builder self-tests." if allow_synthetic else ""
    return check(
        status,
        "required_field_sources",
        "All Adams-equivalent required fields must be populated and must not be tagged as assumptions, proxies, missing, or to-verify." + mode_note,
        f"required={len(required_rows)}, missing={len(missing_rows)}, blocking_source={len(blocking_rows)}",
        [row["path"] for row in (missing_rows + blocking_rows)[:80]],
    )


def validate_coordinate_system(template: dict[str, Any]) -> dict[str, Any]:
    coord = template.get("coordinate_system", {})
    required = ["rocket_body_origin", "rocket_body_axes", "deck_frame_transform"]
    blockers = []
    for key in required:
        record = coord.get(key)
        if is_missing(raw_value(record)) or category(record) in BLOCKING_SOURCE_CATEGORIES:
            blockers.append(f"coordinate_system.{key}")
    return check(
        "PASS" if not blockers else "MISSING",
        "coordinate_system",
        "Rocket body frame and HAMS/Cummins deck-frame transform must be defined before Chrono can build an Adams-equivalent mechanism.",
        "all coordinate-system records are usable" if not blockers else f"{len(blockers)} coordinate-system fields are missing or blocked",
        blockers,
    )


def validate_geometry(template: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    geometry_rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    legs = template.get("legs", [])
    if len(legs) != 4:
        return check("CHECK", "leg_count", "Exactly four legs are required for the current Thies-based model.", f"leg_count={len(legs)}"), geometry_rows

    for leg in legs:
        leg_id = leg.get("id", "leg")
        dims = leg.get("published_plane_dimensions", {})
        markers = {name: marker_xyz(leg, name) for name in ("B", "T", "K", "P")}
        if any(value is None for value in markers.values()):
            blockers.append(f"{leg_id}: missing B/T/K/P 3D marker coordinates")
            geometry_rows.append({"leg_id": leg_id, "status": "MISSING", "reason": "missing marker coordinates"})
            continue
        b = markers["B"]
        t = markers["T"]
        k = markers["K"]
        p = markers["P"]
        assert b and t and k and p
        checks = [
            ("PB", distance(p, b), numeric_value(dims.get("PB_length_m"))),
            ("PT", distance(p, t), numeric_value(dims.get("PT_length_m"))),
            ("PK", distance(p, k), numeric_value(dims.get("PK_length_m"))),
        ]
        errors = []
        for label, actual, target in checks:
            if target is None:
                errors.append({"id": label, "actual_m": actual, "target_m": None, "abs_error_m": None, "pass": False})
            else:
                errors.append(
                    {
                        "id": label,
                        "actual_m": actual,
                        "target_m": target,
                        "abs_error_m": abs(actual - target),
                        "pass": abs(actual - target) <= GEOMETRY_TOLERANCE_M,
                    }
                )
        azimuth_record = leg.get("azimuth_deg")
        azimuth_value = numeric_value(azimuth_record)
        px, py, _ = p
        actual_azimuth = math.degrees(math.atan2(py, px))
        if actual_azimuth < 0.0:
            actual_azimuth += 360.0
        azimuth_error = None if azimuth_value is None else abs(((actual_azimuth - azimuth_value + 180.0) % 360.0) - 180.0)
        azimuth_pass = azimuth_error is not None and azimuth_error <= ANGLE_TOLERANCE_DEG and category(azimuth_record) not in BLOCKING_SOURCE_CATEGORIES
        leg_pass = all(row["pass"] for row in errors) and azimuth_pass
        if not leg_pass:
            blockers.append(f"{leg_id}: geometry closure or azimuth source check failed")
        geometry_rows.append(
            {
                "leg_id": leg_id,
                "status": "PASS" if leg_pass else "CHECK",
                "marker_coordinates_m": {"B": b, "T": t, "K": k, "P": p},
                "length_checks": errors,
                "actual_azimuth_deg": actual_azimuth,
                "target_azimuth_deg": azimuth_value,
                "azimuth_error_deg": azimuth_error,
                "azimuth_source_category": category(azimuth_record),
                "azimuth_pass": azimuth_pass,
            }
        )
    return check(
        "PASS" if not blockers else "MISSING" if any("missing" in item for item in blockers) else "CHECK",
        "geometry_closure",
        "Per-leg B/T/K/P coordinates must close against published PB/PT/PK lengths and use non-assumption azimuth data.",
        "all four legs close within tolerance" if not blockers else f"{len(blockers)} leg geometry checks are blocked",
        blockers,
    ), geometry_rows


def validate_topology(template: dict[str, Any]) -> dict[str, Any]:
    allowed_joint_types = {"revolute", "spherical", "universal", "prismatic", "fixed", "distance", "compound", "bushing"}
    blockers: list[str] = []
    for idx, leg in enumerate(template.get("legs", []), start=1):
        topology = leg.get("constraint_topology", {})
        for key in ["B_joint_type", "T_joint_type", "K_joint_type", "P_joint_type"]:
            record = topology.get(key)
            value = str(raw_value(record)).lower() if not is_missing(raw_value(record)) else ""
            if value not in allowed_joint_types or category(record) in BLOCKING_SOURCE_CATEGORIES:
                blockers.append(f"legs[{idx - 1}].constraint_topology.{key}")
        for key in ["absorber_slider_axis_xyz", "joint_limit_definitions"]:
            record = topology.get(key)
            if is_missing(raw_value(record)) or category(record) in BLOCKING_SOURCE_CATEGORIES:
                blockers.append(f"legs[{idx - 1}].constraint_topology.{key}")
        axis_norm = vector_norm(topology.get("absorber_slider_axis_xyz"))
        if axis_norm is not None and not (0.95 <= axis_norm <= 1.05):
            blockers.append(f"legs[{idx - 1}].constraint_topology.absorber_slider_axis_xyz: axis norm {axis_norm:.3f} is not unit length")
    return check(
        "PASS" if not blockers else "MISSING",
        "constraint_topology",
        "Joint types, axes, slider direction, and limits must be defined from the real mechanism topology.",
        "topology is populated and source-tagged" if not blockers else f"{len(blockers)} topology fields are missing or blocked",
        blockers[:80],
    )


def validate_body_properties(template: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    for leg_idx, leg in enumerate(template.get("legs", [])):
        bodies = leg.get("body_properties", {})
        for body_name, body in bodies.items():
            mass = numeric_value(body.get("mass_kg"))
            if mass is None or mass <= 0.0 or category(body.get("mass_kg")) in BLOCKING_SOURCE_CATEGORIES:
                blockers.append(f"legs[{leg_idx}].body_properties.{body_name}.mass_kg")
            if is_missing(raw_value(body.get("com_xyz_m"))) or category(body.get("com_xyz_m")) in BLOCKING_SOURCE_CATEGORIES:
                blockers.append(f"legs[{leg_idx}].body_properties.{body_name}.com_xyz_m")
            if is_missing(raw_value(body.get("inertia_kg_m2"))) or category(body.get("inertia_kg_m2")) in BLOCKING_SOURCE_CATEGORIES:
                blockers.append(f"legs[{leg_idx}].body_properties.{body_name}.inertia_kg_m2")
    return check(
        "PASS" if not blockers else "MISSING",
        "body_mass_inertia",
        "Each moving leg body must have positive mass, COM, and inertia tensor from CAD, Adams export, measurement, or calibrated data.",
        "all body properties are ready" if not blockers else f"{len(blockers)} body-property fields are missing or blocked",
        blockers[:80],
    )


def validate_buffer_and_lock(template: dict[str, Any]) -> list[dict[str, Any]]:
    buffer_law = template.get("buffer_law", {})
    buffer_blockers: list[str] = []
    for key in ["linear_k_n_m", "linear_c_n_s_m", "stroke_limit_m", "extension_behavior"]:
        record = buffer_law.get(key)
        if is_missing(raw_value(record)) or category(record) in BLOCKING_SOURCE_CATEGORIES:
            buffer_blockers.append(f"buffer_law.{key}")
    table_record = buffer_law.get("nonlinear_force_stroke_table")
    table_path_value = raw_value(table_record)
    table_exists = False
    if isinstance(table_path_value, str) and table_path_value:
        table_path = (ROOT / table_path_value).resolve()
        table_exists = table_path.exists()

    lock = template.get("lock_hardware", {})
    lock_blockers: list[str] = []
    for key in ["mechanism_type", "trigger_logic", "constraint_stiffness"]:
        record = lock.get(key)
        if is_missing(raw_value(record)) or category(record) in BLOCKING_SOURCE_CATEGORIES:
            lock_blockers.append(f"lock_hardware.{key}")

    return [
        check(
            "PASS" if not buffer_blockers and table_exists else "PARTIAL" if table_exists else "MISSING",
            "buffer_law",
            "Absorber model must include k/c or nonlinear curves, stroke limits, and rebound/extension behavior.",
            f"table_exists={table_exists}, blockers={len(buffer_blockers)}",
            buffer_blockers,
        ),
        check(
            "PASS" if not lock_blockers else "MISSING",
            "lock_hardware",
            "Post-touchdown locking must be represented by real mechanism data or explicitly kept outside the Adams-equivalent leg model.",
            "lock hardware is populated" if not lock_blockers else f"{len(lock_blockers)} lock fields are missing or blocked",
            lock_blockers,
        ),
    ]


def build_validation(input_path: Path = TEMPLATE_JSON, allow_synthetic: bool = False) -> dict[str, Any]:
    template = read_json(input_path)
    rows = flatten_values(template)
    checks: list[dict[str, Any]] = []
    checks.append(validate_required_fields(rows, allow_synthetic=allow_synthetic))
    checks.append(validate_coordinate_system(template))
    geometry_check, geometry_rows = validate_geometry(template)
    checks.append(geometry_check)
    checks.append(validate_topology(template))
    checks.append(validate_body_properties(template))
    checks.extend(validate_buffer_and_lock(template))

    blocking_checks = [row for row in checks if row["status"] != "PASS"]
    required_rows = [row for row in rows if ADAMS_GATE in row.get("required_for", [])]
    field_blockers = [
        row
        for row in required_rows
        if is_missing(row.get("value"))
        or not source_is_ready(row, allow_synthetic)
    ]
    ready = not blocking_checks and not field_blockers
    category_counts: dict[str, int] = {}
    for row in rows:
        category_name = str(row.get("source_category"))
        category_counts[category_name] = category_counts.get(category_name, 0) + 1

    return {
        "validation_id": "ChronoLegMechanismDataValidation",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "validation_mode": "synthetic_selftest" if allow_synthetic else "strict_real_data",
        "input_path": rel(input_path.resolve()),
        "overall_status": "ready_for_adams_equivalent_chrono_model" if ready else "incomplete_for_adams_equivalent_chrono_model",
        "ready": ready,
        "summary": {
            "check_count": len(checks),
            "passing_check_count": sum(1 for row in checks if row["status"] == "PASS"),
            "blocking_check_count": len(blocking_checks),
            "adams_required_field_count": len(required_rows),
            "blocking_field_count": len(field_blockers),
            "source_category_counts": category_counts,
        },
        "checks": checks,
        "blocking_checks": blocking_checks,
        "blocking_fields": field_blockers[:200],
        "geometry_checks": geometry_rows,
        "gate": {
            "name": ADAMS_GATE,
            "pass": ready,
            "mode": "synthetic_selftest" if allow_synthetic else "strict_real_data",
            "if_false": "Keep using Stage 3A proxy/diagnostic branches; do not build or claim an Adams-equivalent Chrono mechanism from this data.",
            "if_true": (
                "Synthetic fixture is internally consistent for importer/builder self-tests only; do not claim Adams equivalence from synthetic data."
                if allow_synthetic
                else "The data can be consumed by a future Chrono CAD/topology builder for a real mechanism branch."
            ),
        },
    }


def write_validation_markdown(validation: dict[str, Any]) -> None:
    lines = [
        "# Chrono Leg Mechanism Data Validation",
        "",
        f"- Overall status: `{validation['overall_status']}`",
        f"- Ready: `{validation['ready']}`",
        f"- Validation mode: `{validation.get('validation_mode', 'strict_real_data')}`",
        f"- Input: `{validation['input_path']}`",
        f"- Generated UTC: `{validation['generated_utc']}`",
        f"- Checks: `{validation['summary']['passing_check_count']}/{validation['summary']['check_count']}` passing",
        f"- Blocking fields: `{validation['summary']['blocking_field_count']}`",
        "",
        "## Checks",
        "",
        "| ID | Status | Evidence | Blockers |",
        "| --- | --- | --- | --- |",
    ]
    for row in validation["checks"]:
        blockers = ", ".join(row.get("blockers", [])[:10])
        if len(row.get("blockers", [])) > 10:
            blockers += f", ... {len(row['blockers']) - 10} more"
        lines.append(
            "| {id} | **{status}** | {evidence} | {blockers} |".format(
                id=row["id"],
                status=row["status"],
                evidence=str(row["evidence"]).replace("|", "\\|"),
                blockers=blockers.replace("|", "\\|"),
            )
        )
    lines.extend(["", "## Geometry Checks", ""])
    for row in validation["geometry_checks"]:
        lines.append(f"- `{row.get('leg_id')}`: {row.get('status')} {row.get('reason', '')}")
    lines.extend(["", "## Gate", "", validation["gate"]["if_false" if not validation["ready"] else "if_true"]])
    VALIDATION_MD.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_validation_js(validation: dict[str, Any]) -> None:
    VALIDATION_JS.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_JS.write_text(
        "window.LEG_MECHANISM_VALIDATION = "
        + json.dumps(validation, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a filled leg-mechanism data template before it is used to replace the Chrono proxy legs.")
    parser.add_argument("command", choices=["validate", "report"], nargs="?", default="validate")
    parser.add_argument("--input", type=Path, default=TEMPLATE_JSON)
    parser.add_argument("--allow-synthetic", action="store_true", help="Accept synthetic_test_fixture source tags for importer/builder self-tests only.")
    args = parser.parse_args()

    input_path = args.input.resolve()
    validation = build_validation(input_path, allow_synthetic=args.allow_synthetic)
    write_json(VALIDATION_JSON, validation)
    write_validation_markdown(validation)
    write_validation_js(validation)

    print(f"Ready: {validation['ready']}")
    print(f"Overall: {validation['overall_status']}")
    print(f"Checks: {validation['summary']['passing_check_count']}/{validation['summary']['check_count']} passing")
    print(f"Blocking fields: {validation['summary']['blocking_field_count']}")
    print(f"Validation JSON: {VALIDATION_JSON}")
    print(f"Validation MD: {VALIDATION_MD}")
    print(f"Validation JS: {VALIDATION_JS}")
    if args.command == "report":
        print("Open: http://127.0.0.1:8765/leg-mechanism-validation.html")


if __name__ == "__main__":
    main()
