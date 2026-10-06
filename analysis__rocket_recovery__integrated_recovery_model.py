from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import numpy as np
try:
    from .common import G, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from .landing_leg_contact import LITERATURE_INPUTS, kinetic_energy_kj, thies_footprint_radius_m
    from .wang_2023 import (
        PAPER_ROOT as WANG_ROOT,
        build_wave_force_components,
        hydro_matrices,
        plume_generalized_force,
        plume_load_n,
        wave_generalized_force,
    )
except ImportError:
    from common import G, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from landing_leg_contact import LITERATURE_INPUTS, kinetic_energy_kj, thies_footprint_radius_m
    from wang_2023 import (
        PAPER_ROOT as WANG_ROOT,
        build_wave_force_components,
        hydro_matrices,
        plume_generalized_force,
        plume_load_n,
        wave_generalized_force,
    )


CASE_ROOT = ROCKET_CASES_DIR / "Integrated_LeggedRecovery"
REPORT_JS = VISUALIZATION_DIR / "integrated-recovery-data.js"
WANG_RESPONSE = WANG_ROOT / "Output" / "RocketRecovery" / "wang-2023-response.json"


NARGOLKAR_EQUIVALENT_BEAM = {
    "source": "Nargolkar & Vijayan 2025 Table 2, MARMAC 302 equivalent RLV modes",
    "axial": {"stiffness_n_m": 2.95e8, "equivalent_mass_kg": 8307.97},
    "rotation": {"stiffness_nm_rad": 1.50e6, "equivalent_mass_kg": 381.08},
    "target_frequencies_hz": {"axial": 30.0, "bending_rotation": 10.0},
}


DEFAULT_CONFIG: dict[str, Any] = {
    "case_id": "Integrated_LeggedRecovery",
    "title": "HAMS/Cummins + Wang wave/plume + Nargolkar beam + Thies four-leg contact",
    "input_cases": ["calm_center", "wave_center", "wave_bow_15m", "wave_port_15m"],
    "time_domain": {
        "prehistory_start_s": 450.0,
        "coupled_start_s": 506.0,
        "end_s": 526.0,
        "dt_s": 0.002,
        "prehistory_dt_s": 0.02,
        "touchdown_reference_s": 510.0,
        "visualization_start_s": 506.0,
        "visualization_end_s": 526.0,
    },
    "rocket": {
        "source": "Thies 2022 RETALT1 mass and inertia table",
        "landing_mass_kg": 61_288.0,
        "cog_from_base_m": 22.059,
        "height_m": 103.0,
        "base_diameter_m": 6.0,
        "nozzle_clearance_required_m": 0.5475,
        "inertia_kg_m2": {"roll": 3.76e5, "pitch": 2.57e7, "yaw": 2.57e7},
        "touchdown_vertical_velocity_m_s": 5.0,
        "pre_touchdown_mode": "prescribed_constant_velocity_with_weight_balancing_thrust",
        "post_touchdown_thrust": "zero_after_touchdown; Wang plume remains an external deck load through 511s",
    },
    "legs": {
        "source": "Thies 2022 Table 4 plus explicit symmetric azimuth convention",
        "count": 4,
        "azimuths_deg": [45.0, 135.0, 225.0, 315.0],
        "footprint_radius_m": thies_footprint_radius_m(),
        "damper_stiffness_n_m": LITERATURE_INPUTS["thies_2022"]["linear_contact_parameters"]["damper_stiffness_n_m"],
        "damper_damping_ns_m": LITERATURE_INPUTS["thies_2022"]["linear_contact_parameters"]["damper_damping_ns_m"],
        "stroke_reference_m": LITERATURE_INPUTS["thies_2022"]["reported_dimensioning_result"]["damper_deformation_m"],
        "force_reference_n": LITERATURE_INPUTS["thies_2022"]["reported_dimensioning_result"]["spring_damper_force_kn"] * 1000.0,
        "hard_stop_stiffness_n_m": LITERATURE_INPUTS["thies_2022"]["linear_contact_parameters"]["platform_stiffness_n_m"],
        "friction_coefficient_nominal": LITERATURE_INPUTS["thies_2022"]["requirements"]["friction_coefficient_nominal"],
        "contact_law": "unilateral compression-only spring-damper with Thies Table 8 force saturation and stroke hard-stop",
    },
    "equivalent_beam": {
        "source": NARGOLKAR_EQUIVALENT_BEAM["source"],
        "axial_stiffness_n_m": NARGOLKAR_EQUIVALENT_BEAM["axial"]["stiffness_n_m"],
        "axial_equivalent_mass_kg": NARGOLKAR_EQUIVALENT_BEAM["axial"]["equivalent_mass_kg"],
        "rotational_stiffness_nm_rad": NARGOLKAR_EQUIVALENT_BEAM["rotation"]["stiffness_nm_rad"],
        "rotational_equivalent_mass_kg": NARGOLKAR_EQUIVALENT_BEAM["rotation"]["equivalent_mass_kg"],
        "damping_ratio": 0.02,
        "coupling_note": "Axial and two rotational beam modes alter foot heights and are driven by total normal force and contact moments.",
    },
    "model_limits": [
        "No original AQWA, STAR-CCM+, MSC Adams, or nonlinear hydropneumatic damper tables are available in the supplied files.",
        "Pre-touchdown rocket GNC is not modeled; Thies touchdown velocity is imposed until the contact reference time.",
        "Four-leg azimuths are a symmetric convention because exact leg azimuths are not published in the supplied Thies material.",
        "Tangential friction forces are recorded as a future extension; this reduced model has no lateral rocket DOFs, so friction does not feed back dynamically.",
    ],
}


def ensure_case_dirs() -> None:
    (CASE_ROOT / "Output" / "RocketRecovery").mkdir(parents=True, exist_ok=True)
    (CASE_ROOT / "validation").mkdir(parents=True, exist_ok=True)


def load_wang_config() -> dict[str, Any]:
    path = WANG_ROOT / "platform_config.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing Wang 2023 platform config: {path}. Run wang_2023.py generate first.")
    return read_json(path)


def load_wang_response() -> dict[str, Any] | None:
    if WANG_RESPONSE.exists():
        return read_json(WANG_RESPONSE)
    return None


def leg_positions(config: dict[str, Any]) -> list[dict[str, float]]:
    radius = float(config["legs"]["footprint_radius_m"])
    out = []
    for idx, azimuth in enumerate(config["legs"]["azimuths_deg"], start=1):
        rad = math.radians(float(azimuth))
        out.append({"id": f"leg_{idx}", "azimuth_deg": float(azimuth), "x": radius * math.cos(rad), "y": radius * math.sin(rad)})
    return out


def find_offset(wang_config: dict[str, Any], offset_id: str) -> dict[str, Any]:
    for offset in wang_config["landing_offsets_m"]:
        if offset["id"] == offset_id:
            return offset
    raise KeyError(offset_id)


def split_case_id(case_id: str) -> tuple[str, str]:
    env, offset = case_id.split("_", 1)
    return env, offset


def wang_deck_z_at_time(wang_response: dict[str, Any] | None, case_id: str, t_abs: float, x: float, y: float) -> float:
    if not wang_response or case_id not in wang_response.get("simulations", {}):
        return 0.0
    sim = wang_response["simulations"][case_id]
    time = np.array(sim["time_s"], dtype=float)
    heave = np.array(sim["responses"]["heave_m"], dtype=float)
    roll = np.array(sim["responses"]["roll_rad"], dtype=float)
    pitch = np.array(sim["responses"]["pitch_rad"], dtype=float)
    return float(np.interp(t_abs, time, heave + roll * y - pitch * x))


def modal_damping(mass: float, stiffness: float, damping_ratio: float) -> float:
    return 2.0 * damping_ratio * math.sqrt(max(mass * stiffness, 0.0))


def rk4_integrate(rhs: Any, t0: float, t1: float, y0: np.ndarray, dt: float) -> tuple[np.ndarray, np.ndarray]:
    step_count = int(round((t1 - t0) / dt))
    time = np.linspace(t0, t1, step_count + 1)
    y = np.empty((len(y0), step_count + 1), dtype=float)
    y[:, 0] = y0
    for idx in range(step_count):
        h = float(time[idx + 1] - time[idx])
        t = float(time[idx])
        current = y[:, idx]
        k1 = rhs(t, current)
        k2 = rhs(t + 0.5 * h, current + 0.5 * h * k1)
        k3 = rhs(t + 0.5 * h, current + 0.5 * h * k2)
        k4 = rhs(t + h, current + h * k3)
        y[:, idx + 1] = current + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        if not np.all(np.isfinite(y[:, idx + 1])):
            raise FloatingPointError(f"Non-finite state at t={time[idx + 1]:.6f} s")
    return time, y


def deck_kinematics(platform_q: np.ndarray, platform_qd: np.ndarray, x: float, y: float) -> tuple[float, float]:
    z = platform_q[0] + platform_q[1] * y - platform_q[2] * x
    zd = platform_qd[0] + platform_qd[1] * y - platform_qd[2] * x
    return float(z), float(zd)


def foot_kinematics(
    rocket_q: np.ndarray,
    rocket_qd: np.ndarray,
    beam_q: np.ndarray,
    beam_qd: np.ndarray,
    leg: dict[str, float],
    cg_from_base_m: float,
) -> tuple[float, float]:
    x = leg["x"]
    y = leg["y"]
    total_roll = rocket_q[1] + beam_q[1]
    total_pitch = rocket_q[2] + beam_q[2]
    total_roll_d = rocket_qd[1] + beam_qd[1]
    total_pitch_d = rocket_qd[2] + beam_qd[2]
    z = rocket_q[0] - cg_from_base_m + beam_q[0] + total_roll * y - total_pitch * x
    zd = rocket_qd[0] + beam_qd[0] + total_roll_d * y - total_pitch_d * x
    return float(z), float(zd)


def contact_forces(
    config: dict[str, Any],
    platform_q: np.ndarray,
    platform_qd: np.ndarray,
    rocket_q: np.ndarray,
    rocket_qd: np.ndarray,
    beam_q: np.ndarray,
    beam_qd: np.ndarray,
    offset: dict[str, Any],
    active: bool,
) -> dict[str, Any]:
    legs = leg_positions(config)
    leg_config = config["legs"]
    cg = float(config["rocket"]["cog_from_base_m"])
    k = float(leg_config["damper_stiffness_n_m"])
    c = float(leg_config["damper_damping_ns_m"])
    stroke_ref = float(leg_config["stroke_reference_m"])
    force_ref = float(leg_config["force_reference_n"])
    k_stop = float(leg_config["hard_stop_stiffness_n_m"])
    rows = []
    total_force = 0.0
    total_roll_moment = 0.0
    total_pitch_moment = 0.0
    platform_force = np.zeros(3, dtype=float)

    for leg in legs:
        deck_x = float(offset["x"]) + leg["x"]
        deck_y = float(offset["y"]) + leg["y"]
        deck_z, deck_vz = deck_kinematics(platform_q, platform_qd, deck_x, deck_y)
        foot_z, foot_vz = foot_kinematics(rocket_q, rocket_qd, beam_q, beam_qd, leg, cg)
        penetration = deck_z - foot_z
        compression_rate = deck_vz - foot_vz
        stroke = max(0.0, penetration) if active else 0.0
        rate = compression_rate if active and stroke > 0.0 else 0.0
        force = 0.0
        if stroke > 0.0:
            spring = k * stroke
            damper = force_ref * math.tanh(c * rate / max(force_ref, 1.0))
            force = spring + damper
            if stroke > stroke_ref:
                force += force_ref * math.tanh(k_stop * (stroke - stroke_ref) / max(force_ref, 1.0))
            force = min(2.0 * force_ref, force)
            force = max(0.0, force)
        total_force += force
        total_roll_moment += leg["y"] * force
        total_pitch_moment += -leg["x"] * force
        reaction_z = -force
        platform_force += np.array([reaction_z, deck_y * reaction_z, -deck_x * reaction_z], dtype=float)
        rows.append(
            {
                **leg,
                "deck_x": deck_x,
                "deck_y": deck_y,
                "deck_z": deck_z,
                "foot_z": foot_z,
                "penetration_m": penetration,
                "stroke_m": stroke,
                "stroke_rate_m_s": rate,
                "force_n": force,
                "in_contact": bool(stroke > 0.0),
            }
        )

    return {
        "legs": rows,
        "total_force_n": total_force,
        "rocket_generalized": np.array([total_force, total_roll_moment, total_pitch_moment], dtype=float),
        "platform_generalized": platform_force,
    }


def summarize_series(series: np.ndarray) -> dict[str, float]:
    return {"peak_abs": float(np.max(np.abs(series))), "rms": float(math.sqrt(np.mean(series**2))), "final": float(series[-1])}


def first_time(time: np.ndarray, mask: np.ndarray) -> float | None:
    idx = np.where(mask)[0]
    if len(idx) == 0:
        return None
    return float(time[int(idx[0])])


def simulate_case(config: dict[str, Any], wang_config: dict[str, Any], matrices: dict[str, Any], case_id: str, wang_response: dict[str, Any] | None) -> dict[str, Any]:
    env, offset_id = split_case_id(case_id)
    offset = find_offset(wang_config, offset_id)
    with_wave = env == "wave"
    wave = build_wave_force_components(wang_config, matrices, with_wave)
    td = config["time_domain"]
    prehistory_start = float(td["prehistory_start_s"])
    coupled_start = float(td["coupled_start_s"])
    end = float(td["end_s"])
    dt = float(td["dt_s"])
    pre_dt = float(td["prehistory_dt_s"])
    touchdown = float(td["touchdown_reference_s"])
    omega = matrices["omega_rad_s"]
    radiation = matrices["radiation_damping"]
    radiation_weights = matrices["radiation_weights"]
    mass_inv_platform = np.linalg.inv(matrices["mass"])
    memory_count = len(omega)

    pre_y0 = np.zeros(6 + 2 * memory_count * 3, dtype=float)

    def prehistory_rhs(t_abs: float, y: np.ndarray) -> np.ndarray:
        q_p = y[:3]
        qd_p = y[3:6]
        memory = y[6:].reshape(2, memory_count, 3)
        cos_state = memory[0]
        sin_state = memory[1]
        memory_force = np.einsum("k,kij,kj->i", radiation_weights, radiation, cos_state)
        platform_force = (
            plume_generalized_force(t_abs, wang_config, offset)
            + wave_generalized_force(t_abs, matrices, wave, wang_config["time_domain"]["start_s"])
            - matrices["linear_damping"] @ qd_p
            - matrices["restoring"] @ q_p
            - memory_force
        )
        qdd_p = mass_inv_platform @ platform_force
        cos_dot = qd_p[None, :] - omega[:, None] * sin_state
        sin_dot = omega[:, None] * cos_state
        return np.concatenate([qd_p, qdd_p, cos_dot.reshape(-1), sin_dot.reshape(-1)])

    _pre_time, pre_y = rk4_integrate(prehistory_rhs, prehistory_start, coupled_start, pre_y0, pre_dt)

    rocket = config["rocket"]
    beam = config["equivalent_beam"]
    m_r = float(rocket["landing_mass_kg"])
    i_roll = float(rocket["inertia_kg_m2"]["roll"])
    i_pitch = float(rocket["inertia_kg_m2"]["pitch"])
    cg = float(rocket["cog_from_base_m"])
    touchdown_v = float(rocket["touchdown_vertical_velocity_m_s"])
    deck_z_touchdown = wang_deck_z_at_time(wang_response, case_id, touchdown, float(offset["x"]), float(offset["y"]))
    z_c_start = deck_z_touchdown + cg + touchdown_v * (touchdown - coupled_start)

    m_ax = float(beam["axial_equivalent_mass_kg"])
    k_ax = float(beam["axial_stiffness_n_m"])
    c_ax = modal_damping(m_ax, k_ax, float(beam["damping_ratio"]))
    m_rot = float(beam["rotational_equivalent_mass_kg"])
    k_rot = float(beam["rotational_stiffness_nm_rad"])
    c_rot = modal_damping(m_rot, k_rot, float(beam["damping_ratio"]))

    state_size = 6 + 2 * memory_count * 3 + 6 + 6
    y0 = np.zeros(state_size, dtype=float)
    rocket_start = 6 + 2 * memory_count * 3
    beam_start = rocket_start + 6
    y0[:rocket_start] = pre_y[:, -1]
    y0[rocket_start + 0] = z_c_start
    y0[rocket_start + 3] = -touchdown_v

    def rhs(t_abs: float, y: np.ndarray) -> np.ndarray:
        q_p = y[:3]
        qd_p = y[3:6]
        memory = y[6:rocket_start].reshape(2, memory_count, 3)
        q_r = y[rocket_start : rocket_start + 3]
        qd_r = y[rocket_start + 3 : rocket_start + 6]
        q_b = y[beam_start : beam_start + 3]
        qd_b = y[beam_start + 3 : beam_start + 6]

        active = t_abs >= touchdown
        contact = contact_forces(config, q_p, qd_p, q_r, qd_r, q_b, qd_b, offset, active)
        cos_state = memory[0]
        sin_state = memory[1]
        memory_force = np.einsum("k,kij,kj->i", radiation_weights, radiation, cos_state)
        platform_force = (
            plume_generalized_force(t_abs, wang_config, offset)
            + wave_generalized_force(t_abs, matrices, wave, wang_config["time_domain"]["start_s"])
            + contact["platform_generalized"]
            - matrices["linear_damping"] @ qd_p
            - matrices["restoring"] @ q_p
            - memory_force
        )
        qdd_p = mass_inv_platform @ platform_force
        cos_dot = qd_p[None, :] - omega[:, None] * sin_state
        sin_dot = omega[:, None] * cos_state

        rocket_qdd = np.zeros(3, dtype=float)
        if t_abs < touchdown:
            # Thies supplies the touchdown condition, not a GNC trajectory. Hold
            # constant approach velocity until the contact reference instant.
            rocket_qdd[:] = 0.0
        else:
            generalized = contact["rocket_generalized"]
            rocket_qdd[0] = (generalized[0] - m_r * G) / m_r
            rocket_qdd[1] = generalized[1] / i_roll
            rocket_qdd[2] = generalized[2] / i_pitch

        beam_force = contact["rocket_generalized"] if active else np.zeros(3, dtype=float)
        beam_qdd = np.array(
            [
                (beam_force[0] - c_ax * qd_b[0] - k_ax * q_b[0]) / m_ax,
                (beam_force[1] - c_rot * qd_b[1] - k_rot * q_b[1]) / m_rot,
                (beam_force[2] - c_rot * qd_b[2] - k_rot * q_b[2]) / m_rot,
            ],
            dtype=float,
        )

        return np.concatenate(
            [
                qd_p,
                qdd_p,
                cos_dot.reshape(-1),
                sin_dot.reshape(-1),
                qd_r,
                rocket_qdd,
                qd_b,
                beam_qdd,
            ]
        )

    time, y = rk4_integrate(rhs, coupled_start, end, y0, dt)
    platform_q = y[:3, :]
    platform_qd = y[3:6, :]
    rocket_q = y[rocket_start : rocket_start + 3, :]
    rocket_qd = y[rocket_start + 3 : rocket_start + 6, :]
    beam_q = y[beam_start : beam_start + 3, :]
    beam_qd = y[beam_start + 3 : beam_start + 6, :]

    leg_ids = [leg["id"] for leg in leg_positions(config)]
    leg_force = {leg_id: [] for leg_id in leg_ids}
    leg_stroke = {leg_id: [] for leg_id in leg_ids}
    leg_contact = {leg_id: [] for leg_id in leg_ids}
    plume = []
    deck_center = []
    foot_center = []
    total_contact = []

    for idx, t_abs in enumerate(time):
        active = t_abs >= touchdown
        contact = contact_forces(
            config,
            platform_q[:, idx],
            platform_qd[:, idx],
            rocket_q[:, idx],
            rocket_qd[:, idx],
            beam_q[:, idx],
            beam_qd[:, idx],
            offset,
            active,
        )
        total_contact.append(contact["total_force_n"])
        for row in contact["legs"]:
            leg_force[row["id"]].append(row["force_n"])
            leg_stroke[row["id"]].append(row["stroke_m"])
            leg_contact[row["id"]].append(1 if row["in_contact"] else 0)
        dz, _ = deck_kinematics(platform_q[:, idx], platform_qd[:, idx], float(offset["x"]), float(offset["y"]))
        deck_center.append(dz)
        foot_center.append(rocket_q[0, idx] - cg + beam_q[0, idx])
        plume.append(plume_load_n(float(t_abs), wang_config) if offset["with_plume"] else 0.0)

    leg_force_arrays = {key: np.array(value, dtype=float) for key, value in leg_force.items()}
    leg_stroke_arrays = {key: np.array(value, dtype=float) for key, value in leg_stroke.items()}
    leg_contact_arrays = {key: np.array(value, dtype=int) for key, value in leg_contact.items()}
    all_contact_count = np.sum(np.stack(list(leg_contact_arrays.values()), axis=0), axis=0)
    first_contact = first_time(time, all_contact_count > 0)
    all_legs_contact = first_time(time, all_contact_count == len(leg_ids))
    max_force_leg = max(max(values) for values in leg_force_arrays.values()) / 1000.0
    max_stroke_leg = max(max(values) for values in leg_stroke_arrays.values())

    result = {
        "id": case_id,
        "environment": env,
        "offset": offset,
        "with_wave": with_wave,
        "with_plume": bool(offset["with_plume"]),
        "time_s": time.tolist(),
        "forces": {
            "plume_load_n": plume,
            "total_contact_n": [float(v) for v in total_contact],
            "leg_force_n": {key: values.tolist() for key, values in leg_force_arrays.items()},
        },
        "contact": {
            "leg_stroke_m": {key: values.tolist() for key, values in leg_stroke_arrays.items()},
            "leg_contact": {key: values.tolist() for key, values in leg_contact_arrays.items()},
            "contact_count": all_contact_count.astype(int).tolist(),
        },
        "platform": {
            "heave_m": platform_q[0, :].tolist(),
            "roll_rad": platform_q[1, :].tolist(),
            "pitch_rad": platform_q[2, :].tolist(),
            "roll_deg": np.degrees(platform_q[1, :]).tolist(),
            "pitch_deg": np.degrees(platform_q[2, :]).tolist(),
            "deck_center_z_m": deck_center,
        },
        "rocket": {
            "cg_z_m": rocket_q[0, :].tolist(),
            "base_center_z_m": foot_center,
            "vertical_velocity_m_s": rocket_qd[0, :].tolist(),
            "roll_rad": rocket_q[1, :].tolist(),
            "pitch_rad": rocket_q[2, :].tolist(),
            "roll_deg": np.degrees(rocket_q[1, :]).tolist(),
            "pitch_deg": np.degrees(rocket_q[2, :]).tolist(),
        },
        "beam": {
            "axial_m": beam_q[0, :].tolist(),
            "flex_roll_rad": beam_q[1, :].tolist(),
            "flex_pitch_rad": beam_q[2, :].tolist(),
            "flex_roll_deg": np.degrees(beam_q[1, :]).tolist(),
            "flex_pitch_deg": np.degrees(beam_q[2, :]).tolist(),
        },
        "summary": {
            "first_contact_time_s": first_contact,
            "all_legs_contact_time_s": all_legs_contact,
            "final_time_s": float(time[-1]),
            "final_contact_count": int(all_contact_count[-1]),
            "parking_like_state": bool(all_contact_count[-1] == len(leg_ids) and abs(float(rocket_qd[0, -1])) < 0.1),
            "parking_check_note": "True only when all four legs are in contact at final time and vertical speed is below 0.1 m/s.",
            "max_leg_force_kn": float(max_force_leg),
            "max_leg_stroke_m": float(max_stroke_leg),
            "max_total_contact_mn": float(max(total_contact) / 1.0e6),
            "platform_heave": summarize_series(platform_q[0, :]),
            "platform_roll_deg": summarize_series(np.degrees(platform_q[1, :])),
            "platform_pitch_deg": summarize_series(np.degrees(platform_q[2, :])),
            "rocket_cg_z": summarize_series(rocket_q[0, :]),
            "rocket_vertical_velocity": summarize_series(rocket_qd[0, :]),
            "rocket_roll_deg": summarize_series(np.degrees(rocket_q[1, :])),
            "rocket_pitch_deg": summarize_series(np.degrees(rocket_q[2, :])),
            "beam_axial_m": summarize_series(beam_q[0, :]),
            "beam_flex_roll_deg": summarize_series(np.degrees(beam_q[1, :])),
            "beam_flex_pitch_deg": summarize_series(np.degrees(beam_q[2, :])),
        },
    }
    return result


def compact_case(sim: dict[str, Any], config: dict[str, Any], max_points: int = 1500) -> dict[str, Any]:
    time = sim["time_s"]
    start = float(config["time_domain"]["visualization_start_s"])
    end = float(config["time_domain"]["visualization_end_s"])
    indices = [idx for idx, value in enumerate(time) if start <= value <= end]
    if not indices:
        indices = list(range(len(time)))
    stride = max(1, math.ceil(len(indices) / max_points))
    indices = indices[::stride]
    if indices[-1] != max(i for i, value in enumerate(time) if value <= end):
        last = max(i for i, value in enumerate(time) if value <= end)
        if last not in indices:
            indices.append(last)

    def sample_list(values: list[float] | list[int]) -> list[float] | list[int]:
        return [values[i] for i in indices]

    out = {
        "id": sim["id"],
        "environment": sim["environment"],
        "offset": sim["offset"],
        "with_wave": sim["with_wave"],
        "with_plume": sim["with_plume"],
        "summary": sim["summary"],
        "time_s": sample_list(time),
        "forces": {
            "plume_load_n": sample_list(sim["forces"]["plume_load_n"]),
            "total_contact_n": sample_list(sim["forces"]["total_contact_n"]),
            "leg_force_n": {key: sample_list(values) for key, values in sim["forces"]["leg_force_n"].items()},
        },
        "contact": {
            "leg_stroke_m": {key: sample_list(values) for key, values in sim["contact"]["leg_stroke_m"].items()},
            "leg_contact": {key: sample_list(values) for key, values in sim["contact"]["leg_contact"].items()},
            "contact_count": sample_list(sim["contact"]["contact_count"]),
        },
        "platform": {key: sample_list(values) for key, values in sim["platform"].items()},
        "rocket": {key: sample_list(values) for key, values in sim["rocket"].items()},
        "beam": {key: sample_list(values) for key, values in sim["beam"].items()},
    }
    return out


def build_comparison(config: dict[str, Any], simulations: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    thies = LITERATURE_INPUTS["thies_2022"]
    energy = kinetic_energy_kj(config["rocket"]["landing_mass_kg"], config["rocket"]["touchdown_vertical_velocity_m_s"])
    rows.append(
        {
            "id": "thies_touchdown_energy",
            "paper": 766.0,
            "computed": energy,
            "unit": "kJ",
            "source": "Thies Table 7",
            "note": "Direct check from published mass and nominal touchdown velocity.",
        }
    )
    rows.append(
        {
            "id": "thies_reported_damper_deformation",
            "paper": thies["reported_dimensioning_result"]["damper_deformation_m"],
            "computed": simulations["wave_center"]["summary"]["max_leg_stroke_m"] if "wave_center" in simulations else None,
            "unit": "m",
            "source": "Thies Table 8 vs integrated wave_center",
            "note": "Different deck/platform and reduced contact law; comparison is scale/trend only.",
        }
    )
    rows.append(
        {
            "id": "thies_reported_leg_force",
            "paper": thies["reported_dimensioning_result"]["leg_force_magnitude_kn"],
            "computed": simulations["wave_center"]["summary"]["max_leg_force_kn"] if "wave_center" in simulations else None,
            "unit": "kN",
            "source": "Thies Table 8 vs integrated wave_center",
            "note": "Different model; not an Adams-force reproduction.",
        }
    )
    wang_targets = {
        "wave_bow_15m": ("pitch", 0.267, "deg", "Wang Zhi Section 3.2.2"),
        "wave_port_15m": ("roll", 2.898, "deg", "Wang Zhi Section 3.2.2"),
    }
    for case_id, (metric, paper, unit, source) in wang_targets.items():
        if case_id in simulations:
            key = "platform_pitch_deg" if metric == "pitch" else "platform_roll_deg"
            computed = simulations[case_id]["summary"][key]["peak_abs"]
            rows.append(
                {
                    "id": f"wang_{case_id}_{metric}_peak",
                    "paper": paper,
                    "computed": computed,
                    "unit": unit,
                    "source": source,
                    "note": "Integrated model includes rocket contact after 510s, so this is not identical to Wang's platform-only case.",
                }
            )
    return rows


def build_report_data() -> dict[str, Any]:
    ensure_case_dirs()
    config = dict(DEFAULT_CONFIG)
    config["legs"] = dict(DEFAULT_CONFIG["legs"])
    config["rocket"] = dict(DEFAULT_CONFIG["rocket"])
    config["equivalent_beam"] = dict(DEFAULT_CONFIG["equivalent_beam"])
    wang_config = load_wang_config()
    matrices = hydro_matrices(wang_config, WANG_ROOT)
    wang_response = load_wang_response()
    simulations = {}
    for case_id in config["input_cases"]:
        simulations[case_id] = simulate_case(config, wang_config, matrices, case_id, wang_response)
        print(f"Simulated {case_id}: max leg force {simulations[case_id]['summary']['max_leg_force_kn']:.3f} kN")
    comparison = build_comparison(config, simulations)
    full = {
        "case_id": config["case_id"],
        "title": config["title"],
        "config": config,
        "literature_inputs": LITERATURE_INPUTS,
        "hydrodynamic_source": {
            "hams_case": str(WANG_ROOT),
            "dofs": ["heave", "roll", "pitch"],
            "memory_frequencies_rad_s": matrices["omega_rad_s"].tolist(),
            "a_infinite_3dof": matrices["a_inf"].tolist(),
            "rigid_mass_3dof": matrices["rigid_mass"].tolist(),
            "restoring_3dof": matrices["restoring"].tolist(),
        },
        "leg_positions": leg_positions(config),
        "comparison": comparison,
        "simulations": simulations,
        "model_audit": {
            "implemented": [
                "HAMS-derived added mass, radiation damping and hydrostatic restoring for heave/roll/pitch.",
                "Cummins/Ogilvie radiation-memory states in the time-domain ODE.",
                "Wang Zhi 2023 JONSWAP irregular-wave synthesis and plume-load piecewise expression.",
                "Thies RETALT1 rocket mass/inertia/touchdown velocity and four-leg geometry envelope.",
                "Nargolkar equivalent axial and rotational beam modes coupled to the foot heights.",
                "Four independent unilateral leg contact states with compression-only damping and Thies stroke hard-stop.",
            ],
            "not_implemented_because_not_public": DEFAULT_CONFIG["model_limits"],
        },
    }
    write_json(CASE_ROOT / "Output" / "RocketRecovery" / "integrated-recovery-full.json", full)
    compact = {
        **full,
        "simulations": {case_id: compact_case(sim, config) for case_id, sim in simulations.items()},
    }
    write_json(CASE_ROOT / "integrated-recovery-report-data.json", compact)
    return compact


def write_report_js(data: dict[str, Any], path: Path = REPORT_JS) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("window.INTEGRATED_RECOVERY_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the integrated HAMS/Cummins + wave/plume + four-leg contact recovery model.")
    parser.add_argument("action", choices=["report"], nargs="?", default="report")
    args = parser.parse_args()
    if args.action == "report":
        data = build_report_data()
        write_report_js(data)
        print(f"Wrote {CASE_ROOT / 'Output' / 'RocketRecovery' / 'integrated-recovery-full.json'}")
        print(f"Wrote {CASE_ROOT / 'integrated-recovery-report-data.json'}")
        print(f"Wrote {REPORT_JS}")


if __name__ == "__main__":
    main()
