from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json
    from .landing_leg_contact import LITERATURE_INPUTS, thies_footprint_radius_m
except ImportError:
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json
    from landing_leg_contact import LITERATURE_INPUTS, thies_footprint_radius_m


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
CONTRACT_JSON = CASE_ROOT / "leg-mechanism-data-contract.json"
TEMPLATE_JSON = CASE_ROOT / "Input" / "leg_mechanism_data_template.json"
CONTRACT_MD = ROOT / "docs" / "leg-mechanism-data-contract.md"
CONTRACT_JS = VISUALIZATION_DIR / "leg-mechanism-contract-data.js"

ADAMS_GATE = "adams_equivalent_chrono_mechanism"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def value(
    current_value: Any,
    unit: str | None,
    source_category: str,
    source_detail: str,
    required_for_adams: bool = True,
) -> dict[str, Any]:
    return {
        "value": current_value,
        "unit": unit,
        "source_category": source_category,
        "source_detail": source_detail,
        "required_for": [ADAMS_GATE] if required_for_adams else [],
    }


def missing(unit: str | None, source_detail: str, required_for_adams: bool = True) -> dict[str, Any]:
    return value(None, unit, "missing_required", source_detail, required_for_adams)


def requirement(
    req_id: str,
    component: str,
    description: str,
    current_status: str,
    current_evidence: str,
    next_action: str,
    required_for_adams: bool = True,
) -> dict[str, Any]:
    return {
        "id": req_id,
        "component": component,
        "description": description,
        "required_for": [ADAMS_GATE] if required_for_adams else [],
        "current_status": current_status,
        "current_evidence": current_evidence,
        "next_action": next_action,
    }


def build_requirements() -> list[dict[str, Any]]:
    return [
        requirement(
            "coordinate_system_body_frame",
            "coordinate_system",
            "A published or CAD-defined rocket body frame and deck frame, including origin, axis directions, handedness, and units.",
            "partially_available",
            "Project HAMS/Cummins deck frame is defined; the Thies/Adams rocket leg CAD frame is not published.",
            "Use the CAD/Adams export frame or author-provided frame metadata; record any transform into the HAMS deck frame.",
        ),
        requirement(
            "leg_azimuths",
            "geometry",
            "Four leg azimuths and handedness in the rocket body frame.",
            "engineering_assumption",
            "Current model assumes symmetric 45/135/225/315 deg azimuths.",
            "Replace the assumed azimuths with CAD or paper values.",
        ),
        requirement(
            "joint_coordinates_b_t_k_p",
            "geometry",
            "Per-leg 3D coordinates for lower main joint B, upper strut joint T, middle strut joint K, and footpad joint P.",
            "partially_available",
            "Thies Table 4 gives B/T/K heights and PT/KP/PB lengths; full x/y/z hinge coordinates are not available.",
            "Export hinge marker coordinates from CAD/Adams or obtain author tables.",
        ),
        requirement(
            "joint_types_and_axes",
            "topology",
            "Joint type and axis for every connection: revolute, spherical, universal, prismatic, fixed, or compound joint.",
            "missing_required",
            "The papers show the tripod concept but not the Adams constraint graph.",
            "Define the exact Chrono constraint graph from CAD/Adams topology before claiming Adams equivalence.",
        ),
        requirement(
            "telescopic_absorber_topology",
            "absorber",
            "Telescopic absorber topology, including housing/body markers, slider axis, stroke limits, preload, extension behavior, and hard-stop behavior.",
            "missing_required",
            "Only stiffness/damping/table curves and reference deformation are available; internal multi-body topology is not published.",
            "Add absorber CAD/Adams markers and measured force law metadata.",
        ),
        requirement(
            "body_masses_inertias",
            "dynamics",
            "Mass, center of mass, and inertia tensor for each leg body: main strut, auxiliary struts, footpad, absorber housing, piston/rod, and lock hardware.",
            "missing_required",
            "Stage 3C uses explicit placeholder rod masses/inertias only as a failed diagnostic.",
            "Use CAD mass properties or validated engineering mass budget per component.",
        ),
        requirement(
            "force_stroke_velocity_curves",
            "absorber",
            "Machine-readable nonlinear force-stroke and force-velocity curves with units and digitization/source metadata.",
            "available_digitized",
            "Thies Figure 4/5 raster curves have been digitized and connected to a Chrono table buffer branch.",
            "Prefer original author tables or measured hardware data when available; keep raster digitization uncertainty recorded.",
            required_for_adams=False,
        ),
        requirement(
            "footpad_contact_material",
            "contact",
            "Footpad geometry, contact patch, friction model, normal stiffness/damping, restitution, and deck contact material.",
            "engineering_assumption",
            "Current model uses Li 2025 contact values and explicit material assumptions, not Thies-specific hardware data.",
            "Replace with measured footpad/deck values or a calibrated contact model.",
        ),
        requirement(
            "lock_hardware",
            "lock",
            "Physical locking or hold-down hardware topology, trigger condition, constraint stiffness, damping, and load path.",
            "implementation_proxy",
            "Current Stage 3 lock uses ChLinkMateFix as a proxy after stability criteria are met.",
            "Add actual post-landing securing hardware or define this as a separate platform-side model.",
        ),
        requirement(
            "validation_curves",
            "validation",
            "Author-level or reliably digitized time histories for leg force, damper stroke, footpad slip, body attitude, and nozzle clearance.",
            "partially_available",
            "Current registry contains table-scale checks and digitized buffer curves; many full dynamic curves remain gaps.",
            "Digitize the remaining figures or obtain source data for pointwise validation.",
            required_for_adams=False,
        ),
    ]


def build_leg_template() -> dict[str, Any]:
    thies = LITERATURE_INPUTS["thies_2022"]
    leg = thies["landing_leg"]
    rocket = thies["rocket"]
    req = thies["requirements"]
    result = thies["reported_dimensioning_result"]
    radius = thies_footprint_radius_m()
    azimuths = [45.0, 135.0, 225.0, 315.0]

    legs: list[dict[str, Any]] = []
    for idx, azimuth in enumerate(azimuths, start=1):
        legs.append(
            {
                "id": f"leg_{idx}",
                "azimuth_deg": value(
                    azimuth,
                    "deg",
                    "engineering_assumption",
                    "Symmetric azimuth used by the current Chrono proxy; not a published Thies value.",
                ),
                "published_plane_dimensions": {
                    "PB_length_m": value(leg["leg_length_m"], "m", "paper", "Thies 2022 Table 4"),
                    "PT_length_m": value(leg["strut_lengths_m"][0], "m", "paper", "Thies 2022 Table 4"),
                    "PK_length_m": value(leg["strut_lengths_m"][1], "m", "paper", "Thies 2022 Table 4"),
                    "B_height_m": value(leg["lower_attachment_b_height_m"], "m", "paper", "Thies 2022 Table 4"),
                    "T_height_m": value(leg["upper_attachment_t_height_m"], "m", "paper", "Thies 2022 Table 4"),
                    "K_height_m": value(leg["upper_attachment_k_height_m"], "m", "paper", "Thies 2022 Table 4"),
                    "leg_angle_deg": value(leg["leg_angle_to_hinge_plane_deg"], "deg", "paper", "Thies 2022 Table 4"),
                    "strut_angle_deg": value(leg["strut_angle_to_hinge_plane_deg"], "deg", "paper", "Thies 2022 Table 4"),
                },
                "adams_equivalent_geometry": {
                    "B_rocket_marker_xyz_m": {
                        "x": missing("m", "Not published in the current paper extraction."),
                        "y": missing("m", "Not published in the current paper extraction."),
                        "z": value(leg["lower_attachment_b_height_m"], "m", "paper", "Thies 2022 Table 4"),
                    },
                    "T_rocket_marker_xyz_m": {
                        "x": missing("m", "Not published in the current paper extraction."),
                        "y": missing("m", "Not published in the current paper extraction."),
                        "z": value(leg["upper_attachment_t_height_m"], "m", "paper", "Thies 2022 Table 4"),
                    },
                    "K_rocket_marker_xyz_m": {
                        "x": missing("m", "Not published in the current paper extraction."),
                        "y": missing("m", "Not published in the current paper extraction."),
                        "z": value(leg["upper_attachment_k_height_m"], "m", "paper", "Thies 2022 Table 4"),
                    },
                    "P_footpad_marker_xyz_m": {
                        "x": missing("m", "The proxy derives a footprint radius, but real CAD P coordinates are not published."),
                        "y": missing("m", "The proxy derives a footprint radius, but real CAD P coordinates are not published."),
                        "z": missing("m", "Footpad joint height relative to pad/contact geometry is not published."),
                    },
                    "proxy_footprint_radius_m": value(
                        radius,
                        "m",
                        "computed",
                        "Derived from PB length and leg angle: radius = PB*cos(angle).",
                    ),
                },
                "constraint_topology": {
                    "B_joint_type": missing(None, "Required for a Chrono/Adams-equivalent linkage."),
                    "T_joint_type": missing(None, "Required for a Chrono/Adams-equivalent linkage."),
                    "K_joint_type": missing(None, "Required for a Chrono/Adams-equivalent linkage."),
                    "P_joint_type": missing(None, "Required for a Chrono/Adams-equivalent linkage."),
                    "absorber_slider_axis_xyz": missing(None, "Required if the main leg is telescopic."),
                    "joint_limit_definitions": missing(None, "Required for stops, deployment locks, and post-touchdown constraints."),
                },
                "body_properties": {
                    "main_strut": {
                        "mass_kg": missing("kg", "CAD/Adams body mass not published."),
                        "com_xyz_m": missing("m", "CAD/Adams body COM not published."),
                        "inertia_kg_m2": missing("kg m^2", "CAD/Adams inertia tensor not published."),
                    },
                    "long_auxiliary_strut": {
                        "mass_kg": missing("kg", "CAD/Adams body mass not published."),
                        "com_xyz_m": missing("m", "CAD/Adams body COM not published."),
                        "inertia_kg_m2": missing("kg m^2", "CAD/Adams inertia tensor not published."),
                    },
                    "short_auxiliary_strut": {
                        "mass_kg": missing("kg", "CAD/Adams body mass not published."),
                        "com_xyz_m": missing("m", "CAD/Adams body COM not published."),
                        "inertia_kg_m2": missing("kg m^2", "CAD/Adams inertia tensor not published."),
                    },
                    "footpad": {
                        "mass_kg": missing("kg", "Current 80 kg value is an engineering placeholder, not paper data."),
                        "com_xyz_m": missing("m", "CAD/Adams body COM not published."),
                        "inertia_kg_m2": missing("kg m^2", "CAD/Adams inertia tensor not published."),
                    },
                },
            }
        )

    return {
        "schema_id": "ChronoLegMechanismDataContract/v1",
        "purpose": "Replace Stage 3A/3B/3C proxy legs with an Adams-equivalent Chrono mechanism only when these fields are populated and source-tagged.",
        "source_files": {
            "thies_markdown": "海上平台火箭回收文献/P3_Thies_2022.md",
            "thies_pdf": "海上平台火箭回收文献/P3_Thies_2022.pdf",
        },
        "coordinate_system": {
            "global_note": "Use SI units. Define all CAD markers in the rocket body frame, then supply the transform into the HAMS/Cummins deck frame.",
            "rocket_body_origin": missing(None, "Use CAD/Adams exported frame origin."),
            "rocket_body_axes": missing(None, "Use CAD/Adams exported axis convention."),
            "deck_frame_transform": missing(None, "Rigid transform from rocket landing frame to HAMS/Cummins deck frame."),
        },
        "rocket": {
            "landing_mass_kg": value(rocket["landing_mass_kg"], "kg", "paper", "Thies 2022 vehicle data table"),
            "height_m": value(rocket["height_m"], "m", "paper", "Thies 2022 vehicle data table"),
            "base_diameter_m": value(rocket["base_diameter_m"], "m", "paper", "Thies 2022 vehicle data table"),
            "cog_from_base_m": value(rocket["cog_from_launcher_base_m"], "m", "paper", "Thies 2022 vehicle data table"),
            "inertia_kg_m2": value(rocket["inertia_kg_m2"], "kg m^2", "paper", "Thies 2022 vehicle data table"),
        },
        "landing_conditions": {
            "touchdown_vertical_velocity_m_s": value(
                req["touchdown_vertical_velocity_nominal_m_s"],
                "m/s",
                "paper",
                "Thies 2022 Table 6/7 nominal case",
            ),
            "friction_coefficient_nominal": value(req["friction_coefficient_nominal"], None, "paper", "Thies 2022 Table 6"),
            "reported_nozzle_clearance_m": value(result["nozzle_clearance_m"], "m", "paper", "Thies 2022 Table 8"),
            "reported_damper_deformation_m": value(result["damper_deformation_m"], "m", "paper", "Thies 2022 Table 8"),
            "reported_spring_damper_force_kn": value(result["spring_damper_force_kn"], "kN", "paper", "Thies 2022 Table 8"),
        },
        "legs": legs,
        "buffer_law": {
            "linear_k_n_m": value(
                thies["linear_contact_parameters"]["damper_stiffness_n_m"],
                "N/m",
                "paper",
                "Thies 2022 Table 10, converted from N/mm.",
            ),
            "linear_c_n_s_m": value(
                thies["linear_contact_parameters"]["damper_damping_ns_m"],
                "N s/m",
                "paper",
                "Thies 2022 Table 10, converted from N sec/mm.",
            ),
            "nonlinear_force_stroke_table": value(
                rel(CASE_ROOT / "validation" / "thies_absorber_curves" / "thies-buffer-curves.json"),
                None,
                "digitized_paper_figure",
                "Digitized from Thies 2022 Figure 4 raster image; replace with original table if available.",
                required_for_adams=False,
            ),
            "stroke_limit_m": missing("m", "Need physical absorber stroke limit and hard-stop definition."),
            "extension_behavior": missing(None, "Need whether the absorber can carry tension/extension after rebound."),
        },
        "lock_hardware": {
            "mechanism_type": missing(None, "Current ChLinkMateFix lock is a numerical proxy only."),
            "trigger_logic": missing(None, "Need real platform or leg securing logic."),
            "constraint_stiffness": missing(None, "Need hardware stiffness/damping or equivalent constraint model."),
        },
    }


def flatten_values(node: Any, path: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(node, dict) and {"value", "source_category", "source_detail", "required_for"}.issubset(node.keys()):
        rows.append({"path": path, **node})
    elif isinstance(node, dict):
        for key, child in node.items():
            child_path = f"{path}.{key}" if path else key
            rows.extend(flatten_values(child, child_path))
    elif isinstance(node, list):
        for idx, child in enumerate(node):
            rows.extend(flatten_values(child, f"{path}[{idx}]"))
    return rows


def build_contract() -> dict[str, Any]:
    requirements = build_requirements()
    template = build_leg_template()
    rows = flatten_values(template)
    adams_required_rows = [row for row in rows if ADAMS_GATE in row.get("required_for", [])]
    blocking_categories = {"missing_required", "engineering_assumption", "implementation_proxy"}
    blocking_rows = [row for row in adams_required_rows if row.get("source_category") in blocking_categories]
    requirement_blockers = [
        row
        for row in requirements
        if ADAMS_GATE in row.get("required_for", [])
        and row["current_status"] in {"missing_required", "engineering_assumption", "implementation_proxy", "partially_available"}
    ]
    category_counts: dict[str, int] = {}
    for row in rows:
        category = str(row.get("source_category"))
        category_counts[category] = category_counts.get(category, 0) + 1

    return {
        "contract_id": "ChronoLegMechanismDataContract",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overall_status": "incomplete_for_adams_equivalent_chrono_model",
        "readiness": {
            "adams_equivalent_chrono_mechanism": {
                "pass": False,
                "blocking_requirement_count": len(requirement_blockers),
                "blocking_field_count": len(blocking_rows),
                "reason": "Published papers do not provide enough hinge coordinates, topology, body mass properties, absorber topology, and lock hardware data.",
            },
            "stage3a_proxy_can_continue": {
                "pass": True,
                "reason": "Stage 3A remains the accepted runnable proxy branch for computed landing animations and loose coupling studies.",
            },
        },
        "summary": {
            "requirement_count": len(requirements),
            "adams_required_field_count": len(adams_required_rows),
            "blocking_field_count": len(blocking_rows),
            "source_category_counts": category_counts,
        },
        "requirements": requirements,
        "blocking_requirements": requirement_blockers,
        "blocking_fields": blocking_rows[:200],
        "template_path": rel(TEMPLATE_JSON),
        "template": template,
        "usage": {
            "next_step": "Fill leg_mechanism_data_template.json with CAD/Adams or author data, keeping every source_category/source_detail field, then use it to replace Stage 3A proxy geometry.",
            "do_not_claim": "Do not call Stage 3B/3C an Adams-equivalent model until the blocking rows are replaced by paper, CAD, measured, or calibrated data.",
        },
    }


def write_contract_markdown(contract: dict[str, Any]) -> None:
    lines = [
        "# Chrono Leg Mechanism Data Contract",
        "",
        f"- Overall status: `{contract['overall_status']}`",
        f"- Generated UTC: `{contract['generated_utc']}`",
        f"- Template: `{contract['template_path']}`",
        f"- Blocking requirements: `{contract['readiness']['adams_equivalent_chrono_mechanism']['blocking_requirement_count']}`",
        f"- Blocking fields: `{contract['readiness']['adams_equivalent_chrono_mechanism']['blocking_field_count']}`",
        "",
        "## Purpose",
        "",
        "This contract defines the data needed to replace the current Stage 3A/3B/3C proxy legs with an Adams-equivalent Project Chrono mechanism.",
        "It intentionally keeps the current model incomplete for Adams equivalence until real hinge, topology, body-property, absorber, and lock data are supplied.",
        "",
        "## Requirements",
        "",
        "| ID | Component | Status | Evidence | Next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in contract["requirements"]:
        lines.append(
            "| {id} | {component} | **{status}** | {evidence} | {action} |".format(
                id=row["id"],
                component=row["component"],
                status=row["current_status"],
                evidence=row["current_evidence"].replace("|", "\\|"),
                action=row["next_action"].replace("|", "\\|"),
            )
        )
    lines.extend(["", "## Blocking Fields", ""])
    for row in contract["blocking_fields"][:80]:
        lines.append(f"- `{row['path']}`: {row['source_detail']}")
    if len(contract["blocking_fields"]) > 80:
        lines.append(f"- ... {len(contract['blocking_fields']) - 80} more rows in the JSON report.")
    lines.extend(
        [
            "",
            "## Use",
            "",
            "1. Fill `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_template.json` from CAD, Adams export, author data, or calibrated measurements.",
            "2. Keep each value's `source_category` and `source_detail` explicit.",
            "3. Replace Stage 3A proxy geometry only after the blocking rows are no longer assumptions or missing values.",
        ]
    )
    CONTRACT_MD.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_contract_js(contract: dict[str, Any]) -> None:
    CONTRACT_JS.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT_JS.write_text(
        "window.LEG_MECHANISM_CONTRACT = "
        + json.dumps(contract, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Write the data contract for replacing proxy landing legs with an Adams-equivalent Chrono mechanism.")
    parser.add_argument("command", choices=["report", "template", "check"], nargs="?", default="report")
    args = parser.parse_args()

    contract = build_contract()
    write_json(TEMPLATE_JSON, contract["template"])
    if args.command in {"report", "check"}:
        write_json(CONTRACT_JSON, contract)
        write_contract_markdown(contract)
        write_contract_js(contract)

    print(f"Adams-equivalent ready: {contract['readiness']['adams_equivalent_chrono_mechanism']['pass']}")
    print(f"Blocking requirements: {contract['readiness']['adams_equivalent_chrono_mechanism']['blocking_requirement_count']}")
    print(f"Blocking fields: {contract['readiness']['adams_equivalent_chrono_mechanism']['blocking_field_count']}")
    print(f"Template JSON: {TEMPLATE_JSON}")
    if args.command in {"report", "check"}:
        print(f"Contract JSON: {CONTRACT_JSON}")
        print(f"Contract MD: {CONTRACT_MD}")
        print(f"Contract JS: {CONTRACT_JS}")
        if args.command == "report":
            print("Open: http://127.0.0.1:8765/leg-mechanism-contract.html")


if __name__ == "__main__":
    main()
