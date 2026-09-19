from __future__ import annotations

import math
from typing import Any

try:
    from .chrono_leg_model import (
        ChronoUnavailableError,
        add_to_system,
        chrono_vec,
        import_pychrono,
        make_elastic_brace_tsda,
        make_spherical_mate_relative,
        make_system,
        set_body_fixed,
    )
    from .leg_mechanism_data_validator import BLOCKING_SOURCE_CATEGORIES, SYNTHETIC_SOURCE_CATEGORY
except ImportError:
    from chrono_leg_model import (
        ChronoUnavailableError,
        add_to_system,
        chrono_vec,
        import_pychrono,
        make_elastic_brace_tsda,
        make_spherical_mate_relative,
        make_system,
        set_body_fixed,
    )
    from leg_mechanism_data_validator import BLOCKING_SOURCE_CATEGORIES, SYNTHETIC_SOURCE_CATEGORY


BODY_ENDPOINTS = {
    "main_strut": ("B", "P"),
    "long_auxiliary_strut": ("T", "P"),
    "short_auxiliary_strut": ("K", "P"),
}


def point_tuple(value: Any) -> tuple[float, float, float]:
    if isinstance(value, dict):
        return float(value["x"]), float(value["y"]), float(value["z"])
    return float(value[0]), float(value[1]), float(value[2])


def point_sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def point_distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    dx, dy, dz = point_sub(a, b)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def inertia_tuple(value: Any) -> tuple[float, float, float]:
    if isinstance(value, dict):
        return float(value.get("ixx", value.get("roll_x", 1.0))), float(value.get("iyy", value.get("pitch_y", 1.0))), float(value.get("izz", value.get("yaw_z", 1.0)))
    if isinstance(value, list | tuple) and len(value) >= 3:
        return float(value[0]), float(value[1]), float(value[2])
    return 1.0, 1.0, 1.0


def source_gate(config: dict[str, Any], allow_synthetic: bool = False) -> dict[str, Any]:
    rows = config.get("source_map") if isinstance(config.get("source_map"), list) else []
    blockers = []
    for row in rows:
        category = row.get("source_category")
        if category in BLOCKING_SOURCE_CATEGORIES or not str(row.get("source_detail", "")).strip():
            blockers.append(row)
        elif category == SYNTHETIC_SOURCE_CATEGORY and not allow_synthetic:
            blockers.append(row)
    return {
        "pass": not blockers,
        "allow_synthetic": allow_synthetic,
        "blocked_row_count": len(blockers),
        "sample_blocked_paths": [row.get("path") for row in blockers[:20]],
    }


def backend_manifest(config: dict[str, Any]) -> dict[str, Any]:
    legs = config.get("legs", [])
    body_rows = []
    joint_rows = []
    force_rows = []
    for leg in legs:
        leg_id = leg.get("id")
        markers = leg.get("markers_body_frame_m", {})
        for body_name, endpoints in BODY_ENDPOINTS.items():
            if body_name in (leg.get("body_properties") or {}) and all(marker in markers for marker in endpoints):
                body_rows.append({"leg_id": leg_id, "body": body_name, "endpoints": endpoints})
                joint_rows.extend(
                    [
                        {"leg_id": leg_id, "body": body_name, "marker": endpoints[0], "connects": "rocket_to_link", "type": "spherical"},
                        {"leg_id": leg_id, "body": body_name, "marker": endpoints[1], "connects": "link_to_footpad", "type": "spherical"},
                    ]
                )
        if "footpad" in (leg.get("body_properties") or {}) and "P" in markers:
            body_rows.append({"leg_id": leg_id, "body": "footpad", "endpoints": ("P", "P")})
        if "B" in markers and "P" in markers:
            force_rows.append({"leg_id": leg_id, "element": "main_absorber_tsda", "endpoints": ("B", "P")})
    return {
        "backend_id": "ChronoRealLegBackend/v1",
        "leg_count": len(legs),
        "body_count": len(body_rows),
        "joint_count": len(joint_rows),
        "force_element_count": len(force_rows),
        "body_rows": body_rows,
        "joint_rows": joint_rows,
        "force_rows": force_rows,
        "scope": "generic marker/topology adapter; not a CAD-specific validated Adams clone by itself",
    }


def make_body(chrono: Any, body_spec: dict[str, Any], default_pos: tuple[float, float, float]) -> Any:
    body = chrono.ChBody()
    body.SetMass(float(body_spec.get("mass_kg", 1.0)))
    body.SetInertiaXX(chrono_vec(chrono, *inertia_tuple(body_spec.get("inertia_kg_m2"))))
    com = point_tuple(body_spec.get("com_xyz_m", default_pos))
    body.SetPos(chrono_vec(chrono, *com))
    return body


def smoke_assemble_chrono_system(config: dict[str, Any], allow_synthetic: bool = False) -> dict[str, Any]:
    gate = source_gate(config, allow_synthetic=allow_synthetic)
    if not gate["pass"]:
        return {
            "pass": False,
            "stage": "source_gate",
            "source_gate": gate,
            "error": "Config contains blocked or synthetic source rows.",
        }

    chrono = import_pychrono()
    minimal_solver_config = {"solver": {"gravity_m_s2": 9.80665}}
    system = make_system(chrono, minimal_solver_config)
    manifest = backend_manifest(config)
    created_bodies = 0
    created_links = 0
    unsupported: list[str] = []

    deck = chrono.ChBody()
    deck.SetMass(1.0)
    deck.SetPos(chrono_vec(chrono, 0.0, 0.0, 0.0))
    set_body_fixed(deck, True)
    add_to_system(system, deck)
    created_bodies += 1

    rocket = chrono.ChBody()
    rocket_cfg = config["rocket"]
    inertia = rocket_cfg.get("inertia_kg_m2", {})
    rocket.SetMass(float(rocket_cfg["landing_mass_kg"]))
    rocket.SetInertiaXX(
        chrono_vec(
            chrono,
            float(inertia.get("roll_iyy", inertia.get("roll_x", 1.0))),
            float(inertia.get("pitch_ixx", inertia.get("pitch_y", 1.0))),
            float(inertia.get("yaw_izz", inertia.get("yaw_z", 1.0))),
        )
    )
    rocket.SetPos(chrono_vec(chrono, 0.0, 0.0, 0.0))
    set_body_fixed(rocket, True)
    add_to_system(system, rocket)
    created_bodies += 1

    linear_k = float(config.get("buffer_law", {}).get("linear_k_n_m", 0.0) or 0.0)
    linear_c = float(config.get("buffer_law", {}).get("linear_c_n_s_m", 0.0) or 0.0)

    for leg in config.get("legs", []):
        leg_id = str(leg.get("id"))
        markers = {name: point_tuple(value) for name, value in (leg.get("markers_body_frame_m") or {}).items()}
        body_properties = leg.get("body_properties") or {}
        bodies: dict[str, Any] = {}
        body_positions: dict[str, tuple[float, float, float]] = {}
        for body_name, spec in body_properties.items():
            default = markers.get("P", (0.0, 0.0, 0.0))
            if isinstance(spec, dict) and "com_xyz_m" in spec:
                default = point_tuple(spec["com_xyz_m"])
            body = make_body(chrono, spec, default)
            if body_name == "footpad":
                set_body_fixed(body, False)
            add_to_system(system, body)
            bodies[body_name] = body
            body_positions[body_name] = point_tuple(spec.get("com_xyz_m", default)) if isinstance(spec, dict) else default
            created_bodies += 1

        foot = bodies.get("footpad")
        if foot is None:
            unsupported.append(f"{leg_id}: missing footpad body")
            continue
        foot_origin = body_positions.get("footpad", markers.get("P", (0.0, 0.0, 0.0)))

        for body_name, (rocket_marker, foot_marker) in BODY_ENDPOINTS.items():
            link_body = bodies.get(body_name)
            if link_body is None:
                continue
            link_origin = body_positions.get(body_name, markers.get(foot_marker, (0.0, 0.0, 0.0)))
            if rocket_marker not in markers or foot_marker not in markers:
                unsupported.append(f"{leg_id}.{body_name}: missing markers {rocket_marker}/{foot_marker}")
                continue
            joint_type = str((leg.get("joint_topology") or {}).get(f"{rocket_marker}_joint_type", "spherical")).lower()
            foot_joint_type = str((leg.get("joint_topology") or {}).get("P_joint_type", "spherical")).lower()
            if joint_type != "spherical" or foot_joint_type != "spherical":
                unsupported.append(f"{leg_id}.{body_name}: unsupported joint types {joint_type}/{foot_joint_type}")
                continue
            rocket_rel = chrono_vec(chrono, *markers[rocket_marker])
            link_rel_a = chrono_vec(chrono, *point_sub(markers[rocket_marker], link_origin))
            link_rel_b = chrono_vec(chrono, *point_sub(markers[foot_marker], link_origin))
            foot_rel = chrono_vec(chrono, *point_sub(markers[foot_marker], foot_origin))
            add_to_system(system, make_spherical_mate_relative(chrono, rocket, link_body, rocket_rel, link_rel_a))
            add_to_system(system, make_spherical_mate_relative(chrono, link_body, foot, link_rel_b, foot_rel))
            created_links += 2

        if "B" in markers and "P" in markers and linear_k > 0.0:
            absorber = make_elastic_brace_tsda(
                chrono,
                rocket,
                foot,
                chrono_vec(chrono, *markers["B"]),
                chrono_vec(chrono, *point_sub(markers["P"], foot_origin)),
                point_distance(markers["B"], markers["P"]),
                linear_k,
                linear_c,
            )
            add_to_system(system, absorber)
            created_links += 1

    system_time = getattr(system, "GetChTime", lambda: 0.0)()
    return {
        "pass": not unsupported and created_bodies >= 2 and created_links > 0,
        "stage": "chrono_smoke_assembly",
        "source_gate": gate,
        "manifest": manifest,
        "created_body_count": created_bodies,
        "created_link_count": created_links,
        "unsupported": unsupported,
        "system_time_s": float(system_time),
        "note": "This checks that a validated real-config package can be assembled into PyChrono bodies, spherical mates and absorber links. It does not solve a landing trajectory.",
    }
