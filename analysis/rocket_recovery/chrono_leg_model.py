from __future__ import annotations

import importlib
import math
import bisect
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .common import G, ROOT, read_json
    from .landing_leg_contact import LITERATURE_INPUTS, kinetic_energy_kj, thies_footprint_radius_m
except ImportError:
    from common import G, ROOT, read_json
    from landing_leg_contact import LITERATURE_INPUTS, kinetic_energy_kj, thies_footprint_radius_m


INSTALL_HINT = {
    "reason": "Project Chrono is not installed in the active Python environment.",
    "recommended_isolated_prefix": r".tools\chrono-env",
    "create_prefix_env": r'$env:CONDA_NO_PLUGINS="true"; conda create --prefix ".tools\chrono-env" --override-channels -c conda-forge python=3.13 pychrono=10.0.0 numpy -y',
    "install_pychrono": r'$env:CONDA_NO_PLUGINS="true"; conda install --prefix ".tools\chrono-env" --override-channels -c conda-forge pychrono=10.0.0 numpy -y',
    "run_with_prefix_python": r'.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_one_way_recovery.py run',
    "notes": [
        "Use the project-local prefix so the Chrono runtime stays isolated from the rest of the computer.",
        "Do not add Chrono to the system PATH; activate or call the prefix python explicitly.",
    ],
}

THIES_DIGITIZED_BUFFER_JSON = ROOT / "RocketRecoveryCases" / "Chrono_LeggedRecovery" / "validation" / "thies_absorber_curves" / "thies-buffer-curves.json"


class ChronoUnavailableError(RuntimeError):
    pass


def import_pychrono() -> Any:
    errors: list[str] = []
    for module_name in ("pychrono", "chrono"):
        try:
            return importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - depends on local install
            errors.append(f"{module_name}: {exc}")
    raise ChronoUnavailableError("; ".join(errors))


def chrono_environment_report() -> dict[str, Any]:
    try:
        module = import_pychrono()
    except ChronoUnavailableError as exc:
        return {
            "available": False,
            "error": str(exc),
            "install_hint": INSTALL_HINT,
            "adapter_policy": "No fallback to the previous hand-written contact_forces model.",
        }
    version = getattr(module, "__version__", None) or getattr(module, "CHRONO_VERSION", None) or "unknown"
    return {
        "available": True,
        "module": getattr(module, "__name__", "pychrono"),
        "version": version,
        "adapter_policy": "Use Project Chrono as the landing-leg/contact solver.",
    }


def leg_positions_from_config(config: dict[str, Any]) -> list[dict[str, float]]:
    radius = float(config["legs"]["footprint_radius_m"])
    out: list[dict[str, float]] = []
    for idx, azimuth in enumerate(config["legs"]["azimuths_deg"], start=1):
        rad = math.radians(float(azimuth))
        out.append(
            {
                "id": f"leg_{idx}",
                "azimuth_deg": float(azimuth),
                "x_m": radius * math.cos(rad),
                "y_m": radius * math.sin(rad),
            }
        )
    return out


def default_leg_model_config() -> dict[str, Any]:
    thies = LITERATURE_INPUTS["thies_2022"]
    li = LITERATURE_INPUTS["li_2025"]
    rocket = thies["rocket"]
    leg = thies["landing_leg"]
    req = thies["requirements"]
    contact = thies["linear_contact_parameters"]
    result = thies["reported_dimensioning_result"]
    config = {
        "model_id": "ChronoLeggedRecovery_Stage1",
        "solver": {
            "engine": "Project Chrono / PyChrono",
            "contact_method": "SMC",
            "contact_coefficient_mode": "explicit_stiffness_damping",
            "time_step_s": 0.0005,
            "output_step_s": 0.01,
            "start_s": 506.0,
            "end_s": 526.0,
            "gravity_m_s2": G,
            "pre_contact_gravity": "off_until_first_contact_to_preserve_Thies_touchdown_velocity",
            "deck_thickness_m": 0.35,
            "contact_force_threshold_n": 100.0,
            "no_fallback_policy": "If PyChrono is unavailable, stop with an environment report.",
        },
        "rocket": {
            "source": rocket["source"],
            "landing_mass_kg": rocket["landing_mass_kg"],
            "mass_allocation": "published_total_less_explicit_multibody_children",
            "height_m": rocket["height_m"],
            "engine_length_m": rocket["engine_length_m"],
            "base_diameter_m": rocket["base_diameter_m"],
            "cog_from_base_m": rocket["cog_from_launcher_base_m"],
            "inertia_kg_m2": {
                "roll_x": rocket["inertia_kg_m2"]["roll_iyy"],
                "pitch_y": rocket["inertia_kg_m2"]["pitch_ixx"],
                "yaw_z": rocket["inertia_kg_m2"]["yaw_izz"],
            },
            "touchdown_vertical_velocity_m_s": req["touchdown_vertical_velocity_nominal_m_s"],
            "initial_lateral_velocity_m_s": req["touchdown_lateral_velocity_nominal_m_s"],
            "nozzle_clearance_required_m": rocket["allowed_nozzle_clearance_m"],
            "reported_nozzle_clearance_m": result["nozzle_clearance_m"],
            "stage3_proxy_nozzle_reference_height_from_model_base_m": result["nozzle_clearance_m"],
            "stage3_proxy_nozzle_reference_note": (
                "Thies reports nozzle clearance as distance from nozzle end to landing pad. "
                "The Stage 3A proxy does not include CAD nozzle coordinates, so the reported "
                "0.570 m parking clearance is stored as a transparent reference height from "
                "the proxy lower-leg/base plane to the nozzle-end point."
            ),
        },
        "legs": {
            "source": leg["source"],
            "count": leg["leg_count"],
            "configuration": leg["configuration"],
            "azimuths_deg": [45.0, 135.0, 225.0, 315.0],
            "footprint_radius_m": thies_footprint_radius_m(),
            "upper_attachment_height_m": leg["upper_attachment_t_height_m"],
            "lower_attachment_height_m": leg["lower_attachment_b_height_m"],
            "leg_length_m": leg["leg_length_m"],
            "damper_stiffness_n_m": contact["damper_stiffness_n_m"],
            "damper_damping_ns_m": contact["damper_damping_ns_m"],
            "damper_rest_length_m": max(0.1, leg["lower_attachment_b_height_m"] - li["contact"]["radius_m"]),
            "equivalent_guidance_model": "ChLinkMatePrismatic vertical slider at each foot point; stage-1 proxy for the deployed leg linkage.",
            "stroke_reference_m": result["damper_deformation_m"],
            "force_reference_n": result["spring_damper_force_kn"] * 1000.0,
            "footpad_radius_m": li["contact"]["radius_m"],
            "footpad_mass_kg": 80.0,
            "footpad_thickness_m": 0.18,
        },
        "contact": {
            "source": "Thies 2022 Table 9 platform-support stiffness/damping used as a local penalty-contact proxy; Li 2025 Table 2 supplies only the unpublished footpad radius and dynamic-friction proxy.",
            "normal_stiffness_n_m": contact["platform_stiffness_n_m"],
            "normal_damping_ns_m": contact["platform_damping_ns_m"],
            "young_modulus_pa": 2.0e9,
            "poisson_ratio": 0.3,
            "static_friction": req["friction_coefficient_nominal"],
            "dynamic_friction": li["contact"]["dynamic_friction"],
            "restitution": 0.0,
        },
        "validation_targets": {
            "thies_touchdown_energy_kj": thies["dimensioning_case"]["kinetic_energy_kj"],
            "computed_touchdown_energy_kj": kinetic_energy_kj(
                rocket["landing_mass_kg"],
                req["touchdown_vertical_velocity_nominal_m_s"],
            ),
            "max_incident_angle_deg": req["launcher_incident_angle_max_deg"],
            "velocity_range_m_s": [
                req["touchdown_vertical_velocity_min_m_s"],
                req["touchdown_vertical_velocity_max_m_s"],
            ],
            "symmetric_force_tolerance": 0.05,
        },
        "parameter_audit": {
            "published_values": [
                "rocket mass, inertia, height, base diameter, CG and touchdown velocity from Thies 2022",
                "leg count, leg length, leg angle and attachment heights from Thies 2022",
                "damper linear stiffness/damping and reference stroke/force from Thies 2022",
                "reported nozzle clearance 0.570 m from Thies 2022 Table 8",
                "platform-support stiffness/damping transcribed from Thies 2022 Table 9",
                "footpad radius and dynamic friction from Li 2025 where Thies does not publish them",
            ],
            "explicit_assumptions": [
                "four leg azimuths are symmetric at 45/135/225/315 deg because exact azimuths are not published",
                "footpad mass is a transparent engineering placeholder until CAD or paper data is available",
                "nozzle end location is represented by a Stage 3A proxy reference offset because CAD nozzle coordinates are not published",
                "stage 1 uses a TSDA strut plus contact footpad model, not a full Adams-equivalent linkage",
                "stage 1 constrains each footpad with a vertical prismatic mate instead of explicit tripod-link hinges",
                "Chrono SMC Young modulus is set as an explicit contact-material assumption because Li reports contact stiffness/damping, not elastic modulus",
                "Thies reports a platform mass-spring-damper coefficient, not a footpad/deck material law; applying those coefficients to each local SMC contact is a declared numerical proxy and requires stiffness/time-step sensitivity before load interpretation",
            ],
        },
    }
    attach_parameter_provenance(config)
    return config


def tripod_leg_model_config() -> dict[str, Any]:
    config = default_leg_model_config()
    thies = LITERATURE_INPUTS["thies_2022"]
    leg = thies["landing_leg"]
    foot_radius = float(config["legs"]["footpad_radius_m"])
    main_length = float(leg["leg_length_m"])
    lower_height = float(leg["lower_attachment_b_height_m"])
    upper_height = float(leg["upper_attachment_t_height_m"])
    mid_height = float(leg["upper_attachment_k_height_m"])
    brace_long = float(leg["strut_lengths_m"][0])
    brace_short = float(leg["strut_lengths_m"][1])
    main_horizontal = math.sqrt(max(main_length**2 - (lower_height - foot_radius) ** 2, 0.0))
    brace_tangent = min(1.5, 0.9 * math.sqrt(max(brace_short**2 - (mid_height - foot_radius) ** 2, 0.0)))

    def brace_radial(length: float, height: float, tangent: float) -> float:
        horizontal_radial = math.sqrt(max(length**2 - (height - foot_radius) ** 2 - tangent**2, 0.0))
        return main_horizontal - horizontal_radial

    config["model_id"] = "ChronoLeggedRecovery_Stage3A_TripodProxy"
    config["solver"]["time_step_s"] = 0.0005
    config["solver"]["output_step_s"] = 0.01
    config["solver"]["post_touchdown_lock_logic"] = {
        "mode": "diagnostic_only",
        "stable_dwell_s": 1.0,
        "vertical_velocity_limit_m_s": 0.05,
        "angular_rate_limit_deg_s": 0.25,
    }
    config["legs"]["footprint_radius_m"] = main_horizontal
    config["legs"]["damper_rest_length_m"] = main_length
    config["legs"]["equivalent_guidance_model"] = (
        "Stage 3A tripod proxy: inclined ChLinkMatePrismatic main-leg guide, nonlinear compression-only TSDA main buffer, "
        "and two spherical-end elastic TSDA diagonal braces per footpad."
    )
    config["legs"]["stage3_tripod_proxy"] = {
        "source": "Thies 2022 Table 4 dimensions; tangential brace separation is an explicit geometry-closure assumption.",
        "stage": "Stage 3A",
        "main_guide_model": "inclined_prismatic",
        "brace_model": "elastic_tsda",
        "mechanism_elements_per_leg": {
            "main_guide": "ChLinkMatePrismatic along the deployed main-leg axis",
            "main_buffer": "ChLinkTSDA from B attachment to footpad center; nonlinear compression-only force law",
            "long_brace": "ChLinkTSDA spherical-end axial brace from T attachment to footpad center",
            "short_brace": "ChLinkTSDA spherical-end axial brace from K attachment to footpad center",
            "footpad": "ChBodyEasySphere with SMC contact/friction",
        },
        "main_buffer_rest_length_m": main_length,
        "footprint_radius_m": main_horizontal,
        "attachment_radial_m": {
            "B_main": 0.0,
            "T_long": brace_radial(brace_long, upper_height, brace_tangent),
            "K_short": brace_radial(brace_short, mid_height, -brace_tangent),
        },
        "attachment_tangential_m": {"B_main": 0.0, "T_long": brace_tangent, "K_short": -brace_tangent},
        "attachment_height_m": {"B_main": lower_height, "T_long": upper_height, "K_short": mid_height},
        "target_lengths_m": {"main_buffer": main_length, "long_brace": brace_long, "short_brace": brace_short},
        "geometry_closure_error_m": {},
        "brace_axial_stiffness_n_m": 1.0e7,
        "brace_axial_damping_ns_m": 1.0e5,
    }
    for item, length in config["legs"]["stage3_tripod_proxy"]["target_lengths_m"].items():
        if item == "main_buffer":
            radial = config["legs"]["stage3_tripod_proxy"]["attachment_radial_m"]["B_main"]
            tangent = 0.0
            height = lower_height
        elif item == "long_brace":
            radial = config["legs"]["stage3_tripod_proxy"]["attachment_radial_m"]["T_long"]
            tangent = brace_tangent
            height = upper_height
        else:
            radial = config["legs"]["stage3_tripod_proxy"]["attachment_radial_m"]["K_short"]
            tangent = -brace_tangent
            height = mid_height
        actual = math.sqrt((main_horizontal - radial) ** 2 + tangent**2 + (height - foot_radius) ** 2)
        config["legs"]["stage3_tripod_proxy"]["geometry_closure_error_m"][item] = actual - length

    config["legs"]["nonlinear_buffer_law"] = {
        "source": "Thies 2022 Table 9 linear k/c and Table 8 reference stroke; hard stop is an explicit numerical assumption.",
        "type": "compression_only_bilinear_with_hard_stop",
        "supported_types": [
            "compression_only_bilinear_with_hard_stop",
            "compression_only_table",
        ],
        "table_interface_note": (
            "If a digitized or measured hydropneumatic buffer curve becomes available, set type to "
            "compression_only_table and provide force_stroke_points plus optional force_velocity_points. "
            "The default remains bilinear because no machine-readable Thies/Yue/Li buffer curve is published in the supplied files."
        ),
        "linear_stiffness_n_m": config["legs"]["damper_stiffness_n_m"],
        "linear_damping_ns_m": config["legs"]["damper_damping_ns_m"],
        "stroke_limit_m": config["legs"]["stroke_reference_m"],
        "hard_stop_stiffness_n_m": 2.0e8,
        "hard_stop_damping_ns_m": 1.0e7,
        "force_stroke_points": [],
        "force_velocity_points": [],
        "no_tension": True,
    }
    config["parameter_audit"]["published_values"].extend(
        [
            "tripod attachment heights T/K/B and strut lengths from Thies 2022 Table 4",
            "nonlinear buffer base stiffness/damping from Thies 2022 Table 9",
        ]
    )
    config["parameter_audit"]["explicit_assumptions"].extend(
        [
            "Stage 3A uses axial TSDA links as spherical-end elastic braces; brace mass/inertia are not yet modeled as separate CAD rods.",
            "Tangential separation of the two diagonal brace attachment points is set to 1.5 m because the supplied papers do not publish the full 3D CAD hinge coordinates.",
            "The nonlinear buffer hard-stop stiffness/damping are numerical assumptions until a hydraulic or hydropneumatic force-stroke table is available.",
            "Post-touchdown lock is currently a diagnostic stability flag and does not yet actuate a physical locking clamp.",
        ]
    )
    attach_parameter_provenance(config)
    return config


def tripod_rigid_brace_model_config() -> dict[str, Any]:
    config = tripod_leg_model_config()
    proxy = config["legs"]["stage3_tripod_proxy"]
    config["model_id"] = "ChronoLeggedRecovery_Stage3B_RigidBraceProxy"
    config["legs"]["equivalent_guidance_model"] = (
        "Stage 3B rigid-brace proxy: two spherical-end ChLinkDistance braces constrain the footpad geometry, "
        "while the main B-to-foot member remains a compression-only nonlinear TSDA buffer. The Stage 3A inclined "
        "main prismatic guide is disabled to avoid over-constraining the simplified tripod geometry."
    )
    proxy["stage"] = "Stage 3B"
    proxy["main_guide_model"] = "disabled_for_rigid_brace_proxy"
    proxy["brace_model"] = "rigid_distance_constraint"
    proxy["mechanism_elements_per_leg"] = {
        "main_guide": "disabled; two rigid brace constraints plus the main buffer define the footpad motion proxy",
        "main_buffer": "ChLinkTSDA from B attachment to footpad center; nonlinear compression-only force law",
        "long_brace": "ChLinkDistance fixed-length spherical-end constraint from T attachment to footpad center",
        "short_brace": "ChLinkDistance fixed-length spherical-end constraint from K attachment to footpad center",
        "footpad": "ChBodyEasySphere with SMC contact/friction",
    }
    proxy["brace_force_output"] = "not_available_from_ChLinkDistance_in_this_pychrono_build; report length-error only"
    config["parameter_audit"]["published_values"].append("Stage 3B rigid brace rest lengths still use Thies 2022 Table 4 strut lengths")
    config["parameter_audit"]["explicit_assumptions"].extend(
        [
            "Stage 3B uses massless ChLinkDistance braces rather than CAD rods because brace mass and inertia are not published.",
            "Stage 3B disables the Stage 3A main prismatic guide to keep the simplified two-brace tripod from being over-constrained.",
            "Stage 3B rigid-brace proxy is a geometry-constrained open-source substitute for an Adams-style mechanism, not a full CAD replica.",
        ]
    )
    attach_parameter_provenance(config)
    return config


def tripod_rigid_body_link_model_config() -> dict[str, Any]:
    config = tripod_leg_model_config()
    proxy = config["legs"]["stage3_tripod_proxy"]
    config["model_id"] = "ChronoLeggedRecovery_Stage3C_RigidBodyLinkDiagnostic"
    config["legs"]["equivalent_guidance_model"] = (
        "Stage 3C rigid-body link diagnostic: the two published PT/KP support struts are represented "
        "as finite-mass ChBodyEasyCylinder rods with spherical joints at the rocket and footpad ends. "
        "The B-to-foot main member remains the compression-only nonlinear buffer because the paper does "
        "not publish a telescopic absorber CAD topology."
    )
    proxy["stage"] = "Stage 3C"
    proxy["main_guide_model"] = "disabled_for_rigid_body_link_diagnostic"
    proxy["brace_model"] = "rigid_body_spherical_links"
    proxy["mechanism_elements_per_leg"] = {
        "main_guide": "disabled; finite-mass support rods plus main buffer define the diagnostic footpad motion",
        "main_buffer": "ChLinkTSDA from B attachment to footpad center; nonlinear compression-only force law",
        "long_brace": "ChBodyEasyCylinder finite-mass rod with ChLinkMateSpherical at T and footpad P",
        "short_brace": "ChBodyEasyCylinder finite-mass rod with ChLinkMateSpherical at K and footpad P",
        "footpad": "ChBodyEasySphere with SMC contact/friction",
    }
    proxy["rigid_body_links"] = {
        "source": "Mass/inertia are engineering placeholders derived from Thies total landing-leg mass because rod-level masses are not published.",
        "rod_radius_m": 0.08,
        "rod_total_mass_per_leg_kg": 0.35 * float(config["legs"].get("leg_structure_mass_per_leg_kg", 536.0)),
        "mass_split": {"long_brace": 0.58, "short_brace": 0.42},
        "collision": False,
        "visualization": True,
        "force_output": "joint reaction forces are recorded where exposed by PyChrono; axial brace force is not claimed as validated rod load",
    }
    proxy["brace_force_output"] = "joint-reaction diagnostic from ChLinkMateSpherical where available; not a published rod load validation"
    config["parameter_audit"]["published_values"].append("Stage 3C rigid body brace rest lengths still use Thies 2022 Table 4 strut lengths")
    config["parameter_audit"]["explicit_assumptions"].extend(
        [
            "Stage 3C rod radius and rod mass split are engineering placeholders because Thies does not publish rod CAD, masses, or inertias.",
            "Stage 3C disables the main prismatic guide and keeps the B-to-foot member as a TSDA buffer because the telescopic absorber hinge topology is not published.",
            "Stage 3C finite-mass rod bodies are an open-source mechanism diagnostic, not an Adams-equivalent CAD replica.",
        ]
    )
    attach_parameter_provenance(config)
    return config


def tripod_actuated_lock_model_config() -> dict[str, Any]:
    config = tripod_leg_model_config()
    config["model_id"] = "ChronoLeggedRecovery_Stage3A_ActuatedLock"
    config["solver"]["post_touchdown_lock_logic"] = {
        "mode": "actuated_body_deck_fix",
        "stable_dwell_s": 1.0,
        "vertical_velocity_limit_m_s": 0.05,
        "angular_rate_limit_deg_s": 0.25,
        "constraint": "ChLinkMateFix between rocket and prescribed deck, initialized at the current rocket pose",
        "scope_note": "This is an open-source locking proxy for post-touchdown securing; it is not a published hardware clamp model.",
    }
    config["legs"]["stage3_tripod_proxy"]["stage"] = "Stage 3A-lock"
    config["parameter_audit"]["explicit_assumptions"].append(
        "Actuated lock uses a ChLinkMateFix rocket-to-deck constraint after the diagnostic stability window; no published clamp geometry or actuator timing is available."
    )
    attach_parameter_provenance(config)
    return config


def load_thies_digitized_buffer_law(path: Path = THIES_DIGITIZED_BUFFER_JSON) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = read_json(path)
    law = data.get("chrono_buffer_law")
    if not isinstance(law, dict):
        return None
    if law.get("type") != "compression_only_table":
        return None
    if not law.get("force_stroke_points") or not law.get("force_velocity_points"):
        return None
    out = dict(law)
    out["source_json"] = str(path.relative_to(ROOT).as_posix())
    return out


def apply_thies_digitized_buffer_law(config: dict[str, Any], *, required: bool = False) -> bool:
    law = load_thies_digitized_buffer_law()
    if law is None:
        if required:
            raise FileNotFoundError(
                f"Missing digitized Thies buffer law: {THIES_DIGITIZED_BUFFER_JSON}. "
                "Run thies_buffer_digitization.py report first."
            )
        return False
    config["legs"]["nonlinear_buffer_law"] = law
    config["parameter_audit"]["published_values"].append(
        "main-buffer nonlinear force-stroke and force-velocity curves digitized from Thies 2022 Figures 4 and 5"
    )
    config["parameter_audit"]["explicit_assumptions"].append(
        "Digitized Thies buffer law still uses a numerical hard-stop guard beyond the visible Figure 4 stroke range."
    )
    attach_parameter_provenance(config)
    return True


def iter_config_leaves(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    if prefix in {"parameter_audit", "parameter_provenance"}:
        return []
    if isinstance(value, dict):
        rows: list[tuple[str, Any]] = []
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(iter_config_leaves(child, child_prefix))
        return rows
    if isinstance(value, list):
        if not value:
            return [(prefix, value)]
        if all(not isinstance(item, (dict, list)) for item in value):
            return [(prefix, value)]
        rows = []
        for idx, child in enumerate(value):
            rows.extend(iter_config_leaves(child, f"{prefix}[{idx}]"))
        return rows
    return [(prefix, value)]


def classify_parameter_source(path: str, value: Any) -> tuple[str, str]:
    if path.endswith(".source") or "source" in path:
        return "source_metadata", "Source description embedded in the configuration."
    if path.startswith("rocket.") or path.startswith("legs.upper_attachment") or path.startswith("legs.lower_attachment"):
        return "paper", "Thies 2022 RETALT1 values or labels unless the path is separately classified as an assumption."
    if path.startswith("legs.leg_length") or path.startswith("legs.count") or path.startswith("legs.configuration"):
        return "paper", "Thies 2022 landing-leg geometry."
    if path.startswith("legs.damper_stiffness") or path.startswith("legs.damper_damping"):
        return "paper", "Thies 2022 linear damper values."
    if path.startswith("legs.stroke_reference") or path.startswith("legs.force_reference"):
        return "paper", "Thies 2022 reported dimensioning result."
    if path.startswith("contact.static_friction") or path.startswith("validation_targets.max_incident_angle"):
        return "paper", "Thies 2022 landing requirement."
    if path.startswith("contact.normal_"):
        return "paper_proxy", "Value transcribed from Thies 2022 Table 9, but its use as each footpad's local SMC penalty coefficient is an implementation proxy rather than a published contact-material law."
    if path.startswith("contact.dynamic_friction") or path.startswith("legs.footpad_radius"):
        return "paper_proxy", "Li 2025 footpad radius/dynamic friction used only where Thies does not publish the value."
    if path.startswith("validation_targets.computed_touchdown_energy") or path.startswith("legs.footprint_radius"):
        return "computed", "Computed from published input values."
    if path.startswith("legs.stage3_tripod_proxy.geometry_closure_error"):
        return "computed", "Computed closure error from the Stage 3 proxy geometry."
    if path.startswith("legs.stage3_tripod_proxy.target_lengths") or path.startswith("legs.stage3_tripod_proxy.attachment_height"):
        return "paper", "Thies 2022 Table 4 geometry."
    if path.startswith("legs.stage3_tripod_proxy.attachment_radial") or path.startswith("legs.stage3_tripod_proxy.attachment_tangential"):
        return "engineering_assumption", "Proxy geometry closure because full 3D hinge coordinates are not published."
    if path.startswith("solver.time_step") or path.startswith("solver.output_step") or path.startswith("solver.start") or path.startswith("solver.end"):
        return "solver_setting", "Numerical integration/reporting setting."
    if path.startswith("solver.post_touchdown_lock_logic"):
        return "engineering_assumption", "Open-source lock proxy setting; no published clamp hardware model."
    if path.startswith("solver.") or path.startswith("model_id"):
        return "implementation_setting", "Open-source implementation setting."
    if path.startswith("legs.azimuths") or path.startswith("legs.footpad_mass") or path.startswith("legs.footpad_thickness"):
        return "engineering_assumption", "Transparent placeholder because exact CAD/azimuth values are not published."
    if path.startswith("legs.damper_rest_length"):
        return "computed", "Computed proxy rest length from published/assumed geometry."
    if path.startswith("legs.equivalent_guidance_model"):
        return "implementation_assumption", "Chrono proxy model choice."
    if path.startswith("legs.nonlinear_buffer_law.force_stroke_points") or path.startswith("legs.nonlinear_buffer_law.force_velocity_points"):
        if value:
            return "paper", "Digitized from Thies 2022 Figures 4 and 5."
        return "engineering_assumption", "Empty table interface until measured/digitized buffer curves are available."
    if path.startswith("legs.nonlinear_buffer_law.digitization") or path.startswith("legs.nonlinear_buffer_law.source_json"):
        return "source_metadata", "Digitized buffer-curve provenance metadata."
    if path.startswith("legs.nonlinear_buffer_law.hard_stop"):
        return "engineering_assumption", "Hard stop or empty table interface until measured/digitized buffer curves are available."
    if path.startswith("legs.nonlinear_buffer_law"):
        return "implementation_setting", "Buffer-law implementation interface."
    if path.startswith("legs.stage3_tripod_proxy.brace_axial"):
        return "engineering_assumption", "Axial brace stiffness/damping placeholder until rod properties are available."
    if path.startswith("legs.stage3_tripod_proxy.") or path.startswith("contact.young") or path.startswith("contact.poisson"):
        return "engineering_assumption", "Chrono material/mechanism proxy setting because the exact value is not published."
    if path.startswith("contact.restitution"):
        return "engineering_assumption", "Conservative non-bouncing contact assumption."
    if path.startswith("validation_targets."):
        return "paper", "Published validation target or tolerance derived from published values."
    return "to_verify", "No explicit rule matched this path; review before claiming as reproduced."


def attach_parameter_provenance(config: dict[str, Any]) -> dict[str, Any]:
    rows = []
    category_counts: dict[str, int] = {}
    for path, value in iter_config_leaves(config):
        category, detail = classify_parameter_source(path, value)
        category_counts[category] = category_counts.get(category, 0) + 1
        rows.append(
            {
                "path": path,
                "value": value,
                "source_category": category,
                "source_detail": detail,
            }
        )
    config["parameter_provenance"] = {
        "schema_version": 1,
        "coverage": "all scalar/list leaves in config except parameter_audit and parameter_provenance",
        "parameter_count": len(rows),
        "category_counts": category_counts,
        "parameters": rows,
    }
    return config


@dataclass
class DeckMotion:
    time_s: np.ndarray
    heave_m: np.ndarray
    roll_rad: np.ndarray
    pitch_rad: np.ndarray
    heave_m_s: np.ndarray
    roll_rad_s: np.ndarray
    pitch_rad_s: np.ndarray
    surge_m: np.ndarray | None = None
    sway_m: np.ndarray | None = None
    yaw_rad: np.ndarray | None = None
    surge_m_s: np.ndarray | None = None
    sway_m_s: np.ndarray | None = None
    yaw_rad_s: np.ndarray | None = None
    offset_x_m: float = 0.0
    offset_y_m: float = 0.0

    def _hermite_pair(
        self,
        t: float,
        positions: np.ndarray | None,
        velocities: np.ndarray | None,
    ) -> tuple[float, float]:
        """Interpolate a prescribed coordinate with position/velocity consistency."""

        if positions is None or velocities is None:
            return 0.0, 0.0
        time = np.asarray(self.time_s, dtype=float)
        position = np.asarray(positions, dtype=float)
        velocity = np.asarray(velocities, dtype=float)
        if time.ndim != 1 or time.size < 2 or position.shape != time.shape or velocity.shape != time.shape:
            raise ValueError("Deck-motion time, position and velocity arrays must have equal one-dimensional shape.")
        if t <= float(time[0]):
            return float(position[0]), float(velocity[0])
        if t >= float(time[-1]):
            return float(position[-1]), float(velocity[-1])
        right = int(np.searchsorted(time, t, side="right"))
        left = right - 1
        h = float(time[right] - time[left])
        if h <= 0.0:
            raise ValueError("Deck-motion times must be strictly increasing.")
        u = (float(t) - float(time[left])) / h
        u2 = u * u
        u3 = u2 * u
        h00 = 2.0 * u3 - 3.0 * u2 + 1.0
        h10 = u3 - 2.0 * u2 + u
        h01 = -2.0 * u3 + 3.0 * u2
        h11 = u3 - u2
        value = (
            h00 * float(position[left])
            + h10 * h * float(velocity[left])
            + h01 * float(position[right])
            + h11 * h * float(velocity[right])
        )
        derivative = (
            (6.0 * u2 - 6.0 * u) * float(position[left]) / h
            + (3.0 * u2 - 4.0 * u + 1.0) * float(velocity[left])
            + (-6.0 * u2 + 6.0 * u) * float(position[right]) / h
            + (3.0 * u2 - 2.0 * u) * float(velocity[right])
        )
        return value, derivative

    def sample(self, t: float) -> dict[str, float]:
        surge, surge_rate = self._hermite_pair(t, self.surge_m, self.surge_m_s)
        sway, sway_rate = self._hermite_pair(t, self.sway_m, self.sway_m_s)
        heave, heave_rate = self._hermite_pair(t, self.heave_m, self.heave_m_s)
        roll, roll_rate = self._hermite_pair(t, self.roll_rad, self.roll_rad_s)
        pitch, pitch_rate = self._hermite_pair(t, self.pitch_rad, self.pitch_rad_s)
        yaw, yaw_rate = self._hermite_pair(t, self.yaw_rad, self.yaw_rad_s)
        return {
            "surge_m": surge,
            "sway_m": sway,
            "heave_m": heave,
            "roll_rad": roll,
            "pitch_rad": pitch,
            "yaw_rad": yaw,
            "surge_m_s": surge_rate,
            "sway_m_s": sway_rate,
            "heave_m_s": heave_rate,
            "roll_rad_s": roll_rate,
            "pitch_rad_s": pitch_rate,
            "yaw_rad_s": yaw_rate,
        }

    def deck_xy(self, t: float, x_local_m: float, y_local_m: float) -> tuple[float, float]:
        row = self.sample(t)
        yaw = row["yaw_rad"]
        c = math.cos(yaw)
        s = math.sin(yaw)
        return (
            row["surge_m"] + c * x_local_m - s * y_local_m,
            row["sway_m"] + s * x_local_m + c * y_local_m,
        )

    def deck_z(self, t: float, x_m: float, y_m: float) -> float:
        row = self.sample(t)
        dx = x_m - row["surge_m"]
        dy = y_m - row["sway_m"]
        yaw = row["yaw_rad"]
        c = math.cos(yaw)
        s = math.sin(yaw)
        local_x = c * dx + s * dy
        local_y = -s * dx + c * dy
        return row["heave_m"] + row["roll_rad"] * local_y - row["pitch_rad"] * local_x


def chrono_vec(chrono: Any, x: float, y: float, z: float) -> Any:
    if hasattr(chrono, "ChVector3d"):
        return chrono.ChVector3d(float(x), float(y), float(z))
    if hasattr(chrono, "ChVectorD"):
        return chrono.ChVectorD(float(x), float(y), float(z))
    raise ChronoUnavailableError("Cannot find Chrono vector constructor.")


def chrono_quat_from_roll_pitch_yaw(chrono: Any, roll_rad: float, pitch_rad: float, yaw_rad: float) -> Any:
    cr = math.cos(roll_rad * 0.5)
    sr = math.sin(roll_rad * 0.5)
    cp = math.cos(pitch_rad * 0.5)
    sp = math.sin(pitch_rad * 0.5)
    cy = math.cos(yaw_rad * 0.5)
    sy = math.sin(yaw_rad * 0.5)
    # Rotation order Rx(roll), Ry(pitch), then Rz(yaw), z-up.
    e0 = cr * cp * cy - sr * sp * sy
    e1 = sr * cp * cy + cr * sp * sy
    e2 = cr * sp * cy - sr * cp * sy
    e3 = cr * cp * sy + sr * sp * cy
    for name in ("ChQuaterniond", "ChQuaternionD"):
        if hasattr(chrono, name):
            return getattr(chrono, name)(e0, e1, e2, e3)
    raise ChronoUnavailableError("Cannot find Chrono quaternion constructor.")


def chrono_quat_from_roll_pitch(chrono: Any, roll_rad: float, pitch_rad: float) -> Any:
    return chrono_quat_from_roll_pitch_yaw(chrono, roll_rad, pitch_rad, 0.0)


def chrono_quat_from_z_axis(chrono: Any, axis_xyz: tuple[float, float, float]) -> Any:
    ax = [float(axis_xyz[0]), float(axis_xyz[1]), float(axis_xyz[2])]
    norm = math.sqrt(ax[0] ** 2 + ax[1] ** 2 + ax[2] ** 2)
    if norm <= 1.0e-12:
        return getattr(chrono, "QUNIT", None)
    v = [ax[0] / norm, ax[1] / norm, ax[2] / norm]
    dot = max(-1.0, min(1.0, v[2]))
    if dot > 1.0 - 1.0e-12:
        return getattr(chrono, "QUNIT", None)
    if dot < -1.0 + 1.0e-12:
        for name in ("ChQuaterniond", "ChQuaternionD"):
            if hasattr(chrono, name):
                return getattr(chrono, name)(0.0, 1.0, 0.0, 0.0)
    cross = [-v[1], v[0], 0.0]
    quat = [1.0 + dot, cross[0], cross[1], cross[2]]
    qnorm = math.sqrt(sum(value * value for value in quat))
    quat = [value / qnorm for value in quat]
    for name in ("ChQuaterniond", "ChQuaternionD"):
        if hasattr(chrono, name):
            return getattr(chrono, name)(float(quat[0]), float(quat[1]), float(quat[2]), float(quat[3]))
    raise ChronoUnavailableError("Cannot find Chrono quaternion constructor.")


def nozzle_clearance_from_base(config: dict[str, Any], base_clearance_m: float) -> float:
    """Return the proxy nozzle-end clearance relative to the local moving deck."""
    offset = float(config["rocket"].get("stage3_proxy_nozzle_reference_height_from_model_base_m", 0.0))
    return float(base_clearance_m + offset)


def body_pos(body: Any) -> tuple[float, float, float]:
    p = body.GetPos()
    return (float(p.x), float(p.y), float(p.z))


def body_vel(body: Any) -> tuple[float, float, float]:
    if hasattr(body, "GetPosDt"):
        v = body.GetPosDt()
    else:
        v = body.GetLinVel()
    return (float(v.x), float(v.y), float(v.z))


def body_ang_vel(body: Any) -> tuple[float, float, float]:
    if hasattr(body, "GetAngVelParent"):
        v = body.GetAngVelParent()
    else:
        v = body.GetAngVelLocal()
    return (float(v.x), float(v.y), float(v.z))


def body_euler_zyx(body: Any) -> tuple[float, float, float]:
    q = body.GetRot()
    w, x, y, z = float(q.e0), float(q.e1), float(q.e2), float(q.e3)
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)
    sinp = 2.0 * (w * y - z * x)
    pitch = math.copysign(math.pi / 2.0, sinp) if abs(sinp) >= 1.0 else math.asin(sinp)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw


def point_in_body_local(body: Any, point_xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    p = body_pos(body)
    q = body.GetRot()
    w, x, y, z = float(q.e0), float(q.e1), float(q.e2), float(q.e3)
    dx = point_xyz[0] - p[0]
    dy = point_xyz[1] - p[1]
    dz = point_xyz[2] - p[2]
    r00 = 1.0 - 2.0 * (y * y + z * z)
    r01 = 2.0 * (x * y - z * w)
    r02 = 2.0 * (x * z + y * w)
    r10 = 2.0 * (x * y + z * w)
    r11 = 1.0 - 2.0 * (x * x + z * z)
    r12 = 2.0 * (y * z - x * w)
    r20 = 2.0 * (x * z - y * w)
    r21 = 2.0 * (y * z + x * w)
    r22 = 1.0 - 2.0 * (x * x + y * y)
    # Inverse rotation for a unit quaternion is R^T.
    return (
        r00 * dx + r10 * dy + r20 * dz,
        r01 * dx + r11 * dy + r21 * dz,
        r02 * dx + r12 * dy + r22 * dz,
    )


def point_from_body_local(body: Any, chrono: Any, local_xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    if hasattr(body, "TransformPointLocalToParent"):
        p = body.TransformPointLocalToParent(chrono_vec(chrono, *local_xyz))
        return (float(p.x), float(p.y), float(p.z))
    origin = body_pos(body)
    return (origin[0] + float(local_xyz[0]), origin[1] + float(local_xyz[1]), origin[2] + float(local_xyz[2]))


def distance_between_body_points(
    body_a: Any,
    body_b: Any,
    chrono: Any,
    local_a_xyz: tuple[float, float, float],
    local_b_xyz: tuple[float, float, float],
) -> float:
    pa = point_from_body_local(body_a, chrono, local_a_xyz)
    pb = point_from_body_local(body_b, chrono, local_b_xyz)
    return math.sqrt((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2 + (pa[2] - pb[2]) ** 2)


def set_body_velocity(body: Any, chrono: Any, vx: float, vy: float, vz: float) -> None:
    value = chrono_vec(chrono, vx, vy, vz)
    if hasattr(body, "SetPosDt"):
        body.SetPosDt(value)
    elif hasattr(body, "SetLinVel"):
        body.SetLinVel(value)
    else:  # pragma: no cover - Chrono version dependent
        raise ChronoUnavailableError("Cannot set body linear velocity with this PyChrono API.")


def set_body_angular_velocity(body: Any, chrono: Any, wx: float, wy: float, wz: float) -> None:
    value = chrono_vec(chrono, wx, wy, wz)
    if hasattr(body, "SetAngVelParent"):
        body.SetAngVelParent(value)
    elif hasattr(body, "SetWvel_par"):
        body.SetWvel_par(value)


def set_body_fixed(body: Any, fixed: bool) -> None:
    if hasattr(body, "SetFixed"):
        body.SetFixed(fixed)
    elif hasattr(body, "SetBodyFixed"):
        body.SetBodyFixed(fixed)
    else:  # pragma: no cover - Chrono version dependent
        raise ChronoUnavailableError("Cannot set body fixed state with this PyChrono API.")


def enable_collision(body: Any, enabled: bool) -> None:
    if hasattr(body, "EnableCollision"):
        body.EnableCollision(enabled)
    elif hasattr(body, "SetCollide"):
        body.SetCollide(enabled)


def add_to_system(system: Any, item: Any) -> None:
    if hasattr(system, "Add"):
        system.Add(item)
    elif hasattr(system, "AddBody"):
        system.AddBody(item)
    else:  # pragma: no cover - Chrono version dependent
        raise ChronoUnavailableError("Cannot add item to Chrono system.")


def make_contact_material(chrono: Any, config: dict[str, Any]) -> Any:
    material_cls = getattr(chrono, "ChContactMaterialSMC", None) or getattr(chrono, "ChMaterialSurfaceSMC", None)
    if material_cls is None:
        raise ChronoUnavailableError("Cannot find Chrono SMC contact material class.")
    material = material_cls()
    contact = config["contact"]
    foot_mass = float(config["legs"]["footpad_mass_kg"])
    deck_mass = 180.0 * 54.0 * float(config["solver"]["deck_thickness_m"]) * 1000.0
    reference_effective_mass = foot_mass * deck_mass / (foot_mass + deck_mass)
    damping_rate_s_inv = float(contact["normal_damping_ns_m"]) / reference_effective_mass
    for method, value in [
        ("SetKn", contact["normal_stiffness_n_m"]),
        ("SetKt", contact["normal_stiffness_n_m"]),
        ("SetGn", damping_rate_s_inv),
        ("SetGt", damping_rate_s_inv),
        ("SetYoungModulus", contact["young_modulus_pa"]),
        ("SetPoissonRatio", contact["poisson_ratio"]),
        ("SetFriction", contact["static_friction"]),
        ("SetStaticFriction", contact["static_friction"]),
        ("SetSlidingFriction", contact["dynamic_friction"]),
        ("SetRestitution", contact["restitution"]),
    ]:
        if hasattr(material, method):
            getattr(material, method)(float(value))
    return material


def explicit_smc_contact_audit(config: dict[str, Any]) -> dict[str, Any]:
    """Describe the coefficients actually consumed by Chrono's explicit Hooke law."""

    foot_mass = float(config["legs"]["footpad_mass_kg"])
    deck_mass = 180.0 * 54.0 * float(config["solver"]["deck_thickness_m"]) * 1000.0
    effective_mass = foot_mass * deck_mass / (foot_mass + deck_mass)
    desired_damping = float(config["contact"]["normal_damping_ns_m"])
    damping_rate = desired_damping / effective_mass
    return {
        "coefficient_mode": config["solver"].get("contact_coefficient_mode"),
        "normal_force_law": "Fn=max(0, kn*delta - m_eff*gn*v_n)",
        "normal_stiffness_kn_n_m": float(config["contact"]["normal_stiffness_n_m"]),
        "configured_normal_damping_cn_ns_m": desired_damping,
        "reference_foot_mass_kg": foot_mass,
        "fixed_deck_collision_body_mass_kg": deck_mass,
        "reference_effective_contact_mass_kg": effective_mass,
        "material_Gn_s_inv": damping_rate,
        "recovered_reference_damping_ns_m": effective_mass * damping_rate,
        "source_note": (
            "In explicit Hooke mode Project Chrono multiplies material Gn by the contact-pair effective mass; "
            "Gn is therefore supplied in 1/s after converting the literature damping in N s/m."
        ),
    }


def multibody_mass_audit(config: dict[str, Any]) -> dict[str, Any]:
    published_total = float(config["rocket"]["landing_mass_kg"])
    footpads = float(config["legs"]["count"]) * float(config["legs"]["footpad_mass_kg"])
    rigid_links = config.get("legs", {}).get("stage3_tripod_proxy", {}).get("rigid_body_links", {})
    rods = float(config["legs"]["count"]) * float(rigid_links.get("rod_total_mass_per_leg_kg", 0.0)) if rigid_links else 0.0
    rocket_body = published_total - footpads - rods
    return {
        "published_total_landing_mass_kg": published_total,
        "rocket_body_mass_kg": rocket_body,
        "explicit_footpad_mass_kg": footpads,
        "explicit_rigid_link_mass_kg": rods,
        "reconstructed_total_mass_kg": rocket_body + footpads + rods,
        "mass_residual_kg": rocket_body + footpads + rods - published_total,
        "inertia_scope": (
            "Published vehicle inertia is retained on the central body because component-level inertias are unavailable; "
            "the translational mass is closed exactly, but the inertia allocation remains a declared approximation."
        ),
    }


def make_system(chrono: Any, config: dict[str, Any]) -> Any:
    if not hasattr(chrono, "ChSystemSMC"):
        raise ChronoUnavailableError("PyChrono does not expose ChSystemSMC.")
    system = chrono.ChSystemSMC()
    coefficient_mode = config.get("solver", {}).get("contact_coefficient_mode")
    if coefficient_mode != "explicit_stiffness_damping":
        raise ChronoUnavailableError(
            "The landing model requires solver.contact_coefficient_mode="
            "'explicit_stiffness_damping' so SetKn/SetGn are the active SMC coefficients."
        )
    if not hasattr(system, "UseMaterialProperties"):
        raise ChronoUnavailableError(
            "This PyChrono build cannot disable material-property-derived SMC coefficients."
        )
    system.UseMaterialProperties(False)
    if hasattr(system, "UsingMaterialProperties") and bool(system.UsingMaterialProperties()):
        raise ChronoUnavailableError("PyChrono did not activate explicit SMC stiffness/damping coefficients.")
    gravity = chrono_vec(chrono, 0.0, 0.0, -float(config["solver"]["gravity_m_s2"]))
    if hasattr(system, "SetGravitationalAcceleration"):
        system.SetGravitationalAcceleration(gravity)
    elif hasattr(system, "Set_G_acc"):
        system.Set_G_acc(gravity)
    if hasattr(system, "SetContactForceModel") and hasattr(system, "Hooke"):
        system.SetContactForceModel(system.Hooke)
    if hasattr(system, "SetCollisionSystemType") and hasattr(chrono, "ChCollisionSystem"):
        system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
    if hasattr(system, "SetSolverType") and hasattr(chrono, "ChSolver"):
        system.SetSolverType(chrono.ChSolver.Type_SPARSE_LU)
    if hasattr(system, "SetTimestepperType") and hasattr(chrono, "ChTimestepper"):
        system.SetTimestepperType(chrono.ChTimestepper.Type_EULER_IMPLICIT_LINEARIZED)
    return system


def set_system_gravity(system: Any, chrono: Any, gz: float) -> None:
    gravity = chrono_vec(chrono, 0.0, 0.0, gz)
    if hasattr(system, "SetGravitationalAcceleration"):
        system.SetGravitationalAcceleration(gravity)
    elif hasattr(system, "Set_G_acc"):
        system.Set_G_acc(gravity)


def make_box_body(chrono: Any, size_xyz: tuple[float, float, float], density: float, material: Any, collide: bool) -> Any:
    body = chrono.ChBodyEasyBox(size_xyz[0], size_xyz[1], size_xyz[2], density, True, collide, material)
    enable_collision(body, collide)
    return body


def make_sphere_body(chrono: Any, radius: float, density: float, material: Any, collide: bool) -> Any:
    body = chrono.ChBodyEasySphere(radius, density, True, collide, material)
    enable_collision(body, collide)
    return body


def make_cylinder_rod_body(
    chrono: Any,
    point_a: tuple[float, float, float],
    point_b: tuple[float, float, float],
    radius_m: float,
    mass_kg: float,
    material: Any,
    collide: bool,
) -> Any:
    dx = point_b[0] - point_a[0]
    dy = point_b[1] - point_a[1]
    dz = point_b[2] - point_a[2]
    length = max(1.0e-6, math.sqrt(dx * dx + dy * dy + dz * dz))
    volume = math.pi * radius_m * radius_m * length
    density = max(1.0, mass_kg / max(volume, 1.0e-12))
    body = chrono.ChBodyEasyCylinder(chrono.ChAxis_Z, radius_m, length, density, True, collide, material)
    body.SetMass(float(mass_kg))
    body.SetPos(
        chrono_vec(
            chrono,
            0.5 * (point_a[0] + point_b[0]),
            0.5 * (point_a[1] + point_b[1]),
            0.5 * (point_a[2] + point_b[2]),
        )
    )
    body.SetRot(chrono_quat_from_z_axis(chrono, (dx, dy, dz)))
    enable_collision(body, collide)
    return body


def make_rocket_body(chrono: Any, config: dict[str, Any], material: Any) -> Any:
    rocket = config["rocket"]
    # Collision on the rocket body is disabled; footpads own the ground contact.
    body = chrono.ChBody()
    published_total_mass = float(rocket["landing_mass_kg"])
    explicit_child_mass = float(config["legs"]["count"]) * float(config["legs"]["footpad_mass_kg"])
    rigid_links = config.get("legs", {}).get("stage3_tripod_proxy", {}).get("rigid_body_links", {})
    if rigid_links:
        explicit_child_mass += float(config["legs"]["count"]) * float(rigid_links.get("rod_total_mass_per_leg_kg", 0.0))
    if rocket.get("mass_allocation") != "published_total_less_explicit_multibody_children":
        raise ChronoUnavailableError("Rocket mass allocation must prevent explicit child bodies from double-counting published landing mass.")
    rocket_body_mass = published_total_mass - explicit_child_mass
    if rocket_body_mass <= 0.0:
        raise ChronoUnavailableError("Explicit multibody child mass exceeds the published landing mass.")
    body.SetMass(rocket_body_mass)
    body.SetInertiaXX(
        chrono_vec(
            chrono,
            float(rocket["inertia_kg_m2"]["roll_x"]),
            float(rocket["inertia_kg_m2"]["pitch_y"]),
            float(rocket["inertia_kg_m2"]["yaw_z"]),
        )
    )
    enable_collision(body, False)
    return body


def make_tsda(chrono: Any, rocket_body: Any, foot_body: Any, rocket_anchor: Any, foot_anchor: Any, config: dict[str, Any]) -> Any:
    if not hasattr(chrono, "ChLinkTSDA"):
        raise ChronoUnavailableError("PyChrono does not expose ChLinkTSDA.")
    leg = config["legs"]
    link = chrono.ChLinkTSDA()
    link.Initialize(rocket_body, foot_body, False, rocket_anchor, foot_anchor)
    link.SetRestLength(float(leg["damper_rest_length_m"]))
    link.SetSpringCoefficient(float(leg["damper_stiffness_n_m"]))
    link.SetDampingCoefficient(float(leg["damper_damping_ns_m"]))
    if hasattr(link, "IsStiff"):
        link.IsStiff(True)
    return link


def make_nonlinear_tsda(chrono: Any, rocket_body: Any, foot_body: Any, rocket_anchor_rel: Any, foot_anchor_rel: Any, config: dict[str, Any]) -> tuple[Any, Any]:
    if not hasattr(chrono, "ChLinkTSDA") or not hasattr(chrono, "ForceFunctor"):
        raise ChronoUnavailableError("PyChrono does not expose ChLinkTSDA ForceFunctor support.")
    law = config["legs"]["nonlinear_buffer_law"]

    def sorted_xy(points: list[dict[str, float]], x_key: str, y_key: str) -> tuple[list[float], list[float]]:
        rows = sorted((float(row[x_key]), float(row[y_key])) for row in points)
        return [row[0] for row in rows], [row[1] for row in rows]

    stroke_x, stroke_y = sorted_xy(law.get("force_stroke_points", []), "stroke_m", "force_n")
    velocity_x, velocity_y = sorted_xy(law.get("force_velocity_points", []), "velocity_m_s", "force_n")

    def table_value(xs: list[float], ys: list[float], value: float) -> float:
        if not xs:
            return 0.0
        if value <= xs[0]:
            return ys[0]
        if value >= xs[-1]:
            return ys[-1]
        idx = bisect.bisect_left(xs, value)
        x0, x1 = xs[idx - 1], xs[idx]
        y0, y1 = ys[idx - 1], ys[idx]
        if abs(x1 - x0) <= 1.0e-12:
            return y1
        ratio = (value - x0) / (x1 - x0)
        return y0 + ratio * (y1 - y0)

    class CompressionOnlyBuffer(chrono.ForceFunctor):
        def __init__(self) -> None:
            super().__init__()

        def evaluate(self, time: float, rest_length: float, length: float, vel: float, link: Any) -> float:
            compression = max(0.0, rest_length - length)
            compression_rate = max(0.0, -vel)
            if law["type"] == "compression_only_table":
                force = table_value(stroke_x, stroke_y, compression)
                force += table_value(velocity_x, velocity_y, compression_rate)
            else:
                force = float(law["linear_stiffness_n_m"]) * compression + float(law["linear_damping_ns_m"]) * compression_rate
            excess = max(0.0, compression - float(law["stroke_limit_m"]))
            if excess > 0.0:
                force += float(law["hard_stop_stiffness_n_m"]) * excess + float(law["hard_stop_damping_ns_m"]) * compression_rate
            return max(0.0, force)

    functor = CompressionOnlyBuffer()
    link = chrono.ChLinkTSDA()
    link.Initialize(rocket_body, foot_body, True, rocket_anchor_rel, foot_anchor_rel)
    link.SetRestLength(float(law.get("rest_length_m", config["legs"]["damper_rest_length_m"])))
    link.RegisterForceFunctor(functor)
    if hasattr(link, "IsStiff"):
        link.IsStiff(True)
    return link, functor


def make_distance_brace(chrono: Any, rocket_body: Any, foot_body: Any, rocket_anchor_rel: Any, foot_anchor_rel: Any, length_m: float) -> Any:
    if not hasattr(chrono, "ChLinkDistance"):
        raise ChronoUnavailableError("PyChrono does not expose ChLinkDistance.")
    link = chrono.ChLinkDistance()
    link.Initialize(rocket_body, foot_body, True, rocket_anchor_rel, foot_anchor_rel, False, float(length_m))
    return link


def make_spherical_mate(chrono: Any, body_a: Any, body_b: Any, point_abs: tuple[float, float, float]) -> Any:
    if not hasattr(chrono, "ChLinkMateSpherical"):
        raise ChronoUnavailableError("PyChrono does not expose ChLinkMateSpherical.")
    link = chrono.ChLinkMateSpherical()
    link.Initialize(body_a, body_b, chrono.ChFramed(chrono_vec(chrono, *point_abs), getattr(chrono, "QUNIT", None)))
    return link


def make_spherical_mate_relative(chrono: Any, body_a: Any, body_b: Any, point_a_rel: Any, point_b_rel: Any) -> Any:
    if not hasattr(chrono, "ChLinkMateSpherical"):
        raise ChronoUnavailableError("PyChrono does not expose ChLinkMateSpherical.")
    link = chrono.ChLinkMateSpherical()
    link.Initialize(body_a, body_b, True, point_a_rel, point_b_rel)
    return link


def make_oriented_prismatic_guide(
    chrono: Any,
    rocket_body: Any,
    foot_body: Any,
    foot_anchor_abs: tuple[float, float, float],
    guide_axis_abs: tuple[float, float, float],
) -> Any:
    if hasattr(chrono, "ChLinkMatePrismatic"):
        link = chrono.ChLinkMatePrismatic()
        frame = chrono.ChFramed(chrono_vec(chrono, *foot_anchor_abs), chrono_quat_from_z_axis(chrono, guide_axis_abs))
        link.Initialize(foot_body, rocket_body, frame)
        return link
    if hasattr(chrono, "ChLinkLockPrismatic"):
        link = chrono.ChLinkLockPrismatic()
        frame = chrono.ChFramed(chrono_vec(chrono, *foot_anchor_abs), chrono_quat_from_z_axis(chrono, guide_axis_abs))
        link.Initialize(foot_body, rocket_body, frame)
        return link
    raise ChronoUnavailableError("PyChrono does not expose a prismatic mate/link for guided footpads.")


def make_elastic_brace_tsda(
    chrono: Any,
    rocket_body: Any,
    foot_body: Any,
    rocket_anchor_rel: Any,
    foot_anchor_rel: Any,
    rest_length_m: float,
    stiffness_n_m: float,
    damping_ns_m: float,
) -> Any:
    if not hasattr(chrono, "ChLinkTSDA"):
        raise ChronoUnavailableError("PyChrono does not expose ChLinkTSDA.")
    link = chrono.ChLinkTSDA()
    link.Initialize(rocket_body, foot_body, True, rocket_anchor_rel, foot_anchor_rel)
    link.SetRestLength(float(rest_length_m))
    link.SetSpringCoefficient(float(stiffness_n_m))
    link.SetDampingCoefficient(float(damping_ns_m))
    if hasattr(link, "IsStiff"):
        link.IsStiff(True)
    return link


def make_body_deck_lock(chrono: Any, rocket_body: Any, deck_body: Any) -> Any:
    if hasattr(chrono, "ChLinkMateFix"):
        link = chrono.ChLinkMateFix()
        link.Initialize(rocket_body, deck_body, chrono.ChFramed(rocket_body.GetPos(), rocket_body.GetRot()))
        return link
    if hasattr(chrono, "ChLinkLockLock"):
        link = chrono.ChLinkLockLock()
        link.Initialize(rocket_body, deck_body, chrono.ChFramed(rocket_body.GetPos(), rocket_body.GetRot()))
        return link
    raise ChronoUnavailableError("PyChrono does not expose a fixed body-to-deck lock link.")


def make_vertical_prismatic_guide(chrono: Any, rocket_body: Any, foot_body: Any, foot_anchor: Any) -> Any:
    if hasattr(chrono, "ChLinkMatePrismatic"):
        link = chrono.ChLinkMatePrismatic()
        link.Initialize(foot_body, rocket_body, chrono.ChFramed(foot_anchor, getattr(chrono, "QUNIT", None)))
        return link
    if hasattr(chrono, "ChLinkLockPrismatic"):
        link = chrono.ChLinkLockPrismatic()
        link.Initialize(foot_body, rocket_body, chrono.ChFramed(foot_anchor, getattr(chrono, "QUNIT", None)))
        return link
    raise ChronoUnavailableError("PyChrono does not expose a prismatic mate/link for guided footpads.")


class ChronoOneWayLegModel:
    def __init__(self, config: dict[str, Any], deck_motion: DeckMotion) -> None:
        self.config = config
        self.deck_motion = deck_motion
        self.chrono = import_pychrono()

    def run(self) -> dict[str, Any]:  # pragma: no cover - exercised only when PyChrono is installed
        chrono = self.chrono
        config = self.config
        system = make_system(chrono, config)
        material = make_contact_material(chrono, config)

        deck_thickness = float(config["solver"]["deck_thickness_m"])
        deck = make_box_body(chrono, (180.0, 54.0, deck_thickness), 1000.0, material, True)
        set_body_fixed(deck, True)
        add_to_system(system, deck)

        rocket = make_rocket_body(chrono, config, material)
        leg_rows = leg_positions_from_config(config)
        touchdown = 510.0
        cg = float(config["rocket"]["cog_from_base_m"])
        foot_radius = float(config["legs"]["footpad_radius_m"])
        touchdown_v = float(config["rocket"]["touchdown_vertical_velocity_m_s"])
        target_x, target_y = self.deck_motion.deck_xy(touchdown, self.deck_motion.offset_x_m, self.deck_motion.offset_y_m)
        deck_touch_z = self.deck_motion.deck_z(touchdown, target_x, target_y)
        start = float(config["solver"]["start_s"])
        initial_z = deck_touch_z + cg + foot_radius + touchdown_v * (touchdown - start)
        rocket.SetPos(chrono_vec(chrono, target_x, target_y, initial_z))
        set_body_velocity(rocket, chrono, 0.0, 0.0, -touchdown_v)
        add_to_system(system, rocket)

        feet: dict[str, Any] = {}
        springs: dict[str, Any] = {}
        foot_density = max(1.0, float(config["legs"]["footpad_mass_kg"]) / (4.0 / 3.0 * math.pi * float(config["legs"]["footpad_radius_m"]) ** 3))
        for leg in leg_rows:
            foot = make_sphere_body(chrono, foot_radius, foot_density, material, True)
            foot.SetMass(float(config["legs"]["footpad_mass_kg"]))
            foot_anchor_abs = chrono_vec(
                chrono,
                *self.deck_motion.deck_xy(touchdown, self.deck_motion.offset_x_m + leg["x_m"], self.deck_motion.offset_y_m + leg["y_m"]),
                initial_z - cg + foot_radius,
            )
            foot.SetPos(
                foot_anchor_abs
            )
            set_body_velocity(foot, chrono, 0.0, 0.0, -touchdown_v)
            add_to_system(system, foot)
            feet[leg["id"]] = foot
            guide = make_vertical_prismatic_guide(chrono, rocket, foot, foot_anchor_abs)
            add_to_system(system, guide)
            rocket_anchor = chrono_vec(
                chrono,
                *self.deck_motion.deck_xy(touchdown, self.deck_motion.offset_x_m + leg["x_m"], self.deck_motion.offset_y_m + leg["y_m"]),
                initial_z - cg + float(config["legs"]["lower_attachment_height_m"]),
            )
            foot_anchor = foot_anchor_abs
            spring = make_tsda(chrono, rocket, foot, rocket_anchor, foot_anchor, config)
            add_to_system(system, spring)
            springs[leg["id"]] = spring

        set_system_gravity(system, chrono, 0.0)
        first_contact_seen = False
        time_s: list[float] = []
        rocket_z: list[float] = []
        rocket_vz: list[float] = []
        rocket_roll: list[float] = []
        rocket_pitch: list[float] = []
        rocket_yaw: list[float] = []
        rocket_roll_rate: list[float] = []
        rocket_pitch_rate: list[float] = []
        rocket_yaw_rate: list[float] = []
        deck_heave: list[float] = []
        deck_surge: list[float] = []
        deck_sway: list[float] = []
        deck_roll: list[float] = []
        deck_pitch: list[float] = []
        deck_yaw: list[float] = []
        deck_surge_velocity: list[float] = []
        deck_sway_velocity: list[float] = []
        deck_heave_velocity: list[float] = []
        deck_roll_rate: list[float] = []
        deck_pitch_rate: list[float] = []
        deck_yaw_rate: list[float] = []
        leg_force: dict[str, list[float]] = {leg["id"]: [] for leg in leg_rows}
        leg_contact_force: dict[str, list[float]] = {leg["id"]: [] for leg in leg_rows}
        leg_contact_force_xyz: dict[str, dict[str, list[float]]] = {
            leg["id"]: {"x": [], "y": [], "z": []} for leg in leg_rows
        }
        leg_stroke: dict[str, list[float]] = {leg["id"]: [] for leg in leg_rows}
        leg_contact_penetration: dict[str, list[float]] = {leg["id"]: [] for leg in leg_rows}
        leg_slip: dict[str, list[float]] = {leg["id"]: [] for leg in leg_rows}
        leg_contact: dict[str, list[int]] = {leg["id"]: [] for leg in leg_rows}
        foot_position: dict[str, dict[str, list[float]]] = {
            leg["id"]: {"x_m": [], "y_m": [], "z_m": []} for leg in leg_rows
        }
        base_clearance: list[float] = []
        nozzle_clearance: list[float] = []

        dt = float(config["solver"]["time_step_s"])
        output_dt = float(config["solver"]["output_step_s"])
        next_output = start - 1.0e-12
        t = start
        end = float(config["solver"]["end_s"])
        gravity = float(config["solver"]["gravity_m_s2"])
        contact_force_threshold = float(config["solver"]["contact_force_threshold_n"])
        step_count_float = (end - start) / dt
        step_count = int(round(step_count_float))
        if not math.isclose(step_count_float, step_count, rel_tol=1.0e-10, abs_tol=1.0e-12):
            raise ValueError("Chrono simulation interval must be an integer multiple of time_step_s.")

        for step_index in range(step_count + 1):
            t = end if step_index == step_count else start + step_index * dt
            deck_state = self.deck_motion.sample(t)
            deck.SetPos(chrono_vec(chrono, deck_state["surge_m"], deck_state["sway_m"], deck_state["heave_m"] - 0.5 * deck_thickness))
            deck.SetRot(
                chrono_quat_from_roll_pitch_yaw(
                    chrono,
                    deck_state["roll_rad"],
                    deck_state["pitch_rad"],
                    deck_state["yaw_rad"],
                )
            )
            set_body_velocity(deck, chrono, deck_state["surge_m_s"], deck_state["sway_m_s"], deck_state["heave_m_s"])
            set_body_angular_velocity(deck, chrono, deck_state["roll_rad_s"], deck_state["pitch_rad_s"], deck_state["yaw_rad_s"])
            if not first_contact_seen:
                first_contact_seen = any(body.GetContactForce().z > contact_force_threshold for body in feet.values())
            if first_contact_seen:
                set_system_gravity(system, chrono, -gravity)

            if t + 1.0e-12 >= next_output:
                rp = body_pos(rocket)
                rv = body_vel(rocket)
                ra = body_ang_vel(rocket)
                rr, rpi, ry = body_euler_zyx(rocket)
                rz = rp[2]
                rvz = body_vel(rocket)[2]
                time_s.append(float(t))
                rocket_z.append(rz)
                rocket_vz.append(rvz)
                rocket_roll.append(rr)
                rocket_pitch.append(rpi)
                rocket_yaw.append(ry)
                rocket_roll_rate.append(ra[0])
                rocket_pitch_rate.append(ra[1])
                rocket_yaw_rate.append(ra[2])
                deck_surge.append(deck_state["surge_m"])
                deck_sway.append(deck_state["sway_m"])
                deck_heave.append(deck_state["heave_m"])
                deck_roll.append(deck_state["roll_rad"])
                deck_pitch.append(deck_state["pitch_rad"])
                deck_yaw.append(deck_state["yaw_rad"])
                deck_surge_velocity.append(deck_state["surge_m_s"])
                deck_sway_velocity.append(deck_state["sway_m_s"])
                deck_heave_velocity.append(deck_state["heave_m_s"])
                deck_roll_rate.append(deck_state["roll_rad_s"])
                deck_pitch_rate.append(deck_state["pitch_rad_s"])
                deck_yaw_rate.append(deck_state["yaw_rad_s"])
                base_gap = rz - cg - self.deck_motion.deck_z(t, rp[0], rp[1])
                base_clearance.append(base_gap)
                nozzle_clearance.append(nozzle_clearance_from_base(config, base_gap))
                for leg in leg_rows:
                    leg_id = leg["id"]
                    fp = body_pos(feet[leg_id])
                    cf = feet[leg_id].GetContactForce()
                    local_deck_z = self.deck_motion.deck_z(t, fp[0], fp[1])
                    penetration = max(0.0, local_deck_z - (fp[2] - foot_radius))
                    stroke = max(0.0, float(config["legs"]["damper_rest_length_m"]) - float(springs[leg_id].GetLength()))
                    foot_position[leg_id]["x_m"].append(fp[0])
                    foot_position[leg_id]["y_m"].append(fp[1])
                    foot_position[leg_id]["z_m"].append(fp[2])
                    leg_stroke[leg_id].append(stroke)
                    leg_contact_penetration[leg_id].append(penetration)
                    leg_contact[leg_id].append(1 if cf.z > contact_force_threshold or penetration > 1.0e-5 else 0)
                    local_fp = point_in_body_local(rocket, fp)
                    leg_slip[leg_id].append(math.hypot(local_fp[0] - leg["x_m"], local_fp[1] - leg["y_m"]))
                    leg_force[leg_id].append(float(abs(springs[leg_id].GetForce())))
                    leg_contact_force[leg_id].append(float(max(0.0, cf.z)))
                    leg_contact_force_xyz[leg_id]["x"].append(float(cf.x))
                    leg_contact_force_xyz[leg_id]["y"].append(float(cf.y))
                    leg_contact_force_xyz[leg_id]["z"].append(float(cf.z))
                next_output += output_dt
            if step_index < step_count:
                system.DoStepDynamics(dt)

        return {
            "time_s": time_s,
            "contact_model": explicit_smc_contact_audit(config),
            "mass_model": multibody_mass_audit(config),
            "deck": {
                "surge_m": deck_surge,
                "sway_m": deck_sway,
                "heave_m": deck_heave,
                "roll_rad": deck_roll,
                "pitch_rad": deck_pitch,
                "yaw_rad": deck_yaw,
                "surge_m_s": deck_surge_velocity,
                "sway_m_s": deck_sway_velocity,
                "heave_m_s": deck_heave_velocity,
                "roll_rad_s": deck_roll_rate,
                "pitch_rad_s": deck_pitch_rate,
                "yaw_rad_s": deck_yaw_rate,
            },
            "rocket": {
                "cg_z_m": rocket_z,
                "vertical_velocity_m_s": rocket_vz,
                "roll_rad": rocket_roll,
                "pitch_rad": rocket_pitch,
                "yaw_rad": rocket_yaw,
                "roll_rate_rad_s": rocket_roll_rate,
                "pitch_rate_rad_s": rocket_pitch_rate,
                "yaw_rate_rad_s": rocket_yaw_rate,
                "base_clearance_m": base_clearance,
                "nozzle_clearance_m": nozzle_clearance,
            },
            "forces": {"leg_tsda_force_n": leg_force, "leg_contact_force_n": leg_contact_force, "leg_contact_force_xyz_n": leg_contact_force_xyz},
            "feet": {"position_m": foot_position},
            "contact": {
                "leg_stroke_m": leg_stroke,
                "leg_contact_penetration_m": leg_contact_penetration,
                "leg_slip_m": leg_slip,
                "leg_contact": leg_contact,
            },
            "summary": summarize_chrono_output(
                time_s,
                leg_force,
                leg_contact_force,
                leg_stroke,
                leg_contact_penetration,
                leg_slip,
                leg_contact,
                rocket_vz,
                rocket_roll,
                rocket_pitch,
                base_clearance,
                nozzle_clearance,
            ),
        }


def tripod_anchor_points(
    config: dict[str, Any],
    leg: dict[str, float],
    offset_x_m: float,
    offset_y_m: float,
    rocket_base_z_m: float,
) -> dict[str, tuple[float, float, float]]:
    proxy = config["legs"]["stage3_tripod_proxy"]
    azimuth = math.radians(float(leg["azimuth_deg"]))
    radial = (math.cos(azimuth), math.sin(azimuth))
    tangent = (-math.sin(azimuth), math.cos(azimuth))

    def point(radial_m: float, tangent_m: float, height_m: float) -> tuple[float, float, float]:
        return (
            offset_x_m + radial[0] * radial_m + tangent[0] * tangent_m,
            offset_y_m + radial[1] * radial_m + tangent[1] * tangent_m,
            rocket_base_z_m + height_m,
        )

    return {
        "foot_center": (
            offset_x_m + radial[0] * float(config["legs"]["footprint_radius_m"]),
            offset_y_m + radial[1] * float(config["legs"]["footprint_radius_m"]),
            rocket_base_z_m + float(config["legs"]["footpad_radius_m"]),
        ),
        "B_main": point(
            float(proxy["attachment_radial_m"]["B_main"]),
            float(proxy["attachment_tangential_m"]["B_main"]),
            float(proxy["attachment_height_m"]["B_main"]),
        ),
        "T_long": point(
            float(proxy["attachment_radial_m"]["T_long"]),
            float(proxy["attachment_tangential_m"]["T_long"]),
            float(proxy["attachment_height_m"]["T_long"]),
        ),
        "K_short": point(
            float(proxy["attachment_radial_m"]["K_short"]),
            float(proxy["attachment_tangential_m"]["K_short"]),
            float(proxy["attachment_height_m"]["K_short"]),
        ),
    }


def rel_point(chrono: Any, absolute_xyz: tuple[float, float, float], body_origin_xyz: tuple[float, float, float]) -> Any:
    return chrono_vec(
        chrono,
        absolute_xyz[0] - body_origin_xyz[0],
        absolute_xyz[1] - body_origin_xyz[1],
        absolute_xyz[2] - body_origin_xyz[2],
    )


def support_polygon_margin(point_xy: tuple[float, float], vertices_xy: list[tuple[float, float]]) -> float | None:
    if len(vertices_xy) < 3:
        return None
    cx = sum(x for x, _ in vertices_xy) / len(vertices_xy)
    cy = sum(y for _, y in vertices_xy) / len(vertices_xy)
    ordered = sorted(vertices_xy, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    signed_distances = []
    px, py = point_xy
    area = 0.0
    for idx, (x0, y0) in enumerate(ordered):
        x1, y1 = ordered[(idx + 1) % len(ordered)]
        area += x0 * y1 - x1 * y0
    orientation = 1.0 if area >= 0.0 else -1.0
    for idx, (x0, y0) in enumerate(ordered):
        x1, y1 = ordered[(idx + 1) % len(ordered)]
        ex = x1 - x0
        ey = y1 - y0
        length = math.hypot(ex, ey)
        if length <= 1.0e-12:
            continue
        cross = orientation * (ex * (py - y0) - ey * (px - x0))
        signed_distances.append(cross / length)
    if not signed_distances:
        return None
    return min(signed_distances)


class ChronoTripodLegModel:
    def __init__(self, config: dict[str, Any], deck_motion: DeckMotion) -> None:
        self.config = config
        self.deck_motion = deck_motion
        self.chrono = import_pychrono()

    def run(self) -> dict[str, Any]:  # pragma: no cover - exercised only when PyChrono is installed
        chrono = self.chrono
        config = self.config
        system = make_system(chrono, config)
        material = make_contact_material(chrono, config)

        deck_thickness = float(config["solver"]["deck_thickness_m"])
        deck = make_box_body(chrono, (180.0, 54.0, deck_thickness), 1000.0, material, True)
        set_body_fixed(deck, True)
        add_to_system(system, deck)

        rocket = make_rocket_body(chrono, config, material)
        leg_rows = leg_positions_from_config(config)
        touchdown = 510.0
        cg = float(config["rocket"]["cog_from_base_m"])
        foot_radius = float(config["legs"]["footpad_radius_m"])
        touchdown_v = float(config["rocket"]["touchdown_vertical_velocity_m_s"])
        target_x, target_y = self.deck_motion.deck_xy(touchdown, self.deck_motion.offset_x_m, self.deck_motion.offset_y_m)
        deck_touch_z = self.deck_motion.deck_z(touchdown, target_x, target_y)
        start = float(config["solver"]["start_s"])
        initial_z = deck_touch_z + cg + touchdown_v * (touchdown - start)
        rocket.SetPos(chrono_vec(chrono, target_x, target_y, initial_z))
        set_body_velocity(rocket, chrono, 0.0, 0.0, -touchdown_v)
        add_to_system(system, rocket)
        rocket_origin = (target_x, target_y, initial_z)
        rocket_base_z = initial_z - cg

        feet: dict[str, Any] = {}
        springs: dict[str, Any] = {}
        spring_functors: list[Any] = []
        braces: dict[str, dict[str, Any]] = {}
        anchors: dict[str, dict[str, tuple[float, float, float]]] = {}
        foot_density = max(1.0, float(config["legs"]["footpad_mass_kg"]) / (4.0 / 3.0 * math.pi * foot_radius**3))
        proxy = config["legs"]["stage3_tripod_proxy"]
        for leg in leg_rows:
            leg_id = leg["id"]
            pts = tripod_anchor_points(config, leg, target_x, target_y, rocket_base_z)
            anchors[leg_id] = pts
            foot = make_sphere_body(chrono, foot_radius, foot_density, material, True)
            foot.SetMass(float(config["legs"]["footpad_mass_kg"]))
            foot.SetPos(chrono_vec(chrono, *pts["foot_center"]))
            set_body_velocity(foot, chrono, 0.0, 0.0, -touchdown_v)
            add_to_system(system, foot)
            feet[leg_id] = foot
            main_axis = (
                pts["foot_center"][0] - pts["B_main"][0],
                pts["foot_center"][1] - pts["B_main"][1],
                pts["foot_center"][2] - pts["B_main"][2],
            )
            if proxy.get("main_guide_model", "inclined_prismatic") != "disabled_for_rigid_brace_proxy":
                guide = make_oriented_prismatic_guide(chrono, rocket, foot, pts["foot_center"], main_axis)
                add_to_system(system, guide)

            main_anchor_rel = (
                pts["B_main"][0] - rocket_origin[0],
                pts["B_main"][1] - rocket_origin[1],
                pts["B_main"][2] - rocket_origin[2],
            )
            main, functor = make_nonlinear_tsda(
                chrono,
                rocket,
                foot,
                chrono_vec(chrono, *main_anchor_rel),
                chrono_vec(chrono, 0.0, 0.0, 0.0),
                config,
            )
            add_to_system(system, main)
            springs[leg_id] = main
            spring_functors.append(functor)

            braces[leg_id] = {}
            for brace_id, anchor_id in [("long_brace", "T_long"), ("short_brace", "K_short")]:
                anchor_rel = (
                    pts[anchor_id][0] - rocket_origin[0],
                    pts[anchor_id][1] - rocket_origin[1],
                    pts[anchor_id][2] - rocket_origin[2],
                )
                target_length = float(proxy["target_lengths_m"][brace_id])
                if proxy.get("brace_model", "elastic_tsda") == "rigid_distance_constraint":
                    brace_link = make_distance_brace(
                        chrono,
                        rocket,
                        foot,
                        chrono_vec(chrono, *anchor_rel),
                        chrono_vec(chrono, 0.0, 0.0, 0.0),
                        target_length,
                    )
                    force_available = False
                    brace_body = None
                    mate_foot = None
                elif proxy.get("brace_model", "elastic_tsda") == "rigid_body_spherical_links":
                    link_cfg = proxy.get("rigid_body_links", {})
                    mass_split = link_cfg.get("mass_split", {})
                    total_mass = float(link_cfg.get("rod_total_mass_per_leg_kg", 187.6))
                    brace_mass = total_mass * float(mass_split.get(brace_id, 0.5))
                    brace_body = make_cylinder_rod_body(
                        chrono,
                        pts[anchor_id],
                        pts["foot_center"],
                        float(link_cfg.get("rod_radius_m", 0.08)),
                        brace_mass,
                        material,
                        bool(link_cfg.get("collision", False)),
                    )
                    set_body_velocity(brace_body, chrono, 0.0, 0.0, -touchdown_v)
                    add_to_system(system, brace_body)
                    brace_link = make_spherical_mate_relative(
                        chrono,
                        rocket,
                        brace_body,
                        chrono_vec(chrono, *anchor_rel),
                        chrono_vec(chrono, 0.0, 0.0, -0.5 * target_length),
                    )
                    mate_foot = make_spherical_mate_relative(
                        chrono,
                        foot,
                        brace_body,
                        chrono_vec(chrono, 0.0, 0.0, 0.0),
                        chrono_vec(chrono, 0.0, 0.0, 0.5 * target_length),
                    )
                    add_to_system(system, mate_foot)
                    force_available = True
                else:
                    brace_link = make_elastic_brace_tsda(
                        chrono,
                        rocket,
                        foot,
                        chrono_vec(chrono, *anchor_rel),
                        chrono_vec(chrono, 0.0, 0.0, 0.0),
                        target_length,
                        float(proxy["brace_axial_stiffness_n_m"]),
                        float(proxy["brace_axial_damping_ns_m"]),
                    )
                    force_available = True
                    brace_body = None
                    mate_foot = None
                add_to_system(system, brace_link)
                braces[leg_id][brace_id] = {
                    "link": brace_link,
                    "foot_link": mate_foot,
                    "rod_body": brace_body,
                    "model": proxy.get("brace_model", "elastic_tsda"),
                    "target_length_m": target_length,
                    "rocket_anchor_rel_m": anchor_rel,
                    "foot_anchor_rel_m": (0.0, 0.0, 0.0),
                    "force_available": force_available,
                }

        set_system_gravity(system, chrono, 0.0)
        first_contact_seen = False
        time_s: list[float] = []
        rocket_x: list[float] = []
        rocket_y: list[float] = []
        rocket_z: list[float] = []
        rocket_vz: list[float] = []
        rocket_roll: list[float] = []
        rocket_pitch: list[float] = []
        rocket_yaw: list[float] = []
        rocket_roll_rate: list[float] = []
        rocket_pitch_rate: list[float] = []
        rocket_yaw_rate: list[float] = []
        deck_heave: list[float] = []
        deck_surge: list[float] = []
        deck_sway: list[float] = []
        deck_roll: list[float] = []
        deck_pitch: list[float] = []
        deck_yaw: list[float] = []
        deck_surge_velocity: list[float] = []
        deck_sway_velocity: list[float] = []
        deck_heave_velocity: list[float] = []
        deck_roll_rate: list[float] = []
        deck_pitch_rate: list[float] = []
        deck_yaw_rate: list[float] = []
        leg_force: dict[str, list[float]] = {leg["id"]: [] for leg in leg_rows}
        leg_contact_force: dict[str, list[float]] = {leg["id"]: [] for leg in leg_rows}
        leg_contact_force_xyz: dict[str, dict[str, list[float]]] = {
            leg["id"]: {"x": [], "y": [], "z": []} for leg in leg_rows
        }
        leg_stroke: dict[str, list[float]] = {leg["id"]: [] for leg in leg_rows}
        leg_contact_penetration: dict[str, list[float]] = {leg["id"]: [] for leg in leg_rows}
        leg_slip: dict[str, list[float]] = {leg["id"]: [] for leg in leg_rows}
        leg_contact: dict[str, list[int]] = {leg["id"]: [] for leg in leg_rows}
        foot_position: dict[str, dict[str, list[float]]] = {
            leg["id"]: {"x_m": [], "y_m": [], "z_m": []} for leg in leg_rows
        }
        brace_length: dict[str, dict[str, list[float]]] = {
            leg["id"]: {"long_brace": [], "short_brace": []} for leg in leg_rows
        }
        brace_error: dict[str, dict[str, list[float]]] = {
            leg["id"]: {"long_brace": [], "short_brace": []} for leg in leg_rows
        }
        brace_force: dict[str, dict[str, list[float]]] = {
            leg["id"]: {"long_brace": [], "short_brace": []} for leg in leg_rows
        }
        support_margin: list[float] = []
        base_clearance: list[float] = []
        nozzle_clearance: list[float] = []
        lock_state: list[int] = []
        lock_reaction_force: dict[str, list[float]] = {"x": [], "y": [], "z": []}
        lock_reaction_torque: dict[str, list[float]] = {"x": [], "y": [], "z": []}
        lock_point_position: dict[str, list[float]] = {"x_m": [], "y_m": [], "z_m": []}

        dt = float(config["solver"]["time_step_s"])
        output_dt = float(config["solver"]["output_step_s"])
        next_output = start - 1.0e-12
        t = start
        end = float(config["solver"]["end_s"])
        gravity = float(config["solver"]["gravity_m_s2"])
        contact_force_threshold = float(config["solver"]["contact_force_threshold_n"])
        lock_cfg = config["solver"].get("post_touchdown_lock_logic", {})
        lock_mode = lock_cfg.get("mode", "diagnostic_only")
        lock_dwell = float(lock_cfg.get("stable_dwell_s", 1.0))
        lock_vz_limit = float(lock_cfg.get("vertical_velocity_limit_m_s", 0.05))
        lock_rate_limit = math.radians(float(lock_cfg.get("angular_rate_limit_deg_s", 0.25)))
        lock_link = None
        lock_actuated_time: float | None = None
        stable_lock_duration = 0.0
        step_count_float = (end - start) / dt
        step_count = int(round(step_count_float))
        if not math.isclose(step_count_float, step_count, rel_tol=1.0e-10, abs_tol=1.0e-12):
            raise ValueError("Chrono simulation interval must be an integer multiple of time_step_s.")

        for step_index in range(step_count + 1):
            t = end if step_index == step_count else start + step_index * dt
            deck_state = self.deck_motion.sample(t)
            deck.SetPos(chrono_vec(chrono, deck_state["surge_m"], deck_state["sway_m"], deck_state["heave_m"] - 0.5 * deck_thickness))
            deck.SetRot(
                chrono_quat_from_roll_pitch_yaw(
                    chrono,
                    deck_state["roll_rad"],
                    deck_state["pitch_rad"],
                    deck_state["yaw_rad"],
                )
            )
            set_body_velocity(deck, chrono, deck_state["surge_m_s"], deck_state["sway_m_s"], deck_state["heave_m_s"])
            set_body_angular_velocity(deck, chrono, deck_state["roll_rad_s"], deck_state["pitch_rad_s"], deck_state["yaw_rad_s"])
            if not first_contact_seen:
                first_contact_seen = any(body.GetContactForce().z > contact_force_threshold for body in feet.values())
            if first_contact_seen:
                set_system_gravity(system, chrono, -gravity)
            if lock_mode == "actuated_body_deck_fix" and lock_link is None:
                current_contact_count = sum(1 for body in feet.values() if body.GetContactForce().z > contact_force_threshold)
                rv_now = body_vel(rocket)
                ra_now = body_ang_vel(rocket)
                rate_norm = math.sqrt(ra_now[0] ** 2 + ra_now[1] ** 2)
                if current_contact_count == len(feet) and abs(rv_now[2]) <= lock_vz_limit and rate_norm <= lock_rate_limit:
                    stable_lock_duration += 0.0 if step_index == 0 else dt
                else:
                    stable_lock_duration = 0.0
                if stable_lock_duration >= lock_dwell:
                    lock_link = make_body_deck_lock(chrono, rocket, deck)
                    add_to_system(system, lock_link)
                    lock_actuated_time = float(t)

            if t + 1.0e-12 >= next_output:
                rp = body_pos(rocket)
                rv = body_vel(rocket)
                ra = body_ang_vel(rocket)
                rr, rpi, ry = body_euler_zyx(rocket)
                time_s.append(float(t))
                rocket_x.append(rp[0])
                rocket_y.append(rp[1])
                rocket_z.append(rp[2])
                rocket_vz.append(rv[2])
                rocket_roll.append(rr)
                rocket_pitch.append(rpi)
                rocket_yaw.append(ry)
                rocket_roll_rate.append(ra[0])
                rocket_pitch_rate.append(ra[1])
                rocket_yaw_rate.append(ra[2])
                deck_surge.append(deck_state["surge_m"])
                deck_sway.append(deck_state["sway_m"])
                deck_heave.append(deck_state["heave_m"])
                deck_roll.append(deck_state["roll_rad"])
                deck_pitch.append(deck_state["pitch_rad"])
                deck_yaw.append(deck_state["yaw_rad"])
                deck_surge_velocity.append(deck_state["surge_m_s"])
                deck_sway_velocity.append(deck_state["sway_m_s"])
                deck_heave_velocity.append(deck_state["heave_m_s"])
                deck_roll_rate.append(deck_state["roll_rad_s"])
                deck_pitch_rate.append(deck_state["pitch_rad_s"])
                deck_yaw_rate.append(deck_state["yaw_rad_s"])
                base_gap = rp[2] - cg - self.deck_motion.deck_z(t, rp[0], rp[1])
                base_clearance.append(base_gap)
                nozzle_clearance.append(nozzle_clearance_from_base(config, base_gap))
                lock_state.append(1 if lock_link is not None else 0)
                if lock_link is not None and hasattr(lock_link, "GetReaction1"):
                    reaction = lock_link.GetReaction1()
                    force = reaction.force
                    torque = reaction.torque
                    lock_reaction_force["x"].append(float(force.x))
                    lock_reaction_force["y"].append(float(force.y))
                    lock_reaction_force["z"].append(float(force.z))
                    lock_reaction_torque["x"].append(float(torque.x))
                    lock_reaction_torque["y"].append(float(torque.y))
                    lock_reaction_torque["z"].append(float(torque.z))
                    lock_point_position["x_m"].append(rp[0])
                    lock_point_position["y_m"].append(rp[1])
                    lock_point_position["z_m"].append(rp[2])
                else:
                    lock_reaction_force["x"].append(0.0)
                    lock_reaction_force["y"].append(0.0)
                    lock_reaction_force["z"].append(0.0)
                    lock_reaction_torque["x"].append(0.0)
                    lock_reaction_torque["y"].append(0.0)
                    lock_reaction_torque["z"].append(0.0)
                    lock_point_position["x_m"].append(rp[0])
                    lock_point_position["y_m"].append(rp[1])
                    lock_point_position["z_m"].append(rp[2])
                vertices: list[tuple[float, float]] = []
                for leg in leg_rows:
                    leg_id = leg["id"]
                    fp = body_pos(feet[leg_id])
                    vertices.append((fp[0], fp[1]))
                    cf = feet[leg_id].GetContactForce()
                    local_deck_z = self.deck_motion.deck_z(t, fp[0], fp[1])
                    penetration = max(0.0, local_deck_z - (fp[2] - foot_radius))
                    stroke = max(0.0, float(config["legs"]["damper_rest_length_m"]) - float(springs[leg_id].GetLength()))
                    foot_position[leg_id]["x_m"].append(fp[0])
                    foot_position[leg_id]["y_m"].append(fp[1])
                    foot_position[leg_id]["z_m"].append(fp[2])
                    leg_stroke[leg_id].append(stroke)
                    leg_contact_penetration[leg_id].append(penetration)
                    leg_contact[leg_id].append(1 if cf.z > contact_force_threshold or penetration > 1.0e-5 else 0)
                    local_fp = point_in_body_local(rocket, fp)
                    leg_slip[leg_id].append(math.hypot(local_fp[0] - leg["x_m"], local_fp[1] - leg["y_m"]))
                    leg_force[leg_id].append(float(abs(springs[leg_id].GetForce())))
                    leg_contact_force[leg_id].append(float(max(0.0, cf.z)))
                    leg_contact_force_xyz[leg_id]["x"].append(float(cf.x))
                    leg_contact_force_xyz[leg_id]["y"].append(float(cf.y))
                    leg_contact_force_xyz[leg_id]["z"].append(float(cf.z))
                    for brace_id, target in [
                        ("long_brace", float(proxy["target_lengths_m"]["long_brace"])),
                        ("short_brace", float(proxy["target_lengths_m"]["short_brace"])),
                    ]:
                        brace_row = braces[leg_id][brace_id]
                        link = brace_row["link"]
                        if hasattr(link, "GetLength"):
                            current = float(link.GetLength())
                        else:
                            current = distance_between_body_points(
                                rocket,
                                feet[leg_id],
                                chrono,
                                brace_row["rocket_anchor_rel_m"],
                                brace_row["foot_anchor_rel_m"],
                            )
                        brace_length[leg_id][brace_id].append(current)
                        brace_error[leg_id][brace_id].append(current - target)
                        if hasattr(link, "GetForce"):
                            brace_force[leg_id][brace_id].append(float(link.GetForce()))
                        elif hasattr(link, "GetReaction1"):
                            reaction = link.GetReaction1()
                            force = reaction.force
                            brace_force[leg_id][brace_id].append(
                                float(math.sqrt(force.x * force.x + force.y * force.y + force.z * force.z))
                            )
                        else:
                            brace_force[leg_id][brace_id].append(0.0)
                margin = support_polygon_margin((rp[0], rp[1]), vertices)
                support_margin.append(float(margin) if margin is not None else float("nan"))
                next_output += output_dt
            if step_index < step_count:
                system.DoStepDynamics(dt)

        summary = summarize_chrono_output(
            time_s,
            leg_force,
            leg_contact_force,
            leg_stroke,
            leg_contact_penetration,
            leg_slip,
            leg_contact,
            rocket_vz,
            rocket_roll,
            rocket_pitch,
            base_clearance,
            nozzle_clearance,
        )
        summary.update(
            summarize_stage3_tripod_output(
                config,
                time_s,
                leg_contact,
                leg_stroke,
                brace_error,
                brace_force,
                support_margin,
                rocket_vz,
                rocket_roll,
                rocket_pitch,
                rocket_roll_rate,
                rocket_pitch_rate,
                nozzle_clearance,
                lock_actuated_time,
            )
        )
        return {
            "time_s": time_s,
            "contact_model": explicit_smc_contact_audit(config),
            "mass_model": multibody_mass_audit(config),
            "deck": {
                "surge_m": deck_surge,
                "sway_m": deck_sway,
                "heave_m": deck_heave,
                "roll_rad": deck_roll,
                "pitch_rad": deck_pitch,
                "yaw_rad": deck_yaw,
                "surge_m_s": deck_surge_velocity,
                "sway_m_s": deck_sway_velocity,
                "heave_m_s": deck_heave_velocity,
                "roll_rad_s": deck_roll_rate,
                "pitch_rad_s": deck_pitch_rate,
                "yaw_rad_s": deck_yaw_rate,
            },
            "rocket": {
                "cg_x_m": rocket_x,
                "cg_y_m": rocket_y,
                "cg_z_m": rocket_z,
                "vertical_velocity_m_s": rocket_vz,
                "roll_rad": rocket_roll,
                "pitch_rad": rocket_pitch,
                "yaw_rad": rocket_yaw,
                "roll_rate_rad_s": rocket_roll_rate,
                "pitch_rate_rad_s": rocket_pitch_rate,
                "yaw_rate_rad_s": rocket_yaw_rate,
                "base_clearance_m": base_clearance,
                "nozzle_clearance_m": nozzle_clearance,
            },
            "forces": {
                "leg_tsda_force_n": leg_force,
                "leg_contact_force_n": leg_contact_force,
                "leg_contact_force_xyz_n": leg_contact_force_xyz,
                "lock_reaction_force_xyz_n": lock_reaction_force,
                "lock_reaction_torque_xyz_nm": lock_reaction_torque,
            },
            "feet": {"position_m": foot_position},
            "mechanism": {
                "anchor_position_m": anchors,
                "brace_model": proxy.get("brace_model", "elastic_tsda"),
                "main_guide_model": proxy.get("main_guide_model", "inclined_prismatic"),
                "brace_force_available": proxy.get("brace_model", "elastic_tsda") != "rigid_distance_constraint",
                "brace_length_m": brace_length,
                "brace_length_error_m": brace_error,
                "brace_force_n": brace_force,
                "support_polygon_margin_m": support_margin,
                "lock_state": lock_state,
                "lock_point_position_m": lock_point_position,
            },
            "contact": {
                "leg_stroke_m": leg_stroke,
                "leg_contact_penetration_m": leg_contact_penetration,
                "leg_slip_m": leg_slip,
                "leg_contact": leg_contact,
            },
            "summary": summary,
        }


def contact_intervals(time_s: list[float], states: list[int]) -> list[dict[str, float]]:
    intervals: list[dict[str, float]] = []
    if not time_s or not states:
        return intervals
    n = min(len(time_s), len(states))
    start_idx: int | None = None
    for idx in range(n):
        in_contact = int(states[idx]) != 0
        if in_contact and start_idx is None:
            start_idx = idx
        if start_idx is not None and (not in_contact or idx == n - 1):
            end_idx = idx - 1 if not in_contact else idx
            intervals.append(
                {
                    "start_s": float(time_s[start_idx]),
                    "end_s": float(time_s[end_idx]),
                    "duration_s": float(max(0.0, time_s[end_idx] - time_s[start_idx])),
                }
            )
            start_idx = None
    return intervals


def contact_transitions(time_s: list[float], states: list[int]) -> list[dict[str, Any]]:
    transitions: list[dict[str, Any]] = []
    if not time_s or not states:
        return transitions
    n = min(len(time_s), len(states))
    prev = 0
    seen_contact = False
    for idx in range(n):
        current = 1 if int(states[idx]) != 0 else 0
        if current != prev:
            if current:
                event = "first_contact" if not seen_contact else "recontact"
                seen_contact = True
            else:
                event = "liftoff"
            transitions.append({"time_s": float(time_s[idx]), "event": event, "from": prev, "to": current})
        prev = current
    return transitions


def summarize_contact_state(
    time_s: list[float],
    leg_contact: dict[str, list[int]],
    leg_contact_force: dict[str, list[float]],
    leg_stroke: dict[str, list[float]],
    leg_slip: dict[str, list[float]],
) -> dict[str, Any]:
    per_leg: dict[str, Any] = {}
    first_times: list[float] = []
    liftoff_total = 0
    recontact_total = 0
    final_contacts = 0
    for leg_id, states in leg_contact.items():
        intervals = contact_intervals(time_s, states)
        transitions = contact_transitions(time_s, states)
        first = next((row["time_s"] for row in transitions if row["event"] == "first_contact"), None)
        if first is not None:
            first_times.append(float(first))
        liftoff_count = sum(1 for row in transitions if row["event"] == "liftoff")
        recontact_count = sum(1 for row in transitions if row["event"] == "recontact")
        liftoff_total += liftoff_count
        recontact_total += recontact_count
        final_in_contact = bool(states[-1]) if states else False
        final_contacts += 1 if final_in_contact else 0
        per_leg[leg_id] = {
            "first_contact_time_s": first,
            "liftoff_count": liftoff_count,
            "recontact_count": recontact_count,
            "final_in_contact": final_in_contact,
            "contact_intervals_s": intervals,
            "transitions": transitions,
            "total_contact_duration_s": float(sum(row["duration_s"] for row in intervals)),
            "peak_contact_force_kn": max(leg_contact_force.get(leg_id, [0.0]) or [0.0]) / 1000.0,
            "peak_stroke_m": max(leg_stroke.get(leg_id, [0.0]) or [0.0]),
            "peak_slip_m": max(leg_slip.get(leg_id, [0.0]) or [0.0]),
        }
    contact_counts = np.sum(np.array(list(leg_contact.values()), dtype=int), axis=0) if leg_contact else np.array([], dtype=int)
    all_contact_intervals = contact_intervals(time_s, (contact_counts == len(leg_contact)).astype(int).tolist()) if len(contact_counts) else []
    touchdown_sequence = sorted(
        [{"leg_id": leg_id, "first_contact_time_s": row["first_contact_time_s"]} for leg_id, row in per_leg.items() if row["first_contact_time_s"] is not None],
        key=lambda row: row["first_contact_time_s"],
    )
    touchdown_span = max(first_times) - min(first_times) if len(first_times) == len(leg_contact) and first_times else None
    return {
        "per_leg": per_leg,
        "touchdown_sequence": touchdown_sequence,
        "touchdown_span_s": float(touchdown_span) if touchdown_span is not None else None,
        "liftoff_count_total": liftoff_total,
        "recontact_count_total": recontact_total,
        "final_contact_count": final_contacts,
        "all_contact_intervals_s": all_contact_intervals,
        "all_legs_finally_in_contact": final_contacts == len(leg_contact) if leg_contact else False,
    }


def summarize_chrono_output(
    time_s: list[float],
    leg_force: dict[str, list[float]],
    leg_contact_force: dict[str, list[float]],
    leg_stroke: dict[str, list[float]],
    leg_contact_penetration: dict[str, list[float]],
    leg_slip: dict[str, list[float]],
    leg_contact: dict[str, list[int]],
    rocket_vz: list[float],
    rocket_roll: list[float],
    rocket_pitch: list[float],
    base_clearance: list[float],
    nozzle_clearance: list[float] | None = None,
) -> dict[str, Any]:
    contact_counts = np.sum(np.array(list(leg_contact.values()), dtype=int), axis=0) if leg_contact else np.array([], dtype=int)
    first_contact = None
    all_contact = None
    if len(contact_counts):
        idx = np.where(contact_counts > 0)[0]
        if len(idx):
            first_contact = float(time_s[int(idx[0])])
        idx = np.where(contact_counts == len(leg_contact))[0]
        if len(idx):
            all_contact = float(time_s[int(idx[0])])
    contact_state = summarize_contact_state(time_s, leg_contact, leg_contact_force, leg_stroke, leg_slip)
    return {
        "first_contact_time_s": first_contact,
        "all_legs_contact_time_s": all_contact,
        "contact_state": contact_state,
        "max_leg_tsda_force_kn": max((max(values) for values in leg_force.values() if values), default=0.0) / 1000.0,
        "max_leg_contact_force_kn": max((max(values) for values in leg_contact_force.values() if values), default=0.0) / 1000.0,
        "max_leg_stroke_m": max((max(values) for values in leg_stroke.values() if values), default=0.0),
        "max_contact_penetration_m": max((max(values) for values in leg_contact_penetration.values() if values), default=0.0),
        "max_footpad_slip_m": max((max(values) for values in leg_slip.values() if values), default=0.0),
        "max_rocket_roll_deg": math.degrees(max((abs(v) for v in rocket_roll), default=0.0)),
        "max_rocket_pitch_deg": math.degrees(max((abs(v) for v in rocket_pitch), default=0.0)),
        "min_base_clearance_m": min(base_clearance) if base_clearance else None,
        "min_nozzle_clearance_m": min(nozzle_clearance) if nozzle_clearance else None,
        "final_nozzle_clearance_m": float(nozzle_clearance[-1]) if nozzle_clearance else None,
        "final_contact_count": int(contact_counts[-1]) if len(contact_counts) else 0,
        "final_vertical_velocity_m_s": float(rocket_vz[-1]) if rocket_vz else None,
    }


def summarize_stage3_tripod_output(
    config: dict[str, Any],
    time_s: list[float],
    leg_contact: dict[str, list[int]],
    leg_stroke: dict[str, list[float]],
    brace_error: dict[str, dict[str, list[float]]],
    brace_force: dict[str, dict[str, list[float]]],
    support_margin: list[float],
    rocket_vz: list[float],
    rocket_roll: list[float],
    rocket_pitch: list[float],
    rocket_roll_rate: list[float],
    rocket_pitch_rate: list[float],
    nozzle_clearance: list[float],
    lock_actuated_time: float | None = None,
) -> dict[str, Any]:
    contact_counts = np.sum(np.array(list(leg_contact.values()), dtype=int), axis=0) if leg_contact else np.array([], dtype=int)
    time = np.array(time_s, dtype=float)
    vz = np.array(rocket_vz, dtype=float)
    roll_rate = np.array(rocket_roll_rate, dtype=float)
    pitch_rate = np.array(rocket_pitch_rate, dtype=float)
    lock_cfg = config["solver"].get("post_touchdown_lock_logic", {})
    dwell = float(lock_cfg.get("stable_dwell_s", 1.0))
    vz_limit = float(lock_cfg.get("vertical_velocity_limit_m_s", 0.05))
    rate_limit = math.radians(float(lock_cfg.get("angular_rate_limit_deg_s", 0.25)))
    eligible_lock_time = None
    if len(time) > 2 and len(contact_counts) == len(time):
        dt = float(np.median(np.diff(time)))
        window = max(1, int(round(dwell / max(dt, 1.0e-12))))
        stable = (
            (contact_counts == len(leg_contact))
            & (np.abs(vz) <= vz_limit)
            & (np.sqrt(roll_rate**2 + pitch_rate**2) <= rate_limit)
        )
        for idx in range(window - 1, len(stable)):
            if np.all(stable[idx - window + 1 : idx + 1]):
                eligible_lock_time = float(time[idx])
                break

    max_brace_error = 0.0
    for leg_values in brace_error.values():
        for values in leg_values.values():
            if values:
                max_brace_error = max(max_brace_error, max(abs(value) for value in values))
    max_brace_force = 0.0
    for leg_values in brace_force.values():
        for values in leg_values.values():
            if values:
                max_brace_force = max(max_brace_force, max(abs(value) for value in values))
    stroke_limit = float(config["legs"]["nonlinear_buffer_law"]["stroke_limit_m"])
    max_stroke = max((max(values) for values in leg_stroke.values() if values), default=0.0)
    finite_margin = [value for value in support_margin if math.isfinite(value)]
    final_support_margin = float(support_margin[-1]) if support_margin and math.isfinite(support_margin[-1]) else None
    final_vz = float(vz[-1]) if len(vz) else None
    final_roll = float(rocket_roll[-1]) if rocket_roll else None
    final_pitch = float(rocket_pitch[-1]) if rocket_pitch else None
    final_roll_rate = float(roll_rate[-1]) if len(roll_rate) else None
    final_pitch_rate = float(pitch_rate[-1]) if len(pitch_rate) else None
    final_nozzle = float(nozzle_clearance[-1]) if nozzle_clearance else None
    required_nozzle = float(config["rocket"]["nozzle_clearance_required_m"])
    final_contact_count = int(contact_counts[-1]) if len(contact_counts) else 0
    all_final_contact = final_contact_count == len(leg_contact) if leg_contact else False
    final_rate_norm = math.sqrt((final_roll_rate or 0.0) ** 2 + (final_pitch_rate or 0.0) ** 2)
    stability_flags = {
        "all_legs_in_contact": all_final_contact,
        "vertical_velocity_within_limit": abs(final_vz) <= vz_limit if final_vz is not None else False,
        "angular_rate_within_limit": final_rate_norm <= rate_limit,
        "support_margin_positive": final_support_margin is not None and final_support_margin > 0.0,
        "final_nozzle_clearance_above_required": final_nozzle is not None and final_nozzle >= required_nozzle,
    }
    if lock_cfg.get("mode") == "actuated_body_deck_fix":
        stability_flags["actual_lock_actuated"] = lock_actuated_time is not None
    return {
        "stage3_model": (
            "tripod_rigid_distance_brace_nonlinear_buffer_proxy"
            if config["legs"]["stage3_tripod_proxy"].get("brace_model") == "rigid_distance_constraint"
            else "tripod_prismatic_main_leg_elastic_brace_nonlinear_buffer_proxy"
        ),
        "stage3_substage": config["legs"]["stage3_tripod_proxy"].get("stage", "Stage 3A"),
        "brace_model": config["legs"]["stage3_tripod_proxy"].get("brace_model", "elastic_tsda"),
        "main_guide_model": config["legs"]["stage3_tripod_proxy"].get("main_guide_model", "inclined_prismatic"),
        "brace_force_available": config["legs"]["stage3_tripod_proxy"].get("brace_model", "elastic_tsda") != "rigid_distance_constraint",
        "max_brace_length_error_m": max_brace_error,
        "max_brace_axial_force_kn": max_brace_force / 1000.0,
        "max_buffer_stroke_ratio_to_reference": max_stroke / stroke_limit if stroke_limit > 0.0 else None,
        "min_support_polygon_margin_m": min(finite_margin) if finite_margin else None,
        "final_support_polygon_margin_m": final_support_margin,
        "toppling_risk_diagnostic": {
            "method": "CG projection inside the four-foot support polygon in the simplified Stage 3A geometry.",
            "minimum_margin_m": min(finite_margin) if finite_margin else None,
            "final_margin_m": final_support_margin,
            "ever_outside_support_polygon": any(value < 0.0 for value in finite_margin) if finite_margin else None,
        },
        "stable_standing_diagnostic": {
            "method": "diagnostic_only_final_state_thresholds",
            "threshold_source": "solver.post_touchdown_lock_logic engineering thresholds plus Thies nozzle clearance requirement",
            "flags": stability_flags,
            "all_flags_true": all(stability_flags.values()),
            "final_vertical_velocity_m_s": final_vz,
            "final_roll_deg": math.degrees(final_roll) if final_roll is not None else None,
            "final_pitch_deg": math.degrees(final_pitch) if final_pitch is not None else None,
            "final_angular_rate_deg_s": math.degrees(final_rate_norm),
            "final_nozzle_clearance_m": final_nozzle,
            "required_nozzle_clearance_m": required_nozzle,
        },
        "post_touchdown_lock": {
            "mode": lock_cfg.get("mode", "diagnostic_only"),
            "eligible_lock_time_s": eligible_lock_time,
            "actual_lock_actuated_time_s": lock_actuated_time,
            "actual_lock_final_state": lock_actuated_time is not None,
            "stable_dwell_s": dwell,
            "vertical_velocity_limit_m_s": vz_limit,
            "angular_rate_limit_deg_s": math.degrees(rate_limit),
        },
    }
