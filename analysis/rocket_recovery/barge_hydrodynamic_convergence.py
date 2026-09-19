from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import os
import platform
import shlex
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import numpy as np
except ImportError:  # pragma: no cover - the executable analysis requires numpy
    np = None  # type: ignore[assignment]

try:
    from .common import (
        fortran_float,
        numeric_tokens,
        parse_hydrostar_rao,
        parse_number,
        read_json,
        resolve_case,
        write_json,
        write_pnl,
    )
    from .generate_barge_case import build_barge_mesh
except ImportError:
    from common import fortran_float, numeric_tokens, parse_hydrostar_rao, parse_number, read_json, resolve_case, write_json, write_pnl
    from generate_barge_case import build_barge_mesh


ROOT = Path(__file__).resolve().parents[2]
DOF_NAMES = ("surge", "sway", "heave", "roll", "pitch", "yaw")
DIAGONAL_LABELS = {2: "33", 3: "44", 4: "55"}

MESH_LEVELS: dict[str, dict[str, int | str]] = {
    "coarse": {"nx": 24, "ny": 10, "nz": 4, "target_hull_panels": 500},
    "medium": {"nx": 48, "ny": 20, "nz": 8, "target_hull_panels": 2000},
    "fine": {"nx": 96, "ny": 40, "nz": 16, "target_hull_panels": 8000},
}


def _uniform_grid(start: float, stop: float, step: float) -> list[float]:
    count = int(round((stop - start) / step))
    return [round(start + index * step, 8) for index in range(count + 1)]


def frequency_grid(name: str) -> list[float]:
    """Return a deterministic explicit-frequency list accepted by HAMS."""
    if name == "local025_high025":
        local = _uniform_grid(0.2, 2.0, 0.025)
        high = _uniform_grid(2.25, 5.0, 0.25)
        return local + high
    if name == "mesh_response_anchor":
        return [0.6, 0.8, 1.0]
    raise ValueError(f"Unknown frequency grid: {name}")


RUN_PLAN: tuple[dict[str, str], ...] = (
    {
        "id": "coarse_local025_high5",
        "level": "coarse",
        "frequency_grid": "local025_high025",
        "purpose": "0.025 rad/s local refinement from 0.2 to 2.0 and tail to 5.0",
    },
    {
        "id": "medium_local025_high5",
        "level": "medium",
        "frequency_grid": "local025_high025",
        "purpose": "0.025 rad/s local refinement from 0.2 to 2.0 and tail to 5.0",
    },
    {
        "id": "fine_response_0p6_0p8_1p0",
        "level": "fine",
        "frequency_grid": "mesh_response_anchor",
        "purpose": "fine-mesh response anchors at 0.6, 0.8 and 1.0 rad/s; A_inf tail assessment remains a separate dense medium-mesh calculation",
    },
)


def _require_numpy() -> Any:
    if np is None:
        raise RuntimeError("numpy is required for radiation impedance and IRF analysis")
    return np


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def _first_nonempty(lines: list[str], start: int) -> tuple[int, str]:
    for index in range(start, len(lines)):
        if lines[index].strip():
            return index, lines[index]
    raise ValueError("Expected a non-empty input line")


def _find_line(lines: list[str], marker: str) -> int:
    marker_lower = marker.lower()
    for index, line in enumerate(lines):
        if marker_lower in line.lower():
            return index
    raise ValueError(f"Cannot find {marker!r}")


def _matrix_after(lines: list[str], marker: str) -> tuple[list[list[float]], int]:
    marker_index = _find_line(lines, marker)
    matrix: list[list[float]] = []
    index = marker_index + 1
    while len(matrix) < 6 and index < len(lines):
        values = [parse_number(token) for token in numeric_tokens(lines[index])]
        if len(values) >= 6:
            matrix.append(values[:6])
        index += 1
    if len(matrix) != 6:
        raise ValueError(f"Incomplete 6x6 matrix after {marker!r}")
    return matrix, marker_index + 1


def parse_hydrostatic_input(path: Path) -> dict[str, Any]:
    """Read the exact HAMS Hydrostatic.in values without regenerating them."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    cg_marker = _find_line(lines, "Center of Gravity:")
    cg_line, cg_text = _first_nonempty(lines, cg_marker + 1)
    cg = [parse_number(token) for token in numeric_tokens(cg_text)][:3]
    if len(cg) != 3:
        raise ValueError(f"Invalid center of gravity in {path}")

    matrix_names = (
        "Body Mass Matrix",
        "External Linear Damping Matrix",
        "External Quadratic Damping Matrix",
        "Hydrostatic Restoring Matrix",
        "External Restoring Matrix",
    )
    matrices: dict[str, list[list[float]]] = {}
    matrix_lines: dict[str, int] = {}
    for name in matrix_names:
        matrices[name], matrix_lines[name] = _matrix_after(lines, name)

    mass_matrix = matrices["Body Mass Matrix"]
    xg, yg, zg = cg
    mass = mass_matrix[0][0]
    inertia_cg = {
        "Ixx_kg_m2": mass_matrix[3][3] - mass * (yg**2 + zg**2),
        "Iyy_kg_m2": mass_matrix[4][4] - mass * (xg**2 + zg**2),
        "Izz_kg_m2": mass_matrix[5][5] - mass * (xg**2 + yg**2),
    }

    return {
        "source_file": _relative_path(path),
        "source_sha256": _sha256(path),
        "center_of_gravity_m": cg,
        "center_of_gravity_source_line": cg_line + 1,
        "mass_kg": mass,
        "inertia_about_cg_kg_m2": inertia_cg,
        "body_mass_matrix_at_reference": mass_matrix,
        "linear_damping_matrix": matrices["External Linear Damping Matrix"],
        "quadratic_damping_matrix": matrices["External Quadratic Damping Matrix"],
        "hydrostatic_restoring_matrix": matrices["Hydrostatic Restoring Matrix"],
        "external_restoring_matrix": matrices["External Restoring Matrix"],
        "matrix_source_lines": matrix_lines,
    }


def parse_control_input(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    def field(marker: str, count: int = 1) -> tuple[list[float], int]:
        index = _find_line(lines, marker)
        values = [parse_number(token) for token in numeric_tokens(lines[index])]
        if len(values) < count:
            raise ValueError(f"Cannot read {marker!r} from {path}")
        return values[-count:], index + 1

    reference_point, reference_line = field("Reference_body_center", 3)
    reference_length, reference_length_line = field("Reference_body_length", 1)
    water_depth, water_depth_line = field("Waterdepth", 1)
    return {
        "source_file": _relative_path(path),
        "source_sha256": _sha256(path),
        "reference_point_m": reference_point,
        "reference_point_source_line": reference_line,
        "reference_length_m": reference_length[0],
        "reference_length_source_line": reference_length_line,
        "water_depth_input": water_depth[0],
        "water_depth_source_line": water_depth_line,
    }


def _echo_reference_source(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"source_file": _relative_path(path), "exists": False}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    marker = next((index for index, line in enumerate(lines) if "rotation center" in line.lower()), None)
    return {
        "source_file": _relative_path(path),
        "source_sha256": _sha256(path),
        "exists": True,
        "echo_start_line": marker + 1 if marker is not None else None,
        "echo_text": lines[marker : marker + 3] if marker is not None else [],
    }


def platform_properties(case_dir: Path, config: dict[str, Any], hydro: dict[str, Any], control: dict[str, Any]) -> dict[str, Any]:
    platform = config["platform"]
    length = float(platform["length_m"])
    beam = float(platform["beam_m"])
    draft = float(platform["draft_m"])
    volume = length * beam * draft
    waterplane_area = length * beam
    restoring = hydro["hydrostatic_restoring_matrix"]
    cg = hydro["center_of_gravity_m"]
    reference_point = control["reference_point_m"]
    mass = hydro["mass_kg"]
    linear_damping = hydro["linear_damping_matrix"]
    return {
        "mass_kg": mass,
        "mass_source": "Input/Hydrostatic.in Body Mass Matrix [1,1]",
        "cg_m": cg,
        "cg_source": "Input/Hydrostatic.in Center of Gravity",
        "inertia_about_cg_kg_m2": hydro["inertia_about_cg_kg_m2"],
        "inertia_source": "Input/Hydrostatic.in Body Mass Matrix shifted from its reference point using the parsed CG",
        "K_hydrostatic_matrix": restoring,
        "K33_N_m": restoring[2][2],
        "K44_Nm_rad": restoring[3][3],
        "K55_Nm_rad": restoring[4][4],
        "K_source": "Input/Hydrostatic.in Hydrostatic Restoring Matrix",
        "C_ext_linear_damping_matrix": linear_damping,
        "C_ext_source": "Input/Hydrostatic.in External Linear Damping Matrix; all entries are zero in the existing case",
        "C_ext_quadratic_damping_matrix": hydro["quadratic_damping_matrix"],
        "K_ext_matrix": hydro["external_restoring_matrix"],
        "reference_point_m": reference_point,
        "reference_point_sources": {
            "platform_config": {
                "source_file": _relative_path(case_dir / "platform_config.json"),
                "field": "reference_point_m",
                "value": config["reference_point_m"],
            },
            "control_file": {
                "source_file": control["source_file"],
                "field": "Reference_body_center",
                "source_line": control["reference_point_source_line"],
                "value": reference_point,
            },
            "hams_error_echo": _echo_reference_source(case_dir / "Output" / "ErrorCheck.txt"),
            "existing_hydrostar_header": {
                "source_file": _relative_path(case_dir / "Output" / "Hydrostar_format" / "AddedMass_11.rao"),
                "field": "Reference point of body 1",
            },
        },
        "geometry_derived_checks": {
            "displacement_volume_m3": volume,
            "waterplane_area_m2": waterplane_area,
            "mass_from_rho_times_volume_kg": float(platform["rho_kg_m3"]) * volume,
            "mass_relative_difference": abs(mass - float(platform["rho_kg_m3"]) * volume) / max(abs(mass), 1.0),
            "rho_kg_m3": float(platform["rho_kg_m3"]),
            "gravity_m_s2": float(platform["gravity_m_s2"]),
        },
        "nomenclature": {
            "K_hydrostatic": "HAMS Hydrostatic Restoring Matrix, reported as K33/K44/K55",
            "C_ext": "HAMS External Linear Damping Matrix; this existing case supplies a zero 6x6 matrix",
            "radiation_damping": "Frequency-dependent HAMS WaveDamping output, not the zero external C_ext matrix",
        },
    }


def _write_explicit_control(
    path: Path,
    config: dict[str, Any],
    frequencies: list[float],
    headings: list[float],
    reference_point: list[float],
    threads: int,
) -> None:
    platform = config["platform"]
    x_ref, y_ref, z_ref = reference_point
    lines = [
        "   --------------HAMS Control file---------------",
        "   ",
        f"   Waterdepth  {fortran_float(float(platform['water_depth_m']))}",
        "",
        "   #Start Definition of Wave Frequencies",
        "    0_inf_frequency_limits      0                             # 0: not to include; 1: to include",
        "    Input_frequency_type        3",
        "    Output_frequency_type       3",
        f"    Number_of_frequencies      {len(frequencies)}",
        "    " + " ".join(fortran_float(value) for value in frequencies),
        "   #End Definition of Wave Frequencies",
        "",
        "   #Start Definition of Wave Headings",
        f"    Number_of_headings         {len(headings)}",
        "   " + " ".join(f"{heading:.6f}" for heading in headings),
        "   #End Definition of Wave Headings",
        "",
        f"    Reference_body_center       {x_ref:.3f}       {y_ref:.3f}       {z_ref:.3f}",
        f"    Reference_body_length   {float(platform['length_m']):.6E}".replace("E", "D"),
        "    Wave_diffrac_solution    2",
        "    If_remove_irr_freq       1",
        f"    Number of threads       {threads}",
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


def _mesh_for_level(config: dict[str, Any], level: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if level not in MESH_LEVELS:
        raise ValueError(f"Unknown mesh level: {level}")
    level_spec = MESH_LEVELS[level]
    mesh_config = copy.deepcopy(config)
    mesh_config["mesh"] = {key: int(level_spec[key]) for key in ("nx", "ny", "nz")}
    hull_nodes, hull_panels, water_nodes, water_panels = build_barge_mesh(mesh_config)
    expected_hull = (
        mesh_config["mesh"]["nx"] * mesh_config["mesh"]["ny"]
        + 2 * mesh_config["mesh"]["nx"] * mesh_config["mesh"]["nz"]
        + 2 * mesh_config["mesh"]["ny"] * mesh_config["mesh"]["nz"]
    )
    return mesh_config, {
        "hull_nodes": hull_nodes,
        "hull_panels": hull_panels,
        "water_nodes": water_nodes,
        "water_panels": water_panels,
        "hull_panel_count": len(hull_panels),
        "waterplane_panel_count": len(water_panels),
        "expected_hull_panel_count": expected_hull,
    }


def _prepare_work_case(
    work_dir: Path,
    case_dir: Path,
    config: dict[str, Any],
    level: str,
    frequencies: list[float],
    headings: list[float],
    threads: int,
) -> dict[str, Any]:
    for relative in ("Input", "Output", "Output/Hams_format", "Output/Hydrostar_format", "Output/Wamit_format"):
        (work_dir / relative).mkdir(parents=True, exist_ok=True)
    mesh_config, mesh = _mesh_for_level(config, level)
    write_pnl(work_dir / "Input" / "HullMesh.pnl", "Hull Mesh File", mesh["hull_nodes"], mesh["hull_panels"])
    write_pnl(work_dir / "Input" / "WaterplaneMesh.pnl", "Waterplane Mesh File", mesh["water_nodes"], mesh["water_panels"])
    source_hydrostatic = case_dir / "Input" / "Hydrostatic.in"
    source_control = case_dir / "Input" / "ControlFile.in"
    (work_dir / "Input" / "Hydrostatic.in").write_bytes(source_hydrostatic.read_bytes())
    control = parse_control_input(source_control)
    _write_explicit_control(
        work_dir / "Input" / "ControlFile.in",
        mesh_config,
        frequencies,
        headings,
        [float(value) for value in control["reference_point_m"]],
        threads,
    )
    return {
        "mesh": {
            "nx": mesh_config["mesh"]["nx"],
            "ny": mesh_config["mesh"]["ny"],
            "nz": mesh_config["mesh"]["nz"],
            "hull_panels": mesh["hull_panel_count"],
            "waterplane_panels": mesh["waterplane_panel_count"],
            "hull_nodes": len(mesh["hull_nodes"]),
            "waterplane_nodes": len(mesh["water_nodes"]),
        },
        "source_files": {
            "hydrostatic": _relative_path(source_hydrostatic),
            "control": _relative_path(source_control),
            "generator": _relative_path(ROOT / "analysis" / "rocket_recovery" / "generate_barge_case.py"),
        },
    }


def _output_path(output_dir: Path, kind: str, row: int, column: int) -> Path:
    return output_dir / "Hydrostar_format" / f"{kind}_{row}{column}.rao"


def parse_radiation_outputs(output_dir: Path) -> dict[str, Any]:
    """Parse all 36 HAMS A and B files and retain their frequency matrices."""
    added: dict[tuple[float, tuple[int, int]], float] = {}
    damping: dict[tuple[float, tuple[int, int]], float] = {}
    frequencies: list[float] = []
    headings: list[float] = []
    max_heading_spread = {"added_mass_kg": 0.0, "radiation_damping_kg_s": 0.0}

    for row in range(1, 7):
        for column in range(1, 7):
            for kind, target in (("AddedMass", added), ("WaveDamping", damping)):
                path = _output_path(output_dir, kind, row, column)
                parsed = parse_hydrostar_rao(path)
                if not headings:
                    headings = parsed["headings"]
                if parsed["headings"] != headings:
                    raise ValueError(f"Heading mismatch in {path}")
                for record in parsed["rows"]:
                    frequency = float(record["frequency"])
                    if frequency not in frequencies:
                        frequencies.append(frequency)
                    amplitudes = [float(value) for value in record["amplitudes"]]
                    spread = max(amplitudes) - min(amplitudes) if amplitudes else 0.0
                    spread_key = "added_mass_kg" if kind == "AddedMass" else "radiation_damping_kg_s"
                    max_heading_spread[spread_key] = max(max_heading_spread[spread_key], abs(spread))
                    target[(frequency, (row - 1, column - 1))] = amplitudes[0]

    frequencies = sorted(frequencies)
    if not frequencies:
        raise ValueError(f"No radiation rows found under {output_dir}")
    rows: list[dict[str, Any]] = []
    for frequency in frequencies:
        a_matrix = [[added[(frequency, (row, column))] for column in range(6)] for row in range(6)]
        b_matrix = [[damping[(frequency, (row, column))] for column in range(6)] for row in range(6)]
        rows.append(
            {
                "frequency_rad_s": frequency,
                "added_mass_kg": a_matrix,
                "radiation_damping_kg_s": b_matrix,
            }
        )
    return {
        "frequencies_rad_s": frequencies,
        "headings_deg": headings,
        "heading_invariance_max_spread": max_heading_spread,
        "rows": rows,
    }


def parse_motion_outputs(output_dir: Path) -> dict[str, Any]:
    """Parse heave, roll and pitch RAOs on every solved heading/frequency."""

    dof_files = {"heave": 3, "roll": 4, "pitch": 5}
    headings: list[float] | None = None
    frequency_rows: dict[float, dict[str, list[float]]] = {}
    for name, dof in dof_files.items():
        parsed = parse_hydrostar_rao(output_dir / "Hydrostar_format" / f"Motion_{dof}.rao")
        if headings is None:
            headings = [float(value) for value in parsed["headings"]]
        elif not np.allclose(headings, parsed["headings"], atol=1.0e-9, rtol=0.0):
            raise ValueError(f"Motion heading mismatch in Motion_{dof}.rao")
        for row in parsed["rows"]:
            frequency = float(row["frequency"])
            frequency_rows.setdefault(frequency, {})[name] = [float(value) for value in row["amplitudes"]]
    if headings is None:
        raise ValueError(f"No motion RAO output under {output_dir}")
    rows = [
        {"frequency_rad_s": frequency, "amplitudes_by_heading": frequency_rows[frequency]}
        for frequency in sorted(frequency_rows)
    ]
    peaks: dict[str, dict[str, Any]] = {}
    for dof_name in dof_files:
        for heading_index, heading in enumerate(headings):
            candidates = [
                (float(row["amplitudes_by_heading"][dof_name][heading_index]), float(row["frequency_rad_s"]))
                for row in rows
            ]
            amplitude, frequency = max(candidates, key=lambda item: abs(item[0]))
            peaks[f"{dof_name}_{heading:g}deg"] = {
                "amplitude": amplitude,
                "frequency_rad_s": frequency,
                "sampled_peak_only": True,
            }
    return {"headings_deg": headings, "rows": rows, "sampled_peaks": peaks}


def _trapz(values: Any, x: Any, axis: int) -> Any:
    np_module = _require_numpy()
    function = getattr(np_module, "trapezoid", None)
    if function is None:  # pragma: no cover - compatibility with older NumPy
        function = np_module.trapz
    return function(values, x=x, axis=axis)


def radiation_analysis(parsed: dict[str, Any]) -> dict[str, Any]:
    np_module = _require_numpy()
    frequencies = np_module.asarray(parsed["frequencies_rad_s"], dtype=float)
    added = np_module.asarray([row["added_mass_kg"] for row in parsed["rows"]], dtype=float)
    damping = np_module.asarray([row["radiation_damping_kg_s"] for row in parsed["rows"]], dtype=float)
    finite = bool(np_module.isfinite(added).all() and np_module.isfinite(damping).all())
    added_symmetry = []
    damping_symmetry = []
    damping_min_eigenvalues = []
    negative_damping_count = 0
    for index in range(frequencies.size):
        added_scale = max(float(np_module.linalg.norm(added[index])), 1.0)
        damping_scale = max(float(np_module.linalg.norm(damping[index])), 1.0)
        added_symmetry.append(float(np_module.linalg.norm(added[index] - added[index].T) / added_scale))
        damping_symmetry.append(float(np_module.linalg.norm(damping[index] - damping[index].T) / damping_scale))
        eigenvalues = np_module.linalg.eigvalsh((damping[index] + damping[index].T) / 2.0)
        damping_min_eigenvalues.append(float(eigenvalues.min()))
        if eigenvalues.min() < -1.0e-8 * damping_scale:
            negative_damping_count += 1

    tail_count = min(5, len(frequencies))
    a_inf = added[-tail_count:].mean(axis=0)
    tail_range = np_module.ptp(added[-tail_count:], axis=0)
    a_inf_diagonal = {}
    a_inf_tail_relative_range = {}
    for index, label in DIAGONAL_LABELS.items():
        a_inf_diagonal[label] = float(a_inf[index, index])
        a_inf_tail_relative_range[label] = float(tail_range[index, index] / max(abs(a_inf[index, index]), 1.0))

    selected_indices = []
    for target in (0.2, 1.0, 2.0, 3.0, 4.0, 5.0):
        matches = np_module.where(np_module.isclose(frequencies, target, atol=5.0e-5))[0]
        if matches.size:
            selected_indices.append(int(matches[0]))
    impedance_diagonal: list[dict[str, Any]] = []
    for index in selected_indices:
        row = {"frequency_rad_s": float(frequencies[index]), "diagonal": {}}
        for dof_index, label in DIAGONAL_LABELS.items():
            row["diagonal"][label] = {
                "real_B_kg_s": float(damping[index, dof_index, dof_index]),
                "imag_omega_A_kg_s": float(frequencies[index] * added[index, dof_index, dof_index]),
            }
        impedance_diagonal.append(row)

    irf: dict[str, Any]
    if len(frequencies) >= 3:
        omega_with_zero = np_module.concatenate(([0.0], frequencies))
        damping_with_zero = np_module.concatenate((np_module.zeros((1, 6, 6)), damping), axis=0)
        time = np_module.arange(0.0, 240.0 + 0.125, 0.25)
        cosine = np_module.cos(omega_with_zero[:, None] * time[None, :])
        kernel = (2.0 / math.pi) * _trapz(damping_with_zero[:, :, :, None] * cosine[:, None, None, :], omega_with_zero, axis=0)
        reconstructed = np_module.empty_like(damping)
        for index, frequency in enumerate(frequencies):
            reconstructed[index] = _trapz(kernel * np_module.cos(frequency * time)[None, None, :], time, axis=2)
        interior = (frequencies >= frequencies[0] + 0.05) & (frequencies <= frequencies[-1] - 0.25)
        if interior.any():
            residual = reconstructed[interior] - damping[interior]
            relative_rms = float(np_module.linalg.norm(residual) / max(float(np_module.linalg.norm(damping[interior])), 1.0))
            relative_rms_diagonal = {
                label: float(
                    np_module.linalg.norm(residual[:, index, index])
                    / max(float(np_module.linalg.norm(damping[interior, index, index])), 1.0)
                )
                for index, label in DIAGONAL_LABELS.items()
            }
        else:
            relative_rms = None
            relative_rms_diagonal = {}
        tail_start = max(int(time.size * 0.8), 0)
        irf = {
            "formula": "K(t) = 2/pi * integral_0^omega_max B(omega) cos(omega*t) d omega; B_reconstructed(omega) = integral_0^T K(t) cos(omega*t) dt",
            "time_end_s": float(time[-1]),
            "time_step_s": float(time[1] - time[0]),
            "frequency_cutoff_rad_s": float(frequencies[-1]),
            "zero_frequency_B_assumption": "B(0)=0 for the finite-band reconstruction; HAMS input starts at 0.2 rad/s",
            "kernel_units": "kg/s^2",
            "kernel_finite": bool(np_module.isfinite(kernel).all()),
            "kernel_peak_abs_by_diagonal": {
                label: float(np_module.max(np_module.abs(kernel[index, index]))) for index, label in DIAGONAL_LABELS.items()
            },
            "kernel_tail_rms_by_diagonal": {
                label: float(np_module.sqrt(np_module.mean(kernel[index, index, tail_start:] ** 2)))
                for index, label in DIAGONAL_LABELS.items()
            },
            "roundtrip_relative_rms_all_matrix_interior": relative_rms,
            "roundtrip_relative_rms_by_diagonal_interior": relative_rms_diagonal,
            "roundtrip_scope": "finite-band diagnostic; it is not an infinite-frequency IRF validation",
        }
    else:
        irf = {"status": "not_enough_frequencies", "minimum_frequency_count": 3}

    return {
        "radiation_impedance_convention": "Z_rad(omega) = B(omega) + i*omega*A(omega); reported diagonal real/imaginary parts use HAMS A and B units",
        "finite_values": finite,
        "max_added_mass_relative_asymmetry": max(added_symmetry),
        "max_radiation_damping_relative_asymmetry": max(damping_symmetry),
        "minimum_radiation_damping_eigenvalue_kg_s": min(damping_min_eigenvalues),
        "negative_damping_frequency_count": negative_damping_count,
        "A_inf_estimate_method": f"mean of the last {tail_count} available A(omega) samples; finite-cutoff estimate only",
        "A_inf_cutoff_rad_s": float(frequencies[-1]),
        "A_inf_diagonal_kg": a_inf_diagonal,
        "A_inf_tail_relative_range": a_inf_tail_relative_range,
        "impedance_diagonal": impedance_diagonal,
        "irf_reconstruction": irf,
    }


def _run_command(executable: Path) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline([str(executable)])
    return shlex.join([str(executable)])


def run_hams_job(
    case_dir: Path,
    config: dict[str, Any],
    job: dict[str, str],
    hams_exe: Path,
    runtime_bin: Path | None,
    work_root: Path,
    timeout_s: float,
    headings: list[float],
    threads: int,
) -> dict[str, Any]:
    frequencies = frequency_grid(job["frequency_grid"])
    work_dir = work_root / f"{case_dir.name}-{job['id']}-{uuid.uuid4().hex[:10]}"
    prepared = _prepare_work_case(work_dir, case_dir, config, job["level"], frequencies, headings, threads)
    environment = os.environ.copy()
    if runtime_bin is not None:
        environment["PATH"] = str(runtime_bin) + os.pathsep + environment.get("PATH", "")
    command = _run_command(hams_exe)
    started = datetime.now(timezone.utc)
    status = "failed"
    exit_code: int | None = None
    stdout = ""
    stderr = ""
    error: str | None = None
    try:
        completed = subprocess.run(
            [str(hams_exe)],
            cwd=work_dir,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        status = "solver_completed" if exit_code == 0 else "solver_failed"
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        error = f"HAMS exceeded timeout {timeout_s:g} s"
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
    except OSError as exc:
        status = "launch_failed"
        error = str(exc)
    finished = datetime.now(timezone.utc)
    (work_dir / "hams.stdout.txt").write_text(stdout, encoding="utf-8", errors="replace")
    (work_dir / "hams.stderr.txt").write_text(stderr, encoding="utf-8", errors="replace")

    result: dict[str, Any] = {
        "id": job["id"],
        "level": job["level"],
        "purpose": job["purpose"],
        "frequency_grid": job["frequency_grid"],
        "requested_frequencies_rad_s": frequencies,
        "requested_frequency_count": len(frequencies),
        "command": command,
        "hams_executable": str(hams_exe.resolve()),
        "work_directory": str(work_dir.resolve()),
        "started_utc": started.isoformat(),
        "finished_utc": finished.isoformat(),
        "elapsed_s": (finished - started).total_seconds(),
        "solver_exit_code": exit_code,
        "status": status,
        "error": error,
        "stdout_tail": stdout[-4000:],
        "stderr_tail": stderr[-4000:],
        **prepared,
    }
    if status == "solver_completed":
        try:
            parsed = parse_radiation_outputs(work_dir / "Output")
            result["actual_frequencies_rad_s"] = parsed["frequencies_rad_s"]
            result["missing_requested_frequencies_rad_s"] = [
                value for value in frequencies if not any(abs(value - actual) <= 5.0e-5 for actual in parsed["frequencies_rad_s"])
            ]
            result["hydrodynamics"] = parsed["rows"]
            result["output_metadata"] = {
                "headings_deg": parsed["headings_deg"],
                "heading_invariance_max_spread": parsed["heading_invariance_max_spread"],
            }
            result["radiation_checks"] = radiation_analysis(parsed)
            result["motion_rao"] = parse_motion_outputs(work_dir / "Output")
        except (OSError, KeyError, ValueError, RuntimeError) as exc:
            result["status"] = "output_parse_failed"
            result["error"] = str(exc)
    return result


def _not_run_job(case_dir: Path, config: dict[str, Any], job: dict[str, str]) -> dict[str, Any]:
    _mesh_config, mesh = _mesh_for_level(config, job["level"])
    return {
        "id": job["id"],
        "level": job["level"],
        "purpose": job["purpose"],
        "frequency_grid": job["frequency_grid"],
        "requested_frequencies_rad_s": frequency_grid(job["frequency_grid"]),
        "requested_frequency_count": len(frequency_grid(job["frequency_grid"])),
        "status": "not_run",
        "mesh": {
            "hull_panels": mesh["hull_panel_count"],
            "waterplane_panels": mesh["waterplane_panel_count"],
            "hull_nodes": len(mesh["hull_nodes"]),
            "waterplane_nodes": len(mesh["water_nodes"]),
        },
    }


def _frequency_index(run: dict[str, Any]) -> dict[float, dict[str, Any]]:
    return {round(float(row["frequency_rad_s"]), 4): row for row in run.get("hydrodynamics", [])}


def _norm_relative(first: list[list[float]], second: list[list[float]]) -> float:
    np_module = _require_numpy()
    a = np_module.asarray(first, dtype=float)
    b = np_module.asarray(second, dtype=float)
    return float(np_module.linalg.norm(a - b) / max(float(np_module.linalg.norm(a)), float(np_module.linalg.norm(b)), 1.0))


def convergence_comparisons(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    completed = {run["level"]: run for run in runs if run.get("status") == "solver_completed" and run.get("hydrodynamics")}
    pairs = (("coarse", "medium"), ("medium", "fine"), ("coarse", "fine"))
    comparisons = []
    for coarser, finer in pairs:
        if coarser not in completed or finer not in completed:
            comparisons.append(
                {
                    "coarser": coarser,
                    "finer": finer,
                    "status": "incomplete",
                    "reason": "both mesh levels must have solver_completed radiation output",
                }
            )
            continue
        coarse_rows = _frequency_index(completed[coarser])
        fine_rows = _frequency_index(completed[finer])
        coarse_motion = {
            round(float(row["frequency_rad_s"]), 4): row
            for row in completed[coarser].get("motion_rao", {}).get("rows", [])
        }
        fine_motion = {
            round(float(row["frequency_rad_s"]), 4): row
            for row in completed[finer].get("motion_rao", {}).get("rows", [])
        }
        coarse_headings = [float(value) for value in completed[coarser].get("motion_rao", {}).get("headings_deg", [])]
        fine_headings = [float(value) for value in completed[finer].get("motion_rao", {}).get("headings_deg", [])]
        common_headings = [
            heading for heading in coarse_headings if any(abs(heading - other) <= 1.0e-9 for other in fine_headings)
        ]
        common = sorted(set(coarse_rows) & set(fine_rows))
        per_frequency = []
        for frequency in common:
            coarse_row = coarse_rows[frequency]
            fine_row = fine_rows[frequency]
            metrics: dict[str, float] = {}
            for matrix_name, short_name in (("added_mass_kg", "A"), ("radiation_damping_kg_s", "B")):
                metrics[f"{short_name}_matrix_relative_frobenius"] = _norm_relative(
                    coarse_row[matrix_name], fine_row[matrix_name]
                )
                for index, label in DIAGONAL_LABELS.items():
                    coarse_value = float(coarse_row[matrix_name][index][index])
                    fine_value = float(fine_row[matrix_name][index][index])
                    metrics[f"{short_name}_{label}_relative"] = abs(fine_value - coarse_value) / max(abs(fine_value), abs(coarse_value), 1.0)
            if frequency in coarse_motion and frequency in fine_motion:
                for heading in common_headings:
                    coarse_heading_index = min(range(len(coarse_headings)), key=lambda index: abs(coarse_headings[index] - heading))
                    fine_heading_index = min(range(len(fine_headings)), key=lambda index: abs(fine_headings[index] - heading))
                    for dof_name in ("heave", "roll", "pitch"):
                        coarse_value = float(coarse_motion[frequency]["amplitudes_by_heading"][dof_name][coarse_heading_index])
                        fine_value = float(fine_motion[frequency]["amplitudes_by_heading"][dof_name][fine_heading_index])
                        metrics[f"RAO_{dof_name}_{heading:g}deg_relative"] = abs(fine_value - coarse_value) / max(
                            abs(fine_value), abs(coarse_value), 1.0e-12
                        )
            per_frequency.append({"frequency_rad_s": frequency, **metrics})
        max_metric = max(
            (row["A_matrix_relative_frobenius"] for row in per_frequency),
            default=None,
        )
        max_all = max(
            (
                max(value for key, value in row.items() if key != "frequency_rad_s")
                for row in per_frequency
            ),
            default=None,
        )
        comparisons.append(
            {
                "coarser": coarser,
                "finer": finer,
                "status": "computed",
                "common_frequency_count": len(common),
                "comparison_definition": "fine minus coarse, normalized by max(abs(fine), abs(coarse), 1) for scalar entries and by the larger matrix Frobenius norm for full matrices",
                "maximum_A_matrix_relative_frobenius": max_metric,
                "maximum_all_reported_relative_metrics": max_all,
                "sampled_peak_comparison": {
                    key: {
                        "coarse_amplitude": completed[coarser]["motion_rao"]["sampled_peaks"][key]["amplitude"],
                        "fine_amplitude": completed[finer]["motion_rao"]["sampled_peaks"][key]["amplitude"],
                        "relative_amplitude_change": abs(
                            float(completed[finer]["motion_rao"]["sampled_peaks"][key]["amplitude"])
                            - float(completed[coarser]["motion_rao"]["sampled_peaks"][key]["amplitude"])
                        )
                        / max(
                            abs(float(completed[finer]["motion_rao"]["sampled_peaks"][key]["amplitude"])),
                            abs(float(completed[coarser]["motion_rao"]["sampled_peaks"][key]["amplitude"])),
                            1.0e-12,
                        ),
                        "coarse_frequency_rad_s": completed[coarser]["motion_rao"]["sampled_peaks"][key]["frequency_rad_s"],
                        "fine_frequency_rad_s": completed[finer]["motion_rao"]["sampled_peaks"][key]["frequency_rad_s"],
                    }
                    for key in sorted(
                        set(completed[coarser].get("motion_rao", {}).get("sampled_peaks", {}))
                        & set(completed[finer].get("motion_rao", {}).get("sampled_peaks", {}))
                    )
                },
                "per_frequency": per_frequency,
            }
        )
    return comparisons


def convergence_acceptance(runs: list[dict[str, Any]], comparisons: list[dict[str, Any]]) -> dict[str, Any]:
    required_pairs = {("coarse", "medium"), ("medium", "fine")}
    indexed = {(row["coarser"], row["finer"]): row for row in comparisons}
    selected_keys = {
        "A_33_relative",
        "A_44_relative",
        "A_55_relative",
        "B_33_relative",
        "B_44_relative",
        "B_55_relative",
        "RAO_heave_0deg_relative",
        "RAO_pitch_0deg_relative",
        "RAO_heave_90deg_relative",
        "RAO_roll_90deg_relative",
    }
    pair_checks = []
    for pair in sorted(required_pairs):
        comparison = indexed.get(pair)
        values = []
        if comparison and comparison.get("status") == "computed":
            for row in comparison.get("per_frequency", []):
                if any(abs(float(row["frequency_rad_s"]) - target) <= 5.0e-5 for target in (0.6, 0.8, 1.0)):
                    values.extend(float(value) for key, value in row.items() if key in selected_keys)
        maximum = max(values) if values else None
        pair_checks.append(
            {
                "coarser": pair[0],
                "finer": pair[1],
                "selected_metric_count": len(values),
                "maximum_selected_relative_change": maximum,
                "pass_5_percent": bool(maximum is not None and maximum <= 0.05),
            }
        )
    all_jobs_completed = bool(runs) and all(run.get("status") == "solver_completed" for run in runs)
    return {
        "status": "PASS" if all_jobs_completed and all(row["pass_5_percent"] for row in pair_checks) else "FAIL",
        "all_jobs_completed": all_jobs_completed,
        "criterion": "At 0.6, 0.8 and 1.0 rad/s, selected heave/roll/pitch A, B and non-symmetry RAO entries must change by no more than 5% for coarse-to-medium and medium-to-fine refinement.",
        "pair_checks": pair_checks,
        "note": "A failed criterion is retained as a numerical limitation; no result is promoted to mesh-converged by narrative judgement.",
    }


def _source_manifest(case_dir: Path) -> dict[str, Any]:
    paths = [
        ROOT / "analysis" / "rocket_recovery" / "generate_barge_case.py",
        case_dir / "platform_config.json",
        case_dir / "Input" / "Hydrostatic.in",
        case_dir / "Input" / "ControlFile.in",
        case_dir / "Input" / "HullMesh.pnl",
        case_dir / "Input" / "WaterplaneMesh.pnl",
        case_dir / "Output" / "ErrorCheck.txt",
    ]
    manifest = {}
    for path in paths:
        entry: dict[str, Any] = {"path": _relative_path(path), "exists": path.exists()}
        if path.exists():
            entry["sha256"] = _sha256(path)
            entry["bytes"] = path.stat().st_size
        manifest[path.name if path.parent.name != "Input" else f"Input/{path.name}"] = entry
    return manifest


def build_report(
    case_dir: Path,
    execute: bool,
    hams_exe: Path | None = None,
    runtime_bin: Path | None = None,
    work_root: Path | None = None,
    timeout_s: float = 3600.0,
    selected_jobs: Iterable[str] | None = None,
    headings: list[float] | None = None,
    threads: int = 16,
    merge_existing_report: Path | None = None,
) -> dict[str, Any]:
    config = read_json(case_dir / "platform_config.json")
    hydro = parse_hydrostatic_input(case_dir / "Input" / "Hydrostatic.in")
    control = parse_control_input(case_dir / "Input" / "ControlFile.in")
    properties = platform_properties(case_dir, config, hydro, control)
    requested = set(selected_jobs or (job["id"] for job in RUN_PLAN))
    unknown = requested - {job["id"] for job in RUN_PLAN}
    if unknown:
        raise ValueError(f"Unknown job ids: {sorted(unknown)}")
    selected_plan = [job for job in RUN_PLAN if job["id"] in requested]
    run_root = (work_root or Path(os.environ.get("TEMP", ".")) / "hams-barge-convergence").resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    actual_headings = headings or [0.0]
    new_runs: list[dict[str, Any]] = []
    for job in selected_plan:
        if execute:
            if hams_exe is None:
                raise ValueError("hams_exe is required when execute=True")
            new_runs.append(
                run_hams_job(
                    case_dir,
                    config,
                    job,
                    hams_exe.resolve(),
                    runtime_bin.resolve() if runtime_bin else None,
                    run_root,
                    timeout_s,
                    actual_headings,
                    threads,
                )
            )
        else:
            new_runs.append(_not_run_job(case_dir, config, job))

    existing_by_id: dict[str, dict[str, Any]] = {}
    if merge_existing_report is not None and merge_existing_report.exists():
        existing = read_json(merge_existing_report)
        existing_by_id = {
            str(run["id"]): run
            for run in existing.get("runs", [])
            if run.get("status") == "solver_completed"
        }
    new_by_id = {str(run["id"]): run for run in new_runs}
    runs = [
        new_by_id.get(str(job["id"]), existing_by_id.get(str(job["id"]), _not_run_job(case_dir, config, job)))
        for job in RUN_PLAN
    ]

    complete_runs = [run for run in runs if run.get("status") == "solver_completed"]
    overall_status = "COMPLETED" if len(complete_runs) == len(runs) else "PARTIAL" if complete_runs else "NOT_RUN"
    comparisons = convergence_comparisons(runs)
    command = ["python", str((ROOT / "analysis" / "rocket_recovery" / "barge_hydrodynamic_convergence.py").relative_to(ROOT))]
    if execute:
        command.append("--execute")
    return {
        "case_id": config["case_id"],
        "status": overall_status,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "reproducibility": {
            "python": sys.version,
            "numpy": getattr(np, "__version__", None),
            "platform": platform.platform(),
            "source_manifest": _source_manifest(case_dir),
            "hams_executable": str(hams_exe.resolve()) if hams_exe else None,
            "hams_executable_sha256": _sha256(hams_exe) if hams_exe and hams_exe.exists() else None,
            "runtime_bin": str(runtime_bin.resolve()) if runtime_bin else None,
            "command": " ".join(command),
            "work_root": str(run_root),
            "timeout_s": timeout_s,
        },
        "source_data": {
            "generator": {
                "source_file": _relative_path(ROOT / "analysis" / "rocket_recovery" / "generate_barge_case.py"),
                "symbols": ["DEFAULT_CONFIG", "build_barge_mesh", "rigid_body_mass_matrix", "hydrostatic_restoring_matrix"],
            },
            "platform_config": config,
            "control_input": control,
            "hydrostatic_input": hydro,
            "platform_properties": properties,
        },
        "method": {
            "mesh_definition": "same rectangular closed hull and z=0 waterplane construction as generate_barge_case.build_barge_mesh",
            "mesh_levels": MESH_LEVELS,
            "frequency_grids": {name: frequency_grid(name) for name in ("local025_high025", "mesh_response_anchor")},
            "headings_deg": actual_headings,
            "hams_irregular_frequency_removal": "IRSP=1 with the generated WaterplaneMesh.pnl",
            "radiation_impedance": "Z_rad = B + i*omega*A",
            "irf": "finite-band cosine transform of B(omega), with B(0)=0 and a 240 s reconstruction window",
            "A_inf": "mean of the last five available A samples, explicitly marked as a finite-cutoff estimate",
            "mesh_convergence": "common-frequency comparison of raw HAMS A/B matrices; no Richardson extrapolation",
        },
        "run_plan": list(RUN_PLAN),
        "runs": runs,
        "mesh_convergence": comparisons,
        "acceptance": convergence_acceptance(runs, comparisons),
        "limitations": [
            "The existing platform mass is the value in Hydrostatic.in and equals rho times the rectangular displaced volume; it is a generated hydrostatic model, not a measured mass record.",
            "HAMS does not write an IRF directly; the reported IRF is reconstructed from the finite positive-frequency WaveDamping output.",
            "A_inf is not observable as a mathematical infinity from a 5 rad/s cutoff; the report gives a tail estimate and its last-five-sample range.",
            "A failed or timed-out HAMS job remains explicitly incomplete and contributes no fabricated hydrodynamic values to convergence comparisons.",
            "The fine mesh is evaluated only at 0.6, 0.8 and 1.0 rad/s for active-response convergence; the 4-5 rad/s finite-cutoff A_inf estimate is taken from the completed dense medium-mesh run and is not labelled fine-mesh converged.",
        ],
    }


def write_summary_csv(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "run_id",
        "mesh_level",
        "hull_panels",
        "waterplane_panels",
        "status",
        "frequency_rad_s",
        "A33_kg",
        "A44_kg",
        "A55_kg",
        "B33_kg_s",
        "B44_kg_s",
        "B55_kg_s",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for run in report["runs"]:
            mesh = run.get("mesh", {})
            rows = run.get("hydrodynamics", [])
            if not rows:
                writer.writerow(
                    {
                        "run_id": run["id"],
                        "mesh_level": run["level"],
                        "hull_panels": mesh.get("hull_panels"),
                        "waterplane_panels": mesh.get("waterplane_panels"),
                        "status": run["status"],
                    }
                )
                continue
            for row in rows:
                a = row["added_mass_kg"]
                b = row["radiation_damping_kg_s"]
                writer.writerow(
                    {
                        "run_id": run["id"],
                        "mesh_level": run["level"],
                        "hull_panels": mesh.get("hull_panels"),
                        "waterplane_panels": mesh.get("waterplane_panels"),
                        "status": run["status"],
                        "frequency_rad_s": row["frequency_rad_s"],
                        "A33_kg": a[2][2],
                        "A44_kg": a[3][3],
                        "A55_kg": a[4][4],
                        "B33_kg_s": b[2][2],
                        "B44_kg_s": b[3][3],
                        "B55_kg_s": b[4][4],
                    }
                )


def _default_executable() -> Path:
    candidates = (ROOT / "SourceCode" / "hams.exe", ROOT / "Bin" / "HAMS_x64.exe")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an auditable HAMS barge mesh/frequency convergence study.")
    parser.add_argument("--case", default="Barge_120x50", help="Case name under RocketRecoveryCases or an explicit case path.")
    parser.add_argument("--execute", action="store_true", help="Run HAMS jobs in temporary directories; without this flag only validate inputs and print the plan.")
    parser.add_argument("--hams-exe", default=None, help="HAMS executable; defaults to SourceCode/hams.exe, then Bin/HAMS_x64.exe.")
    parser.add_argument("--runtime-bin", default=None, help="Optional directory prepended to PATH for the HAMS runtime DLLs.")
    parser.add_argument("--work-root", default=None, help="Directory outside the case for temporary HAMS runs.")
    parser.add_argument("--timeout-s", type=float, default=3600.0)
    parser.add_argument("--job", action="append", dest="jobs", help="Run one job id; repeat to select multiple jobs.")
    parser.add_argument("--heading", action="append", type=float, dest="headings", help="Wave heading in degrees; repeat to request more than one.")
    parser.add_argument("--threads", type=int, default=16)
    parser.add_argument("--merge-existing", action="store_true", help="Retain completed unselected jobs from the existing output report.")
    parser.add_argument("--out", default=None, help="Main JSON output; defaults to validation/barge-hydrodynamic-convergence.json.")
    parser.add_argument("--csv-out", default=None, help="Summary CSV output; defaults to validation/barge-hydrodynamic-convergence.csv.")
    args = parser.parse_args()

    case_dir = resolve_case(args.case)
    hams_exe = Path(args.hams_exe).resolve() if args.hams_exe else _default_executable().resolve()
    runtime_bin = Path(args.runtime_bin).resolve() if args.runtime_bin else (ROOT / ".tools" / "msys64" / "mingw64" / "bin")
    if not runtime_bin.exists():
        runtime_bin = None
    json_path = Path(args.out) if args.out else case_dir / "validation" / "barge-hydrodynamic-convergence.json"
    csv_path = Path(args.csv_out) if args.csv_out else case_dir / "validation" / "barge-hydrodynamic-convergence.csv"
    report = build_report(
        case_dir,
        execute=args.execute,
        hams_exe=hams_exe,
        runtime_bin=runtime_bin,
        work_root=Path(args.work_root) if args.work_root else None,
        timeout_s=args.timeout_s,
        selected_jobs=args.jobs,
        headings=args.headings,
        threads=args.threads,
        merge_existing_report=json_path if args.merge_existing else None,
    )
    write_json(json_path, report)
    write_summary_csv(csv_path, report)
    print(f"Status: {report['status']}")
    print(f"JSON: {json_path}")
    print(f"CSV: {csv_path}")
    for run in report["runs"]:
        print(f"- {run['id']}: {run['status']} ({run.get('elapsed_s', 0.0):.1f} s)")


if __name__ == "__main__":
    main()
