from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .common import ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
except ImportError:
    from common import ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Stage3_LandingLegContact"
WANG_RESPONSE = ROCKET_CASES_DIR / "Paper_WangZhi_2023" / "Output" / "RocketRecovery" / "wang-2023-response.json"
REPORT_JS = VISUALIZATION_DIR / "landing-leg-contact-data.js"


LITERATURE_INPUTS: dict[str, Any] = {
    "thies_2022": {
        "source_file": "海上平台火箭回收文献/P3_Thies_2022.md",
        "model_role": "first landing-leg/contact envelope reference",
        "rocket": {
            "height_m": 103.0,
            "core_stage_height_m": 64.7,
            "base_diameter_m": 6.0,
            "engine_length_m": 1.902,
            "nozzle_diameter_m": 1.095,
            "allowed_nozzle_clearance_m": 0.5475,
            "landing_mass_kg": 61_288.0,
            "dry_mass_with_legs_kg": 59_288.0,
            "propellant_at_touchdown_kg": 2_000.0,
            "landing_gear_total_mass_kg": 4_000.0,
            "cog_from_launcher_base_m": 22.059,
            "inertia_kg_m2": {"pitch_ixx": 2.57e7, "roll_iyy": 3.76e5, "yaw_izz": 2.57e7},
            "source": "Table 3 / vehicle data table",
        },
        "landing_leg": {
            "leg_count": 4,
            "configuration": "Tripod",
            "upper_attachment_t_height_m": 9.0,
            "upper_attachment_k_height_m": 5.7,
            "lower_attachment_b_height_m": 4.4,
            "leg_angle_to_hinge_plane_deg": 33.0,
            "strut_angle_to_hinge_plane_deg": 51.0,
            "leg_length_m": 8.1,
            "strut_lengths_m": [11.2, 7.4],
            "source": "Table 4",
        },
        "requirements": {
            "platform_size_m": [50.0, 50.0],
            "launcher_incident_angle_nominal_deg": 0.0,
            "launcher_incident_angle_max_deg": 10.0,
            "touchdown_vertical_velocity_nominal_m_s": 5.0,
            "touchdown_vertical_velocity_min_m_s": 1.0,
            "touchdown_vertical_velocity_max_m_s": 15.0,
            "touchdown_lateral_velocity_nominal_m_s": 0.0,
            "touchdown_lateral_velocity_max_m_s": 5.0,
            "angular_velocity_max_deg_s": 2.0,
            "friction_coefficient_nominal": 0.5,
            "friction_coefficient_min": 0.1,
            "friction_coefficient_max": 1.0,
            "source": "Table 6",
        },
        "dimensioning_case": {
            "vertical_velocity_m_s": 5.0,
            "lateral_velocity_m_s": 0.0,
            "number_of_first_touchdown_legs": 4,
            "kinetic_energy_kj": 766.0,
            "friction": "not applied in the early phase of load derivation",
            "source": "Table 7",
        },
        "reported_dimensioning_result": {
            "nozzle_clearance_m": 0.570,
            "damper_deformation_m": 0.420,
            "leg_force_magnitude_kn": 902.0,
            "spring_damper_force_kn": 935.0,
            "source": "Table 8",
        },
        "linear_contact_parameters": {
            "damper_stiffness_n_m": 2600.0 * 1000.0,
            "platform_stiffness_n_m": 100_000.0 * 1000.0,
            "damper_damping_ns_m": 1300.0 * 1000.0,
            "platform_damping_ns_m": 10.0 * 1000.0,
            "source": "Table 10; converted from N/mm and Nsec/mm",
            "usage_note": "Recorded for later nonlinear contact work; not used to claim force reproduction in this envelope report.",
        },
    },
    "li_2025": {
        "source_file": "海上平台火箭回收文献/P5_Li_2025_Aerospace.md",
        "model_role": "later flexible-rigid contact and friction upgrade",
        "contact": {
            "stiffness_n_m": 1.0e8,
            "damping_ns_m": 1.0e7,
            "radius_m": 0.2,
            "exponent": 2.0,
            "static_friction": 0.6,
            "dynamic_friction": 0.4,
            "source": "Table 2",
        },
        "load_environment": {
            "wind_velocity_m_s": 10.0,
            "drag_factor": 0.9,
            "windward_area_m2": 45.3,
            "air_density_kg_m3": 1.29,
            "source": "Table 2",
        },
        "simulation_velocities_m_s": [1.8, 2.45],
    },
    "yue_2022": {
        "source_file": "海上平台火箭回收文献/P4_Yue_2022.md",
        "model_role": "experimental validation target for future quasi-3D landing-leg model",
        "test_conditions": [
            {"id": "condition_1_2-2", "vertical_velocity_m_s": 1.4, "horizontal_velocity_m_s": 0.354, "tilt_angle_deg": -2.0, "landing_mode": "2-2"},
            {"id": "condition_2_1-2-1", "vertical_velocity_m_s": 1.4, "horizontal_velocity_m_s": 0.354, "tilt_angle_deg": -2.0, "landing_mode": "1-2-1"},
        ],
        "reported_validation_ranges": {
            "damper_stroke_rms_error": "below 18%",
            "main_strut_force_rms_error": "16.9%-22.4%",
            "auxiliary_strut_force_rms_error": "20.2%-40.0%",
            "main_body_acceleration_rms_error": "55.9%-66.0%",
            "energy_absorption_error": "below 22%",
            "energy_dissipation_error": "20.9%-37.5%",
        },
    },
    "wang_actuators_2023": {
        "source_file": "海上平台火箭回收文献/P6_Wang_2023_Actuators.md",
        "model_role": "later state-machine reference for rebound, stick-slip, and crushing buffer",
        "experiment": {"freefall_height_m": 0.2},
        "reported_errors": {
            "impact_force_steady_error": 0.0976,
            "buffering_force_steady_error": 0.1140,
            "impact_force_peak_error": 0.099,
            "buffering_force_peak_error": 0.1972,
            "stroke_steady_error": 0.0028,
            "main_body_acceleration_experiment_m_s2": 43.5,
            "main_body_acceleration_simulation_m_s2": 23.8,
        },
    },
    "xie_2025": {
        "source_file": "海上平台火箭回收文献/P7_Xie_2025.md",
        "model_role": "later Cummins/impact-platform validation target",
        "platform": {
            "length_m": 151.2,
            "breadth_m": 70.0,
            "depth_m": 38.0,
            "draft_m": 21.0,
            "cg_from_stern_m": 73.877,
            "cg_above_bottom_m": 16.27,
            "inertia_kg_m2": {"ixx": 5.14e10, "iyy": 1.19e11, "izz": 1.42e11},
            "source": "Table 1",
        },
        "validation": {
            "scale_ratio": "1:40",
            "frequency_domain_nodes": 2374,
            "frequency_domain_panels": 2304,
            "artificial_damping": {
                "heave_n_s_m": 3.25e6,
                "roll_nm_s_rad": 2.8e9,
                "pitch_nm_s_rad": 1.44e10,
            },
            "regular_wave": {"period_s": 6.0, "height_m": 2.5, "direction_deg": 135.0},
            "impact_force": {"duration_s": 1.9, "peak_n": 2.0e7, "rocket_weight_n": 2.45e6},
            "reported_motion_periods_s": {"heave": 17.5, "pitch": 17.6},
            "moderate_sea_state_bounds": {"max_heave_m": 0.6, "max_pitch_deg": 1.0},
        },
    },
}


def thies_footprint_radius_m(inputs: dict[str, Any] | None = None) -> float:
    thies = (inputs or LITERATURE_INPUTS)["thies_2022"]
    leg = thies["landing_leg"]
    return float(leg["leg_length_m"]) * math.cos(math.radians(float(leg["leg_angle_to_hinge_plane_deg"])))


def kinetic_energy_kj(mass_kg: float, velocity_m_s: float) -> float:
    return 0.5 * mass_kg * velocity_m_s**2 / 1000.0


def _nearest_index(values: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(values - target)))


def compact_series(time: np.ndarray, values: dict[str, np.ndarray], max_points: int = 1200) -> dict[str, Any]:
    stride = max(1, math.ceil(len(time) / max_points))
    indices = list(range(0, len(time), stride))
    if indices[-1] != len(time) - 1:
        indices.append(len(time) - 1)
    return {
        "time_s": [float(time[i]) for i in indices],
        "series": {key: [float(series[i]) for i in indices] for key, series in values.items()},
    }


def deck_footprint_envelope(
    heave_m: np.ndarray,
    roll_rad: np.ndarray,
    pitch_rad: np.ndarray,
    heave_m_s: np.ndarray,
    roll_rad_s: np.ndarray,
    pitch_rad_s: np.ndarray,
    radius_m: float,
) -> dict[str, np.ndarray]:
    heave_m = np.asarray(heave_m, dtype=float)
    roll_rad = np.asarray(roll_rad, dtype=float)
    pitch_rad = np.asarray(pitch_rad, dtype=float)
    heave_m_s = np.asarray(heave_m_s, dtype=float)
    roll_rad_s = np.asarray(roll_rad_s, dtype=float)
    pitch_rad_s = np.asarray(pitch_rad_s, dtype=float)
    angle_rad = np.sqrt(roll_rad**2 + pitch_rad**2)
    angle_rate_rad_s = np.sqrt(roll_rad_s**2 + pitch_rad_s**2)
    dz_halfspan = radius_m * angle_rad
    vertical_velocity_halfspan = radius_m * angle_rate_rad_s
    return {
        "deck_angle_deg": np.degrees(angle_rad),
        "foot_vertical_spread_m": 2.0 * dz_halfspan,
        "deck_vz_min_m_s": heave_m_s - vertical_velocity_halfspan,
        "deck_vz_max_m_s": heave_m_s + vertical_velocity_halfspan,
        "heave_m": heave_m,
    }


def summarize_envelope(time: np.ndarray, envelope: dict[str, np.ndarray], touchdown_velocity_m_s: float) -> dict[str, Any]:
    terminal = (time >= 506.0) & (time <= 511.0)
    plume = (time >= 480.0) & (time <= 511.0)
    touchdown_i = _nearest_index(time, 510.0)

    closing_min = touchdown_velocity_m_s + envelope["deck_vz_min_m_s"]
    closing_max = touchdown_velocity_m_s + envelope["deck_vz_max_m_s"]
    lead = envelope["foot_vertical_spread_m"] / max(touchdown_velocity_m_s, 1.0e-12)

    def max_in(mask: np.ndarray, key: str) -> float:
        if not np.any(mask):
            return float("nan")
        return float(np.max(np.abs(envelope[key][mask])))

    return {
        "touchdown_time_s": float(time[touchdown_i]),
        "touchdown": {
            "deck_angle_deg": float(envelope["deck_angle_deg"][touchdown_i]),
            "foot_vertical_spread_m": float(envelope["foot_vertical_spread_m"][touchdown_i]),
            "first_touch_lead_s": float(lead[touchdown_i]),
            "deck_vz_min_m_s": float(envelope["deck_vz_min_m_s"][touchdown_i]),
            "deck_vz_max_m_s": float(envelope["deck_vz_max_m_s"][touchdown_i]),
            "closing_speed_min_m_s": float(closing_min[touchdown_i]),
            "closing_speed_max_m_s": float(closing_max[touchdown_i]),
        },
        "terminal_506_511": {
            "deck_angle_peak_deg": max_in(terminal, "deck_angle_deg"),
            "foot_vertical_spread_peak_m": max_in(terminal, "foot_vertical_spread_m"),
            "first_touch_lead_peak_s": float(np.max(lead[terminal])) if np.any(terminal) else float("nan"),
            "deck_vz_min_m_s": float(np.min(envelope["deck_vz_min_m_s"][terminal])) if np.any(terminal) else float("nan"),
            "deck_vz_max_m_s": float(np.max(envelope["deck_vz_max_m_s"][terminal])) if np.any(terminal) else float("nan"),
            "closing_speed_min_m_s": float(np.min(closing_min[terminal])) if np.any(terminal) else float("nan"),
            "closing_speed_max_m_s": float(np.max(closing_max[terminal])) if np.any(terminal) else float("nan"),
        },
        "plume_480_511": {
            "deck_angle_peak_deg": max_in(plume, "deck_angle_deg"),
            "foot_vertical_spread_peak_m": max_in(plume, "foot_vertical_spread_m"),
            "first_touch_lead_peak_s": float(np.max(lead[plume])) if np.any(plume) else float("nan"),
        },
    }


def analyze_wang_response(path: Path = WANG_RESPONSE) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing Wang 2023 response JSON: {path}")
    wang = read_json(path)
    thies = LITERATURE_INPUTS["thies_2022"]
    requirements = thies["requirements"]
    mass = float(thies["rocket"]["landing_mass_kg"])
    nominal_v = float(requirements["touchdown_vertical_velocity_nominal_m_s"])
    max_v = float(requirements["touchdown_vertical_velocity_max_m_s"])
    radius = thies_footprint_radius_m()

    simulations: dict[str, Any] = {}
    for sim_id, sim in wang["simulations"].items():
        time = np.array(sim["time_s"], dtype=float)
        envelope = deck_footprint_envelope(
            np.array(sim["responses"]["heave_m"], dtype=float),
            np.array(sim["responses"]["roll_rad"], dtype=float),
            np.array(sim["responses"]["pitch_rad"], dtype=float),
            np.array(sim["velocities"]["heave_m_s"], dtype=float),
            np.array(sim["velocities"]["roll_rad_s"], dtype=float),
            np.array(sim["velocities"]["pitch_rad_s"], dtype=float),
            radius,
        )
        summary = summarize_envelope(time, envelope, nominal_v)
        summary["checks"] = {
            "deck_angle_within_thies_max": summary["terminal_506_511"]["deck_angle_peak_deg"] <= requirements["launcher_incident_angle_max_deg"],
            "closing_speed_within_thies_vertical_velocity_envelope": (
                summary["terminal_506_511"]["closing_speed_min_m_s"] >= requirements["touchdown_vertical_velocity_min_m_s"]
                and summary["terminal_506_511"]["closing_speed_max_m_s"] <= max_v
            ),
        }
        simulations[sim_id] = {
            "id": sim["id"],
            "environment": sim["environment"],
            "offset": sim["offset"],
            "with_wave": sim["with_wave"],
            "with_plume": sim["with_plume"],
            "summary": summary,
            "time_history": compact_series(
                time,
                {
                    "deck_angle_deg": envelope["deck_angle_deg"],
                    "foot_vertical_spread_m": envelope["foot_vertical_spread_m"],
                    "deck_vz_min_m_s": envelope["deck_vz_min_m_s"],
                    "deck_vz_max_m_s": envelope["deck_vz_max_m_s"],
                    "closing_speed_min_m_s": nominal_v + envelope["deck_vz_min_m_s"],
                    "closing_speed_max_m_s": nominal_v + envelope["deck_vz_max_m_s"],
                },
            ),
        }

    energy_nominal = kinetic_energy_kj(mass, nominal_v)
    energy_max = kinetic_energy_kj(mass, max_v)
    paper_energy = float(thies["dimensioning_case"]["kinetic_energy_kj"])
    comparison = [
        {
            "id": "thies_nominal_touchdown_energy",
            "paper_value": paper_energy,
            "computed_value": energy_nominal,
            "unit": "kJ",
            "abs_error": abs(energy_nominal - paper_energy),
            "relative_error": abs(energy_nominal - paper_energy) / paper_energy,
            "source": "Thies Table 7; computed from 0.5*m*v^2 with Table 3 mass and Table 6 nominal velocity",
        }
    ]

    return {
        "case_id": "Stage3_LandingLegContact",
        "title": "Landing-leg-on-moving-deck envelope from Thies 2022 + Wang Zhi 2023",
        "method": {
            "scope": "Kinematic pre-contact/contact-envelope coupling. No force reproduction is claimed.",
            "hydrodynamic_source": str(path),
            "deck_envelope": "For a circular footprint radius r, z_deck = heave + roll*y - pitch*x. The foot spread is 2*r*sqrt(roll^2+pitch^2).",
            "relative_velocity": "Deck vertical velocity is heave_dot +/- r*sqrt(roll_dot^2+pitch_dot^2); closing speed adds Thies vertical touchdown speed.",
            "footprint_radius_m": radius,
            "footprint_radius_source": "r = L_leg*cos(beta0), from Thies Table 4 leg length and leg angle.",
            "why_no_force_reproduction": "Thies force histories were generated in MSC Adams with landing-gear geometry and nonlinear spring-damper curves not published as complete numeric functions; Wang deck motion is a different barge.",
        },
        "literature_inputs": LITERATURE_INPUTS,
        "derived_quantities": {
            "thies_nominal_kinetic_energy_kj": energy_nominal,
            "thies_nominal_energy_per_leg_if_4_legs_kj": energy_nominal / 4.0,
            "thies_nominal_energy_per_leg_if_2_legs_kj": energy_nominal / 2.0,
            "thies_nominal_energy_if_single_leg_kj": energy_nominal,
            "thies_max_velocity_kinetic_energy_kj": energy_max,
            "thies_footprint_radius_m": radius,
        },
        "comparison": comparison,
        "simulations": simulations,
        "model_audit": {
            "published_inputs_used": [
                "Thies 2022: RETALT1 landing mass, nominal/min/max touchdown velocities, incident angle envelope, leg length, leg angle, Table 7 kinetic energy.",
                "Wang Zhi 2023: HAMS/Cummins surrogate time histories generated from the published barge dimensions, JONSWAP sea state, and plume load expression.",
                "Li 2025, Yue 2022, Wang Actuators 2023, Xie 2025: stored as implementation/validation references for the next force-contact stage.",
            ],
            "not_yet_modeled": [
                "Four individual leg azimuths and exact attachment coordinates are not published in the extracted Thies material, so this report uses a circular footprint envelope rather than pretending an exact leg layout.",
                "No hydraulic/pneumatic nonlinear force-stroke and force-velocity curves are machine-readable in the supplied files.",
                "No stick-slip, rebound, structural flexibility, or overturning integration is performed in this stage.",
            ],
        },
    }


def build_report() -> dict[str, Any]:
    data = analyze_wang_response()
    write_json(CASE_ROOT / "landing-leg-contact-envelope.json", data)
    return data


def write_report_js(data: dict[str, Any], path: Path = REPORT_JS) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("window.LANDING_LEG_CONTACT_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Thies/Wang landing-leg moving-deck contact-envelope report.")
    parser.add_argument("action", choices=["report"], nargs="?", default="report")
    args = parser.parse_args()
    if args.action == "report":
        data = build_report()
        write_report_js(data)
        comparison = data["comparison"][0]
        print(f"Wrote {CASE_ROOT / 'landing-leg-contact-envelope.json'}")
        print(f"Wrote {REPORT_JS}")
        print(
            "Thies nominal energy: "
            f"{comparison['computed_value']:.3f} {comparison['unit']} vs paper {comparison['paper_value']:.3f} {comparison['unit']}"
        )
        print(f"Footprint radius from Thies leg geometry: {data['derived_quantities']['thies_footprint_radius_m']:.3f} m")


if __name__ == "__main__":
    main()
