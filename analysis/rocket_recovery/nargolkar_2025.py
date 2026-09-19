from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigh

try:
    from .common import (
        G,
        RHO,
        ROCKET_CASES_DIR,
        VISUALIZATION_DIR,
        ensure_case_output_dirs,
        fortran_float,
        parse_hydrostar_rao,
        parse_pnl,
        read_json,
        write_json,
        write_pnl,
    )
    from .recovery_window_report import mesh_to_three
except ImportError:
    from common import (
        G,
        RHO,
        ROCKET_CASES_DIR,
        VISUALIZATION_DIR,
        ensure_case_output_dirs,
        fortran_float,
        parse_hydrostar_rao,
        parse_pnl,
        read_json,
        write_json,
        write_pnl,
    )
    from recovery_window_report import mesh_to_three


PAPER_ID = "Nargolkar_2025_PMA"
PAPER_ROOT = ROCKET_CASES_DIR / "Paper_Nargolkar_2025"
REPORT_JS = VISUALIZATION_DIR / "nargolkar-2025-data.js"
PAPER_MD = Path("海上平台火箭回收文献") / "065002_1_2.0002061.md"
PAPER_PDF = Path("海上平台火箭回收文献") / "065002_1_2.0002061.pdf"
PAPER_FIGURES_DIR = PAPER_ROOT / "paper_figures"

DOF_LABELS = [
    "barge_surge_m",
    "barge_heave_m",
    "barge_pitch_rad",
    "rlv_transverse_m",
    "rlv_axial_m",
    "rlv_rotation_rad",
]

PAPER_TIME_DIGITIZATION = {
    "Box Barge": {
        "image": "figure9_box_barge.jpg",
        "center_case": "BoxBarge_Center",
        "offset_case": "BoxBarge_Offset5m",
        "axes": {
            "barge_surge_m": {"box": [87, 34, 631, 229], "ylim": [-2.0e-4, 2.0e-4]},
            "rlv_transverse_m": {"box": [803, 34, 1347, 229], "ylim": [-2.0e-4, 2.0e-4]},
            "barge_heave_m": {"box": [87, 317, 631, 512], "ylim": [-2.5e-2, 2.5e-2]},
            "rlv_axial_m": {"box": [803, 317, 1347, 512], "ylim": [-4.0e-2, 4.0e-2]},
            "barge_pitch_rad": {"box": [87, 599, 631, 794], "ylim": [-6.0e-4, 4.0e-4]},
            "rlv_rotation_rad": {"box": [803, 599, 1347, 794], "ylim": [-6.0e-4, 4.0e-4]},
        },
    },
    "MARMAC 302": {
        "image": "figure10_marmac302.jpg",
        "center_case": "MARMAC302_Center",
        "offset_case": "MARMAC302_Offset30m",
        "axes": {
            "barge_surge_m": {"box": [85, 36, 629, 231], "ylim": [-1.0e-6, 1.5e-6]},
            "rlv_transverse_m": {"box": [801, 36, 1345, 231], "ylim": [-1.0e-6, 1.5e-6]},
            "barge_heave_m": {"box": [85, 319, 629, 514], "ylim": [-1.0e-3, 1.0e-3]},
            "rlv_axial_m": {"box": [801, 319, 1345, 514], "ylim": [-1.1e-2, 1.1e-2]},
            "barge_pitch_rad": {"box": [85, 601, 629, 796], "ylim": [-4.0e-7, 4.0e-7]},
            "rlv_rotation_rad": {"box": [801, 601, 1345, 796], "ylim": [-4.0e-7, 4.0e-7]},
        },
    },
}


PAPER_CASES: dict[str, dict[str, Any]] = {
    "BoxBarge_Center": {
        "title": "Box Barge - center landing",
        "barge_family": "Box Barge",
        "landing": {"offset_m": 0.0, "paper_offset_label": "center"},
        "platform": {
            "length_m": 44.0,
            "beam_m": 4.0,
            "depth_m": 4.0,
            "draft_m": 2.0,
            "deck_z_m": 2.0,
            "mass_kg": 260800.0,
            "cg_m": [0.0, 0.0, -0.0238],
            "hull_shape": "rectangular_box",
            "water_depth_m": -1.0,
            "rho_kg_m3": RHO,
            "gravity_m_s2": G,
        },
        "mesh": {"nx": 24, "ny": 8, "nz": 5},
        "rlv": {
            "mass_kg": 100000.0,
            "height_m": 22.0,
            "radius_m": 1.6,
            "thickness_m": 0.004,
            "youngs_modulus_pa": 210.0e9,
            "table": {
                "transverse_stiffness_n_m": 7.85e5,
                "axial_stiffness_n_m": 3.84e8,
                "rotational_stiffness_nm_rad": 6.12e7,
                "transverse_eq_mass_kg": 48.03,
                "axial_eq_mass_kg": 10803.24,
                "rotational_eq_mass_kg": 704.47,
                "heave_corrected_barge_mass_kg": 3.50e5,
            },
        },
    },
    "BoxBarge_Offset5m": {
        "title": "Box Barge - 5 m offset landing",
        "barge_family": "Box Barge",
        "landing": {"offset_m": 5.0, "paper_offset_label": "a = 5 m"},
        "platform": {
            "length_m": 44.0,
            "beam_m": 4.0,
            "depth_m": 4.0,
            "draft_m": 2.0,
            "deck_z_m": 2.0,
            "mass_kg": 260800.0,
            "cg_m": [1.3858, 0.0, -0.0238],
            "hull_shape": "rectangular_box",
            "water_depth_m": -1.0,
            "rho_kg_m3": RHO,
            "gravity_m_s2": G,
        },
        "mesh": {"nx": 24, "ny": 8, "nz": 5},
        "rlv": {
            "mass_kg": 100000.0,
            "height_m": 22.0,
            "radius_m": 1.6,
            "thickness_m": 0.004,
            "youngs_modulus_pa": 210.0e9,
            "table": {
                "transverse_stiffness_n_m": 7.85e5,
                "axial_stiffness_n_m": 3.84e8,
                "rotational_stiffness_nm_rad": 6.12e7,
                "transverse_eq_mass_kg": 48.03,
                "axial_eq_mass_kg": 10803.24,
                "rotational_eq_mass_kg": 704.47,
                "heave_corrected_barge_mass_kg": 3.50e5,
            },
        },
    },
    "MARMAC302_Center": {
        "title": "MARMAC 302 - center landing",
        "barge_family": "MARMAC 302",
        "landing": {"offset_m": 0.0, "paper_offset_label": "center"},
        "platform": {
            "length_m": 91.44,
            "beam_m": 30.48,
            "depth_m": 6.0198,
            "draft_m": 2.9718,
            "deck_z_m": 3.048,
            "mass_kg": 7129486.0,
            "cg_m": [0.0, 0.0, -0.0025],
            "hull_shape": "trapezoidal_prism_mass_matched",
            "water_depth_m": -1.0,
            "rho_kg_m3": RHO,
            "gravity_m_s2": G,
        },
        "mesh": {"nx": 30, "ny": 12, "nz": 5},
        "rlv": {
            "mass_kg": 20000.0,
            "height_m": 40.9,
            "radius_m": 1.83,
            "thickness_m": 0.005,
            "youngs_modulus_pa": 210.0e9,
            "table": {
                "transverse_stiffness_n_m": 5.52e4,
                "axial_stiffness_n_m": 2.95e8,
                "rotational_stiffness_nm_rad": 1.50e6,
                "transverse_eq_mass_kg": 13.98,
                "axial_eq_mass_kg": 8307.97,
                "rotational_eq_mass_kg": 381.08,
                "heave_corrected_barge_mass_kg": 7.14e6,
            },
        },
    },
    "MARMAC302_Offset30m": {
        "title": "MARMAC 302 - 30 m offset landing",
        "barge_family": "MARMAC 302",
        "landing": {"offset_m": 30.0, "paper_offset_label": "a = 30 m"},
        "platform": {
            "length_m": 91.44,
            "beam_m": 30.48,
            "depth_m": 6.0198,
            "draft_m": 2.9718,
            "deck_z_m": 3.048,
            "mass_kg": 7129486.0,
            "cg_m": [0.0839, 0.0, -0.0025],
            "hull_shape": "trapezoidal_prism_mass_matched",
            "water_depth_m": -1.0,
            "rho_kg_m3": RHO,
            "gravity_m_s2": G,
        },
        "mesh": {"nx": 30, "ny": 12, "nz": 5},
        "rlv": {
            "mass_kg": 20000.0,
            "height_m": 40.9,
            "radius_m": 1.83,
            "thickness_m": 0.005,
            "youngs_modulus_pa": 210.0e9,
            "table": {
                "transverse_stiffness_n_m": 5.52e4,
                "axial_stiffness_n_m": 2.95e8,
                "rotational_stiffness_nm_rad": 1.50e6,
                "transverse_eq_mass_kg": 13.98,
                "axial_eq_mass_kg": 8307.97,
                "rotational_eq_mass_kg": 381.08,
                "heave_corrected_barge_mass_kg": 7.14e6,
            },
        },
    },
}


def linspace(start: float, end: float, count: int) -> list[float]:
    if count == 1:
        return [start]
    step = (end - start) / (count - 1)
    return [start + i * step for i in range(count)]


def paper_config(case_id: str, base: dict[str, Any]) -> dict[str, Any]:
    config = {
        "case_id": case_id,
        "paper_id": PAPER_ID,
        "title": base["title"],
        "barge_family": base["barge_family"],
        "platform": dict(base["platform"]),
        "mesh": dict(base["mesh"]),
        "reference_point_m": [0.0, 0.0, 0.0],
        "landing": dict(base["landing"]),
        "rlv": dict(base["rlv"]),
        "frequency": {"min_rad_s": 0.2, "max_rad_s": 4.0, "step_rad_s": 0.1},
        "headings_deg": [0.0],
        "touchdown_velocity_m_s": [1.0, 2.0, 3.0],
        "time_domain": {
            "duration_s": 10.0,
            "dt_s": 0.002,
            "hydro_damping_sample_rad_s": 1.0,
            "hydrodynamic_memory": "cummins_cosine_quadrature_from_hams_B",
            "added_mass_infinite_estimate": "highest_computed_frequency",
            "structural_damping_ratio": 0.0,
            "barge_viscous_damping_ratio": 0.0,
            "contact_damping_ratio": 0.0,
            "surge_mooring_stiffness_n_m": 0.0,
            "use_target_structural_frequencies": False,
        },
        "paper_targets": {
            "source_markdown": str(PAPER_MD.as_posix()),
            "source_pdf": str(PAPER_PDF.as_posix()),
            "qualitative_claims": [
                "Center landing does not excite pitch in the symmetric XZ model.",
                "Offset landing induces heave-pitch coupling.",
                "Offset landing increases barge pitch and RLV transverse response.",
                "Hydrodynamic low-frequency response and structural 10/30 Hz response are separated by a bandgap.",
            ],
        },
        "model_notes": {
            "scope": "Paper-oriented reproduction of the 3DOF barge plus 3DOF equivalent-RLV touchdown model.",
            "hams_role": "HAMS supplies frequency-domain added mass and radiation damping; touchdown coupling is solved externally.",
            "limits": "The paper does not publish MATLAB code, impact law, mesh, mooring stiffness, or digitized figure values. This is a transparent parameter-matched surrogate, not a hidden rebaseline.",
        },
    }
    add_derived_platform_fields(config)
    add_derived_rlv_fields(config)
    return config


def add_derived_platform_fields(config: dict[str, Any]) -> None:
    platform = config["platform"]
    length = platform["length_m"]
    beam = platform["beam_m"]
    draft = platform["draft_m"]
    rho = platform["rho_kg_m3"]
    mass_volume = platform["mass_kg"] / rho
    rectangular_volume = length * beam * draft
    if platform["hull_shape"] == "trapezoidal_prism_mass_matched":
        bottom_beam = max(0.1 * beam, min(beam, 2.0 * mass_volume / (length * draft) - beam))
    else:
        bottom_beam = beam
    platform["bottom_beam_m"] = bottom_beam
    platform["geometry_displacement_volume_m3"] = length * draft * 0.5 * (beam + bottom_beam)
    platform["paper_mass_displacement_volume_m3"] = mass_volume
    platform["rectangular_displacement_volume_m3"] = rectangular_volume
    platform["waterplane_area_m2"] = length * beam


def add_derived_rlv_fields(config: dict[str, Any]) -> None:
    table = config["rlv"]["table"]
    target_freq = {"transverse": 10.0, "axial": 30.0, "rotational": 10.0}
    stiffness = {
        "transverse": table["transverse_stiffness_n_m"],
        "axial": table["axial_stiffness_n_m"],
        "rotational": table["rotational_stiffness_nm_rad"],
    }
    paper_mass = {
        "transverse": table["transverse_eq_mass_kg"],
        "axial": table["axial_eq_mass_kg"],
        "rotational": table["rotational_eq_mass_kg"],
    }
    target_mass = {mode: stiffness[mode] / (2.0 * math.pi * freq) ** 2 for mode, freq in target_freq.items()}
    table_freq = {mode: math.sqrt(stiffness[mode] / paper_mass[mode]) / (2.0 * math.pi) for mode in target_freq}
    config["rlv"]["derived"] = {
        "target_frequency_hz": target_freq,
        "table_frequency_hz": table_freq,
        "target_frequency_eq_mass_kg": target_mass,
        "mass_used_note": "Strict mode uses the equivalent masses printed in Table 2. The table-implied frequencies are reported separately because Table 2 is not fully consistent with the paper text.",
    }


def append_surface(
    nodes: list[tuple[float, float, float]],
    panels: list[list[int]],
    grid: list[list[tuple[float, float, float]]],
    orientation: str,
) -> None:
    start = len(nodes) + 1
    for row in grid:
        nodes.extend(row)
    cols = len(grid[0])
    for r in range(len(grid) - 1):
        for c in range(cols - 1):
            n00 = start + r * cols + c
            n10 = start + r * cols + c + 1
            n01 = start + (r + 1) * cols + c
            n11 = start + (r + 1) * cols + c + 1
            if orientation in {"up", "minus_y", "plus_x"}:
                panels.append([n00, n01, n11, n10])
            else:
                panels.append([n00, n10, n11, n01])


def half_beam_at_z(platform: dict[str, Any], z: float) -> float:
    draft = platform["draft_m"]
    top = platform["beam_m"] / 2.0
    bottom = platform["bottom_beam_m"] / 2.0
    t = (z + draft) / draft
    return bottom + (top - bottom) * t


def build_paper_mesh(config: dict[str, Any]) -> tuple[list[tuple[float, float, float]], list[list[int]], list[tuple[float, float, float]], list[list[int]]]:
    platform = config["platform"]
    mesh = config["mesh"]
    length = platform["length_m"]
    beam = platform["beam_m"]
    draft = platform["draft_m"]
    bottom_beam = platform["bottom_beam_m"]
    nx = int(mesh["nx"])
    ny = int(mesh["ny"])
    nz = int(mesh["nz"])

    xs = linspace(-length / 2.0, length / 2.0, nx + 1)
    ys_top = linspace(-beam / 2.0, beam / 2.0, ny + 1)
    ys_bottom = linspace(-bottom_beam / 2.0, bottom_beam / 2.0, ny + 1)
    zs = linspace(-draft, 0.0, nz + 1)

    hull_nodes: list[tuple[float, float, float]] = []
    hull_panels: list[list[int]] = []

    bottom_grid = [[(x, y, -draft) for x in xs] for y in ys_bottom]
    append_surface(hull_nodes, hull_panels, bottom_grid, "up")

    port_grid = [[(x, -half_beam_at_z(platform, z), z) for x in xs] for z in zs]
    append_surface(hull_nodes, hull_panels, port_grid, "plus_y")

    starboard_grid = [[(x, half_beam_at_z(platform, z), z) for x in xs] for z in zs]
    append_surface(hull_nodes, hull_panels, starboard_grid, "minus_y")

    aft_grid = []
    forward_grid = []
    for z in zs:
        half_beam = half_beam_at_z(platform, z)
        ys = linspace(-half_beam, half_beam, ny + 1)
        aft_grid.append([(-length / 2.0, y, z) for y in ys])
        forward_grid.append([(length / 2.0, y, z) for y in ys])
    append_surface(hull_nodes, hull_panels, aft_grid, "plus_x")
    append_surface(hull_nodes, hull_panels, forward_grid, "minus_x")

    water_nodes: list[tuple[float, float, float]] = []
    water_panels: list[list[int]] = []
    water_grid = [[(x, y, 0.0) for x in xs] for y in ys_top]
    append_surface(water_nodes, water_panels, water_grid, "up")
    return hull_nodes, hull_panels, water_nodes, water_panels


def rigid_mass_matrix_6d(config: dict[str, Any]) -> list[list[float]]:
    platform = config["platform"]
    length = platform["length_m"]
    beam = platform["beam_m"]
    depth = platform["depth_m"]
    mass = platform["mass_kg"]
    xg, yg, zg = platform["cg_m"]
    ixx_cg = mass * (beam**2 + depth**2) / 12.0
    iyy_cg = mass * (length**2 + depth**2) / 12.0
    izz_cg = mass * (length**2 + beam**2) / 12.0
    matrix = [[0.0 for _ in range(6)] for _ in range(6)]
    for i in range(3):
        matrix[i][i] = mass
    matrix[0][4] = matrix[4][0] = mass * zg
    matrix[0][5] = matrix[5][0] = -mass * yg
    matrix[1][3] = matrix[3][1] = -mass * zg
    matrix[1][5] = matrix[5][1] = mass * xg
    matrix[2][3] = matrix[3][2] = mass * yg
    matrix[2][4] = matrix[4][2] = -mass * xg
    matrix[3][3] = ixx_cg + mass * (yg**2 + zg**2)
    matrix[4][4] = iyy_cg + mass * (xg**2 + zg**2)
    matrix[5][5] = izz_cg + mass * (xg**2 + yg**2)
    matrix[3][4] = matrix[4][3] = -mass * xg * yg
    matrix[3][5] = matrix[5][3] = -mass * xg * zg
    matrix[4][5] = matrix[5][4] = -mass * yg * zg
    return matrix


def hydrostatic_matrix_6d(config: dict[str, Any]) -> list[list[float]]:
    platform = config["platform"]
    length = platform["length_m"]
    beam = platform["beam_m"]
    draft = platform["draft_m"]
    xg, _yg, zg = platform["cg_m"]
    rho = platform["rho_kg_m3"]
    gravity = platform["gravity_m_s2"]
    volume = platform["geometry_displacement_volume_m3"]
    waterplane_area = platform["waterplane_area_m2"]
    kb = -draft / 2.0
    iwp_roll = length * beam**3 / 12.0
    iwp_pitch = beam * length**3 / 12.0
    gm_roll = kb + iwp_roll / max(volume, 1.0e-9) - zg
    gm_pitch = kb + iwp_pitch / max(volume, 1.0e-9) - zg
    matrix = [[0.0 for _ in range(6)] for _ in range(6)]
    matrix[2][2] = rho * gravity * waterplane_area
    matrix[3][3] = rho * gravity * volume * gm_roll
    matrix[4][4] = rho * gravity * volume * gm_pitch
    matrix[2][4] = matrix[4][2] = -rho * gravity * waterplane_area * xg
    return matrix


def write_matrix(lines: list[str], title: str, matrix: list[list[float]]) -> None:
    lines.append(f" {title}:")
    for row in matrix:
        lines.append("  " + "  ".join(f"{value:12.5E}" for value in row))


def zero_matrix_6d() -> list[list[float]]:
    return [[0.0 for _ in range(6)] for _ in range(6)]


def write_hydrostatic(path: Path, config: dict[str, Any]) -> dict[str, Any]:
    platform = config["platform"]
    mass = rigid_mass_matrix_6d(config)
    restoring = hydrostatic_matrix_6d(config)
    lines = [" Center of Gravity:", "  " + "  ".join(f"{value:23.15E}" for value in platform["cg_m"])]
    write_matrix(lines, "Body Mass Matrix", mass)
    write_matrix(lines, "External Linear Damping Matrix", zero_matrix_6d())
    write_matrix(lines, "External Quadratic Damping Matrix", zero_matrix_6d())
    write_matrix(lines, "Hydrostatic Restoring Matrix", restoring)
    write_matrix(lines, "External Restoring Matrix", zero_matrix_6d())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "body_mass_matrix": mass,
        "hydrostatic_restoring_matrix": restoring,
        "waterplane_area_m2": platform["waterplane_area_m2"],
        "geometry_displacement_volume_m3": platform["geometry_displacement_volume_m3"],
        "paper_mass_displacement_volume_m3": platform["paper_mass_displacement_volume_m3"],
        "heave_restoring_n_m": restoring[2][2],
        "pitch_restoring_nm_rad": restoring[4][4],
    }


def frequency_count(config: dict[str, Any]) -> int:
    freq = config["frequency"]
    return int(round((freq["max_rad_s"] - freq["min_rad_s"]) / freq["step_rad_s"])) + 1


def write_control(path: Path, config: dict[str, Any]) -> None:
    platform = config["platform"]
    freq = config["frequency"]
    headings = config["headings_deg"]
    nfreq = frequency_count(config)
    ref = config["reference_point_m"]
    lines = [
        "   --------------HAMS Control file---------------",
        "",
        f"   Waterdepth  {fortran_float(platform['water_depth_m'])}",
        "",
        "   #Start Definition of Wave Frequencies",
        "    0_inf_frequency_limits      0",
        "    Input_frequency_type        3",
        "    Output_frequency_type       3",
        f"    Number_of_frequencies      {-nfreq}",
        f"    Minimum_frequency_Wmin    {fortran_float(freq['min_rad_s'])}",
        f"    Frequency_step            {fortran_float(freq['step_rad_s'])}",
        "   #End Definition of Wave Frequencies",
        "",
        "   #Start Definition of Wave Headings",
        f"    Number_of_headings         {len(headings)}",
        "   " + " ".join(f"{heading:.6f}" for heading in headings),
        "   #End Definition of Wave Headings",
        "",
        f"    Reference_body_center       {ref[0]:.3f}       {ref[1]:.3f}       {ref[2]:.3f}",
        f"    Reference_body_length   {fortran_float(platform['length_m'])}",
        "    Wave_diffrac_solution    2",
        "    If_remove_irr_freq       1",
        "    Number of threads       16",
        "",
        "   #Start Definition of Pressure and/or Elevation (PE)",
        "    Number_of_field_points     0",
        "   #End Definition of Pressure and/or Elevation",
        "",
        "   ----------End HAMS Control file---------------",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_gdf(path: Path, nodes: list[tuple[float, float, float]], panels: list[list[int]], config: dict[str, Any]) -> None:
    lines = [
        f"Generated {config['title']}",
        f"1 {G:.5f} \tULEN GRAV",
        "0 0 \tISX  ISY",
        str(len(panels)),
    ]
    for panel in panels:
        for x, y, z in [nodes[index - 1] for index in panel]:
            lines.append(f"{x:12.5f} {y:12.5f} {z:12.5f}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def self_check(config: dict[str, Any], hull_nodes: list[tuple[float, float, float]], hull_panels: list[list[int]], water_nodes: list[tuple[float, float, float]], water_panels: list[list[int]], hydro: dict[str, Any]) -> dict[str, Any]:
    mesh = config["mesh"]
    platform = config["platform"]
    expected_hull_panels = mesh["nx"] * mesh["ny"] + 2 * mesh["nx"] * mesh["nz"] + 2 * mesh["ny"] * mesh["nz"]
    expected_water_panels = mesh["nx"] * mesh["ny"]
    mass_displacement_ratio = platform["paper_mass_displacement_volume_m3"] / max(platform["geometry_displacement_volume_m3"], 1.0e-9)
    checks = [
        {"id": "hull_panel_count", "expected": expected_hull_panels, "actual": len(hull_panels), "passed": len(hull_panels) == expected_hull_panels},
        {"id": "waterplane_panel_count", "expected": expected_water_panels, "actual": len(water_panels), "passed": len(water_panels) == expected_water_panels},
        {"id": "hull_z_not_above_free_surface", "expected": "<= 0", "actual": max(z for _, _, z in hull_nodes), "passed": max(z for _, _, z in hull_nodes) <= 1.0e-9},
        {"id": "waterplane_z_equal_zero", "expected": 0.0, "actual": max(abs(z) for _, _, z in water_nodes), "passed": max(abs(z) for _, _, z in water_nodes) <= 1.0e-9},
        {"id": "positive_heave_restoring", "expected": "> 0", "actual": hydro["heave_restoring_n_m"], "passed": hydro["heave_restoring_n_m"] > 0.0},
        {"id": "positive_pitch_restoring", "expected": "> 0", "actual": hydro["pitch_restoring_nm_rad"], "passed": hydro["pitch_restoring_nm_rad"] > 0.0},
    ]
    return {
        "case_id": config["case_id"],
        "mesh": {"hull_nodes": len(hull_nodes), "hull_panels": len(hull_panels), "waterplane_nodes": len(water_nodes), "waterplane_panels": len(water_panels)},
        "hydrostatic": hydro,
        "mass_displacement_ratio": mass_displacement_ratio,
        "checks": checks,
        "passed": all(check["passed"] for check in checks),
    }


def generate_cases() -> dict[str, Any]:
    results = {}
    PAPER_ROOT.mkdir(parents=True, exist_ok=True)
    for case_id, base in PAPER_CASES.items():
        config = paper_config(case_id, base)
        case_dir = PAPER_ROOT / case_id
        ensure_case_output_dirs(case_dir)
        input_dir = case_dir / "Input"
        geometry_dir = case_dir / "geometry"
        hull_nodes, hull_panels, water_nodes, water_panels = build_paper_mesh(config)
        write_pnl(input_dir / "HullMesh.pnl", "Hull Mesh File", hull_nodes, hull_panels)
        write_pnl(input_dir / "WaterplaneMesh.pnl", "Waterplane Mesh File", water_nodes, water_panels)
        all_nodes = hull_nodes + water_nodes
        all_panels = hull_panels + [[node + len(hull_nodes) for node in panel] for panel in water_panels]
        write_gdf(geometry_dir / f"{case_id}.gdf", all_nodes, all_panels, config)
        write_control(input_dir / "ControlFile.in", config)
        hydro = write_hydrostatic(input_dir / "Hydrostatic.in", config)
        write_json(case_dir / "platform_config.json", config)
        check = self_check(config, hull_nodes, hull_panels, water_nodes, water_panels, hydro)
        write_json(case_dir / "validation" / "paper-self-check.json", check)
        results[case_id] = {"case_dir": str(case_dir), "self_check_passed": check["passed"]}
    write_json(PAPER_ROOT / "paper_reproduction_manifest.json", {"paper_id": PAPER_ID, "cases": results})
    return results


def extract_real_rao_component(case_dir: Path, prefix: str, i: int, j: int) -> tuple[np.ndarray, np.ndarray]:
    parsed = parse_hydrostar_rao(case_dir / "Output" / "Hydrostar_format" / f"{prefix}_{i}{j}.rao")
    omega = np.array([row["frequency"] for row in parsed["rows"]], dtype=float)
    values = np.array([row["amplitudes"][0] for row in parsed["rows"]], dtype=float)
    return omega, values


def interpolated_hydro_matrix(case_dir: Path, prefix: str, omega_sample: float) -> np.ndarray:
    matrix = np.zeros((3, 3), dtype=float)
    dofs = [1, 3, 5]
    for a, i in enumerate(dofs):
        for b, j in enumerate(dofs):
            omega, values = extract_real_rao_component(case_dir, prefix, i, j)
            matrix[a, b] = float(np.interp(omega_sample, omega, values))
    return 0.5 * (matrix + matrix.T)


def hydro_matrix_series(case_dir: Path, prefix: str) -> tuple[np.ndarray, np.ndarray]:
    dofs = [1, 3, 5]
    omega_ref: np.ndarray | None = None
    matrices: list[np.ndarray] | None = None
    for a, i in enumerate(dofs):
        for b, j in enumerate(dofs):
            omega, values = extract_real_rao_component(case_dir, prefix, i, j)
            if omega_ref is None:
                omega_ref = omega
                matrices = [np.zeros((3, 3), dtype=float) for _ in omega]
            if not np.allclose(omega_ref, omega):
                values = np.interp(omega_ref, omega, values)
            assert matrices is not None
            for k, value in enumerate(values):
                matrices[k][a, b] = value
    assert omega_ref is not None and matrices is not None
    sym = [0.5 * (matrix + matrix.T) for matrix in matrices]
    return omega_ref, np.stack(sym, axis=0)


def quadrature_weights(omega: np.ndarray) -> np.ndarray:
    if len(omega) == 1:
        return np.array([1.0], dtype=float)
    weights = np.zeros_like(omega, dtype=float)
    weights[0] = 0.5 * (omega[1] - omega[0])
    weights[-1] = 0.5 * (omega[-1] - omega[-2])
    for idx in range(1, len(omega) - 1):
        weights[idx] = 0.5 * (omega[idx + 1] - omega[idx - 1])
    return (2.0 / math.pi) * weights


def modal_damping_matrix(mass: np.ndarray, stiffness: np.ndarray, damping_ratio: float) -> np.ndarray:
    eigvals, eigvecs = eigh(stiffness, mass)
    eigvals = np.maximum(eigvals, 0.0)
    modal = np.diag([2.0 * damping_ratio * math.sqrt(value) if value > 0.0 else 0.0 for value in eigvals])
    return mass @ eigvecs @ modal @ eigvecs.T @ mass


def simulation_matrices(config: dict[str, Any], case_dir: Path) -> dict[str, Any]:
    td = config["time_domain"]
    hydro = read_json(case_dir / "validation" / "paper-self-check.json")["hydrostatic"]
    platform = config["platform"]
    rlv = config["rlv"]
    table = rlv["table"]
    derived = rlv["derived"]
    x_offset = config["landing"]["offset_m"]
    deck_z = platform["deck_z_m"]

    added = interpolated_hydro_matrix(case_dir, "AddedMass", td["hydro_damping_sample_rad_s"])
    radiation = interpolated_hydro_matrix(case_dir, "WaveDamping", td["hydro_damping_sample_rad_s"])
    added_omega, added_series = hydro_matrix_series(case_dir, "AddedMass")
    radiation_omega, radiation_series = hydro_matrix_series(case_dir, "WaveDamping")
    a_infinite = added_series[-1]
    radiation_weights = quadrature_weights(radiation_omega)

    rigid = np.array(hydro["body_mass_matrix"], dtype=float)
    restoring_6d = np.array(hydro["hydrostatic_restoring_matrix"], dtype=float)
    idx = [0, 2, 4]
    m_barge = rigid[np.ix_(idx, idx)]
    m_barge[1, 1] = table["heave_corrected_barge_mass_kg"]
    k_barge = restoring_6d[np.ix_(idx, idx)]
    k_barge[0, 0] += td["surge_mooring_stiffness_n_m"]

    masses_used = derived["target_frequency_eq_mass_kg"] if td["use_target_structural_frequencies"] else {
        "transverse": table["transverse_eq_mass_kg"],
        "axial": table["axial_eq_mass_kg"],
        "rotational": table["rotational_eq_mass_kg"],
    }
    m_vehicle = np.diag([masses_used["transverse"], masses_used["axial"], masses_used["rotational"]])
    k_contact = np.diag([table["transverse_stiffness_n_m"], table["axial_stiffness_n_m"], table["rotational_stiffness_nm_rad"]])

    h = np.array(
        [
            [-1.0, 0.0, -deck_z, 1.0, 0.0, 0.0],
            [0.0, -1.0, x_offset, 0.0, 1.0, 0.0],
            [0.0, 0.0, -1.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    mass = np.zeros((6, 6), dtype=float)
    mass[:3, :3] = m_barge + a_infinite
    mass[3:, 3:] = m_vehicle

    stiffness = np.zeros((6, 6), dtype=float)
    stiffness[:3, :3] = k_barge
    stiffness += h.T @ k_contact @ h

    damping = np.zeros((6, 6), dtype=float)
    damping[:3, :3] = modal_damping_matrix(m_barge + a_infinite, k_barge + 1.0e-9 * np.eye(3), td["barge_viscous_damping_ratio"])
    damping[3:, 3:] += modal_damping_matrix(m_vehicle, k_contact, td["structural_damping_ratio"])
    damping += h.T @ (td["contact_damping_ratio"] * modal_damping_matrix(np.eye(3), k_contact, 1.0)) @ h

    return {
        "mass": mass,
        "damping": damping,
        "stiffness": stiffness,
        "added_mass_3dof": added,
        "added_mass_infinite_3dof": a_infinite,
        "radiation_damping_3dof": radiation,
        "radiation_omega_rad_s": radiation_omega,
        "radiation_matrices": radiation_series,
        "radiation_weights": radiation_weights,
        "contact_jacobian": h,
        "masses_used": masses_used,
    }


def solve_touchdown(config: dict[str, Any], case_dir: Path, touchdown_velocity: float) -> dict[str, Any]:
    td = config["time_domain"]
    matrices = simulation_matrices(config, case_dir)
    mass = matrices["mass"]
    damping = matrices["damping"]
    stiffness = matrices["stiffness"]
    radiation_omega = matrices["radiation_omega_rad_s"]
    radiation_matrices = matrices["radiation_matrices"]
    radiation_weights = matrices["radiation_weights"]
    mass_inv = np.linalg.inv(mass)
    memory_count = len(radiation_omega)

    y0 = np.zeros(12 + 2 * memory_count * 3, dtype=float)
    y0[6 + 4] = -abs(touchdown_velocity)

    def rhs(_t: float, y: np.ndarray) -> np.ndarray:
        q = y[:6]
        qd = y[6:]
        qd = y[6:12]
        memory = y[12:].reshape(2, memory_count, 3)
        cos_state = memory[0]
        sin_state = memory[1]
        memory_force = np.einsum("k,kij,kj->i", radiation_weights, radiation_matrices, cos_state)
        force = -damping @ qd - stiffness @ q
        force[:3] -= memory_force
        qdd = mass_inv @ force
        cos_dot = qd[:3][None, :] - radiation_omega[:, None] * sin_state
        sin_dot = radiation_omega[:, None] * cos_state
        return np.concatenate([qd, qdd, cos_dot.reshape(-1), sin_dot.reshape(-1)])

    duration = td["duration_s"]
    dt = td["dt_s"]
    t_eval = np.arange(0.0, duration + 0.5 * dt, dt)
    sol = solve_ivp(rhs, (0.0, duration), y0, t_eval=t_eval, method="DOP853", rtol=1.0e-7, atol=1.0e-9)
    if not sol.success:
        raise RuntimeError(sol.message)
    q = sol.y[:6, :]
    qd = sol.y[6:12, :]
    accel = np.gradient(qd, dt, axis=1)
    rel = matrices["contact_jacobian"] @ q

    channels = {}
    spectra = {}
    for idx, label in enumerate(DOF_LABELS):
        series = q[idx, :]
        channels[label] = summarize_series(sol.t, series)
        spectra[label] = spectrum_series(sol.t, series)
    rel_labels = ["relative_transverse_m", "relative_axial_m", "relative_rotation_rad"]
    for idx, label in enumerate(rel_labels):
        channels[label] = summarize_series(sol.t, rel[idx, :])
        spectra[label] = spectrum_series(sol.t, rel[idx, :])

    return {
        "touchdown_velocity_m_s": touchdown_velocity,
        "time_s": sol.t.tolist(),
        "responses": {label: q[idx, :].tolist() for idx, label in enumerate(DOF_LABELS)},
        "velocities": {label.replace("_m", "_m_s").replace("_rad", "_rad_s"): qd[idx, :].tolist() for idx, label in enumerate(DOF_LABELS)},
        "accelerations": {label.replace("_m", "_m_s2").replace("_rad", "_rad_s2"): accel[idx, :].tolist() for idx, label in enumerate(DOF_LABELS)},
        "relative": {label: rel[idx, :].tolist() for idx, label in enumerate(rel_labels)},
        "summary": channels,
        "spectra": spectra,
    }


def summarize_series(time: np.ndarray, series: np.ndarray) -> dict[str, Any]:
    peak_abs = float(np.max(np.abs(series)))
    rms = float(math.sqrt(np.mean(series**2)))
    dominant = dominant_frequencies(time, series)
    return {"peak_abs": peak_abs, "rms": rms, "dominant_frequencies_hz": dominant}


def dominant_frequencies(time: np.ndarray, series: np.ndarray) -> list[dict[str, float]]:
    dt = float(time[1] - time[0])
    values = series - np.mean(series)
    if np.max(np.abs(values)) <= 1.0e-14:
        return []
    window = np.hanning(len(values))
    spectrum = np.fft.rfft(values * window)
    freqs = np.fft.rfftfreq(len(values), dt)
    amp = np.abs(spectrum)
    mask = freqs > 0.05
    candidates = [(float(freqs[i]), float(amp[i])) for i in np.where(mask)[0]]
    candidates.sort(key=lambda item: item[1], reverse=True)
    selected: list[dict[str, float]] = []
    for freq, value in candidates:
        if all(abs(freq - existing["frequency_hz"]) > 0.2 for existing in selected):
            selected.append({"frequency_hz": freq, "relative_amplitude": value / max(candidates[0][1], 1.0e-30)})
        if len(selected) == 3:
            break
    return selected


def spectrum_series(time: np.ndarray, series: np.ndarray, max_frequency_hz: float = 40.0) -> list[list[float]]:
    dt = float(time[1] - time[0])
    values = series - np.mean(series)
    if np.max(np.abs(values)) <= 1.0e-14:
        return []
    window = np.hanning(len(values))
    spectrum = np.fft.rfft(values * window)
    freqs = np.fft.rfftfreq(len(values), dt)
    amp = np.abs(spectrum)
    mask = (freqs > 0.0) & (freqs <= max_frequency_hz)
    freq_values = freqs[mask]
    amp_values = amp[mask]
    if len(freq_values) > 1200:
        indices = np.linspace(0, len(freq_values) - 1, 1200).round().astype(int)
        freq_values = freq_values[indices]
        amp_values = amp_values[indices]
    scale = float(np.max(amp_values)) or 1.0
    return [[float(freq), float(value / scale)] for freq, value in zip(freq_values, amp_values)]


def natural_frequencies(mass: np.ndarray, stiffness: np.ndarray) -> list[float]:
    eigvals = eigh(stiffness, mass, eigvals_only=True)
    out = []
    for eigval in eigvals:
        if eigval > 1.0e-9:
            out.append(float(math.sqrt(eigval) / (2.0 * math.pi)))
        else:
            out.append(0.0)
    return out


def compare_trends(case_outputs: dict[str, Any]) -> dict[str, Any]:
    comparisons = []
    for family, center_id, offset_id in [
        ("Box Barge", "BoxBarge_Center", "BoxBarge_Offset5m"),
        ("MARMAC 302", "MARMAC302_Center", "MARMAC302_Offset30m"),
    ]:
        center = case_outputs[center_id]
        offset = case_outputs[offset_id]
        v_key = "2.0"
        center_summary = center["simulations"][v_key]["summary"]
        offset_summary = offset["simulations"][v_key]["summary"]
        pitch_center = center_summary["barge_pitch_rad"]["peak_abs"]
        pitch_offset = offset_summary["barge_pitch_rad"]["peak_abs"]
        transverse_center = center_summary["rlv_transverse_m"]["peak_abs"]
        transverse_offset = offset_summary["rlv_transverse_m"]["peak_abs"]
        comparisons.append(
            {
                "family": family,
                "velocity_m_s": 2.0,
                "pitch_peak_center_rad": pitch_center,
                "pitch_peak_offset_rad": pitch_offset,
                "pitch_offset_to_center_ratio": ratio_or_inf(pitch_offset, pitch_center),
                "transverse_peak_center_m": transverse_center,
                "transverse_peak_offset_m": transverse_offset,
                "transverse_offset_to_center_ratio": ratio_or_inf(transverse_offset, transverse_center),
                "matches_paper_claim": pitch_offset > max(pitch_center, 1.0e-12) and transverse_offset > max(transverse_center, 1.0e-12),
            }
        )
    return {
        "claims": [
            {
                "claim": "Center landing keeps pitch nearly unexcited.",
                "status": all(case_outputs[cid]["simulations"]["2.0"]["summary"]["barge_pitch_rad"]["peak_abs"] < 1.0e-8 for cid in ["BoxBarge_Center", "MARMAC302_Center"]),
            },
            {
                "claim": "Offset landing increases pitch and RLV transverse response.",
                "status": all(item["matches_paper_claim"] for item in comparisons),
            },
        ],
        "center_offset": comparisons,
    }


def ratio_or_inf(numerator: float, denominator: float) -> float:
    if abs(denominator) < 1.0e-15:
        return math.inf if abs(numerator) > 0 else 1.0
    return numerator / denominator


def simulate_cases() -> dict[str, Any]:
    outputs: dict[str, Any] = {}
    for case_id in PAPER_CASES:
        case_dir = PAPER_ROOT / case_id
        config = read_json(case_dir / "platform_config.json")
        matrices = simulation_matrices(config, case_dir)
        eig_freq = natural_frequencies(matrices["mass"], matrices["stiffness"])
        simulations = {}
        for velocity in config["touchdown_velocity_m_s"]:
            simulations[f"{velocity:.1f}"] = solve_touchdown(config, case_dir, float(velocity))
        result = {
            "case_id": case_id,
            "title": config["title"],
            "case_dir": str(case_dir),
            "config": config,
            "hydrodynamic_sample": {
                "omega_rad_s": config["time_domain"]["hydro_damping_sample_rad_s"],
                "added_mass_3dof": matrices["added_mass_3dof"].tolist(),
                "added_mass_infinite_3dof": matrices["added_mass_infinite_3dof"].tolist(),
                "radiation_damping_3dof": matrices["radiation_damping_3dof"].tolist(),
                "memory_frequencies_rad_s": matrices["radiation_omega_rad_s"].tolist(),
                "memory_quadrature_weights": matrices["radiation_weights"].tolist(),
            },
            "system_natural_frequencies_hz": eig_freq,
            "simulations": simulations,
        }
        write_json(case_dir / "Output" / "RocketRecovery" / "nargolkar-touchdown-response.json", result)
        outputs[case_id] = result
    comparison = compare_trends(outputs)
    bundle = {"paper_id": PAPER_ID, "cases": outputs, "comparison": comparison}
    write_json(PAPER_ROOT / "nargolkar-2025-reproduction.json", bundle)
    return bundle


def load_mesh(case_dir: Path) -> dict[str, Any]:
    return {
        "hull": mesh_to_three(parse_pnl(case_dir / "Input" / "HullMesh.pnl")),
        "waterplane": mesh_to_three(parse_pnl(case_dir / "Input" / "WaterplaneMesh.pnl")),
    }


def paper_asset_status() -> dict[str, Any]:
    md = PAPER_MD
    pdf = PAPER_PDF
    return {
        "markdown_exists": md.exists(),
        "pdf_exists": pdf.exists(),
        "markdown_path": str(md),
        "pdf_path": str(pdf),
        "pdf_size_bytes": pdf.stat().st_size if pdf.exists() else None,
    }


def parse_markdown_tables(path: Path = PAPER_MD) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    tables: list[list[str]] = []
    current: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            current.append(stripped)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)

    parsed = []
    for raw in tables:
        rows = []
        for line in raw:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(set(cell.replace(":", "").strip()) <= {"-"} for cell in cells):
                continue
            rows.append(cells)
        if rows:
            parsed.append({"headers": rows[0], "rows": rows[1:], "raw": raw})
    return parsed


def markdown_number(cell: str) -> float | None:
    import re

    cleaned = (
        cell.replace("$", "")
        .replace("\\mathrm", "")
        .replace("{", "")
        .replace("}", "")
        .replace("~", "")
        .replace(",", "")
    )
    sci = re.search(r"([-+]?\d+(?:\.\d+)?)\s*\\times\s*10\^([-+]?\d+)", cleaned)
    if sci:
        return float(sci.group(1)) * 10.0 ** int(sci.group(2))
    number = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?", cleaned)
    if not number:
        return None
    return float(number.group(0))


def compare_value(source_cell: str, implemented: float, unit: str, label: str, tolerance: float = 1.0e-9) -> dict[str, Any]:
    source = markdown_number(source_cell)
    if source is None:
        return {"label": label, "source": source_cell, "implemented": implemented, "unit": unit, "status": "missing_source_number"}
    scale = max(1.0, abs(source))
    abs_error = abs(implemented - source)
    return {
        "label": label,
        "source": source,
        "source_cell": source_cell,
        "implemented": implemented,
        "unit": unit,
        "abs_error": abs_error,
        "relative_error": abs_error / scale,
        "status": "match" if abs_error <= tolerance * scale else "check",
    }


def find_table(tables: list[dict[str, Any]], required_headers: set[str]) -> dict[str, Any] | None:
    for table in tables:
        headers = set(table["headers"])
        if required_headers.issubset(headers):
            return table
    return None


def build_paper_data_audit() -> dict[str, Any]:
    tables = parse_markdown_tables()
    table1 = find_table(tables, {"Parameter", "Box Barge", "MARMAC 302"})
    table2 = find_table(tables, {"Barge Case", "Mode", "$\\omega_{j}^{\\text {nat }}(\\mathrm{Hz})$"})
    table3 = find_table(tables, {"Parameter", "Box Barge (5m Offset)", "MARMAC 302 (30m Offset)"})
    comparisons: list[dict[str, Any]] = []
    consistency: list[dict[str, Any]] = []

    if table1:
        rows = {row[0]: row for row in table1["rows"]}
        table1_map = [
            ("Barge Mass", "platform.mass_kg", "kg", lambda cfg: cfg["platform"]["mass_kg"]),
            ("Barge Length", "platform.length_m", "m", lambda cfg: cfg["platform"]["length_m"]),
            ("Barge Breadth", "platform.beam_m", "m", lambda cfg: cfg["platform"]["beam_m"]),
            ("Barge Depth", "platform.depth_m", "m", lambda cfg: cfg["platform"]["depth_m"]),
            ("Design Draft", "platform.draft_m", "m", lambda cfg: cfg["platform"]["draft_m"]),
            ("RLV Mass", "rlv.mass_kg", "kg", lambda cfg: cfg["rlv"]["mass_kg"]),
            ("RLV Height", "rlv.height_m", "m", lambda cfg: cfg["rlv"]["height_m"]),
            ("RLV Radius", "rlv.radius_m", "m", lambda cfg: cfg["rlv"]["radius_m"]),
            ("RLV Thickness", "rlv.thickness_m", "mm", lambda cfg: cfg["rlv"]["thickness_m"] * 1000.0),
        ]
        for parameter, field, unit, getter in table1_map:
            row = rows.get(parameter)
            if not row:
                continue
            for case_id, column in [("BoxBarge_Center", 1), ("MARMAC302_Center", 2)]:
                cfg = paper_config(case_id, PAPER_CASES[case_id])
                comparisons.append(compare_value(row[column], getter(cfg), unit, f"Table 1 {case_id} {field}"))

    if table2:
        table2_index = {
            (row[0], row[1]): row
            for row in table2["rows"]
            if len(row) >= 6
        }
        mode_map = {
            "Transverse": ("transverse_stiffness_n_m", "transverse_eq_mass_kg", "transverse"),
            "Axial": ("axial_stiffness_n_m", "axial_eq_mass_kg", "axial"),
            "Rotational": ("rotational_stiffness_nm_rad", "rotational_eq_mass_kg", "rotational"),
        }
        for family, case_id in [("Box Barge", "BoxBarge_Center"), ("MARMAC 302", "MARMAC302_Center")]:
            cfg = paper_config(case_id, PAPER_CASES[case_id])
            for mode_label, (k_key, m_key, derived_key) in mode_map.items():
                row = table2_index.get((family, mode_label))
                if not row:
                    continue
                table = cfg["rlv"]["table"]
                comparisons.append(compare_value(row[2], cfg["rlv"]["derived"]["target_frequency_hz"][derived_key], "Hz", f"Table 2 {family} {mode_label} printed frequency"))
                comparisons.append(compare_value(row[3], table[k_key], "N/m or Nm/rad", f"Table 2 {family} {mode_label} stiffness", tolerance=5.0e-3))
                comparisons.append(compare_value(row[4], table[m_key], "kg", f"Table 2 {family} {mode_label} equivalent mass", tolerance=5.0e-5))
                printed_frequency = markdown_number(row[2])
                implied_frequency = cfg["rlv"]["derived"]["table_frequency_hz"][derived_key]
                consistency.append(
                    {
                        "label": f"{family} {mode_label}",
                        "printed_frequency_hz": printed_frequency,
                        "frequency_from_printed_k_and_m_hz": implied_frequency,
                        "abs_difference_hz": None if printed_frequency is None else abs(implied_frequency - printed_frequency),
                        "status": "match" if printed_frequency is not None and abs(implied_frequency - printed_frequency) <= 0.25 else "check",
                    }
                )

    if table3:
        rows = {row[0]: row for row in table3["rows"]}
        mapping = [
            ("CoM X", "platform.cg_m[0]", "m", 0),
            ("CoM Z", "platform.cg_m[2]", "m", 2),
        ]
        for parameter, field, unit, idx in mapping:
            row = rows.get(parameter)
            if not row:
                continue
            for case_id, column in [("BoxBarge_Offset5m", 1), ("MARMAC302_Offset30m", 2)]:
                cfg = paper_config(case_id, PAPER_CASES[case_id])
                comparisons.append(compare_value(row[column], cfg["platform"]["cg_m"][idx], unit, f"Table 3 {case_id} {field}"))

    unresolved = [
        {
            "item": "MARMAC 302 trapezoidal hull coordinates",
            "reason": "The paper states that a trapezoidal approximation is used but gives only length, breadth, depth, draft and mass.",
            "impact": "HAMS coefficients for the MARMAC cases cannot be claimed as a unique exact reproduction from the PDF alone.",
        },
        {
            "item": "Cummins retardation-kernel implementation details",
            "reason": "The paper gives the equation but not the MATLAB source, integration time step, kernel truncation, or A-infinity treatment.",
            "impact": "The external time response can be an auditable reproduction attempt, but not a pointwise reproduction of Figure 9/10.",
        },
        {
            "item": "Touchdown initial velocities used in Figures 9 and 10",
            "reason": "The Markdown text says velocity sensitivity is analysed, but the exact plotted velocity set is not machine-readable in the supplied text.",
            "impact": "The report uses selectable velocities 1, 2 and 3 m/s and records them explicitly.",
        },
        {
            "item": "Structural/contact damping and mooring stiffness",
            "reason": "The supplied paper text does not provide numeric values.",
            "impact": "These must be treated as model settings, not paper data.",
        },
    ]
    return {
        "source_markdown": str(PAPER_MD),
        "tables_found": len(tables),
        "numeric_comparisons": comparisons,
        "internal_consistency_checks": consistency,
        "unresolved": unresolved,
        "all_printed_values_matched": all(row["status"] == "match" for row in comparisons),
        "all_internal_consistency_matched": all(row["status"] == "match" for row in consistency),
    }


def curve_color_mask(rgb: np.ndarray, curve_id: str) -> np.ndarray:
    r = rgb[:, :, 0].astype(int)
    g = rgb[:, :, 1].astype(int)
    b = rgb[:, :, 2].astype(int)
    if curve_id == "base_v1":
        return (r < 120) & (g < 145) & (b < 180) & (b > r + 12) & (b > g + 3)
    if curve_id == "base_v2":
        return (r > 130) & (g < 135) & (b < 145) & (r > g + 25)
    if curve_id == "offset_v1":
        return (g > 105) & (b > 120) & (r < 160) & (b > r + 20)
    if curve_id == "offset_v2":
        return (r > 150) & (g > 100) & (b < 155) & (r > g + 8) & (g > b + 15)
    raise ValueError(f"Unknown curve color id: {curve_id}")


def digitize_curve(
    image_rgb: np.ndarray,
    box: list[int],
    ylim: list[float],
    curve_id: str,
    *,
    time_min_s: float = 0.0,
    time_max_s: float = 3.0,
    max_points: int = 220,
) -> dict[str, Any]:
    x0, y0, x1, y1 = box
    crop = image_rgb[y0 : y1 + 1, x0 : x1 + 1]
    margin = 5
    inner = crop[margin:-margin, margin:-margin]
    mask = curve_color_mask(inner, curve_id)
    points: list[tuple[float, float]] = []
    for col in range(mask.shape[1]):
        ys = np.where(mask[:, col])[0]
        if len(ys) == 0:
            continue
        y_pixel = float(np.median(ys)) + margin
        x_pixel = float(col + margin)
        x_frac = x_pixel / max(crop.shape[1] - 1, 1)
        y_frac = y_pixel / max(crop.shape[0] - 1, 1)
        t = time_min_s + x_frac * (time_max_s - time_min_s)
        value = ylim[1] - y_frac * (ylim[1] - ylim[0])
        points.append((t, value))

    source_point_count = len(points)
    coverage_ratio = source_point_count / max(mask.shape[1], 1)
    if source_point_count == 0:
        quality = "no_curve_pixels"
        quality_note = "No pixels matching this curve color were found inside the calibrated axis box."
    elif coverage_ratio < 0.12:
        quality = "low_coverage"
        quality_note = "Too few curve pixels were recovered from the raster figure for quantitative overlay."
    else:
        quality = "ok"
        quality_note = "Raster curve coverage is sufficient for first-pass visual comparison."

    if len(points) > max_points:
        indices = np.linspace(0, len(points) - 1, max_points).round().astype(int)
        points = [points[int(index)] for index in indices]

    values = [value for _, value in points]
    return {
        "curve_id": curve_id,
        "points": [[float(t), float(value)] for t, value in points],
        "point_count": len(points),
        "source_point_count": source_point_count,
        "coverage_ratio": coverage_ratio,
        "value_span": float(max(values) - min(values)) if values else 0.0,
        "quality": quality,
        "quality_note": quality_note,
        "axis_box_px": box,
        "axis_time_range_s": [time_min_s, time_max_s],
        "axis_value_range": ylim,
    }


def build_paper_time_digitization() -> dict[str, Any]:
    try:
        from PIL import Image
    except ImportError:
        return {
            "status": "unavailable",
            "reason": "Pillow is not installed, so raster paper figures could not be digitized.",
            "cases": {},
        }

    cases: dict[str, Any] = {}
    figures: dict[str, Any] = {}
    for family, spec in PAPER_TIME_DIGITIZATION.items():
        image_path = PAPER_FIGURES_DIR / spec["image"]
        figure_status = {"family": family, "image": str(image_path), "exists": image_path.exists()}
        if not image_path.exists():
            figure_status["status"] = "missing"
            figures[family] = figure_status
            continue
        rgb = np.asarray(Image.open(image_path).convert("RGB"))
        figure_status["status"] = "digitized"
        figure_status["size_px"] = [int(rgb.shape[1]), int(rgb.shape[0])]
        figures[family] = figure_status
        curve_map = [
            (spec["center_case"], "1.0", "base_v1", "Base Case, v=-1 m/s"),
            (spec["center_case"], "2.0", "base_v2", "Base Case, v=-2 m/s"),
            (spec["offset_case"], "1.0", "offset_v1", "Offset Case, v=-1 m/s"),
            (spec["offset_case"], "2.0", "offset_v2", "Offset Case, v=-2 m/s"),
        ]
        for case_id, velocity, curve_id, legend in curve_map:
            cases.setdefault(case_id, {}).setdefault(velocity, {})
            for response_id, axis in spec["axes"].items():
                curve = digitize_curve(rgb, axis["box"], axis["ylim"], curve_id)
                cases[case_id][velocity][response_id] = {
                    **curve,
                    "legend": legend,
                    "figure": spec["image"],
                    "family": family,
                    "digitization_note": "Raster curve digitized from the supplied paper figure image; not original author data.",
                }

    return {
        "status": "digitized",
        "method": "Manual axis calibration plus RGB thresholding of raster curves in Figure 9(a) and Figure 10(a).",
        "figures": figures,
        "cases": cases,
    }


def build_paper_time_comparison(bundle: dict[str, Any], digitized: dict[str, Any]) -> dict[str, Any]:
    if digitized.get("status") != "digitized":
        return {
            "status": "unavailable",
            "reason": digitized.get("reason", "Paper curves were not digitized."),
            "cases": {},
        }

    compared_cases: dict[str, Any] = {}
    for case_id, velocities in digitized.get("cases", {}).items():
        case = bundle.get("cases", {}).get(case_id)
        if not case:
            continue
        for velocity, responses in velocities.items():
            sim = case.get("simulations", {}).get(velocity)
            if not sim:
                continue
            time = np.asarray(sim["time_s"], dtype=float)
            compared_cases.setdefault(case_id, {}).setdefault(velocity, {})
            for response_id, paper_curve in responses.items():
                entry = {
                    "paper_quality": paper_curve.get("quality"),
                    "paper_quality_note": paper_curve.get("quality_note"),
                    "paper_point_count": paper_curve.get("point_count", 0),
                }
                if paper_curve.get("quality") != "ok":
                    entry["status"] = "skipped"
                    compared_cases[case_id][velocity][response_id] = entry
                    continue
                if response_id not in sim["responses"]:
                    entry["status"] = "missing_response"
                    compared_cases[case_id][velocity][response_id] = entry
                    continue

                paper_points = np.asarray(paper_curve["points"], dtype=float)
                if paper_points.ndim != 2 or paper_points.shape[0] < 2:
                    entry["status"] = "skipped"
                    entry["paper_quality_note"] = "Too few digitized paper points for interpolation."
                    compared_cases[case_id][velocity][response_id] = entry
                    continue

                valid = (paper_points[:, 0] >= time[0]) & (paper_points[:, 0] <= time[-1])
                paper_points = paper_points[valid]
                if paper_points.shape[0] < 2:
                    entry["status"] = "skipped"
                    entry["paper_quality_note"] = "Digitized paper curve lies outside the computed time range."
                    compared_cases[case_id][velocity][response_id] = entry
                    continue

                response = np.asarray(sim["responses"][response_id], dtype=float)
                our_values = np.interp(paper_points[:, 0], time, response)
                paper_values = paper_points[:, 1]
                diff = our_values - paper_values
                paper_peak = float(np.max(np.abs(paper_values)))
                our_peak = float(np.max(np.abs(our_values)))
                rmse = float(np.sqrt(np.mean(diff * diff)))
                denominator = max(paper_peak, 1.0e-12)
                paper_centered = paper_values - float(np.mean(paper_values))
                our_centered = our_values - float(np.mean(our_values))
                corr_den = float(np.linalg.norm(paper_centered) * np.linalg.norm(our_centered))
                entry.update(
                    {
                        "status": "compared",
                        "n_points": int(paper_points.shape[0]),
                        "time_range_s": [float(paper_points[0, 0]), float(paper_points[-1, 0])],
                        "rmse": rmse,
                        "normalized_rmse_vs_paper_peak": rmse / denominator,
                        "paper_peak_abs": paper_peak,
                        "our_peak_abs": our_peak,
                        "peak_ratio_our_over_paper": None if paper_peak <= 1.0e-12 else our_peak / paper_peak,
                        "mean_error": float(np.mean(diff)),
                        "correlation": None if corr_den <= 1.0e-20 else float(np.dot(paper_centered, our_centered) / corr_den),
                    }
                )
                compared_cases[case_id][velocity][response_id] = entry

    return {
        "status": "computed",
        "method": "Computed response interpolated to digitized paper Figure 9(a)/10(a) time samples over 0..3 s.",
        "cases": compared_cases,
    }


def build_report_data() -> dict[str, Any]:
    bundle_path = PAPER_ROOT / "nargolkar-2025-reproduction.json"
    if not bundle_path.exists():
        bundle = simulate_cases()
    else:
        bundle = read_json(bundle_path)
    report_bundle = compact_bundle_for_report(bundle)
    mesh = {case_id: load_mesh(PAPER_ROOT / case_id) for case_id in PAPER_CASES}
    self_checks = {
        case_id: read_json(PAPER_ROOT / case_id / "validation" / "paper-self-check.json")
        for case_id in PAPER_CASES
    }
    paper_time_digitized = build_paper_time_digitization()
    data = {
        **report_bundle,
        "mesh": mesh,
        "self_checks": self_checks,
        "paper_assets": paper_asset_status(),
        "paper_audit": build_paper_data_audit(),
        "paper_time_digitized": paper_time_digitized,
        "paper_time_comparison": build_paper_time_comparison(bundle, paper_time_digitized),
        "paper_tables": {
            "geometry_mass": [
                {"parameter": "Barge Mass", "box": "260800 kg", "marmac302": "7129486 kg"},
                {"parameter": "Barge Length", "box": "44 m", "marmac302": "91.44 m"},
                {"parameter": "Barge Breadth", "box": "4 m", "marmac302": "30.48 m"},
                {"parameter": "Barge Depth", "box": "4 m", "marmac302": "6.0198 m"},
                {"parameter": "Design Draft", "box": "2 m", "marmac302": "2.9718 m"},
                {"parameter": "RLV Mass", "box": "100000 kg", "marmac302": "20000 kg"},
                {"parameter": "RLV Height", "box": "22 m", "marmac302": "40.9 m"},
                {"parameter": "RLV Radius", "box": "1.6 m", "marmac302": "1.83 m"},
                {"parameter": "RLV Thickness", "box": "4 mm", "marmac302": "5 mm"},
            ],
            "offset_com": [
                {"case": "Box Barge 5 m offset", "com_x_m": 1.3858, "com_z_m": -0.0238},
                {"case": "MARMAC 302 30 m offset", "com_x_m": 0.0839, "com_z_m": -0.0025},
            ],
        },
    }
    write_json(PAPER_ROOT / "nargolkar-2025-report-data.json", data)
    return data


def compact_bundle_for_report(bundle: dict[str, Any], max_time_points: int = 1600) -> dict[str, Any]:
    cases: dict[str, Any] = {}
    for case_id, case in bundle["cases"].items():
        compact_case = {
            "case_id": case["case_id"],
            "title": case["title"],
            "case_dir": case["case_dir"],
            "config": case["config"],
            "hydrodynamic_sample": case["hydrodynamic_sample"],
            "system_natural_frequencies_hz": case["system_natural_frequencies_hz"],
            "simulations": {},
        }
        for velocity, sim in case["simulations"].items():
            time = sim["time_s"]
            stride = max(1, math.ceil(len(time) / max_time_points))
            indices = list(range(0, len(time), stride))
            if indices[-1] != len(time) - 1:
                indices.append(len(time) - 1)
            compact_case["simulations"][velocity] = {
                "touchdown_velocity_m_s": sim["touchdown_velocity_m_s"],
                "time_s": [time[i] for i in indices],
                "responses": {
                    label: [series[i] for i in indices]
                    for label, series in sim["responses"].items()
                },
                "relative": {
                    label: [series[i] for i in indices]
                    for label, series in sim["relative"].items()
                },
                "summary": sim["summary"],
                "spectra": sim["spectra"],
            }
        cases[case_id] = compact_case
    return {"paper_id": bundle["paper_id"], "cases": cases, "comparison": bundle["comparison"]}


def write_report_js(data: dict[str, Any], path: Path = REPORT_JS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "window.NARGOLKAR_2025_DATA = " + json_dumps_compact(data) + ";\n",
        encoding="utf-8",
    )


def json_dumps_compact(data: dict[str, Any]) -> str:
    import json

    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce the Nargolkar & Vijayan 2025 barge touchdown study with HAMS-backed external dynamics.")
    parser.add_argument("action", choices=["generate", "simulate", "report", "all"], nargs="?", default="generate")
    args = parser.parse_args()

    if args.action in {"generate", "all"}:
        generated = generate_cases()
        print("Generated paper cases:")
        for case_id, result in generated.items():
            print(f"- {case_id}: self-check {'PASS' if result['self_check_passed'] else 'CHECK'}")
    if args.action in {"simulate", "all"}:
        bundle = simulate_cases()
        print("Simulated touchdown responses:")
        for case_id in bundle["cases"]:
            print(f"- {case_id}")
        print(f"Trend checks: {sum(1 for c in bundle['comparison']['claims'] if c['status'])}/{len(bundle['comparison']['claims'])} matched")
    if args.action in {"report", "all"}:
        data = build_report_data()
        write_report_js(data)
        print(f"Wrote {REPORT_JS}")


if __name__ == "__main__":
    main()
