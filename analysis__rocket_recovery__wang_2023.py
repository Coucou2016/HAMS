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
        hams_amp_phase_to_complex,
        parse_hydrostar_rao,
        parse_pnl,
        read_json,
        trapezoid_integral,
        write_json,
        write_pnl,
    )
    from .recovery_window_report import mesh_to_three
    from .sea_state_response import jonswap_spectrum
except ImportError:
    from common import (
        G,
        RHO,
        ROCKET_CASES_DIR,
        VISUALIZATION_DIR,
        ensure_case_output_dirs,
        fortran_float,
        hams_amp_phase_to_complex,
        parse_hydrostar_rao,
        parse_pnl,
        read_json,
        trapezoid_integral,
        write_json,
        write_pnl,
    )
    from recovery_window_report import mesh_to_three
    from sea_state_response import jonswap_spectrum


PAPER_ID = "WangZhi_2023_ShipSciTech"
PAPER_ROOT = ROCKET_CASES_DIR / "Paper_WangZhi_2023"
REPORT_JS = VISUALIZATION_DIR / "wang-2023-data.js"
PAPER_MD = Path("海上平台火箭回收文献") / "海上火箭回收过程中船舶耦合运动响应分析_王智.md"
PAPER_PDF = Path("海上平台火箭回收文献") / "P2_WangZhi_2023_ShipSciTech.pdf"

DOF_IDS = [3, 4, 5]
DOF_LABELS = ["heave_m", "roll_rad", "pitch_rad"]


BASE_CONFIG: dict[str, Any] = {
    "case_id": "WangZhi_2023_RecoveryBarge",
    "paper_id": PAPER_ID,
    "title": "Wang Zhi 2023 recovery barge - HAMS/Cummins surrogate",
    "platform": {
        "length_m": 165.0,
        "beam_m": 40.0,
        "draft_m": 5.0,
        "deadweight_t": 22000.0,
        "mass_kg": 22_000_000.0,
        "reported_cg_from_aft_m": [70.5, 0.0, -2.32],
        "cg_m": [0.0, 0.0, -2.32],
        "reference_point_note": "The reduced model origin is the deck point vertically above the reported CG; x/y landing offsets are measured from that point.",
        "inertia_radius_m": {"roll": 13.5, "pitch": 38.8, "yaw": 40.3},
        "water_depth_m": -1.0,
        "rho_kg_m3": RHO,
        "gravity_m_s2": G,
        "deck_z_m": 0.0,
    },
    "mesh": {
        "nx": 48,
        "ny": 14,
        "nz": 5,
        "paper_aqwa_panel_count": 13367,
        "note": "The paper's AQWA mesh is not published. This HAMS mesh is regenerated from the published principal dimensions.",
    },
    "frequency": {"min_rad_s": 0.2, "max_rad_s": 4.0, "step_rad_s": 0.1},
    "headings_deg": [135.0],
    "reference_point_m": [0.0, 0.0, 0.0],
    "sea_state": {"id": "JONSWAP_Hs1p75_Tp4p5_gamma3_heading135", "hs_m": 1.75, "tp_s": 4.5, "gamma": 3.0, "heading_deg": 135.0},
    "mooring": {
        "line_count": 4,
        "line_length_m": 820.0,
        "azimuths_deg": [45.0, 135.0, 225.0, 315.0],
        "linear_stiffness": "disabled",
        "reason": "The paper reports catenary layout and line length, but not line diameter, wet weight, EA, fairlead/anchor coordinates, or pre-tension.",
    },
    "plume_load": {
        "time_absolute_s": {"ignition": 480.0, "vertical_descent": 506.0, "landing": 510.0, "shutdown_complete": 511.0},
        "plateau_n": 20_400_000.0,
        "ramp_up_slope_n_s": 788_462.0,
        "ramp_up_intercept_n": -378_461_538.0,
        "ramp_down_slope_n_s": -20_400_000.0,
        "ramp_down_intercept_n": 10_424_400_000.0,
        "vertical_descent_cfd_trace": "not_machine_readable",
        "note": "The 506-510 s Fp segment is approximated as the paper-stated 20400 kN plateau because Figure 6 is not supplied as numeric data.",
    },
    "landing_offsets_m": [
        {"id": "no_plume", "label": "No plume", "x": 0.0, "y": 0.0, "with_plume": False},
        {"id": "center", "label": "Center", "x": 0.0, "y": 0.0, "with_plume": True},
        {"id": "bow_5m", "label": "Longitudinal 5 m", "x": 5.0, "y": 0.0, "with_plume": True},
        {"id": "bow_10m", "label": "Longitudinal 10 m", "x": 10.0, "y": 0.0, "with_plume": True},
        {"id": "bow_15m", "label": "Longitudinal 15 m", "x": 15.0, "y": 0.0, "with_plume": True},
        {"id": "port_5m", "label": "Transverse 5 m", "x": 0.0, "y": 5.0, "with_plume": True},
        {"id": "port_10m", "label": "Transverse 10 m", "x": 0.0, "y": 10.0, "with_plume": True},
        {"id": "port_15m", "label": "Transverse 15 m", "x": 0.0, "y": 15.0, "with_plume": True},
    ],
    "time_domain": {
        "start_s": 450.0,
        "end_s": 550.0,
        "dt_s": 0.05,
        "hydrodynamic_memory": "cummins_cosine_quadrature_from_hams_B",
        "added_mass_infinite_estimate": "highest_computed_frequency",
        "linear_damping_ratio": 0.01,
        "wave_seed": 2023,
        "include_second_order_wave_force": False,
        "include_mooring_stiffness": False,
    },
    "paper_targets": [
        {"id": "calm_bow_15_pitch_deg", "environment": "calm", "case": "bow_15m", "metric": "pitch_peak_deg", "paper_value": 0.25, "unit": "deg", "source": "Section 3.2.1 text"},
        {"id": "calm_port_15_roll_deg", "environment": "calm", "case": "port_15m", "metric": "roll_peak_deg", "paper_value": 2.858, "unit": "deg", "source": "Section 3.2.1 text"},
        {"id": "wave_bow_15_pitch_deg", "environment": "wave", "case": "bow_15m", "metric": "pitch_peak_deg", "paper_value": 0.267, "unit": "deg", "source": "Section 3.2.2 text"},
        {"id": "wave_port_15_roll_deg", "environment": "wave", "case": "port_15m", "metric": "roll_peak_deg", "paper_value": 2.898, "unit": "deg", "source": "Section 3.2.2 text"},
        {"id": "wave_heave_impact_delta_m", "environment": "wave_delta", "case": "center", "metric": "heave_delta_peak_m", "paper_value": 0.41, "unit": "m", "source": "Section 3.2.2 text"},
    ],
    "model_notes": {
        "scope": "Reproduces the Wang Zhi 2023 wave-plume-platform response chain as an open HAMS/Cummins surrogate.",
        "limits": "The paper does not publish STAR-CCM+ load samples, AQWA mesh/project, second-order wave force data, or catenary line mechanical properties.",
    },
}


def linspace(start: float, end: float, count: int) -> list[float]:
    if count == 1:
        return [start]
    step = (end - start) / (count - 1)
    return [start + i * step for i in range(count)]


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


def add_derived_fields(config: dict[str, Any]) -> None:
    platform = config["platform"]
    length = platform["length_m"]
    beam = platform["beam_m"]
    draft = platform["draft_m"]
    mass = platform["mass_kg"]
    mass_volume = mass / platform["rho_kg_m3"]
    bottom_beam = max(0.1 * beam, min(beam, 2.0 * mass_volume / (length * draft) - beam))
    platform["bottom_beam_m"] = bottom_beam
    platform["geometry_displacement_volume_m3"] = length * draft * 0.5 * (beam + bottom_beam)
    platform["paper_mass_displacement_volume_m3"] = mass_volume
    platform["waterplane_area_m2"] = length * beam
    reported_x = platform["reported_cg_from_aft_m"][0]
    platform["mesh_x_min_m"] = -reported_x
    platform["mesh_x_max_m"] = length - reported_x
    platform["deck_points"] = [
        {"id": row["id"], "label": row["label"], "position_m": [row["x"], row["y"], platform["deck_z_m"]]}
        for row in config["landing_offsets_m"]
        if row["id"] != "no_plume"
    ]


def half_beam_at_z(platform: dict[str, Any], z: float) -> float:
    draft = platform["draft_m"]
    top = platform["beam_m"] / 2.0
    bottom = platform["bottom_beam_m"] / 2.0
    t = (z + draft) / draft
    return bottom + (top - bottom) * t


def build_mesh(config: dict[str, Any]) -> tuple[list[tuple[float, float, float]], list[list[int]], list[tuple[float, float, float]], list[list[int]]]:
    platform = config["platform"]
    mesh = config["mesh"]
    x_min = platform["mesh_x_min_m"]
    x_max = platform["mesh_x_max_m"]
    beam = platform["beam_m"]
    draft = platform["draft_m"]
    bottom_beam = platform["bottom_beam_m"]
    nx = int(mesh["nx"])
    ny = int(mesh["ny"])
    nz = int(mesh["nz"])

    xs = linspace(x_min, x_max, nx + 1)
    ys_top = linspace(-beam / 2.0, beam / 2.0, ny + 1)
    ys_bottom = linspace(-bottom_beam / 2.0, bottom_beam / 2.0, ny + 1)
    zs = linspace(-draft, 0.0, nz + 1)

    hull_nodes: list[tuple[float, float, float]] = []
    hull_panels: list[list[int]] = []
    append_surface(hull_nodes, hull_panels, [[(x, y, -draft) for x in xs] for y in ys_bottom], "up")
    append_surface(hull_nodes, hull_panels, [[(x, -half_beam_at_z(platform, z), z) for x in xs] for z in zs], "plus_y")
    append_surface(hull_nodes, hull_panels, [[(x, half_beam_at_z(platform, z), z) for x in xs] for z in zs], "minus_y")
    aft_grid = []
    forward_grid = []
    for z in zs:
        half_beam = half_beam_at_z(platform, z)
        ys = linspace(-half_beam, half_beam, ny + 1)
        aft_grid.append([(x_min, y, z) for y in ys])
        forward_grid.append([(x_max, y, z) for y in ys])
    append_surface(hull_nodes, hull_panels, aft_grid, "plus_x")
    append_surface(hull_nodes, hull_panels, forward_grid, "minus_x")

    water_nodes: list[tuple[float, float, float]] = []
    water_panels: list[list[int]] = []
    append_surface(water_nodes, water_panels, [[(x, y, 0.0) for x in xs] for y in ys_top], "up")
    return hull_nodes, hull_panels, water_nodes, water_panels


def mass_matrix_6d(config: dict[str, Any]) -> list[list[float]]:
    platform = config["platform"]
    mass = platform["mass_kg"]
    xg, yg, zg = platform["cg_m"]
    radii = platform["inertia_radius_m"]
    ixx_cg = mass * radii["roll"] ** 2
    iyy_cg = mass * radii["pitch"] ** 2
    izz_cg = mass * radii["yaw"] ** 2
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
    _xg, _yg, zg = platform["cg_m"]
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
    return matrix


def zero_matrix_6d() -> list[list[float]]:
    return [[0.0 for _ in range(6)] for _ in range(6)]


def write_matrix(lines: list[str], title: str, matrix: list[list[float]]) -> None:
    lines.append(f" {title}:")
    for row in matrix:
        lines.append("  " + "  ".join(f"{value:12.5E}" for value in row))


def write_hydrostatic(path: Path, config: dict[str, Any]) -> dict[str, Any]:
    platform = config["platform"]
    mass = mass_matrix_6d(config)
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
        "roll_restoring_nm_rad": restoring[3][3],
        "pitch_restoring_nm_rad": restoring[4][4],
    }


def write_control(path: Path, config: dict[str, Any]) -> None:
    platform = config["platform"]
    freq = config["frequency"]
    headings = config["headings_deg"]
    nfreq = int(round((freq["max_rad_s"] - freq["min_rad_s"]) / freq["step_rad_s"])) + 1
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


def self_check(
    config: dict[str, Any],
    hull_nodes: list[tuple[float, float, float]],
    hull_panels: list[list[int]],
    water_nodes: list[tuple[float, float, float]],
    water_panels: list[list[int]],
    hydro: dict[str, Any],
) -> dict[str, Any]:
    platform = config["platform"]
    mesh = config["mesh"]
    expected_hull_panels = mesh["nx"] * mesh["ny"] + 2 * mesh["nx"] * mesh["nz"] + 2 * mesh["ny"] * mesh["nz"]
    expected_water_panels = mesh["nx"] * mesh["ny"]
    checks = [
        {"id": "paper_length", "expected": 165.0, "actual": platform["length_m"], "passed": platform["length_m"] == 165.0},
        {"id": "paper_beam", "expected": 40.0, "actual": platform["beam_m"], "passed": platform["beam_m"] == 40.0},
        {"id": "paper_draft", "expected": 5.0, "actual": platform["draft_m"], "passed": platform["draft_m"] == 5.0},
        {"id": "paper_mass", "expected": 22_000_000.0, "actual": platform["mass_kg"], "passed": platform["mass_kg"] == 22_000_000.0},
        {"id": "hull_panel_count", "expected": expected_hull_panels, "actual": len(hull_panels), "passed": len(hull_panels) == expected_hull_panels},
        {"id": "waterplane_panel_count", "expected": expected_water_panels, "actual": len(water_panels), "passed": len(water_panels) == expected_water_panels},
        {"id": "hull_z_not_above_free_surface", "expected": "<=0", "actual": max(z for _, _, z in hull_nodes), "passed": max(z for _, _, z in hull_nodes) <= 1.0e-9},
        {"id": "waterplane_z_zero", "expected": 0.0, "actual": max(abs(z) for _, _, z in water_nodes), "passed": max(abs(z) for _, _, z in water_nodes) <= 1.0e-9},
        {"id": "jonswap_hs", "expected": 1.75, "actual": config["sea_state"]["hs_m"], "passed": config["sea_state"]["hs_m"] == 1.75},
        {"id": "jonswap_tp", "expected": 4.5, "actual": config["sea_state"]["tp_s"], "passed": config["sea_state"]["tp_s"] == 4.5},
        {"id": "plume_plateau", "expected": 20_400_000.0, "actual": config["plume_load"]["plateau_n"], "passed": config["plume_load"]["plateau_n"] == 20_400_000.0},
        {"id": "positive_hydrostatics", "expected": ">0", "actual": hydro["heave_restoring_n_m"], "passed": hydro["heave_restoring_n_m"] > 0.0 and hydro["roll_restoring_nm_rad"] > 0.0 and hydro["pitch_restoring_nm_rad"] > 0.0},
    ]
    return {
        "case_id": config["case_id"],
        "mesh": {"hull_nodes": len(hull_nodes), "hull_panels": len(hull_panels), "waterplane_nodes": len(water_nodes), "waterplane_panels": len(water_panels)},
        "hydrostatic": hydro,
        "published_aqwa_panel_count": mesh["paper_aqwa_panel_count"],
        "checks": checks,
        "passed": all(check["passed"] for check in checks),
    }


def generate_case() -> dict[str, Any]:
    config = {**BASE_CONFIG, "platform": dict(BASE_CONFIG["platform"]), "mesh": dict(BASE_CONFIG["mesh"])}
    config["sea_state"] = dict(BASE_CONFIG["sea_state"])
    config["mooring"] = dict(BASE_CONFIG["mooring"])
    config["plume_load"] = dict(BASE_CONFIG["plume_load"])
    config["time_domain"] = dict(BASE_CONFIG["time_domain"])
    config["landing_offsets_m"] = [dict(row) for row in BASE_CONFIG["landing_offsets_m"]]
    config["paper_targets"] = [dict(row) for row in BASE_CONFIG["paper_targets"]]
    config["model_notes"] = dict(BASE_CONFIG["model_notes"])
    add_derived_fields(config)

    ensure_case_output_dirs(PAPER_ROOT)
    hull_nodes, hull_panels, water_nodes, water_panels = build_mesh(config)
    input_dir = PAPER_ROOT / "Input"
    geometry_dir = PAPER_ROOT / "geometry"
    write_pnl(input_dir / "HullMesh.pnl", "Hull Mesh File", hull_nodes, hull_panels)
    write_pnl(input_dir / "WaterplaneMesh.pnl", "Waterplane Mesh File", water_nodes, water_panels)
    all_nodes = hull_nodes + water_nodes
    all_panels = hull_panels + [[node + len(hull_nodes) for node in panel] for panel in water_panels]
    write_gdf(geometry_dir / "wang_2023_recovery_barge.gdf", all_nodes, all_panels, config)
    write_control(input_dir / "ControlFile.in", config)
    hydro = write_hydrostatic(input_dir / "Hydrostatic.in", config)
    write_json(PAPER_ROOT / "platform_config.json", config)
    check = self_check(config, hull_nodes, hull_panels, water_nodes, water_panels, hydro)
    write_json(PAPER_ROOT / "validation" / "wang-self-check.json", check)
    return check


def extract_real_matrix_series(case_dir: Path, prefix: str) -> tuple[np.ndarray, np.ndarray]:
    omega_ref: np.ndarray | None = None
    matrices: list[np.ndarray] | None = None
    for a, i in enumerate(DOF_IDS):
        for b, j in enumerate(DOF_IDS):
            parsed = parse_hydrostar_rao(case_dir / "Output" / "Hydrostar_format" / f"{prefix}_{i}{j}.rao")
            omega = np.array([row["frequency"] for row in parsed["rows"]], dtype=float)
            values = np.array([row["amplitudes"][0] for row in parsed["rows"]], dtype=float)
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


def wave_excitation_series(case_dir: Path, omega: np.ndarray) -> np.ndarray:
    values = np.zeros((len(omega), 3), dtype=complex)
    for a, dof in enumerate(DOF_IDS):
        parsed = parse_hydrostar_rao(case_dir / "Output" / "Hydrostar_format" / f"Excitation_{dof}.rao")
        row_omega = np.array([row["frequency"] for row in parsed["rows"]], dtype=float)
        row_complex = np.array(
            [hams_amp_phase_to_complex(row["amplitudes"][0], row["phases_deg"][0]) for row in parsed["rows"]],
            dtype=complex,
        )
        values[:, a] = np.interp(omega, row_omega, row_complex.real) + 1j * np.interp(omega, row_omega, row_complex.imag)
    return values


def modal_damping_matrix(mass: np.ndarray, stiffness: np.ndarray, damping_ratio: float) -> np.ndarray:
    eigvals, eigvecs = eigh(stiffness, mass)
    eigvals = np.maximum(eigvals, 0.0)
    modal = np.diag([2.0 * damping_ratio * math.sqrt(value) if value > 0.0 else 0.0 for value in eigvals])
    return mass @ eigvecs @ modal @ eigvecs.T @ mass


def hydro_matrices(config: dict[str, Any], case_dir: Path) -> dict[str, Any]:
    hydro = read_json(case_dir / "validation" / "wang-self-check.json")["hydrostatic"]
    rigid_6 = np.array(hydro["body_mass_matrix"], dtype=float)
    restoring_6 = np.array(hydro["hydrostatic_restoring_matrix"], dtype=float)
    idx = [dof - 1 for dof in DOF_IDS]
    rigid = rigid_6[np.ix_(idx, idx)]
    restoring = restoring_6[np.ix_(idx, idx)]
    omega, added = extract_real_matrix_series(case_dir, "AddedMass")
    rad_omega, radiation = extract_real_matrix_series(case_dir, "WaveDamping")
    if not np.allclose(omega, rad_omega):
        raise ValueError("Added-mass and radiation-damping frequency grids differ.")
    a_inf = added[-1]
    mass = rigid + a_inf
    damping = modal_damping_matrix(mass, restoring + 1.0e-6 * np.eye(3), config["time_domain"]["linear_damping_ratio"])
    return {
        "omega_rad_s": omega,
        "added_mass": added,
        "radiation_damping": radiation,
        "radiation_weights": quadrature_weights(omega),
        "wave_excitation": wave_excitation_series(case_dir, omega),
        "rigid_mass": rigid,
        "a_inf": a_inf,
        "mass": mass,
        "restoring": restoring,
        "linear_damping": damping,
    }


def plume_load_n(t_abs: float, config: dict[str, Any]) -> float:
    load = config["plume_load"]
    times = load["time_absolute_s"]
    t1 = times["ignition"]
    t2 = times["vertical_descent"]
    t3 = times["landing"]
    t4 = times["shutdown_complete"]
    if t1 <= t_abs < t2:
        return max(0.0, load["ramp_up_slope_n_s"] * t_abs + load["ramp_up_intercept_n"])
    if t2 <= t_abs < t3:
        return load["plateau_n"]
    if t3 <= t_abs < t4:
        return max(0.0, load["ramp_down_slope_n_s"] * t_abs + load["ramp_down_intercept_n"])
    return 0.0


def plume_generalized_force(t_abs: float, config: dict[str, Any], offset: dict[str, Any]) -> np.ndarray:
    if not offset["with_plume"]:
        return np.zeros(3, dtype=float)
    force_z = -plume_load_n(t_abs, config)
    x = float(offset["x"])
    y = float(offset["y"])
    return np.array([force_z, y * force_z, -x * force_z], dtype=float)


def build_wave_force_components(config: dict[str, Any], matrices: dict[str, Any], enabled: bool) -> dict[str, Any]:
    omega = matrices["omega_rad_s"]
    if not enabled:
        return {"enabled": False, "amplitudes_m": np.zeros_like(omega), "phases_rad": np.zeros_like(omega), "force_complex": np.zeros((len(omega), 3), dtype=complex)}
    sea = config["sea_state"]
    spectrum = np.array(jonswap_spectrum(omega.tolist(), sea["hs_m"], sea["tp_s"], sea["gamma"]), dtype=float)
    weights = np.zeros_like(omega)
    weights[0] = omega[1] - omega[0]
    weights[-1] = omega[-1] - omega[-2]
    for i in range(1, len(omega) - 1):
        weights[i] = 0.5 * (omega[i + 1] - omega[i - 1])
    amplitudes = np.sqrt(np.maximum(2.0 * spectrum * weights, 0.0))
    rng = np.random.default_rng(config["time_domain"]["wave_seed"])
    phases = rng.uniform(0.0, 2.0 * math.pi, size=len(omega))
    return {
        "enabled": True,
        "spectrum_m2_s": spectrum,
        "amplitudes_m": amplitudes,
        "phases_rad": phases,
        "force_complex": matrices["wave_excitation"] * amplitudes[:, None],
    }


def wave_generalized_force(t_abs: float, matrices: dict[str, Any], wave: dict[str, Any], start_s: float) -> np.ndarray:
    if not wave["enabled"]:
        return np.zeros(3, dtype=float)
    phase = matrices["omega_rad_s"] * (t_abs - start_s) + wave["phases_rad"]
    terms = wave["force_complex"] * np.exp(1j * phase[:, None])
    return np.real(np.sum(terms, axis=0))


def solve_case(config: dict[str, Any], case_dir: Path, offset: dict[str, Any], environment: str, matrices: dict[str, Any]) -> dict[str, Any]:
    td = config["time_domain"]
    with_wave = environment == "wave"
    wave = build_wave_force_components(config, matrices, with_wave)
    omega = matrices["omega_rad_s"]
    radiation = matrices["radiation_damping"]
    radiation_weights = matrices["radiation_weights"]
    mass_inv = np.linalg.inv(matrices["mass"])
    memory_count = len(omega)
    y0 = np.zeros(6 + 2 * memory_count * 3, dtype=float)

    def rhs(t_abs: float, y: np.ndarray) -> np.ndarray:
        q = y[:3]
        qd = y[3:6]
        memory = y[6:].reshape(2, memory_count, 3)
        cos_state = memory[0]
        sin_state = memory[1]
        memory_force = np.einsum("k,kij,kj->i", radiation_weights, radiation, cos_state)
        force = (
            plume_generalized_force(t_abs, config, offset)
            + wave_generalized_force(t_abs, matrices, wave, td["start_s"])
            - matrices["linear_damping"] @ qd
            - matrices["restoring"] @ q
        )
        force -= memory_force
        qdd = mass_inv @ force
        cos_dot = qd[None, :] - omega[:, None] * sin_state
        sin_dot = omega[:, None] * cos_state
        return np.concatenate([qd, qdd, cos_dot.reshape(-1), sin_dot.reshape(-1)])

    step_count = int(round((td["end_s"] - td["start_s"]) / td["dt_s"]))
    t_eval = np.linspace(td["start_s"], td["end_s"], step_count + 1)
    sol = solve_ivp(rhs, (td["start_s"], td["end_s"]), y0, t_eval=t_eval, method="DOP853", rtol=1.0e-7, atol=1.0e-8)
    if not sol.success:
        raise RuntimeError(sol.message)

    q = sol.y[:3, :]
    qd = sol.y[3:6, :]
    force = np.array([plume_load_n(t, config) if offset["with_plume"] else 0.0 for t in sol.t], dtype=float)
    result = {
        "id": f"{environment}_{offset['id']}",
        "environment": environment,
        "offset": offset,
        "with_wave": with_wave,
        "with_plume": bool(offset["with_plume"]),
        "time_s": sol.t.tolist(),
        "plume_load_n": force.tolist(),
        "responses": {
            "heave_m": q[0, :].tolist(),
            "roll_rad": q[1, :].tolist(),
            "pitch_rad": q[2, :].tolist(),
            "roll_deg": np.degrees(q[1, :]).tolist(),
            "pitch_deg": np.degrees(q[2, :]).tolist(),
        },
        "velocities": {
            "heave_m_s": qd[0, :].tolist(),
            "roll_rad_s": qd[1, :].tolist(),
            "pitch_rad_s": qd[2, :].tolist(),
        },
        "summary": {
            "heave_peak_m": float(np.max(np.abs(q[0, :]))),
            "roll_peak_deg": float(np.max(np.abs(np.degrees(q[1, :])))),
            "pitch_peak_deg": float(np.max(np.abs(np.degrees(q[2, :])))),
            "heave_rms_m": float(math.sqrt(np.mean(q[0, :] ** 2))),
            "roll_rms_deg": float(math.sqrt(np.mean(np.degrees(q[1, :]) ** 2))),
            "pitch_rms_deg": float(math.sqrt(np.mean(np.degrees(q[2, :]) ** 2))),
            "max_plume_load_mn": float(np.max(force) / 1.0e6),
        },
    }
    return result


def compact_simulation(sim: dict[str, Any], max_points: int = 1400) -> dict[str, Any]:
    time = sim["time_s"]
    stride = max(1, math.ceil(len(time) / max_points))
    indices = list(range(0, len(time), stride))
    if indices[-1] != len(time) - 1:
        indices.append(len(time) - 1)
    compact = {
        key: sim[key]
        for key in ["id", "environment", "offset", "with_wave", "with_plume", "summary"]
    }
    compact["time_s"] = [time[i] for i in indices]
    compact["plume_load_n"] = [sim["plume_load_n"][i] for i in indices]
    compact["responses"] = {key: [series[i] for i in indices] for key, series in sim["responses"].items()}
    compact["velocities"] = {key: [series[i] for i in indices] for key, series in sim["velocities"].items()}
    return compact


def compare_targets(config: dict[str, Any], simulations: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for target in config["paper_targets"]:
        if target["environment"] == "wave_delta":
            base = simulations["wave_no_plume"]["responses"]["heave_m"]
            case = simulations[f"wave_{target['case']}"]["responses"]["heave_m"]
            computed = max(abs(a - b) for a, b in zip(case, base))
        else:
            sim = simulations[f"{target['environment']}_{target['case']}"]
            computed = sim["summary"][target["metric"]]
        paper = target["paper_value"]
        rows.append(
            {
                **target,
                "computed_value": computed,
                "abs_error": abs(computed - paper),
                "relative_error": abs(computed - paper) / max(abs(paper), 1.0e-12),
                "status": "reference_only",
            }
        )
    return rows


def simulate() -> dict[str, Any]:
    config = read_json(PAPER_ROOT / "platform_config.json")
    matrices = hydro_matrices(config, PAPER_ROOT)
    simulations: dict[str, Any] = {}
    for environment in ["calm", "wave"]:
        for offset in config["landing_offsets_m"]:
            if environment == "calm" and offset["id"] == "no_plume":
                continue
            sim = solve_case(config, PAPER_ROOT, offset, environment, matrices)
            simulations[sim["id"]] = sim
    comparison = compare_targets(config, simulations)
    result = {
        "paper_id": PAPER_ID,
        "case_id": config["case_id"],
        "config": config,
        "hydrodynamic_sample": {
            "omega_rad_s": matrices["omega_rad_s"].tolist(),
            "added_mass_infinite_3dof": matrices["a_inf"].tolist(),
            "rigid_mass_3dof": matrices["rigid_mass"].tolist(),
            "restoring_3dof": matrices["restoring"].tolist(),
            "linear_damping_3dof": matrices["linear_damping"].tolist(),
        },
        "natural_frequencies_hz": natural_frequencies(matrices["mass"], matrices["restoring"]),
        "simulations": simulations,
        "comparison": comparison,
    }
    write_json(PAPER_ROOT / "Output" / "RocketRecovery" / "wang-2023-response.json", result)
    return result


def natural_frequencies(mass: np.ndarray, stiffness: np.ndarray) -> list[float]:
    eigvals = eigh(stiffness, mass, eigvals_only=True)
    out = []
    for eigval in eigvals:
        out.append(float(math.sqrt(max(eigval, 0.0)) / (2.0 * math.pi)))
    return out


def paper_asset_status() -> dict[str, Any]:
    return {
        "markdown_exists": PAPER_MD.exists(),
        "pdf_exists": PAPER_PDF.exists(),
        "markdown_path": str(PAPER_MD),
        "pdf_path": str(PAPER_PDF),
        "pdf_size_bytes": PAPER_PDF.stat().st_size if PAPER_PDF.exists() else None,
    }


def build_model_audit(config: dict[str, Any]) -> dict[str, Any]:
    published = [
        {"item": "Hull length", "value": config["platform"]["length_m"], "unit": "m", "source": "Table 1"},
        {"item": "Hull beam", "value": config["platform"]["beam_m"], "unit": "m", "source": "Table 1"},
        {"item": "Draft", "value": config["platform"]["draft_m"], "unit": "m", "source": "Table 1"},
        {"item": "Deadweight/mass input", "value": config["platform"]["deadweight_t"], "unit": "t", "source": "Table 1"},
        {"item": "CG reported", "value": config["platform"]["reported_cg_from_aft_m"], "unit": "m", "source": "Table 1"},
        {"item": "Inertia radii", "value": config["platform"]["inertia_radius_m"], "unit": "m", "source": "Table 1"},
        {"item": "Mooring line count", "value": config["mooring"]["line_count"], "unit": "-", "source": "Section 2.2"},
        {"item": "Mooring line length", "value": config["mooring"]["line_length_m"], "unit": "m", "source": "Section 2.2"},
        {"item": "JONSWAP Hs/Tp/gamma/heading", "value": config["sea_state"], "unit": "-", "source": "Section 3.2.2"},
        {"item": "Plume plateau", "value": config["plume_load"]["plateau_n"], "unit": "N", "source": "Section 3.1.2/3.1.3"},
    ]
    unresolved = [
        {"item": "STAR-CCM+ Figure 6 load samples", "impact": "506-510 s Fp is a plateau from text, not the CFD oscillatory trace."},
        {"item": "AQWA mesh and hull offsets", "impact": "HAMS mesh is regenerated from principal dimensions and mass-matched trapezoid."},
        {"item": "Second-order wave force", "impact": "Current wave load uses HAMS first-order excitation only."},
        {"item": "Catenary mooring mechanical properties", "impact": "Mooring stiffness is not inserted because line EA, wet weight, anchor/fairlead geometry and pretension are absent."},
    ]
    return {"published_inputs_used": published, "unresolved": unresolved}


def build_report_data() -> dict[str, Any]:
    response_path = PAPER_ROOT / "Output" / "RocketRecovery" / "wang-2023-response.json"
    if not response_path.exists():
        result = simulate()
    else:
        result = read_json(response_path)
    compact = {
        **result,
        "simulations": {key: compact_simulation(sim) for key, sim in result["simulations"].items()},
        "mesh": {
            "hull": mesh_to_three(parse_pnl(PAPER_ROOT / "Input" / "HullMesh.pnl")),
            "waterplane": mesh_to_three(parse_pnl(PAPER_ROOT / "Input" / "WaterplaneMesh.pnl")),
        },
        "self_check": read_json(PAPER_ROOT / "validation" / "wang-self-check.json"),
        "paper_assets": paper_asset_status(),
        "model_audit": build_model_audit(result["config"]),
    }
    write_json(PAPER_ROOT / "wang-2023-report-data.json", compact)
    return compact


def write_report_js(data: dict[str, Any], path: Path = REPORT_JS) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("window.WANG_2023_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Advance Wang Zhi 2023 plume-wave-platform reproduction with HAMS-backed time-domain dynamics.")
    parser.add_argument("action", choices=["generate", "simulate", "report", "all"], nargs="?", default="generate")
    args = parser.parse_args()

    if args.action in {"generate", "all"}:
        check = generate_case()
        print(f"Generated {PAPER_ROOT}")
        print(f"Self-check passed: {check['passed']}")
        for item in check["checks"]:
            print(f"- {item['id']}: {'PASS' if item['passed'] else 'CHECK'}")
    if args.action in {"simulate", "all"}:
        result = simulate()
        print(f"Simulated {len(result['simulations'])} Wang 2023 cases")
        for row in result["comparison"]:
            print(f"- {row['id']}: computed {row['computed_value']:.6g} {row['unit']} vs paper {row['paper_value']:.6g}")
    if args.action in {"report", "all"}:
        data = build_report_data()
        write_report_js(data)
        print(f"Wrote {REPORT_JS}")


if __name__ == "__main__":
    main()
