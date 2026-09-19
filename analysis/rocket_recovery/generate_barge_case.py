from __future__ import annotations

import argparse
import math
from pathlib import Path

try:
    from .common import G, RHO, ensure_case_output_dirs, fortran_float, resolve_case, write_json, write_pnl
except ImportError:
    from common import G, RHO, ensure_case_output_dirs, fortran_float, resolve_case, write_json, write_pnl


DEFAULT_CONFIG = {
    "case_id": "Barge_120x50",
    "platform": {
        "length_m": 120.0,
        "beam_m": 50.0,
        "draft_m": 7.0,
        "deck_z_m": 3.0,
        "water_depth_m": -1.0,
        "cg_m": [0.0, 0.0, -2.0],
        "rho_kg_m3": RHO,
        "gravity_m_s2": G,
    },
    "mesh": {"nx": 24, "ny": 10, "nz": 4},
    "reference_point_m": [0.0, 0.0, 0.0],
    "deck_points": [
        {"id": "landing_center", "position_m": [0.0, 0.0, 3.0]},
        {"id": "leg_forward_port", "position_m": [9.0, 9.0, 3.0]},
        {"id": "leg_forward_starboard", "position_m": [9.0, -9.0, 3.0]},
        {"id": "leg_aft_port", "position_m": [-9.0, 9.0, 3.0]},
        {"id": "leg_aft_starboard", "position_m": [-9.0, -9.0, 3.0]},
    ],
    "frequency": {"min_rad_s": 0.2, "max_rad_s": 2.0, "step_rad_s": 0.1},
    "headings_deg": [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0],
    "sea_states": [
        {"id": f"Hs{hs:g}_Tp{tp:g}", "hs_m": float(hs), "tp_s": float(tp), "gamma": 3.3, "duration_s": 600.0}
        for hs in [1.0, 2.0, 3.0]
        for tp in [6.0, 8.0, 10.0]
    ],
    "model_notes": {
        "scope": "Frequency-domain platform and deck-point motion prediction for landing-leg studies.",
        "excluded": "No plume, rocket GNC, landing-leg structural loads, touchdown switching, or DP time-domain controller in v1.",
        "angular_motion_convention": "HAMS Hydrostar Motion_4..6 values are interpreted as radians per metre despite the header text.",
    },
}


def append_grid(
    nodes: list[tuple[float, float, float]],
    panels: list[list[int]],
    xs: list[float],
    ys: list[float],
    zs: list[float],
    fixed_axis: str,
    orientation: str,
) -> None:
    start = len(nodes) + 1
    if fixed_axis == "z":
        for y in ys:
            for x in xs:
                nodes.append((x, y, zs[0]))
        row = len(xs)
        for j in range(len(ys) - 1):
            for i in range(len(xs) - 1):
                n00 = start + j * row + i
                n10 = start + j * row + i + 1
                n01 = start + (j + 1) * row + i
                n11 = start + (j + 1) * row + i + 1
                panels.append([n00, n01, n11, n10] if orientation == "up" else [n00, n10, n11, n01])
    elif fixed_axis == "y":
        y = ys[0]
        for z in zs:
            for x in xs:
                nodes.append((x, y, z))
        row = len(xs)
        for k in range(len(zs) - 1):
            for i in range(len(xs) - 1):
                n00 = start + k * row + i
                n10 = start + k * row + i + 1
                n01 = start + (k + 1) * row + i
                n11 = start + (k + 1) * row + i + 1
                panels.append([n00, n01, n11, n10] if orientation == "minus_y" else [n00, n10, n11, n01])
    elif fixed_axis == "x":
        x = xs[0]
        for z in zs:
            for y in ys:
                nodes.append((x, y, z))
        row = len(ys)
        for k in range(len(zs) - 1):
            for j in range(len(ys) - 1):
                n00 = start + k * row + j
                n10 = start + k * row + j + 1
                n01 = start + (k + 1) * row + j
                n11 = start + (k + 1) * row + j + 1
                panels.append([n00, n10, n11, n01] if orientation == "minus_x" else [n00, n01, n11, n10])
    else:
        raise ValueError(f"Unsupported fixed axis: {fixed_axis}")


def linspace(start: float, end: float, count: int) -> list[float]:
    if count == 1:
        return [start]
    step = (end - start) / (count - 1)
    return [start + i * step for i in range(count)]


def build_barge_mesh(config: dict) -> tuple[list[tuple[float, float, float]], list[list[int]], list[tuple[float, float, float]], list[list[int]]]:
    platform = config["platform"]
    mesh = config["mesh"]
    length = platform["length_m"]
    beam = platform["beam_m"]
    draft = platform["draft_m"]
    nx = int(mesh["nx"])
    ny = int(mesh["ny"])
    nz = int(mesh["nz"])

    x = linspace(-length / 2.0, length / 2.0, nx + 1)
    y = linspace(-beam / 2.0, beam / 2.0, ny + 1)
    z = linspace(-draft, 0.0, nz + 1)

    hull_nodes: list[tuple[float, float, float]] = []
    hull_panels: list[list[int]] = []
    append_grid(hull_nodes, hull_panels, x, y, [-draft], "z", "up")
    append_grid(hull_nodes, hull_panels, x, [-beam / 2.0], z, "y", "plus_y")
    append_grid(hull_nodes, hull_panels, x, [beam / 2.0], z, "y", "minus_y")
    append_grid(hull_nodes, hull_panels, [-length / 2.0], y, z, "x", "plus_x")
    append_grid(hull_nodes, hull_panels, [length / 2.0], y, z, "x", "minus_x")

    water_nodes: list[tuple[float, float, float]] = []
    water_panels: list[list[int]] = []
    append_grid(water_nodes, water_panels, x, y, [0.0], "z", "up")
    return hull_nodes, hull_panels, water_nodes, water_panels


def rigid_body_mass_matrix(config: dict) -> list[list[float]]:
    platform = config["platform"]
    length = platform["length_m"]
    beam = platform["beam_m"]
    draft = platform["draft_m"]
    deck_z = platform["deck_z_m"]
    xg, yg, zg = platform["cg_m"]
    volume = length * beam * draft
    mass = platform["rho_kg_m3"] * volume
    hull_depth = draft + deck_z

    ixx_cg = mass * (beam**2 + hull_depth**2) / 12.0
    iyy_cg = mass * (length**2 + hull_depth**2) / 12.0
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


def hydrostatic_restoring_matrix(config: dict) -> list[list[float]]:
    platform = config["platform"]
    length = platform["length_m"]
    beam = platform["beam_m"]
    draft = platform["draft_m"]
    _xg, _yg, zg = platform["cg_m"]
    rho = platform["rho_kg_m3"]
    gravity = platform["gravity_m_s2"]
    volume = length * beam * draft
    waterplane_area = length * beam
    kb = -draft / 2.0
    iwp_roll = length * beam**3 / 12.0
    iwp_pitch = beam * length**3 / 12.0
    gm_roll = kb + iwp_roll / volume - zg
    gm_pitch = kb + iwp_pitch / volume - zg

    matrix = [[0.0 for _ in range(6)] for _ in range(6)]
    matrix[2][2] = rho * gravity * waterplane_area
    matrix[3][3] = rho * gravity * volume * gm_roll
    matrix[4][4] = rho * gravity * volume * gm_pitch
    return matrix


def zero_matrix() -> list[list[float]]:
    return [[0.0 for _ in range(6)] for _ in range(6)]


def write_matrix(lines: list[str], title: str, matrix: list[list[float]]) -> None:
    lines.append(f" {title}:")
    for row in matrix:
        lines.append("  " + "  ".join(f"{value:12.5E}" for value in row))


def write_hydrostatic(path: Path, config: dict) -> dict:
    platform = config["platform"]
    length = platform["length_m"]
    beam = platform["beam_m"]
    draft = platform["draft_m"]
    volume = length * beam * draft
    waterplane_area = length * beam
    mass_matrix = rigid_body_mass_matrix(config)
    restoring = hydrostatic_restoring_matrix(config)

    lines = [" Center of Gravity:", "  " + "  ".join(f"{value:23.15E}" for value in platform["cg_m"])]
    write_matrix(lines, "Body Mass Matrix", mass_matrix)
    write_matrix(lines, "External Linear Damping Matrix", zero_matrix())
    write_matrix(lines, "External Quadratic Damping Matrix", zero_matrix())
    write_matrix(lines, "Hydrostatic Restoring Matrix", restoring)
    write_matrix(lines, "External Restoring Matrix", zero_matrix())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "displacement_volume_m3": volume,
        "waterplane_area_m2": waterplane_area,
        "mass_kg": platform["rho_kg_m3"] * volume,
        "heave_restoring_n_m": restoring[2][2],
        "roll_restoring_nm_rad": restoring[3][3],
        "pitch_restoring_nm_rad": restoring[4][4],
    }


def frequency_count(freq: dict) -> int:
    return int(round((freq["max_rad_s"] - freq["min_rad_s"]) / freq["step_rad_s"])) + 1


def write_control(path: Path, config: dict) -> None:
    platform = config["platform"]
    freq = config["frequency"]
    headings = config["headings_deg"]
    nfreq = frequency_count(freq)
    lines = [
        "   --------------HAMS Control file---------------",
        "   ",
        f"   Waterdepth  {fortran_float(platform['water_depth_m'])}",
        "",
        "   #Start Definition of Wave Frequencies",
        "    0_inf_frequency_limits      0                             # 0: not to include; 1: to include",
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
        "    Reference_body_center       0.000       0.000       0.000",
        "    Reference_body_length   120.D0",
        "    Wave_diffrac_solution    2",
        "    If_remove_irr_freq       1",
        "    Number of threads       16",
        "   ",
        "   #Start Definition of Pressure and/or Elevation (PE)",
        "    Number_of_field_points     0                           # number of field points where to calculate PE",
        "   #End Definition of Pressure and/or Elevation",
        "   ",
        "   ----------End HAMS Control file---------------",
        "   ",
        "   Input_frequency_type options: ",
        "   1--deepwater wave number; 2--finite-depth wave number; 3--wave frequency; 4--wave period; 5--wave length",
        "   Output_frequency_type options: same as Input_frequency_type options",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_gdf(path: Path, nodes: list[tuple[float, float, float]], panels: list[list[int]], config: dict) -> None:
    lines = [
        "Generated rectangular recovery barge",
        f"1 {G:.5f} \tULEN GRAV",
        "0 0 \tISX  ISY",
        str(len(panels)),
    ]
    for panel in panels:
        verts = [nodes[index - 1] for index in panel]
        for x, y, z in verts:
            lines.append(f"{x:12.5f} {y:12.5f} {z:12.5f}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_self_check(config: dict, hull_nodes: list[tuple[float, float, float]], hull_panels: list[list[int]], water_nodes: list[tuple[float, float, float]], water_panels: list[list[int]], hydro: dict) -> dict:
    mesh = config["mesh"]
    platform = config["platform"]
    expected_hull_panels = mesh["nx"] * mesh["ny"] + 2 * mesh["nx"] * mesh["nz"] + 2 * mesh["ny"] * mesh["nz"]
    expected_hull_nodes = (mesh["nx"] + 1) * (mesh["ny"] + 1) + 2 * (mesh["nx"] + 1) * (mesh["nz"] + 1) + 2 * (mesh["ny"] + 1) * (mesh["nz"] + 1)
    expected_water_panels = mesh["nx"] * mesh["ny"]
    expected_water_nodes = (mesh["nx"] + 1) * (mesh["ny"] + 1)
    expected_volume = platform["length_m"] * platform["beam_m"] * platform["draft_m"]
    expected_area = platform["length_m"] * platform["beam_m"]

    checks = [
        {"id": "hull_panel_count", "expected": expected_hull_panels, "actual": len(hull_panels), "passed": len(hull_panels) == expected_hull_panels},
        {"id": "hull_node_count", "expected": expected_hull_nodes, "actual": len(hull_nodes), "passed": len(hull_nodes) == expected_hull_nodes},
        {"id": "waterplane_panel_count", "expected": expected_water_panels, "actual": len(water_panels), "passed": len(water_panels) == expected_water_panels},
        {"id": "waterplane_node_count", "expected": expected_water_nodes, "actual": len(water_nodes), "passed": len(water_nodes) == expected_water_nodes},
        {"id": "hull_z_not_above_free_surface", "expected": "<= 0", "actual": max(z for _, _, z in hull_nodes), "passed": max(z for _, _, z in hull_nodes) <= 1.0e-9},
        {"id": "waterplane_z_equal_zero", "expected": 0.0, "actual": max(abs(z) for _, _, z in water_nodes), "passed": max(abs(z) for _, _, z in water_nodes) <= 1.0e-9},
        {"id": "displacement_volume", "expected": expected_volume, "actual": hydro["displacement_volume_m3"], "relative_error": 0.0, "passed": abs(hydro["displacement_volume_m3"] - expected_volume) <= 1.0e-9},
        {"id": "waterplane_area", "expected": expected_area, "actual": hydro["waterplane_area_m2"], "relative_error": 0.0, "passed": abs(hydro["waterplane_area_m2"] - expected_area) <= 1.0e-9},
        {"id": "heave_restoring", "expected": RHO * G * expected_area, "actual": hydro["heave_restoring_n_m"], "relative_error": 0.0, "passed": abs(hydro["heave_restoring_n_m"] - RHO * G * expected_area) <= 1.0e-6},
    ]
    return {
        "case_id": config["case_id"],
        "mesh": {
            "expected_hull_panels": expected_hull_panels,
            "expected_hull_nodes": expected_hull_nodes,
            "expected_waterplane_panels": expected_water_panels,
            "expected_waterplane_nodes": expected_water_nodes,
        },
        "hydrostatic": hydro,
        "checks": checks,
        "passed": all(check["passed"] for check in checks),
    }


def generate(case_dir: Path) -> dict:
    config = dict(DEFAULT_CONFIG)
    config["case_id"] = case_dir.name
    ensure_case_output_dirs(case_dir)

    input_dir = case_dir / "Input"
    geometry_dir = case_dir / "geometry"
    hull_nodes, hull_panels, water_nodes, water_panels = build_barge_mesh(config)
    write_pnl(input_dir / "HullMesh.pnl", "Hull Mesh File", hull_nodes, hull_panels)
    write_pnl(input_dir / "WaterplaneMesh.pnl", "Waterplane Mesh File", water_nodes, water_panels)
    write_gdf(geometry_dir / "barge_120x50.gdf", hull_nodes + water_nodes, hull_panels + [[index + len(hull_nodes) for index in panel] for panel in water_panels], config)
    write_control(input_dir / "ControlFile.in", config)
    hydro = write_hydrostatic(input_dir / "Hydrostatic.in", config)
    write_json(case_dir / "platform_config.json", config)
    self_check = build_self_check(config, hull_nodes, hull_panels, water_nodes, water_panels, hydro)
    write_json(case_dir / "validation" / "barge-self-check.json", self_check)
    return self_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the rectangular rocket-recovery barge HAMS case.")
    parser.add_argument("--case", default="Barge_120x50", help="Case name under RocketRecoveryCases or an explicit path.")
    args = parser.parse_args()
    case_dir = resolve_case(args.case)
    result = generate(case_dir)
    print(f"Generated {case_dir}")
    print(f"Self-check passed: {result['passed']}")
    for check in result["checks"]:
        print(f"- {check['id']}: {'PASS' if check['passed'] else 'FAIL'}")


if __name__ == "__main__":
    main()
