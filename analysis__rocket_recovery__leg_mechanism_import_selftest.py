from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from .leg_mechanism_data_importer import SCHEMA_FILES, import_from_csv
    from .leg_mechanism_data_validator import SYNTHETIC_SOURCE_CATEGORY, build_validation
    from .real_leg_mechanism_builder import REAL_CONFIG_JSON, build_gate
except ImportError:
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from leg_mechanism_data_importer import SCHEMA_FILES, import_from_csv
    from leg_mechanism_data_validator import SYNTHETIC_SOURCE_CATEGORY, build_validation
    from real_leg_mechanism_builder import REAL_CONFIG_JSON, build_gate


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
SELFTEST_ROOT = CASE_ROOT / "validation" / "synthetic_leg_import"
SELFTEST_CSV_DIR = SELFTEST_ROOT / "csv"
SELFTEST_IMPORTED_TEMPLATE = SELFTEST_ROOT / "leg_mechanism_data_synthetic.json"
SELFTEST_BUFFER_TABLE = SELFTEST_ROOT / "synthetic-buffer-curve.json"
SELFTEST_CONFIG = SELFTEST_ROOT / "chrono_real_leg_mechanism_config.synthetic.json"
SELFTEST_VALIDATION_JSON = SELFTEST_ROOT / "synthetic-leg-import-validation.json"
SELFTEST_BUILDER_JSON = SELFTEST_ROOT / "synthetic-real-leg-builder-gate.json"
SELFTEST_REPORT_JSON = CASE_ROOT / "leg-mechanism-import-selftest-report.json"
SELFTEST_REPORT_MD = ROOT / "docs" / "leg-mechanism-import-selftest.md"
SELFTEST_REPORT_JS = VISUALIZATION_DIR / "leg-mechanism-import-selftest-data.js"

SOURCE_DETAIL = (
    "Synthetic importer self-test fixture generated from Thies published plane lengths; "
    "not production, CAD, Adams, author, measured, or calibrated data."
)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    header = SCHEMA_FILES[path.name]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def radial_marker(radius_m: float, z_m: float, azimuth_deg: float) -> tuple[float, float, float]:
    theta = math.radians(azimuth_deg)
    return radius_m * math.cos(theta), radius_m * math.sin(theta), z_m


def horizontal_projection(length_m: float, dz_m: float) -> float:
    value = length_m * length_m - dz_m * dz_m
    if value < 0.0:
        raise ValueError(f"invalid synthetic closure: length={length_m}, dz={dz_m}")
    return math.sqrt(value)


def unit_vector(a: tuple[float, float, float], b: tuple[float, float, float]) -> dict[str, float]:
    dx, dy, dz = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    norm = math.sqrt(dx * dx + dy * dy + dz * dz)
    if norm == 0.0:
        raise ValueError("cannot normalize zero-length vector")
    return {"x": dx / norm, "y": dy / norm, "z": dz / norm}


def body_com_for(body: str, markers: dict[str, tuple[float, float, float]]) -> dict[str, float]:
    if body == "main_strut":
        a, b = markers["B"], markers["P"]
    elif body == "long_auxiliary_strut":
        a, b = markers["T"], markers["P"]
    elif body == "short_auxiliary_strut":
        a, b = markers["K"], markers["P"]
    else:
        a = b = markers["P"]
    return {"x": 0.5 * (a[0] + b[0]), "y": 0.5 * (a[1] + b[1]), "z": 0.5 * (a[2] + b[2])}


def synthetic_leg_markers(azimuth_deg: float) -> dict[str, tuple[float, float, float]]:
    p_radius = 8.0
    p_z = 0.0
    dimensions = {
        "B": {"length_m": 8.1, "z_m": 4.4},
        "T": {"length_m": 11.2, "z_m": 9.0},
        "K": {"length_m": 7.4, "z_m": 5.7},
    }
    markers = {"P": radial_marker(p_radius, p_z, azimuth_deg)}
    for marker, row in dimensions.items():
        inward_offset = horizontal_projection(row["length_m"], row["z_m"] - p_z)
        markers[marker] = radial_marker(p_radius - inward_offset, row["z_m"], azimuth_deg)
    return markers


def write_synthetic_buffer_table() -> dict[str, Any]:
    data = {
        "curve_id": "synthetic_buffer_curve_for_import_selftest_only",
        "source_category": SYNTHETIC_SOURCE_CATEGORY,
        "source_detail": SOURCE_DETAIL,
        "force_stroke_points": [
            {"stroke_m": 0.0, "force_n": 0.0},
            {"stroke_m": 0.2, "force_n": 420000.0},
            {"stroke_m": 0.42, "force_n": 935000.0},
            {"stroke_m": 0.8, "force_n": 1800000.0},
        ],
        "force_velocity_points": [
            {"velocity_m_s": 0.0, "force_n": 0.0},
            {"velocity_m_s": 1.0, "force_n": 110000.0},
            {"velocity_m_s": 5.0, "force_n": 550000.0},
        ],
    }
    write_json(SELFTEST_BUFFER_TABLE, data)
    return data


def write_synthetic_csvs(source_dir: Path = SELFTEST_CSV_DIR) -> dict[str, Any]:
    write_synthetic_buffer_table()
    source_dir.mkdir(parents=True, exist_ok=True)

    coordinate_rows = [
        {
            "field": "rocket_body_origin",
            "value_json": json_text({"origin": "rocket_base_center", "position_m": [0.0, 0.0, 0.0]}),
            "source_category": SYNTHETIC_SOURCE_CATEGORY,
            "source_detail": SOURCE_DETAIL,
        },
        {
            "field": "rocket_body_axes",
            "value_json": json_text({"x": "forward", "y": "port", "z": "up", "handedness": "right"}),
            "source_category": SYNTHETIC_SOURCE_CATEGORY,
            "source_detail": SOURCE_DETAIL,
        },
        {
            "field": "deck_frame_transform",
            "value_json": json_text(
                {
                    "translation_m": [0.0, 0.0, 0.0],
                    "rotation_matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
                }
            ),
            "source_category": SYNTHETIC_SOURCE_CATEGORY,
            "source_detail": SOURCE_DETAIL,
        },
    ]
    write_csv(source_dir / "coordinate_system.csv", coordinate_rows)

    azimuths = {"leg_1": 45.0, "leg_2": 135.0, "leg_3": 225.0, "leg_4": 315.0}
    write_csv(
        source_dir / "leg_azimuths.csv",
        [
            {
                "leg_id": leg_id,
                "azimuth_deg": azimuth,
                "source_category": SYNTHETIC_SOURCE_CATEGORY,
                "source_detail": SOURCE_DETAIL,
            }
            for leg_id, azimuth in azimuths.items()
        ],
    )

    marker_rows: list[dict[str, Any]] = []
    topology_rows: list[dict[str, Any]] = []
    body_rows: list[dict[str, Any]] = []
    masses = {
        "main_strut": 250.0,
        "long_auxiliary_strut": 140.0,
        "short_auxiliary_strut": 110.0,
        "footpad": 80.0,
    }
    for leg_id, azimuth in azimuths.items():
        markers = synthetic_leg_markers(azimuth)
        for marker, (x_m, y_m, z_m) in markers.items():
            marker_rows.append(
                {
                    "leg_id": leg_id,
                    "marker": marker,
                    "x_m": f"{x_m:.9f}",
                    "y_m": f"{y_m:.9f}",
                    "z_m": f"{z_m:.9f}",
                    "source_category": SYNTHETIC_SOURCE_CATEGORY,
                    "source_detail": SOURCE_DETAIL,
                }
            )
        for field, value in [
            ("B_joint_type", "spherical"),
            ("T_joint_type", "spherical"),
            ("K_joint_type", "spherical"),
            ("P_joint_type", "spherical"),
            ("absorber_slider_axis_xyz", unit_vector(markers["B"], markers["P"])),
            ("joint_limit_definitions", {"stroke_min_m": 0.0, "stroke_max_m": 0.8, "hard_stop_policy": "synthetic_selftest_only"}),
        ]:
            topology_rows.append(
                {
                    "leg_id": leg_id,
                    "field": field,
                    "value_json": json_text(value),
                    "source_category": SYNTHETIC_SOURCE_CATEGORY,
                    "source_detail": SOURCE_DETAIL,
                }
            )
        for body, mass in masses.items():
            body_rows.extend(
                [
                    {
                        "leg_id": leg_id,
                        "body": body,
                        "field": "mass_kg",
                        "value_json": json_text(mass),
                        "unit": "kg",
                        "source_category": SYNTHETIC_SOURCE_CATEGORY,
                        "source_detail": SOURCE_DETAIL,
                    },
                    {
                        "leg_id": leg_id,
                        "body": body,
                        "field": "com_xyz_m",
                        "value_json": json_text(body_com_for(body, markers)),
                        "unit": "m",
                        "source_category": SYNTHETIC_SOURCE_CATEGORY,
                        "source_detail": SOURCE_DETAIL,
                    },
                    {
                        "leg_id": leg_id,
                        "body": body,
                        "field": "inertia_kg_m2",
                        "value_json": json_text({"ixx": 1.0, "iyy": 1.0, "izz": 1.0, "ixy": 0.0, "ixz": 0.0, "iyz": 0.0}),
                        "unit": "kg m^2",
                        "source_category": SYNTHETIC_SOURCE_CATEGORY,
                        "source_detail": SOURCE_DETAIL,
                    },
                ]
            )
    write_csv(source_dir / "marker_coordinates.csv", marker_rows)
    write_csv(source_dir / "constraint_topology.csv", topology_rows)
    write_csv(source_dir / "body_properties.csv", body_rows)

    buffer_rows = [
        {
            "section": "buffer_law",
            "field": "nonlinear_force_stroke_table",
            "value_json": json_text(rel(SELFTEST_BUFFER_TABLE)),
            "unit": "",
            "source_category": SYNTHETIC_SOURCE_CATEGORY,
            "source_detail": SOURCE_DETAIL,
        },
        {
            "section": "buffer_law",
            "field": "stroke_limit_m",
            "value_json": json_text(0.8),
            "unit": "m",
            "source_category": SYNTHETIC_SOURCE_CATEGORY,
            "source_detail": SOURCE_DETAIL,
        },
        {
            "section": "buffer_law",
            "field": "extension_behavior",
            "value_json": json_text("compression_only_with_rebound_gap"),
            "unit": "",
            "source_category": SYNTHETIC_SOURCE_CATEGORY,
            "source_detail": SOURCE_DETAIL,
        },
        {
            "section": "lock_hardware",
            "field": "mechanism_type",
            "value_json": json_text("synthetic_fixed_clamp"),
            "unit": "",
            "source_category": SYNTHETIC_SOURCE_CATEGORY,
            "source_detail": SOURCE_DETAIL,
        },
        {
            "section": "lock_hardware",
            "field": "trigger_logic",
            "value_json": json_text({"stable_dwell_s": 1.0, "max_body_rate_rad_s": 0.01}),
            "unit": "",
            "source_category": SYNTHETIC_SOURCE_CATEGORY,
            "source_detail": SOURCE_DETAIL,
        },
        {
            "section": "lock_hardware",
            "field": "constraint_stiffness",
            "value_json": json_text({"linear_n_m": 100000000.0, "angular_nm_rad": 100000000.0}),
            "unit": "",
            "source_category": SYNTHETIC_SOURCE_CATEGORY,
            "source_detail": SOURCE_DETAIL,
        },
    ]
    write_csv(source_dir / "buffer_lock.csv", buffer_rows)

    return {
        "source_dir": rel(source_dir),
        "files": [
            {"path": rel(source_dir / filename), "rows": len(list(csv.DictReader((source_dir / filename).open("r", encoding="utf-8"))))}
            for filename in SCHEMA_FILES
        ],
    }


def build_selftest() -> dict[str, Any]:
    csv_summary = write_synthetic_csvs()
    import_report = import_from_csv(SELFTEST_CSV_DIR.resolve(), output_path=SELFTEST_IMPORTED_TEMPLATE.resolve())
    validation = build_validation(SELFTEST_IMPORTED_TEMPLATE.resolve(), allow_synthetic=True)
    write_json(SELFTEST_VALIDATION_JSON, validation)
    builder_gate = build_gate(
        SELFTEST_IMPORTED_TEMPLATE.resolve(),
        output_path=SELFTEST_CONFIG.resolve(),
        write_config=True,
        allow_synthetic=True,
        validation_source_path=SELFTEST_BUILDER_JSON.resolve(),
    )
    write_json(SELFTEST_BUILDER_JSON, builder_gate)

    production_config_written = REAL_CONFIG_JSON.resolve() == SELFTEST_CONFIG.resolve() and SELFTEST_CONFIG.exists()
    pass_status = bool(validation.get("ready")) and bool(builder_gate.get("config_written")) and SELFTEST_CONFIG.exists() and not production_config_written
    return {
        "selftest_id": "ChronoLegMechanismImportSyntheticSelfTest",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS" if pass_status else "FAIL",
        "synthetic_only": True,
        "not_literature_reproduction": True,
        "not_production_data": True,
        "source_category": SYNTHETIC_SOURCE_CATEGORY,
        "csv_summary": csv_summary,
        "import_report": import_report,
        "validation_path": rel(SELFTEST_VALIDATION_JSON),
        "validation_ready": validation.get("ready"),
        "validation_mode": validation.get("validation_mode"),
        "builder_path": rel(SELFTEST_BUILDER_JSON),
        "builder_status": builder_gate.get("overall_status"),
        "synthetic_config_path": rel(SELFTEST_CONFIG),
        "synthetic_config_written": builder_gate.get("config_written"),
        "production_config_path": rel(REAL_CONFIG_JSON),
        "production_config_written_by_selftest": production_config_written,
        "checks": [
            {
                "id": "csv_import",
                "pass": import_report.get("change_count", 0) > 0 and Path(SELFTEST_IMPORTED_TEMPLATE).exists(),
                "evidence": f"changes={import_report.get('change_count', 0)}, output={rel(SELFTEST_IMPORTED_TEMPLATE)}",
            },
            {
                "id": "synthetic_validation",
                "pass": bool(validation.get("ready")) and validation.get("validation_mode") == "synthetic_selftest",
                "evidence": f"ready={validation.get('ready')}, mode={validation.get('validation_mode')}",
            },
            {
                "id": "builder_nonproduction_output",
                "pass": bool(builder_gate.get("config_written")) and SELFTEST_CONFIG.exists() and not production_config_written,
                "evidence": f"config={rel(SELFTEST_CONFIG)}, production={rel(REAL_CONFIG_JSON)}",
            },
        ],
        "warning": "This fixture proves the importer, validator and builder code path only. It must not be used as CAD/Adams-quality leg data.",
    }


def write_selftest_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Chrono Leg Mechanism Import Self-Test",
        "",
        f"- Status: `{report['status']}`",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Source category: `{report['source_category']}`",
        f"- Synthetic config: `{report['synthetic_config_path']}`",
        f"- Production config: `{report['production_config_path']}`",
        f"- Production config written by self-test: `{report['production_config_written_by_selftest']}`",
        "",
        report["warning"],
        "",
        "## Checks",
        "",
        "| ID | Pass | Evidence |",
        "| --- | --- | --- |",
    ]
    for row in report["checks"]:
        lines.append(f"| `{row['id']}` | `{row['pass']}` | {str(row['evidence']).replace('|', '\\|')} |")
    lines.extend(["", "## CSV Files", ""])
    for row in report["csv_summary"]["files"]:
        lines.append(f"- `{row['path']}`: {row['rows']} rows")
    SELFTEST_REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    SELFTEST_REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_selftest_js(report: dict[str, Any]) -> None:
    SELFTEST_REPORT_JS.parent.mkdir(parents=True, exist_ok=True)
    SELFTEST_REPORT_JS.write_text(
        "window.LEG_MECHANISM_IMPORT_SELFTEST = "
        + json.dumps(report, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a synthetic CSV import/validator/builder self-test without writing production real-leg config data.")
    parser.add_argument("command", choices=["run", "report"], nargs="?", default="run")
    args = parser.parse_args()

    report = build_selftest()
    write_json(SELFTEST_REPORT_JSON, report)
    write_selftest_markdown(report)
    write_selftest_js(report)

    print(f"Status: {report['status']}")
    print(f"Validation ready: {report['validation_ready']}")
    print(f"Builder status: {report['builder_status']}")
    print(f"Synthetic config written: {report['synthetic_config_written']}")
    print(f"Production config written by self-test: {report['production_config_written_by_selftest']}")
    print(f"Self-test JSON: {SELFTEST_REPORT_JSON}")
    print(f"Self-test MD: {SELFTEST_REPORT_MD}")
    print(f"Self-test JS: {SELFTEST_REPORT_JS}")
    if args.command == "report":
        print("Open: http://127.0.0.1:8765/leg-mechanism-import-selftest.html")


if __name__ == "__main__":
    main()
