from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .common import (
        G,
        ROCKET_CASES_DIR,
        hams_amp_phase_to_complex,
        numeric_tokens,
        parse_hydrostar_rao,
        parse_number,
        read_json,
        write_json,
    )
    from .integrated_recovery_model import DEFAULT_CONFIG as CURRENT_SMOOTH_CONFIG
    from .landing_leg_contact import LITERATURE_INPUTS, thies_footprint_radius_m
    from .sea_state_response import jonswap_spectrum
    from .wang_2023 import plume_load_n
except ImportError:
    from common import G, ROCKET_CASES_DIR, hams_amp_phase_to_complex, numeric_tokens, parse_hydrostar_rao, parse_number, read_json, write_json
    from integrated_recovery_model import DEFAULT_CONFIG as CURRENT_SMOOTH_CONFIG
    from landing_leg_contact import LITERATURE_INPUTS, thies_footprint_radius_m
    from sea_state_response import jonswap_spectrum
    from wang_2023 import plume_load_n


ROOT = Path(__file__).resolve().parents[2]
CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
BARGE_ROOT = ROCKET_CASES_DIR / "Barge_120x50"
WANG_ROOT = ROCKET_CASES_DIR / "Paper_WangZhi_2023"
WANG_CONFIG_PATH = WANG_ROOT / "platform_config.json"
WANG_RESPONSE_PATH = WANG_ROOT / "Output" / "RocketRecovery" / "wang-2023-response.json"
REPORT_PATH = CASE_ROOT / "chrono-revision-study-report.json"
RESPONSE_PATH = CASE_ROOT / "Output" / "RocketRecovery" / "chrono-revision-study-response.json"
ALGORITHM_CSV_PATH = CASE_ROOT / "Output" / "RocketRecovery" / "chrono-revision-study-algorithms.csv"
CONVERGENCE_CSV_PATH = CASE_ROOT / "Output" / "RocketRecovery" / "chrono-revision-study-convergence.csv"

DOF_NAMES_6 = ("surge_m", "sway_m", "heave_m", "roll_rad", "pitch_rad", "yaw_rad")
ACTIVE_DOF_INDICES = np.array([2, 3, 4], dtype=int)
ACTIVE_DOF_NAMES = ("heave_m", "roll_rad", "pitch_rad")


def default_study_config() -> dict[str, Any]:
    rocket = LITERATURE_INPUTS["thies_2022"]["rocket"]
    requirements = LITERATURE_INPUTS["thies_2022"]["requirements"]
    return {
        "case_id": "Chrono_LeggedRecovery_ChronoRevisionStudy",
        "platform": {
            "source_case": str(BARGE_ROOT),
            "length_m": 120.0,
            "beam_m": 50.0,
            "draft_m": 7.0,
            "operator_reference_m": [0.0, 0.0, 0.0],
            "deck_reference_z_m": 0.0,
        },
        "time_domain": {
            "start_s": 506.0,
            "end_s": 516.0,
            "touchdown_reference_s": 510.0,
            "platform_dt_s": 0.01,
            "contact_dt_s": 0.0005,
        },
        "wave": {
            "heading_deg": 90.0,
            "hs_m": 1.75,
            "tp_s": 4.5,
            "gamma": 3.0,
            "random_phase_seed": 2023,
            "force_order": "HAMS first-order Excitation RAOs only",
        },
        "plume": {
            "enabled": True,
            "application_x_m": 15.0,
            "application_y_m": 10.0,
            "source": str(WANG_CONFIG_PATH),
            "load_definition": "Wang 2023 plume_load_n waveform, including 506-510 s plateau approximation",
            "vehicle_platform_consistency": "pre_touchdown_only",
            "cutoff_time_s": 510.0,
        },
        "rocket": {
            "mass_kg": float(rocket["landing_mass_kg"]),
            "inertia_roll_kg_m2": float(rocket["inertia_kg_m2"]["roll_iyy"]),
            "inertia_pitch_kg_m2": float(rocket["inertia_kg_m2"]["pitch_ixx"]),
            "cog_from_base_m": float(rocket["cog_from_launcher_base_m"]),
            "touchdown_speed_m_s": float(requirements["touchdown_vertical_velocity_nominal_m_s"]),
            "gravity_m_s2": G,
            "pre_contact_gravity": "off_until_detected_first_geometric_contact",
        },
        "legs": {
            "count": 4,
            "azimuths_deg": [45.0, 135.0, 225.0, 315.0],
            "footprint_radius_m": thies_footprint_radius_m(),
            "contact_definition": "delta > 0, with delta = deck_z - foot_z",
        },
        "coupling": {
            "platform_grid": "fixed 0.01 s HAMS/Cummins operator grid",
            "contact_grid": "requested contact dt; platform q and qd linearly interpolated to it",
            "feedback_resampling": "conservative interval-average of fine contact wrench onto platform-grid Voronoi bins",
            "relaxation": 1.0,
            "iterative_max_passes": 8,
            "iterative_tolerance": 1.0e-4,
        },
    }


def make_time_grid(start_s: float, end_s: float, dt_s: float) -> np.ndarray:
    start = float(start_s)
    end = float(end_s)
    step = float(dt_s)
    if not (math.isfinite(start) and math.isfinite(end) and math.isfinite(step)) or step <= 0.0:
        raise ValueError("Time bounds must be finite and dt_s must be positive.")
    count_float = (end - start) / step
    count = int(round(count_float))
    if count < 0 or not math.isclose(count_float, count, rel_tol=1.0e-10, abs_tol=1.0e-12):
        raise ValueError(f"{end - start:g} s is not an integer multiple of dt={step:g} s.")
    return np.linspace(start, end, count + 1, dtype=float)


def integrate_series(time_s: np.ndarray, values: np.ndarray) -> float:
    time = np.asarray(time_s, dtype=float)
    array = np.asarray(values, dtype=float)
    if len(time) < 2:
        return 0.0
    if array.ndim == 1:
        return float(np.trapezoid(array, time))
    return float(np.trapezoid(array, time, axis=0))


def current_smooth_contact_parameters() -> dict[str, float]:
    """Read the parameters used by integrated_recovery_model.contact_forces."""
    legs = CURRENT_SMOOTH_CONFIG["legs"]
    return {
        "damper_stiffness_n_m": float(legs["damper_stiffness_n_m"]),
        "damper_damping_ns_m": float(legs["damper_damping_ns_m"]),
        "stroke_reference_m": float(legs["stroke_reference_m"]),
        "force_reference_n": float(legs["force_reference_n"]),
        "hard_stop_stiffness_n_m": float(legs["hard_stop_stiffness_n_m"]),
    }


def smooth_contact_components(
    delta_m: float | np.ndarray,
    delta_dot_m_s: float | np.ndarray,
    parameters: dict[str, float] | None = None,
    active: bool = True,
) -> dict[str, np.ndarray]:
    """Exact scalar/vector form of the current smooth contact force law.

    The implementation mirrors integrated_recovery_model.contact_forces:
    penetration is unilateral, the damping term is bounded by tanh, a hard
    stop is added only beyond stroke_reference, and the total is clamped to
    [0, 2*force_reference].  delta_dot is positive in compression.
    """
    p = parameters or current_smooth_contact_parameters()
    delta = np.asarray(delta_m, dtype=float)
    delta_dot = np.asarray(delta_dot_m_s, dtype=float)
    stroke = np.maximum(delta, 0.0) if active else np.zeros_like(delta)
    rate = np.where((stroke > 0.0) & active, delta_dot, 0.0)
    spring = float(p["damper_stiffness_n_m"]) * stroke
    damper = float(p["force_reference_n"]) * np.tanh(
        float(p["damper_damping_ns_m"]) * rate / max(float(p["force_reference_n"]), 1.0)
    )
    hard_stop = np.where(
        stroke > float(p["stroke_reference_m"]),
        float(p["force_reference_n"])
        * np.tanh(
            float(p["hard_stop_stiffness_n_m"])
            * (stroke - float(p["stroke_reference_m"]))
            / max(float(p["force_reference_n"]), 1.0)
        ),
        0.0,
    )
    raw_force = spring + damper + hard_stop
    force = np.maximum(0.0, np.minimum(2.0 * float(p["force_reference_n"]), raw_force))
    return {
        "stroke_m": stroke,
        "rate_m_s": rate,
        "spring_n": spring,
        "damper_n": damper,
        "hard_stop_n": hard_stop,
        "raw_force_n": raw_force,
        "force_n": force,
    }


def smooth_contact_potential_j(stroke_m: float | np.ndarray, parameters: dict[str, float] | None = None) -> np.ndarray:
    p = parameters or current_smooth_contact_parameters()
    stroke = np.maximum(np.asarray(stroke_m, dtype=float), 0.0)
    spring_energy = 0.5 * float(p["damper_stiffness_n_m"]) * stroke**2
    excess = np.maximum(stroke - float(p["stroke_reference_m"]), 0.0)
    hard_stop_energy = (
        float(p["force_reference_n"]) ** 2
        / float(p["hard_stop_stiffness_n_m"])
        * np.log(np.cosh(float(p["hard_stop_stiffness_n_m"]) * excess / float(p["force_reference_n"])))
    )
    return spring_energy + hard_stop_energy


def contact_force_audit() -> dict[str, Any]:
    p = current_smooth_contact_parameters()
    delta = 0.148
    target = 2.678e6
    linear_100 = 100.0e6 * delta
    spring_at_delta = p["damper_stiffness_n_m"] * delta
    force_at_zero_rate = float(smooth_contact_components(delta, 0.0, p)["force_n"])
    force_at_high_rate = float(smooth_contact_components(delta, 1.0e6, p)["force_n"])
    required_damper = target - spring_at_delta
    tanh_reachable = required_damper <= p["force_reference_n"]
    return {
        "source": {
            "module": "analysis/rocket_recovery/integrated_recovery_model.py",
            "function": "contact_forces",
            "formula_lines": "201-243 in the current worktree",
            "delta_definition": "max(deck_z - foot_z, 0) while active",
            "delta_dot_definition": "deck_vz - foot_vz; positive means compression",
        },
        "implemented_formula": "Fn=max(0,min(2*Fref,k*delta+Fref*tanh(c*deltadot/Fref)+I(delta>delta_ref)*Fref*tanh(k_stop*(delta-delta_ref)/Fref)))",
        "parameters": p,
        "chronosmc_parameter_that_is_not_used_by_this_formula": {
            "normal_stiffness_n_m": 1.0e8,
            "normal_damping_ns_m": 1.0e7,
            "source": "Chrono Stage-1 contact material config from Li 2025 values",
        },
        "review_triplet_check": {
            "delta_m": delta,
            "nominal_linear_stiffness_n_m": 1.0e8,
            "nominal_linear_force_n": linear_100,
            "nominal_linear_force_mn": linear_100 / 1.0e6,
            "reported_force_n": target,
            "reported_force_mn": target / 1.0e6,
            "force_ratio_reported_to_100mn_linear": target / linear_100,
            "implied_delta_at_100mn_per_m_m": target / 1.0e8,
            "implied_stiffness_at_delta_0p148_n_m": target / delta,
            "current_smooth_spring_force_at_delta_n": spring_at_delta,
            "current_smooth_force_at_delta_zero_rate_n": force_at_zero_rate,
            "current_smooth_force_at_delta_very_high_compression_rate_n": force_at_high_rate,
            "current_smooth_damper_force_required_to_reach_reported_n": required_damper,
            "reported_force_reachable_by_current_tanh_damper_at_delta": tanh_reachable,
            "conclusion": "100 MN/m * 0.148 m = 14.8 MN, so 2.678 MN is not self-consistent with that pure linear pair. The current smooth law is a different law and gives 0.3848 MN at zero rate; even its high-rate limit at this delta is below 2.678 MN.",
        },
    }


def read_hydrostatic_matrix(path: Path, marker: str) -> np.ndarray:
    lines = path.read_text(errors="replace").splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if marker in line) + 1
    except StopIteration as exc:
        raise ValueError(f"Missing hydrostatic section {marker!r} in {path}") from exc
    rows: list[list[float]] = []
    for line in lines[start:]:
        values = [parse_number(token) for token in numeric_tokens(line)]
        if len(values) >= 6:
            rows.append(values[:6])
        if len(rows) == 6:
            break
    if len(rows) != 6:
        raise ValueError(f"Could not read 6 rows for {marker!r} in {path}")
    return np.asarray(rows, dtype=float)


def extract_real_matrix_series(case_dir: Path, prefix: str) -> tuple[np.ndarray, np.ndarray]:
    omega_ref: np.ndarray | None = None
    matrices: list[np.ndarray] | None = None
    for row_index, i in enumerate(range(1, 7)):
        for column_index, j in enumerate(range(1, 7)):
            parsed = parse_hydrostar_rao(case_dir / "Output" / "Hydrostar_format" / f"{prefix}_{i}{j}.rao")
            omega = np.asarray([row["frequency"] for row in parsed["rows"]], dtype=float)
            values = np.asarray([row["amplitudes"][0] for row in parsed["rows"]], dtype=float)
            if omega_ref is None:
                omega_ref = omega
                matrices = [np.zeros((6, 6), dtype=float) for _ in omega]
            if not np.allclose(omega_ref, omega):
                values = np.interp(omega_ref, omega, values)
            assert matrices is not None
            for frequency_index, value in enumerate(values):
                matrices[frequency_index][row_index, column_index] = value
    if omega_ref is None or matrices is None:
        raise ValueError(f"No {prefix} HAMS matrix files found under {case_dir}")
    return omega_ref, np.stack([0.5 * (matrix + matrix.T) for matrix in matrices], axis=0)


def quadrature_weights(omega: np.ndarray) -> np.ndarray:
    if len(omega) == 1:
        return np.asarray([2.0 / math.pi], dtype=float)
    weights = np.zeros_like(omega, dtype=float)
    weights[0] = 0.5 * (omega[1] - omega[0])
    weights[-1] = 0.5 * (omega[-1] - omega[-2])
    weights[1:-1] = 0.5 * (omega[2:] - omega[:-2])
    return (2.0 / math.pi) * weights


def trapezoid_frequency_weights(omega: np.ndarray) -> np.ndarray:
    if len(omega) == 1:
        return np.ones(1, dtype=float)
    weights = np.zeros_like(omega, dtype=float)
    weights[0] = 0.5 * (omega[1] - omega[0])
    weights[-1] = 0.5 * (omega[-1] - omega[-2])
    weights[1:-1] = 0.5 * (omega[2:] - omega[:-2])
    return weights


def inverse_square_matrix_scaled(matrix: np.ndarray) -> np.ndarray:
    """Invert a small dense matrix without the external LAPACK runtime."""

    source = np.asarray(matrix, dtype=float)
    if source.ndim != 2 or source.shape[0] != source.shape[1]:
        raise ValueError("Expected a square matrix")
    size = source.shape[0]
    work = source.copy()
    inverse = np.eye(size, dtype=float)
    row_scale = np.max(np.abs(work), axis=1)
    if np.any(row_scale == 0.0):
        raise ValueError("Singular matrix with a zero row")
    for column in range(size):
        pivot_row = max(range(column, size), key=lambda row: abs(work[row, column]) / row_scale[row])
        pivot = float(work[pivot_row, column])
        if abs(pivot) <= np.finfo(float).eps * float(row_scale[pivot_row]) * size:
            raise ValueError("Singular matrix during scaled-pivot elimination")
        if pivot_row != column:
            work[[column, pivot_row], :] = work[[pivot_row, column], :]
            inverse[[column, pivot_row], :] = inverse[[pivot_row, column], :]
            row_scale[[column, pivot_row]] = row_scale[[pivot_row, column]]
        pivot = float(work[column, column])
        work[column, :] /= pivot
        inverse[column, :] /= pivot
        for row in range(size):
            if row == column:
                continue
            factor = float(work[row, column])
            work[row, :] -= factor * work[column, :]
            inverse[row, :] -= factor * inverse[column, :]
    residual = np.einsum("ij,jk->ik", source, inverse) - np.eye(size)
    if float(np.max(np.abs(residual))) > 1.0e-8:
        raise ValueError("Matrix inverse residual exceeds 1e-8")
    return inverse


def minimum_symmetric_eigenvalue_jacobi(matrix: np.ndarray) -> float:
    """Return the minimum eigenvalue of a small symmetric matrix using Jacobi rotations."""

    work = 0.5 * (np.asarray(matrix, dtype=float) + np.asarray(matrix, dtype=float).T)
    for _ in range(64):
        off = np.triu(np.abs(work), 1)
        flat = int(np.argmax(off))
        p, q = np.unravel_index(flat, off.shape)
        if off[p, q] <= 1.0e-12 * max(1.0, float(np.max(np.abs(np.diag(work))))):
            break
        angle = 0.5 * math.atan2(2.0 * work[p, q], work[q, q] - work[p, p])
        c = math.cos(angle)
        s = math.sin(angle)
        rotation = np.eye(work.shape[0])
        rotation[p, p] = c
        rotation[q, q] = c
        rotation[p, q] = s
        rotation[q, p] = -s
        work = np.einsum("ji,jk,kl->il", rotation, work, rotation)
    return float(np.min(np.diag(work)))


def extract_wave_excitation(case_dir: Path, omega: np.ndarray, heading_deg: float) -> tuple[np.ndarray, float]:
    complex_values = np.zeros((len(omega), 6), dtype=complex)
    selected_heading: float | None = None
    for dof_index, dof in enumerate(range(1, 7)):
        parsed = parse_hydrostar_rao(case_dir / "Output" / "Hydrostar_format" / f"Excitation_{dof}.rao")
        headings = np.asarray(parsed["headings"], dtype=float)
        heading_index = int(np.argmin(np.abs(headings - float(heading_deg))))
        if selected_heading is None:
            selected_heading = float(headings[heading_index])
        row_omega = np.asarray([row["frequency"] for row in parsed["rows"]], dtype=float)
        row_complex = np.asarray(
            [hams_amp_phase_to_complex(row["amplitudes"][heading_index], row["phases_deg"][heading_index]) for row in parsed["rows"]],
            dtype=complex,
        )
        complex_values[:, dof_index] = np.interp(omega, row_omega, row_complex.real) + 1j * np.interp(omega, row_omega, row_complex.imag)
    if selected_heading is None:
        raise ValueError("HAMS excitation heading table is empty.")
    return complex_values, selected_heading


@dataclass(frozen=True)
class PlatformOperator:
    case_dir: Path
    hydrodynamic_source_dir: Path
    geometry: dict[str, Any]
    dof_names: tuple[str, ...]
    active_indices: np.ndarray
    omega_rad_s: np.ndarray
    added_mass: np.ndarray
    radiation_damping: np.ndarray
    radiation_weights: np.ndarray
    rigid_mass: np.ndarray
    restoring: np.ndarray
    wave_excitation_complex: np.ndarray
    selected_heading_deg: float
    a_inf_matrix: np.ndarray
    a_inf_source: dict[str, Any]
    active_mass_inverse: np.ndarray

    @property
    def a_inf(self) -> np.ndarray:
        return self.a_inf_matrix

    @property
    def mass(self) -> np.ndarray:
        return self.rigid_mass + self.a_inf

    def active_matrix(self, matrix: np.ndarray) -> np.ndarray:
        return np.asarray(matrix)[np.ix_(self.active_indices, self.active_indices)]

    def active_radiation(self) -> np.ndarray:
        return np.asarray(self.radiation_damping)[:, self.active_indices][:, :, self.active_indices]

    def audit(self) -> dict[str, Any]:
        active_mass = self.active_matrix(self.mass)
        active_radiation = self.active_radiation()
        return {
            "case_dir": str(self.case_dir),
            "hydrodynamic_source_dir": str(self.hydrodynamic_source_dir),
            "geometry": self.geometry,
            "operator_dofs": list(self.dof_names),
            "active_dofs": [self.dof_names[index] for index in self.active_indices],
            "constrained_dofs": [self.dof_names[index] for index in range(6) if index not in set(self.active_indices.tolist())],
            "frequency_count": int(len(self.omega_rad_s)),
            "frequency_range_rad_s": [float(self.omega_rad_s[0]), float(self.omega_rad_s[-1])],
            "active_radiation_minimum_eigenvalue_kg_s": min(
                minimum_symmetric_eigenvalue_jacobi(matrix) for matrix in active_radiation
            ),
            "radiation_memory_band_policy": (
                "The 0.2-2.0 rad/s positive-semidefinite active radiation band is used in the memory kernel; "
                "the separately computed 4-5 rad/s tail is used only for the finite-cutoff A_inf estimate."
            ),
            "selected_wave_heading_deg": float(self.selected_heading_deg),
            "added_mass_infinite_definition": self.a_inf_source,
            "mass_matrix_full_6x6": self.mass.tolist(),
            "restoring_matrix_full_6x6": self.restoring.tolist(),
            "active_mass_matrix": self.active_matrix(self.mass).tolist(),
            "active_restoring_matrix": self.active_matrix(self.restoring).tolist(),
            "active_mass_min_eigenvalue": minimum_symmetric_eigenvalue_jacobi(active_mass),
            "active_mass_inverse_residual": float(
                np.max(
                    np.abs(
                        np.einsum("ij,jk->ik", active_mass, self.active_mass_inverse)
                        - np.eye(len(self.active_indices))
                    )
                )
            ),
            "horizontal_restoring_rows_are_zero": bool(np.allclose(self.restoring[np.ix_([0, 1, 5], range(6))], 0.0)),
            "external_linear_damping_from_hydrostatic_input": "zero matrix",
            "horizontal_dof_boundary": "surge, sway and yaw are held fixed because supplied HAMS Hydrostatic.in has no horizontal restoring or mooring stiffness; no artificial horizontal stiffness is inserted",
            "source_files": {
                "hydrostatic": str(self.case_dir / "Input" / "Hydrostatic.in"),
                "added_mass": str(self.hydrodynamic_source_dir / "Output" / "Hydrostar_format" / "AddedMass_11.rao"),
                "radiation_damping": str(self.hydrodynamic_source_dir / "Output" / "Hydrostar_format" / "WaveDamping_11.rao"),
                "wave_excitation": str(self.hydrodynamic_source_dir / "Output" / "Hydrostar_format" / "Excitation_3.rao"),
            },
            "hydrodynamic_grid_consistency": "A(omega), B(omega), wave excitation and the finite-cutoff A_inf estimate are selected from the same completed mesh level.",
        }


def load_finite_cutoff_a_inf(
    case_dir: Path,
    fallback: np.ndarray,
    fallback_omega: float,
) -> tuple[np.ndarray, dict[str, Any]]:
    report_path = case_dir / "validation" / "barge-hydrodynamic-convergence.json"
    fallback_source: dict[str, Any] = {
        "method": "single highest available HAMS added-mass matrix",
        "cutoff_rad_s": float(fallback_omega),
        "source": str(case_dir / "Output" / "Hydrostar_format" / "AddedMass_11.rao"),
        "status": "fallback_finite_cutoff_not_mathematical_infinity",
    }
    if not report_path.exists():
        return np.asarray(fallback, dtype=float), fallback_source
    try:
        report = read_json(report_path)
        candidates = []
        level_rank = {"coarse": 0, "medium": 1, "fine": 2}
        for run in report.get("runs", []):
            rows = run.get("hydrodynamics", [])
            if run.get("status") != "solver_completed" or len(rows) < 5:
                continue
            ordered = sorted(rows, key=lambda row: float(row["frequency_rad_s"]))
            cutoff = float(ordered[-1]["frequency_rad_s"])
            if cutoff < 4.999:
                continue
            dense_tail = sum(float(row["frequency_rad_s"]) >= 4.0 for row in ordered)
            candidates.append((dense_tail, level_rank.get(str(run.get("level")), -1), len(ordered), run, ordered))
        if not candidates:
            fallback_source["convergence_report"] = str(report_path)
            fallback_source["convergence_report_status"] = "no completed >=5 rad/s run with at least five frequencies"
            return np.asarray(fallback, dtype=float), fallback_source
        _dense_tail, _rank, _count, run, ordered = max(candidates, key=lambda item: item[:3])
        tail = ordered[-5:]
        matrices = np.asarray([row["added_mass_kg"] for row in tail], dtype=float)
        estimate = np.mean(matrices, axis=0)
        tail_range = np.ptp(matrices, axis=0)
        return estimate, {
            "method": "mean of the last five computed added-mass matrices",
            "status": "finite_cutoff_estimate_not_mathematical_infinity",
            "cutoff_rad_s": float(tail[-1]["frequency_rad_s"]),
            "tail_frequencies_rad_s": [float(row["frequency_rad_s"]) for row in tail],
            "mesh_level": run.get("level"),
            "hull_panels": run.get("mesh", {}).get("hull_panels"),
            "run_id": run.get("id"),
            "source": str(report_path),
            "diagonal_tail_relative_range": {
                DOF_NAMES_6[index]: float(tail_range[index, index] / max(abs(estimate[index, index]), 1.0))
                for index in range(6)
            },
        }
    except (KeyError, TypeError, ValueError, OSError) as exc:
        fallback_source["convergence_report"] = str(report_path)
        fallback_source["convergence_report_error"] = str(exc)
        return np.asarray(fallback, dtype=float), fallback_source


def load_platform_operator(config: dict[str, Any]) -> PlatformOperator:
    case_dir = Path(config["platform"]["source_case"])
    if not case_dir.is_absolute():
        case_dir = ROOT / case_dir
    hydrostatic_path = case_dir / "Input" / "Hydrostatic.in"
    rigid_mass = read_hydrostatic_matrix(hydrostatic_path, "Body Mass Matrix:")
    restoring = read_hydrostatic_matrix(hydrostatic_path, "Hydrostatic Restoring Matrix:")
    archived_medium = case_dir / "validation" / "hydrodynamic_runs" / "medium_local025_high5"
    required_medium_files = (
        archived_medium / "Output" / "Hydrostar_format" / "AddedMass_11.rao",
        archived_medium / "Output" / "Hydrostar_format" / "WaveDamping_11.rao",
        archived_medium / "Output" / "Hydrostar_format" / "Excitation_3.rao",
    )
    hydrodynamic_source_dir = archived_medium if all(path.exists() for path in required_medium_files) else case_dir
    full_omega, full_added = extract_real_matrix_series(hydrodynamic_source_dir, "AddedMass")
    radiation_omega, full_radiation = extract_real_matrix_series(hydrodynamic_source_dir, "WaveDamping")
    if not np.allclose(full_omega, radiation_omega):
        raise ValueError("Barge AddedMass and WaveDamping frequency grids differ.")
    memory_mask = full_omega <= 2.0 + 1.0e-12
    omega = full_omega[memory_mask]
    added = full_added[memory_mask]
    radiation = full_radiation[memory_mask]
    if len(omega) < 3:
        raise ValueError("The selected radiation-memory band has fewer than three frequencies.")
    active_minimum = min(
        minimum_symmetric_eigenvalue_jacobi(matrix[np.ix_(ACTIVE_DOF_INDICES, ACTIVE_DOF_INDICES)])
        for matrix in radiation
    )
    if active_minimum < -1.0e-6:
        raise ValueError(f"The selected active radiation-memory band is not positive semidefinite: {active_minimum:g}")
    wave_excitation, selected_heading = extract_wave_excitation(
        hydrodynamic_source_dir,
        omega,
        float(config["wave"]["heading_deg"]),
    )
    geometry = {
        key: config["platform"][key]
        for key in ["length_m", "beam_m", "draft_m", "operator_reference_m", "deck_reference_z_m"]
    }
    a_inf, a_inf_source = load_finite_cutoff_a_inf(case_dir, full_added[-1], float(full_omega[-1]))
    total_mass = rigid_mass + a_inf
    active_mass_inverse = inverse_square_matrix_scaled(total_mass[np.ix_(ACTIVE_DOF_INDICES, ACTIVE_DOF_INDICES)])
    return PlatformOperator(
        case_dir=case_dir,
        hydrodynamic_source_dir=hydrodynamic_source_dir,
        geometry=geometry,
        dof_names=DOF_NAMES_6,
        active_indices=ACTIVE_DOF_INDICES.copy(),
        omega_rad_s=omega,
        added_mass=added,
        radiation_damping=radiation,
        radiation_weights=quadrature_weights(omega),
        rigid_mass=rigid_mass,
        restoring=restoring,
        wave_excitation_complex=wave_excitation,
        selected_heading_deg=selected_heading,
        a_inf_matrix=a_inf,
        a_inf_source=a_inf_source,
        active_mass_inverse=active_mass_inverse,
    )


def build_wave_components(operator: PlatformOperator, config: dict[str, Any]) -> dict[str, Any]:
    wave = config["wave"]
    spectrum = np.asarray(
        jonswap_spectrum(
            operator.omega_rad_s.tolist(),
            float(wave["hs_m"]),
            float(wave["tp_s"]),
            float(wave["gamma"]),
        ),
        dtype=float,
    )
    weights = trapezoid_frequency_weights(operator.omega_rad_s)
    amplitudes = np.sqrt(np.maximum(2.0 * spectrum * weights, 0.0))
    rng = np.random.default_rng(int(wave["random_phase_seed"]))
    phases = rng.uniform(0.0, 2.0 * math.pi, size=len(operator.omega_rad_s))
    return {
        "enabled": True,
        "heading_deg": float(operator.selected_heading_deg),
        "spectrum_m2_s": spectrum,
        "quadrature_weights_s": weights,
        "amplitudes_m": amplitudes,
        "phases_rad": phases,
        "force_complex_n": operator.wave_excitation_complex * amplitudes[:, None],
    }


def wave_force_series(time_s: np.ndarray, start_s: float, operator: PlatformOperator, wave: dict[str, Any]) -> np.ndarray:
    phase = operator.omega_rad_s[None, :] * (np.asarray(time_s)[:, None] - float(start_s)) + np.asarray(wave["phases_rad"])[None, :]
    terms = np.asarray(wave["force_complex_n"])[None, :, :] * np.exp(1j * phase[:, :, None])
    full = np.real(np.sum(terms, axis=1))
    return full[:, operator.active_indices]


def wang_plume_force_6dof(time_s: np.ndarray, wang_config: dict[str, Any], config: dict[str, Any]) -> np.ndarray:
    times = np.asarray(time_s, dtype=float)
    out = np.zeros((len(times), 6), dtype=float)
    if not bool(config["plume"]["enabled"]):
        return out
    x = float(config["plume"]["application_x_m"])
    y = float(config["plume"]["application_y_m"])
    load = np.asarray([plume_load_n(float(t), wang_config) for t in times], dtype=float)
    if config["plume"].get("vehicle_platform_consistency") == "pre_touchdown_only":
        load = np.where(times < float(config["plume"]["cutoff_time_s"]), load, 0.0)
    force_z = -load
    out[:, 2] = force_z
    out[:, 3] = y * force_z
    out[:, 4] = -x * force_z
    return out


def platform_rhs(
    state: np.ndarray,
    external_force: np.ndarray,
    operator: PlatformOperator,
) -> np.ndarray:
    ndof = len(ACTIVE_DOF_INDICES)
    frequency_count = len(operator.omega_rad_s)
    q = state[:ndof]
    qd = state[ndof : 2 * ndof]
    memory = state[2 * ndof :].reshape(2, frequency_count, ndof)
    memory_force = np.einsum("k,kij,kj->i", operator.radiation_weights, operator.active_radiation(), memory[0])
    restoring = operator.active_matrix(operator.restoring)
    linear_damping = np.zeros((ndof, ndof), dtype=float)
    damping_term = np.einsum("ij,j->i", linear_damping, qd)
    restoring_term = np.einsum("ij,j->i", restoring, q)
    qdd = np.einsum(
        "ij,j->i",
        operator.active_mass_inverse,
        external_force - damping_term - restoring_term - memory_force,
    )
    cos_dot = qd[None, :] - operator.omega_rad_s[:, None] * memory[1]
    sin_dot = operator.omega_rad_s[:, None] * memory[0]
    return np.concatenate([qd, qdd, cos_dot.reshape(-1), sin_dot.reshape(-1)])


def solve_platform(
    operator: PlatformOperator,
    config: dict[str, Any],
    wang_config: dict[str, Any],
    wave: dict[str, Any],
    time_s: np.ndarray,
    feedback_active: np.ndarray,
) -> dict[str, Any]:
    time = np.asarray(time_s, dtype=float)
    feedback = np.asarray(feedback_active, dtype=float)
    if feedback.shape != (len(time), 3):
        raise ValueError(f"Platform feedback must have shape ({len(time)}, 3), got {feedback.shape}.")
    wave_force = wave_force_series(time, float(config["time_domain"]["start_s"]), operator, wave)
    plume_full = wang_plume_force_6dof(time, wang_config, config)
    plume_force = plume_full[:, operator.active_indices]
    external = wave_force + plume_force + feedback
    ndof = 3
    frequency_count = len(operator.omega_rad_s)
    state = np.zeros(2 * ndof + 2 * frequency_count * ndof, dtype=float)
    q_hist = np.zeros((len(time), ndof), dtype=float)
    qd_hist = np.zeros((len(time), ndof), dtype=float)
    memory_force_hist = np.zeros((len(time), ndof), dtype=float)
    active_radiation = operator.active_radiation()
    active_mass = operator.active_matrix(operator.mass)
    active_restoring = operator.active_matrix(operator.restoring)

    for index, current_time in enumerate(time):
        q_hist[index] = state[:ndof]
        qd_hist[index] = state[ndof : 2 * ndof]
        memory = state[2 * ndof :].reshape(2, frequency_count, ndof)
        memory_force_hist[index] = np.einsum("k,kij,kj->i", operator.radiation_weights, active_radiation, memory[0])
        if index == len(time) - 1:
            break
        h = float(time[index + 1] - current_time)
        force_0 = external[index]
        force_1 = external[index + 1]
        force_half = 0.5 * (force_0 + force_1)
        k1 = platform_rhs(state, force_0, operator)
        k2 = platform_rhs(state + 0.5 * h * k1, force_half, operator)
        k3 = platform_rhs(state + 0.5 * h * k2, force_half, operator)
        k4 = platform_rhs(state + h * k3, force_1, operator)
        state = state + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        if not np.all(np.isfinite(state)):
            raise FloatingPointError(f"Non-finite platform state at t={time[index + 1]:.9f} s")

    kinetic = 0.5 * np.einsum("ni,ij,nj->n", qd_hist, active_mass, qd_hist)
    restoring_energy = 0.5 * np.einsum("ni,ij,nj->n", q_hist, active_restoring, q_hist)
    wave_power = np.einsum("ni,ni->n", wave_force, qd_hist)
    plume_power = np.einsum("ni,ni->n", plume_force, qd_hist)
    contact_power = np.einsum("ni,ni->n", feedback, qd_hist)
    damping_power = np.zeros(len(time), dtype=float)
    radiation_power = -np.einsum("ni,ni->n", qd_hist, memory_force_hist)
    work_wave = integrate_series(time, wave_power)
    work_plume = integrate_series(time, plume_power)
    work_contact = integrate_series(time, contact_power)
    work_damping = integrate_series(time, damping_power)
    work_radiation = integrate_series(time, radiation_power)
    initial_mechanical = float(kinetic[0] + restoring_energy[0])
    final_mechanical = float(kinetic[-1] + restoring_energy[-1])
    energy_residual = final_mechanical - initial_mechanical - (work_wave + work_plume + work_contact + work_damping + work_radiation)

    full_q = np.zeros((len(time), 6), dtype=float)
    full_qd = np.zeros((len(time), 6), dtype=float)
    full_q[:, operator.active_indices] = q_hist
    full_qd[:, operator.active_indices] = qd_hist
    summary = {
        "heave_peak_m": float(np.max(np.abs(q_hist[:, 0]))),
        "roll_peak_deg": float(np.max(np.abs(np.degrees(q_hist[:, 1])))),
        "pitch_peak_deg": float(np.max(np.abs(np.degrees(q_hist[:, 2])))),
        "heave_rms_m": float(math.sqrt(np.mean(q_hist[:, 0] ** 2))),
        "roll_rms_deg": float(math.sqrt(np.mean(np.degrees(q_hist[:, 1]) ** 2))),
        "pitch_rms_deg": float(math.sqrt(np.mean(np.degrees(q_hist[:, 2]) ** 2))),
        "heave_velocity_peak_m_s": float(np.max(np.abs(qd_hist[:, 0]))),
        "roll_rate_peak_deg_s": float(np.max(np.abs(np.degrees(qd_hist[:, 1])))),
        "pitch_rate_peak_deg_s": float(np.max(np.abs(np.degrees(qd_hist[:, 2])))),
    }
    return {
        "time_s": time,
        "q_active": q_hist,
        "qd_active": qd_hist,
        "q_full": full_q,
        "qd_full": full_qd,
        "wave_force_active": wave_force,
        "plume_force_active": plume_force,
        "feedback_active": feedback,
        "memory_force_active": memory_force_hist,
        "summary": summary,
        "energy": {
            "initial_mechanical_energy_j": initial_mechanical,
            "final_mechanical_energy_j": final_mechanical,
            "final_kinetic_energy_j": float(kinetic[-1]),
            "final_hydrostatic_potential_energy_j": float(restoring_energy[-1]),
            "work_wave_j": work_wave,
            "work_plume_j": work_plume,
            "work_contact_feedback_j": work_contact,
            "work_linear_damping_j": work_damping,
            "work_radiation_j": work_radiation,
            "radiation_energy_proxy_absorbed_j": -work_radiation,
            "platform_energy_residual_j": float(energy_residual),
            "platform_energy_residual_relative": float(energy_residual / max(abs(final_mechanical), abs(initial_mechanical), 1.0)),
            "definition": "T_platform + U_hydrostatic; radiation energy is reported as negative radiation work proxy, not a hidden stored state",
        },
    }


def leg_positions(config: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    radius = float(config["legs"]["footprint_radius_m"])
    azimuth = np.radians(np.asarray(config["legs"]["azimuths_deg"], dtype=float))
    return radius * np.cos(azimuth), radius * np.sin(azimuth)


def evaluate_contact(
    platform_q: np.ndarray,
    platform_qd: np.ndarray,
    rocket_q: np.ndarray,
    rocket_qd: np.ndarray,
    leg_x: np.ndarray,
    leg_y: np.ndarray,
    offset_x_m: float,
    offset_y_m: float,
    parameters: dict[str, float],
    cog_from_base_m: float,
) -> dict[str, np.ndarray]:
    deck_x = float(offset_x_m) + leg_x
    deck_y = float(offset_y_m) + leg_y
    deck_z = platform_q[0] + platform_q[1] * deck_y - platform_q[2] * deck_x
    deck_vz = platform_qd[0] + platform_qd[1] * deck_y - platform_qd[2] * deck_x
    foot_z = rocket_q[0] - float(cog_from_base_m) + rocket_q[1] * leg_y - rocket_q[2] * leg_x
    foot_vz = rocket_qd[0] + rocket_qd[1] * leg_y - rocket_qd[2] * leg_x
    delta = deck_z - foot_z
    delta_dot = deck_vz - foot_vz
    components = smooth_contact_components(delta, delta_dot, parameters, active=True)
    force = components["force_n"]
    rocket_generalized = np.asarray(
        [np.sum(force), np.sum(leg_y * force), np.sum(-leg_x * force)],
        dtype=float,
    )
    per_leg_platform = np.column_stack(
        [
            np.zeros_like(force),
            np.zeros_like(force),
            -force,
            deck_y * (-force),
            -deck_x * (-force),
            np.zeros_like(force),
        ]
    )
    return {
        **components,
        "deck_x_m": deck_x,
        "deck_y_m": deck_y,
        "deck_z_m": deck_z,
        "deck_vz_m_s": deck_vz,
        "foot_z_m": foot_z,
        "foot_vz_m_s": foot_vz,
        "delta_m": delta,
        "delta_dot_m_s": delta_dot,
        "in_contact": delta > 0.0,
        "rocket_generalized": rocket_generalized,
        "rocket_wrench_about_platform_6dof": -np.sum(per_leg_platform, axis=0),
        "platform_wrench_6dof": np.sum(per_leg_platform, axis=0),
        "platform_wrench_per_leg_6dof": per_leg_platform,
        "potential_j": smooth_contact_potential_j(components["stroke_m"], parameters),
    }


def interpolate_matrix(time_s: np.ndarray, values: np.ndarray, target_time_s: np.ndarray) -> np.ndarray:
    source_time = np.asarray(time_s, dtype=float)
    source_values = np.asarray(values, dtype=float)
    target = np.asarray(target_time_s, dtype=float)
    return np.column_stack([np.interp(target, source_time, source_values[:, column]) for column in range(source_values.shape[1])])


def detect_contact_events(time_s: np.ndarray, delta_m: np.ndarray) -> dict[str, Any]:
    time = np.asarray(time_s, dtype=float)
    delta = np.asarray(delta_m, dtype=float)
    leg_events: dict[str, list[dict[str, Any]]] = {}
    first_contact_times: list[float] = []
    for leg_index in range(delta.shape[1]):
        events: list[dict[str, Any]] = []
        for index in range(len(time) - 1):
            left = float(delta[index, leg_index])
            right = float(delta[index + 1, leg_index])
            if left <= 0.0 < right:
                fraction = (0.0 - left) / (right - left)
                events.append({"type": "contact_on", "time_s": float(time[index] + fraction * (time[index + 1] - time[index]))})
            elif left > 0.0 >= right:
                fraction = (0.0 - left) / (right - left)
                events.append({"type": "contact_off", "time_s": float(time[index] + fraction * (time[index + 1] - time[index]))})
        leg_events[f"leg_{leg_index + 1}"] = events
        first_on = [event["time_s"] for event in events if event["type"] == "contact_on"]
        if first_on:
            first_contact_times.append(float(first_on[0]))
    in_contact = delta > 0.0
    all_contact = np.all(in_contact, axis=1)
    any_contact = np.any(in_contact, axis=1)
    all_time = None
    any_time = None
    if np.any(all_contact):
        all_time = float(time[int(np.where(all_contact)[0][0])])
    if np.any(any_contact):
        any_time = float(time[int(np.where(any_contact)[0][0])])
    return {
        "per_leg": leg_events,
        "first_contact_time_s": min(first_contact_times) if first_contact_times else None,
        "first_contact_time_by_leg_s": {f"leg_{index + 1}": (times[0] if times else None) for index, times in enumerate([[event["time_s"] for event in leg_events[f"leg_{index + 1}"] if event["type"] == "contact_on"] for index in range(delta.shape[1])])},
        "any_contact_sample_time_s": any_time,
        "all_legs_contact_sample_time_s": all_time,
        "event_count": int(sum(len(events) for events in leg_events.values())),
        "event_interpolation": "linear root of delta across adjacent 0.0005 s contact samples; contact state itself is delta > 0",
    }


def simulate_contact(
    platform_time_s: np.ndarray,
    platform_q_active: np.ndarray,
    platform_qd_active: np.ndarray,
    config: dict[str, Any],
    wang_config: dict[str, Any],
    contact_dt_s: float,
) -> dict[str, Any]:
    td = config["time_domain"]
    time = make_time_grid(float(td["start_s"]), float(td["end_s"]), float(contact_dt_s))
    source_time = np.asarray(platform_time_s, dtype=float)
    source_q = np.asarray(platform_q_active, dtype=float)
    source_qd = np.asarray(platform_qd_active, dtype=float)
    platform_q = interpolate_matrix(source_time, source_q, time)
    platform_qd = interpolate_matrix(source_time, source_qd, time)
    leg_x, leg_y = leg_positions(config)
    parameters = current_smooth_contact_parameters()
    rocket = config["rocket"]
    mass = float(rocket["mass_kg"])
    inertia = np.asarray([float(rocket["inertia_roll_kg_m2"]), float(rocket["inertia_pitch_kg_m2"])], dtype=float)
    cg = float(rocket["cog_from_base_m"])
    touchdown_reference = float(td["touchdown_reference_s"])
    offset_x = float(config["plume"]["application_x_m"])
    offset_y = float(config["plume"]["application_y_m"])
    reference_deck = interpolate_matrix(source_time, source_q, np.asarray([touchdown_reference]))[0]
    reference_deck_z = reference_deck[0] + reference_deck[1] * offset_y - reference_deck[2] * offset_x
    touchdown_speed = float(rocket["touchdown_speed_m_s"])
    state = np.asarray(
        [reference_deck_z + cg + touchdown_speed * (touchdown_reference - time[0]), 0.0, 0.0, -touchdown_speed, 0.0, 0.0],
        dtype=float,
    )
    rocket_q = np.zeros((len(time), 3), dtype=float)
    rocket_qd = np.zeros((len(time), 3), dtype=float)
    force = np.zeros((len(time), 4), dtype=float)
    delta = np.zeros((len(time), 4), dtype=float)
    delta_dot = np.zeros((len(time), 4), dtype=float)
    spring = np.zeros((len(time), 4), dtype=float)
    damper = np.zeros((len(time), 4), dtype=float)
    hard_stop = np.zeros((len(time), 4), dtype=float)
    raw_force = np.zeros((len(time), 4), dtype=float)
    deck_vz = np.zeros((len(time), 4), dtype=float)
    foot_vz = np.zeros((len(time), 4), dtype=float)
    potential = np.zeros((len(time), 4), dtype=float)
    wrench = np.zeros((len(time), 6), dtype=float)
    rocket_wrench_about_platform = np.zeros((len(time), 6), dtype=float)
    rocket_generalized = np.zeros((len(time), 3), dtype=float)
    gravity_enabled = np.zeros(len(time), dtype=bool)
    gravity_on = False

    def platform_at(t: float) -> tuple[np.ndarray, np.ndarray]:
        return (
            np.asarray([np.interp(t, source_time, source_q[:, column]) for column in range(3)], dtype=float),
            np.asarray([np.interp(t, source_time, source_qd[:, column]) for column in range(3)], dtype=float),
        )

    def derivative(t: float, current: np.ndarray, gravity_active: bool) -> np.ndarray:
        q = current[:3]
        qd = current[3:]
        p_q, p_qd = platform_at(t)
        evaluation = evaluate_contact(p_q, p_qd, q, qd, leg_x, leg_y, offset_x, offset_y, parameters, cg)
        generalized = evaluation["rocket_generalized"]
        acceleration = np.asarray(
            [
                (generalized[0] - (mass * float(rocket["gravity_m_s2"]) if gravity_active else 0.0)) / mass,
                generalized[1] / inertia[0],
                generalized[2] / inertia[1],
            ],
            dtype=float,
        )
        return np.concatenate([qd, acceleration])

    for index, current_time in enumerate(time):
        rocket_q[index] = state[:3]
        rocket_qd[index] = state[3:]
        evaluation = evaluate_contact(platform_q[index], platform_qd[index], state[:3], state[3:], leg_x, leg_y, offset_x, offset_y, parameters, cg)
        if not gravity_on and bool(np.any(evaluation["in_contact"])):
            gravity_on = True
        gravity_enabled[index] = gravity_on
        force[index] = evaluation["force_n"]
        delta[index] = evaluation["delta_m"]
        delta_dot[index] = evaluation["rate_m_s"]
        spring[index] = evaluation["spring_n"]
        damper[index] = evaluation["damper_n"]
        hard_stop[index] = evaluation["hard_stop_n"]
        raw_force[index] = evaluation["raw_force_n"]
        deck_vz[index] = evaluation["deck_vz_m_s"]
        foot_vz[index] = evaluation["foot_vz_m_s"]
        potential[index] = evaluation["potential_j"]
        wrench[index] = evaluation["platform_wrench_6dof"]
        rocket_wrench_about_platform[index] = evaluation["rocket_wrench_about_platform_6dof"]
        rocket_generalized[index] = evaluation["rocket_generalized"]
        if index == len(time) - 1:
            break
        h = float(time[index + 1] - current_time)
        k1 = derivative(float(current_time), state, gravity_on)
        k2 = derivative(float(current_time + 0.5 * h), state + 0.5 * h * k1, gravity_on)
        k3 = derivative(float(current_time + 0.5 * h), state + 0.5 * h * k2, gravity_on)
        k4 = derivative(float(time[index + 1]), state + h * k3, gravity_on)
        state = state + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        if not np.all(np.isfinite(state)):
            raise FloatingPointError(f"Non-finite rocket state at t={time[index + 1]:.9f} s")

    events = detect_contact_events(time, delta)
    rate = delta_dot
    rate_effective = np.where(delta > 0.0, rate, 0.0)
    damping_power = np.sum(damper * rate_effective, axis=1)
    relative_power = np.sum(force * rate_effective, axis=1)
    projection_power = np.sum((force - raw_force) * rate_effective, axis=1)
    rocket_contact_power = np.sum(force * foot_vz, axis=1)
    platform_source_power = np.einsum("ni,ni->n", wrench[:, ACTIVE_DOF_INDICES], platform_qd)
    gravity_power = np.where(gravity_enabled, -mass * float(rocket["gravity_m_s2"]) * rocket_qd[:, 0], 0.0)
    kinetic = (
        0.5 * mass * rocket_qd[:, 0] ** 2
        + 0.5 * inertia[0] * rocket_qd[:, 1] ** 2
        + 0.5 * inertia[1] * rocket_qd[:, 2] ** 2
    )
    work_gravity = integrate_series(time, gravity_power)
    work_contact_rocket = integrate_series(time, rocket_contact_power)
    contact_residual = (kinetic[-1] - kinetic[0]) - (work_gravity + work_contact_rocket)
    elastic_energy = np.sum(potential, axis=1)
    work_relative = integrate_series(time, relative_power)
    dissipation = integrate_series(time, damping_power)
    projection_work = integrate_series(time, projection_power)
    contact_closure_residual = work_relative - ((elastic_energy[-1] - elastic_energy[0]) + dissipation + projection_work)
    contact_wrench_active = wrench[:, ACTIVE_DOF_INDICES]
    wrench_action_reaction_residual = np.max(np.abs(wrench + rocket_wrench_about_platform), axis=0)
    max_wrench = np.max(np.abs(wrench), axis=0)
    summary = {
        "max_total_contact_force_mn": float(np.max(np.sum(force, axis=1)) / 1.0e6),
        "max_leg_contact_force_mn": float(np.max(force) / 1.0e6),
        "max_penetration_m": float(np.max(np.maximum(delta, 0.0))),
        "max_penetration_mm": float(np.max(np.maximum(delta, 0.0)) * 1000.0),
        "max_compression_rate_m_s": float(np.max(rate_effective)),
        "max_platform_wrench_abs": {name: float(value) for name, value in zip(DOF_NAMES_6, max_wrench)},
        "max_action_reaction_residual_by_component": {name: float(value) for name, value in zip(DOF_NAMES_6, wrench_action_reaction_residual)},
        "first_contact_time_s": events["first_contact_time_s"],
        "all_legs_contact_sample_time_s": events["all_legs_contact_sample_time_s"],
        "final_contact_count": int(np.sum(delta[-1] > 0.0)),
        "contact_dt_s": float(contact_dt_s),
        "sample_count": int(len(time)),
        "gravity_on_time_s": events["first_contact_time_s"],
    }
    return {
        "time_s": time,
        "platform_source_q_active": platform_q,
        "platform_source_qd_active": platform_qd,
        "rocket_q": rocket_q,
        "rocket_qd": rocket_qd,
        "leg_x_m": leg_x,
        "leg_y_m": leg_y,
        "force_n": force,
        "delta_m": delta,
        "delta_dot_m_s": delta_dot,
        "spring_n": spring,
        "damper_n": damper,
        "hard_stop_n": hard_stop,
        "raw_force_n": raw_force,
        "deck_vz_m_s": deck_vz,
        "foot_vz_m_s": foot_vz,
        "platform_wrench_6dof": wrench,
        "rocket_wrench_about_platform_6dof": rocket_wrench_about_platform,
        "platform_wrench_active": contact_wrench_active,
        "rocket_generalized": rocket_generalized,
        "gravity_enabled": gravity_enabled,
        "events": events,
        "summary": summary,
        "energy": {
            "initial_kinetic_energy_j": float(kinetic[0]),
            "final_kinetic_energy_j": float(kinetic[-1]),
            "gravity_work_on_rocket_j": float(work_gravity),
            "contact_work_on_rocket_j": float(work_contact_rocket),
            "contact_elastic_stored_energy_final_j": float(elastic_energy[-1]),
            "contact_elastic_stored_energy_max_j": float(np.max(elastic_energy)),
            "contact_dissipation_j": float(dissipation),
            "contact_absorbed_energy_j": float(dissipation + elastic_energy[-1]),
            "contact_relative_work_j": float(work_relative),
            "contact_law_projection_work_j": float(projection_work),
            "rocket_energy_residual_j": float(contact_residual),
            "contact_force_energy_closure_residual_j": float(contact_closure_residual),
            "platform_source_contact_work_j": float(integrate_series(time, platform_source_power)),
            "definition": "absorbed = positive smooth-contact damping dissipation + elastic energy still stored at the final sample; clipping work is reported separately",
        },
    }


def interval_average_resample(time_s: np.ndarray, values: np.ndarray, target_time_s: np.ndarray) -> np.ndarray:
    """Average fine values over Voronoi bins centered on target samples."""
    source_time = np.asarray(time_s, dtype=float)
    source_values = np.asarray(values, dtype=float)
    target = np.asarray(target_time_s, dtype=float)
    if source_values.shape[0] != len(source_time):
        raise ValueError("Fine values and fine time axis have different lengths.")
    if len(target) == 1:
        return np.asarray([source_values.mean(axis=0)])
    edges = np.empty(len(target) + 1, dtype=float)
    edges[1:-1] = 0.5 * (target[:-1] + target[1:])
    edges[0] = target[0]
    edges[-1] = target[-1]
    result = np.zeros((len(target), source_values.shape[1]), dtype=float)
    for index in range(len(target)):
        left = edges[index]
        right = edges[index + 1]
        local_time = np.concatenate(([left], source_time[(source_time > left) & (source_time < right)], [right]))
        local_values = interpolate_matrix(source_time, source_values, local_time)
        result[index] = np.asarray(np.trapezoid(local_values, local_time, axis=0) / max(right - left, 1.0e-15), dtype=float)
    return result


def trajectory_difference(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, float]:
    previous_q = np.asarray(previous["q_active"], dtype=float)
    current_q = np.asarray(current["q_active"], dtype=float)
    previous_qd = np.asarray(previous["qd_active"], dtype=float)
    current_qd = np.asarray(current["qd_active"], dtype=float)
    q_scale = np.maximum(np.maximum(np.max(np.abs(previous_q), axis=0), np.max(np.abs(current_q), axis=0)), 1.0e-6)
    qd_scale = np.maximum(np.maximum(np.max(np.abs(previous_qd), axis=0), np.max(np.abs(current_qd), axis=0)), 1.0e-6)
    q_rel = np.max(np.abs(current_q - previous_q), axis=0) / q_scale
    qd_rel = np.max(np.abs(current_qd - previous_qd), axis=0) / qd_scale
    return {
        "max_abs_heave_difference_m": float(np.max(np.abs(current_q[:, 0] - previous_q[:, 0]))),
        "max_abs_roll_difference_rad": float(np.max(np.abs(current_q[:, 1] - previous_q[:, 1]))),
        "max_abs_pitch_difference_rad": float(np.max(np.abs(current_q[:, 2] - previous_q[:, 2]))),
        "max_relative_q_difference": float(np.max(q_rel)),
        "max_relative_qd_difference": float(np.max(qd_rel)),
        "fixed_point_metric": float(max(np.max(q_rel), np.max(qd_rel))),
    }


def updated_platform_contact_work(contact: dict[str, Any], platform: dict[str, Any]) -> float:
    fine_time = np.asarray(contact["time_s"], dtype=float)
    feedback = np.asarray(contact["platform_wrench_active"], dtype=float)
    updated_qd = interpolate_matrix(np.asarray(platform["time_s"], dtype=float), np.asarray(platform["qd_active"], dtype=float), fine_time)
    return integrate_series(fine_time, np.einsum("ni,ni->n", feedback, updated_qd))


def combined_energy_budget(contact: dict[str, Any], platform: dict[str, Any]) -> dict[str, Any]:
    rocket_energy = contact["energy"]
    platform_energy = platform["energy"]
    work_contact_source = float(rocket_energy["platform_source_contact_work_j"])
    work_contact_updated = updated_platform_contact_work(contact, platform)
    coupling_work_mismatch = work_contact_updated - work_contact_source
    delta_rocket_t = float(rocket_energy["final_kinetic_energy_j"] - rocket_energy["initial_kinetic_energy_j"])
    delta_platform_mechanical = float(platform_energy["final_mechanical_energy_j"] - platform_energy["initial_mechanical_energy_j"])
    delta_contact_elastic = float(rocket_energy["contact_elastic_stored_energy_final_j"])
    lhs = delta_rocket_t + delta_platform_mechanical + delta_contact_elastic
    rhs = (
        float(rocket_energy["gravity_work_on_rocket_j"])
        + float(platform_energy["work_wave_j"])
        + float(platform_energy["work_plume_j"])
        + float(platform_energy["work_linear_damping_j"])
        + float(platform_energy["work_radiation_j"])
        - float(rocket_energy["contact_dissipation_j"])
        - float(rocket_energy["contact_law_projection_work_j"])
        + coupling_work_mismatch
    )
    residual = lhs - rhs
    return {
        "initial_kinetic_energy_j": float(rocket_energy["initial_kinetic_energy_j"]),
        "gravity_work_j": float(rocket_energy["gravity_work_on_rocket_j"]),
        "contact_absorbed_energy_j": float(rocket_energy["contact_absorbed_energy_j"]),
        "contact_dissipation_j": float(rocket_energy["contact_dissipation_j"]),
        "contact_elastic_stored_energy_final_j": delta_contact_elastic,
        "contact_law_projection_work_j": float(rocket_energy["contact_law_projection_work_j"]),
        "platform_mechanical_energy_final_j": float(platform_energy["final_mechanical_energy_j"]),
        "platform_radiation_energy_proxy_absorbed_j": float(platform_energy["radiation_energy_proxy_absorbed_j"]),
        "platform_wave_work_j": float(platform_energy["work_wave_j"]),
        "platform_plume_work_j": float(platform_energy["work_plume_j"]),
        "platform_contact_work_on_updated_trajectory_j": float(work_contact_updated),
        "platform_contact_work_on_source_trajectory_j": work_contact_source,
        "loose_coupling_work_mismatch_j": float(coupling_work_mismatch),
        "ledger_left_hand_side_delta_energy_j": float(lhs),
        "ledger_right_hand_side_work_balance_j": float(rhs),
        "combined_energy_residual_j": float(residual),
        "definition": "residual includes the explicit source-vs-updated platform contact-work mismatch; it is not silently discarded",
    }


def series_summary_for_comparison(contact: dict[str, Any], platform: dict[str, Any]) -> dict[str, float | None]:
    return {
        "max_total_contact_force_mn": float(contact["summary"]["max_total_contact_force_mn"]),
        "max_leg_contact_force_mn": float(contact["summary"]["max_leg_contact_force_mn"]),
        "max_penetration_m": float(contact["summary"]["max_penetration_m"]),
        "first_contact_time_s": contact["summary"]["first_contact_time_s"],
        "all_legs_contact_sample_time_s": contact["summary"]["all_legs_contact_sample_time_s"],
        "platform_heave_peak_m": float(platform["summary"]["heave_peak_m"]),
        "platform_roll_peak_deg": float(platform["summary"]["roll_peak_deg"]),
        "platform_pitch_peak_deg": float(platform["summary"]["pitch_peak_deg"]),
        "rocket_final_vertical_speed_m_s": float(contact["rocket_qd"][-1, 0]),
        "contact_absorbed_energy_kj": float(contact["energy"]["contact_absorbed_energy_j"] / 1000.0),
        "contact_dissipation_kj": float(contact["energy"]["contact_dissipation_j"] / 1000.0),
        "combined_energy_residual_kj": None,
    }


def run_coupling_algorithm(
    name: str,
    pass_limit: int,
    operator: PlatformOperator,
    config: dict[str, Any],
    wang_config: dict[str, Any],
    wave: dict[str, Any],
    baseline_platform: dict[str, Any],
    retain_trace: bool,
) -> dict[str, Any]:
    platform_time = np.asarray(baseline_platform["time_s"], dtype=float)
    current_platform = baseline_platform
    previous_feedback: np.ndarray | None = None
    pass_rows: list[dict[str, Any]] = []
    final_contact: dict[str, Any] | None = None
    final_platform: dict[str, Any] | None = None
    final_source_platform: dict[str, Any] | None = None
    tolerance = float(config["coupling"]["iterative_tolerance"])
    for pass_index in range(1, int(pass_limit) + 1):
        contact = simulate_contact(
            platform_time,
            np.asarray(current_platform["q_active"], dtype=float),
            np.asarray(current_platform["qd_active"], dtype=float),
            config,
            wang_config,
            float(config["time_domain"]["contact_dt_s"]),
        )
        feedback = interval_average_resample(np.asarray(contact["time_s"], dtype=float), np.asarray(contact["platform_wrench_active"], dtype=float), platform_time)
        updated_platform = solve_platform(operator, config, wang_config, wave, platform_time, feedback)
        diff = trajectory_difference(current_platform, updated_platform)
        force_change = None
        if previous_feedback is not None:
            force_scale = max(float(np.max(np.abs(feedback))), float(np.max(np.abs(previous_feedback))), 1.0)
            force_change = float(np.max(np.abs(feedback - previous_feedback)) / force_scale)
        budget = combined_energy_budget(contact, updated_platform)
        pass_rows.append(
            {
                "pass": pass_index,
                "algorithm": name,
                "platform_source": "previous pass platform trajectory",
                "platform_source_summary": current_platform["summary"],
                "updated_platform_summary": updated_platform["summary"],
                "contact_summary": contact["summary"],
                "fixed_point": diff,
                "feedback_force_change_metric": force_change,
                "energy": budget,
            }
        )
        final_contact = contact
        final_platform = updated_platform
        final_source_platform = current_platform
        current_platform = updated_platform
        previous_feedback = feedback
        if name == "iterative" and pass_index >= 2 and diff["fixed_point_metric"] <= tolerance:
            break
    if final_contact is None or final_platform is None or final_source_platform is None:
        raise RuntimeError(f"Coupling algorithm {name} produced no pass.")
    final_budget = pass_rows[-1]["energy"]
    result: dict[str, Any] = {
        "name": name,
        "passes_requested": int(pass_limit),
        "passes_completed": len(pass_rows),
        "converged": bool(name == "iterative" and pass_rows[-1]["fixed_point"]["fixed_point_metric"] <= tolerance),
        "convergence_tolerance": tolerance if name == "iterative" else None,
        "passes": pass_rows,
        "final_summary": {
            **series_summary_for_comparison(final_contact, final_platform),
            "max_platform_feedback_force_mn": float(np.max(np.abs(final_contact["platform_wrench_active"])) / 1.0e6),
            "final_platform_energy_residual_kj": float(final_platform["energy"]["platform_energy_residual_j"] / 1000.0),
            "final_combined_energy_residual_kj": float(final_budget["combined_energy_residual_j"] / 1000.0),
            "combined_energy_residual_kj": float(final_budget["combined_energy_residual_j"] / 1000.0),
            "max_action_reaction_residual_by_component": final_contact["summary"]["max_action_reaction_residual_by_component"],
        },
        "final_energy": final_budget,
        "final_platform": final_platform,
        "final_source_platform": final_source_platform,
        "final_contact": final_contact,
    }
    if not retain_trace:
        result["final_platform"] = None
        result["final_source_platform"] = None
        result["final_contact"] = None
    return result


def compare_convergence_runs(runs: dict[str, dict[str, Any]], tolerance: float = 0.10) -> dict[str, Any]:
    ordered = sorted(runs.items(), key=lambda item: float(item[1]["contact_dt_s"]))
    metrics = [
        "max_total_contact_force_mn",
        "max_leg_contact_force_mn",
        "max_penetration_m",
        "platform_heave_peak_m",
        "platform_roll_peak_deg",
        "platform_pitch_peak_deg",
        "contact_absorbed_energy_kj",
    ]
    rows: list[dict[str, Any]] = []
    for (fine_name, fine_run), (coarse_name, coarse_run) in zip(ordered[:-1], ordered[1:]):
        fine = fine_run["final_summary"]
        coarse = coarse_run["final_summary"]
        checks = []
        passed = True
        for metric in metrics:
            fine_value = float(fine[metric])
            coarse_value = float(coarse[metric])
            relative = abs(coarse_value - fine_value) / max(abs(coarse_value), abs(fine_value), 1.0e-12)
            metric_pass = relative <= tolerance
            checks.append({"metric": metric, "fine": fine_value, "coarse": coarse_value, "relative_difference": relative, "pass": metric_pass})
            passed = passed and metric_pass
        fine_event = fine.get("first_contact_time_s")
        coarse_event = coarse.get("first_contact_time_s")
        event_difference = None if fine_event is None or coarse_event is None else abs(float(coarse_event) - float(fine_event))
        rows.append(
            {
                "fine": fine_name,
                "coarse": coarse_name,
                "fine_dt_s": float(fine_run["contact_dt_s"]),
                "coarse_dt_s": float(coarse_run["contact_dt_s"]),
                "event_time_difference_s": event_difference,
                "event_time_tolerance_s": float(coarse_run["contact_dt_s"]),
                "checks": checks,
                "pass": bool(passed and (event_difference is None or event_difference <= float(coarse_run["contact_dt_s"]))),
            }
        )
    return {
        "algorithm": "two_pass",
        "runs": {
            name: {
                "contact_dt_s": float(run["contact_dt_s"]),
                "passes_completed": int(run["passes_completed"]),
                "final_summary": run["final_summary"],
            }
            for name, run in runs.items()
        },
        "pairwise": rows,
        "relative_tolerance": float(tolerance),
        "pass": bool(all(row["pass"] for row in rows)),
        "definition": "two-pass loose coupling repeated at dt, dt/2 and dt/4; peaks use each native contact grid, while event time uses the explicitly interpolated delta crossing",
    }


def wang_baseline_audit(wang_config: dict[str, Any]) -> dict[str, Any]:
    response_exists = WANG_RESPONSE_PATH.exists()
    probe: dict[str, Any] = {}
    if response_exists:
        response = read_json(WANG_RESPONSE_PATH)
        simulations = response.get("simulations", {})
        no_plume = simulations.get("wave_no_plume")
        center = simulations.get("wave_center")
        if no_plume is not None and center is not None:
            no_plume_heave = np.asarray(no_plume["responses"]["heave_m"], dtype=float)
            center_heave = np.asarray(center["responses"]["heave_m"], dtype=float)
            probe = {
                "wave_no_plume_with_wave": bool(no_plume.get("with_wave")),
                "wave_no_plume_with_plume": bool(no_plume.get("with_plume")),
                "wave_center_with_wave": bool(center.get("with_wave")),
                "wave_center_with_plume": bool(center.get("with_plume")),
                "max_wave_heave_difference_with_vs_without_plume_m": float(np.max(np.abs(center_heave - no_plume_heave))),
            }
    return {
        "classification": "load_driven_platform_response",
        "Wang_solver_role": "solves platform heave/roll/pitch from F_wave + F_plume through HAMS/Cummins dynamics",
        "not_plume_only": True,
        "not_prescribed_platform_displacement_in_Wang_solver": True,
        "platform_displacement_in_Wang_output": "derived state response, not an independent external input",
        "external_platform_displacement_in_existing_Chrono_replay": True,
        "current_study_usage": "does not replay Wang displacement; it uses Wang plume_load_n waveform and a separate 120x50x7 Barge HAMS operator",
        "computed_response_probe": probe,
        "plume_source_config": str(WANG_CONFIG_PATH),
        "plume_waveform_definition": wang_config["plume_load"],
    }


def serialize_platform(platform: dict[str, Any]) -> dict[str, Any]:
    return {
        "time_s": np.asarray(platform["time_s"], dtype=float).tolist(),
        "q_full": np.asarray(platform["q_full"], dtype=float).tolist(),
        "qd_full": np.asarray(platform["qd_full"], dtype=float).tolist(),
        "q_active": np.asarray(platform["q_active"], dtype=float).tolist(),
        "qd_active": np.asarray(platform["qd_active"], dtype=float).tolist(),
        "wave_force_active_n": np.asarray(platform["wave_force_active"], dtype=float).tolist(),
        "plume_force_active_n": np.asarray(platform["plume_force_active"], dtype=float).tolist(),
        "feedback_active_n": np.asarray(platform["feedback_active"], dtype=float).tolist(),
        "memory_force_active_n": np.asarray(platform["memory_force_active"], dtype=float).tolist(),
        "summary": platform["summary"],
        "energy": platform["energy"],
    }


def serialize_contact(contact: dict[str, Any]) -> dict[str, Any]:
    return {
        "time_s": np.asarray(contact["time_s"], dtype=float).tolist(),
        "platform_source_q_active": np.asarray(contact["platform_source_q_active"], dtype=float).tolist(),
        "platform_source_qd_active": np.asarray(contact["platform_source_qd_active"], dtype=float).tolist(),
        "rocket_q": np.asarray(contact["rocket_q"], dtype=float).tolist(),
        "rocket_qd": np.asarray(contact["rocket_qd"], dtype=float).tolist(),
        "leg_x_m": np.asarray(contact["leg_x_m"], dtype=float).tolist(),
        "leg_y_m": np.asarray(contact["leg_y_m"], dtype=float).tolist(),
        "force_n": np.asarray(contact["force_n"], dtype=float).tolist(),
        "delta_m": np.asarray(contact["delta_m"], dtype=float).tolist(),
        "delta_dot_m_s": np.asarray(contact["delta_dot_m_s"], dtype=float).tolist(),
        "spring_n": np.asarray(contact["spring_n"], dtype=float).tolist(),
        "damper_n": np.asarray(contact["damper_n"], dtype=float).tolist(),
        "hard_stop_n": np.asarray(contact["hard_stop_n"], dtype=float).tolist(),
        "raw_force_n": np.asarray(contact["raw_force_n"], dtype=float).tolist(),
        "deck_vz_m_s": np.asarray(contact["deck_vz_m_s"], dtype=float).tolist(),
        "foot_vz_m_s": np.asarray(contact["foot_vz_m_s"], dtype=float).tolist(),
        "platform_wrench_6dof_n_nm": np.asarray(contact["platform_wrench_6dof"], dtype=float).tolist(),
        "rocket_generalized_n_nm": np.asarray(contact["rocket_generalized"], dtype=float).tolist(),
        "rocket_wrench_about_platform_6dof_n_nm": np.asarray(contact["rocket_wrench_about_platform_6dof"], dtype=float).tolist(),
        "gravity_enabled": np.asarray(contact["gravity_enabled"], dtype=bool).tolist(),
        "events": contact["events"],
        "summary": contact["summary"],
        "energy": contact["energy"],
    }


def run_convergence(
    operator: PlatformOperator,
    config: dict[str, Any],
    wang_config: dict[str, Any],
    wave: dict[str, Any],
    baseline_platform: dict[str, Any],
) -> dict[str, Any]:
    base_dt = float(config["time_domain"]["contact_dt_s"])
    runs: dict[str, dict[str, Any]] = {}
    for label, dt in [("dt", base_dt), ("dt_over_2", base_dt / 2.0), ("dt_over_4", base_dt / 4.0)]:
        local_config = json.loads(json.dumps(config))
        local_config["time_domain"]["contact_dt_s"] = dt
        local_baseline = solve_platform(
            operator,
            local_config,
            wang_config,
            wave,
            make_time_grid(float(local_config["time_domain"]["start_s"]), float(local_config["time_domain"]["end_s"]), float(local_config["time_domain"]["platform_dt_s"])),
            np.zeros((len(baseline_platform["time_s"]), 3), dtype=float),
        )
        run = run_coupling_algorithm("two_pass", 2, operator, local_config, wang_config, wave, local_baseline, retain_trace=False)
        run["contact_dt_s"] = dt
        runs[label] = run
    return compare_convergence_runs(runs)


def build_report(config: dict[str, Any] | None = None, run_convergence_check: bool = True) -> dict[str, Any]:
    study_config = config or default_study_config()
    wang_config = read_json(WANG_CONFIG_PATH)
    operator = load_platform_operator(study_config)
    wave = build_wave_components(operator, study_config)
    platform_time = make_time_grid(
        float(study_config["time_domain"]["start_s"]),
        float(study_config["time_domain"]["end_s"]),
        float(study_config["time_domain"]["platform_dt_s"]),
    )
    baseline = solve_platform(operator, study_config, wang_config, wave, platform_time, np.zeros((len(platform_time), 3), dtype=float))
    algorithms = {
        "one_pass": run_coupling_algorithm("one_pass", 1, operator, study_config, wang_config, wave, baseline, retain_trace=False),
        "two_pass": run_coupling_algorithm("two_pass", 2, operator, study_config, wang_config, wave, baseline, retain_trace=False),
        "iterative": run_coupling_algorithm(
            "iterative",
            int(study_config["coupling"]["iterative_max_passes"]),
            operator,
            study_config,
            wang_config,
            wave,
            baseline,
            retain_trace=True,
        ),
    }
    convergence = run_convergence(operator, study_config, wang_config, wave, baseline) if run_convergence_check else {"enabled": False}
    iterative = algorithms["iterative"]
    if iterative["final_contact"] is None or iterative["final_platform"] is None or iterative["final_source_platform"] is None:
        raise RuntimeError("Iterative trace was not retained.")
    final_contact = iterative["final_contact"]
    six_wrench_residual = final_contact["summary"]["max_action_reaction_residual_by_component"]
    six_wrench_peak = final_contact["summary"]["max_platform_wrench_abs"]
    report = {
        "case_id": study_config["case_id"],
        "title": "Chrono revision study: current smooth contact on a 120x50x7 HAMS platform operator",
        "status": "computed",
        "config": study_config,
        "platform_operator": operator.audit(),
        "wave": {
            "definition": "deterministic JONSWAP first-order force synthesis on the Barge HAMS frequency grid",
            "heading_deg": float(operator.selected_heading_deg),
            "frequency_rad_s": operator.omega_rad_s.tolist(),
            "amplitudes_m": np.asarray(wave["amplitudes_m"], dtype=float).tolist(),
            "phases_rad": np.asarray(wave["phases_rad"], dtype=float).tolist(),
        },
        "wang_baseline_audit": wang_baseline_audit(wang_config),
        "smooth_contact_audit": contact_force_audit(),
        "six_component_wrench_audit": {
            "dof_order": list(DOF_NAMES_6),
            "platform_wrench_definition": "sum over legs of equal-and-opposite force at [offset_x+leg_x, offset_y+leg_y, deck_z]",
            "computed_components": ["Fx", "Fy", "Fz", "Mx", "My", "Mz"],
            "current_smooth_contact_nonzero_components": ["Fz", "Mx", "My"],
            "omitted_or_zero_by_model": {
                "Fx": "zero because current smooth law has no tangential/contact-friction force",
                "Fy": "zero because current smooth law has no tangential/contact-friction force",
                "Mz": "zero because vertical point forces have no yaw moment",
                "surge_sway_yaw_platform_feedback": "not injected; supplied 120x50x7 Hydrostatic.in has zero horizontal restoring and no mooring properties",
            },
            "computed_peak_abs_by_component": six_wrench_peak,
            "computed_max_action_reaction_residual_by_component": six_wrench_residual,
            "action_reaction_check": "platform receives -F_contact at the same application point; the reported residual is computed from the final iterative fine trace",
            "not_claimed": ["lateral friction work", "yaw response", "full six-DOF mooring-constrained platform response"],
        },
        "interpolation_and_event_detection": {
            "platform_time_step_s": float(study_config["time_domain"]["platform_dt_s"]),
            "contact_time_step_s": float(study_config["time_domain"]["contact_dt_s"]),
            "q_interpolation": "np.interp piecewise-linear interpolation of each platform q component from 0.01 s nodes to every contact substep",
            "qd_interpolation": "np.interp piecewise-linear interpolation of platform qd nodes; no finite-difference velocity is silently substituted",
            "feedback_to_platform": "fine wrench is interval-averaged over platform-grid Voronoi bins before the next platform solve",
            "contact_event": "delta crosses zero; event time is linearly interpolated between adjacent contact samples",
            "force_state": "force is evaluated on delta > 0 using the exact smooth law, so a geometric contact can have zero clipped force during rebound",
        },
        "baseline_platform": {
            "summary": baseline["summary"],
            "energy": baseline["energy"],
        },
        "algorithms": {
            name: {
                "passes_requested": run["passes_requested"],
                "passes_completed": run["passes_completed"],
                "converged": run["converged"],
                "convergence_tolerance": run["convergence_tolerance"],
                "passes": run["passes"],
                "final_summary": run["final_summary"],
                "final_energy": run["final_energy"],
            }
            for name, run in algorithms.items()
        },
        "time_step_convergence": convergence,
        "output_files": {
            "full_iterative_response": str(RESPONSE_PATH),
            "algorithm_summary_csv": str(ALGORITHM_CSV_PATH),
            "convergence_csv": str(CONVERGENCE_CSV_PATH),
        },
        "limitations": [
            "This is a separate revision study and does not modify existing core files or paper/figure assets.",
            "The active platform sub-operator is heave/roll/pitch; horizontal HAMS DOFs are retained for wrench audit but constrained because supplied mooring stiffness is unavailable.",
            "The current smooth contact model has no tangential friction, explicit flexible leg bodies, or Chrono internal SMC force output in this calculation.",
            "The Wang 506-510 s plume segment is the existing paper-text plateau approximation, not the unavailable machine-readable CFD trace.",
            "Loose coupling is iterated replay, not a monolithic strong Chrono/Cummins integrator; the energy ledger reports the resulting work mismatch explicitly.",
        ],
    }
    response = {
        "case_id": study_config["case_id"],
        "status": "computed",
        "operator": operator.audit(),
        "algorithm": "iterative",
        "passes": iterative["passes"],
        "platform": serialize_platform(iterative["final_platform"]),
        "platform_source_for_final_contact": serialize_platform(iterative["final_source_platform"]),
        "contact": serialize_contact(iterative["final_contact"]),
        "energy": iterative["final_energy"],
    }
    write_json(REPORT_PATH, report)
    write_json(RESPONSE_PATH, response)
    write_algorithm_csv(ALGORITHM_CSV_PATH, algorithms)
    write_convergence_csv(CONVERGENCE_CSV_PATH, convergence)
    return report


def write_algorithm_csv(path: Path, algorithms: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "algorithm",
        "pass",
        "passes_completed",
        "fixed_point_metric",
        "max_total_contact_force_mn",
        "max_leg_contact_force_mn",
        "max_penetration_m",
        "first_contact_time_s",
        "all_legs_contact_sample_time_s",
        "platform_heave_peak_m",
        "platform_roll_peak_deg",
        "platform_pitch_peak_deg",
        "contact_absorbed_energy_kj",
        "contact_dissipation_kj",
        "combined_energy_residual_kj",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for name, algorithm in algorithms.items():
            for row in algorithm["passes"]:
                contact_summary = row["contact_summary"]
                energy = row["energy"]
                writer.writerow(
                    {
                        "algorithm": name,
                        "pass": row["pass"],
                        "passes_completed": algorithm["passes_completed"],
                        "fixed_point_metric": row["fixed_point"]["fixed_point_metric"],
                        "max_total_contact_force_mn": contact_summary["max_total_contact_force_mn"],
                        "max_leg_contact_force_mn": contact_summary["max_leg_contact_force_mn"],
                        "max_penetration_m": contact_summary["max_penetration_m"],
                        "first_contact_time_s": contact_summary["first_contact_time_s"],
                        "all_legs_contact_sample_time_s": contact_summary["all_legs_contact_sample_time_s"],
                        "platform_heave_peak_m": row["updated_platform_summary"]["heave_peak_m"],
                        "platform_roll_peak_deg": row["updated_platform_summary"]["roll_peak_deg"],
                        "platform_pitch_peak_deg": row["updated_platform_summary"]["pitch_peak_deg"],
                        "contact_absorbed_energy_kj": energy["contact_absorbed_energy_j"] / 1000.0,
                        "contact_dissipation_kj": energy["contact_dissipation_j"] / 1000.0,
                        "combined_energy_residual_kj": energy["combined_energy_residual_j"] / 1000.0,
                    }
                )


def write_convergence_csv(path: Path, convergence: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["fine", "coarse", "fine_dt_s", "coarse_dt_s", "metric", "fine_value", "coarse_value", "relative_difference", "event_time_difference_s", "event_time_tolerance_s", "pass"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in convergence.get("pairwise", []):
            for check in row["checks"]:
                writer.writerow(
                    {
                        "fine": row["fine"],
                        "coarse": row["coarse"],
                        "fine_dt_s": row["fine_dt_s"],
                        "coarse_dt_s": row["coarse_dt_s"],
                        "metric": check["metric"],
                        "fine_value": check["fine"],
                        "coarse_value": check["coarse"],
                        "relative_difference": check["relative_difference"],
                        "event_time_difference_s": row["event_time_difference_s"],
                        "event_time_tolerance_s": row["event_time_tolerance_s"],
                        "pass": row["pass"] and check["pass"],
                    }
                )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute the Chrono/contact coupling revision study without modifying existing model files.")
    parser.add_argument("command", choices=["audit", "run", "report", "all"], nargs="?", default="run")
    parser.add_argument("--contact-dt", type=float, default=None)
    parser.add_argument("--platform-dt", type=float, default=None)
    parser.add_argument("--start", type=float, default=None)
    parser.add_argument("--end", type=float, default=None)
    parser.add_argument("--skip-convergence", action="store_true")
    args = parser.parse_args()
    config = default_study_config()
    if args.contact_dt is not None:
        config["time_domain"]["contact_dt_s"] = float(args.contact_dt)
    if args.platform_dt is not None:
        config["time_domain"]["platform_dt_s"] = float(args.platform_dt)
    if args.start is not None:
        config["time_domain"]["start_s"] = float(args.start)
    if args.end is not None:
        config["time_domain"]["end_s"] = float(args.end)
    if args.command == "audit":
        print(json.dumps({"smooth_contact": contact_force_audit(), "wang_baseline": wang_baseline_audit(read_json(WANG_CONFIG_PATH))}, ensure_ascii=False, indent=2))
        return
    if args.command in {"run", "report", "all"}:
        report = build_report(config, run_convergence_check=not args.skip_convergence)
        print(f"Wrote {REPORT_PATH}")
        print(f"Wrote {RESPONSE_PATH}")
        print(f"Algorithms: {', '.join(report['algorithms'])}")
        for name, algorithm in report["algorithms"].items():
            summary = algorithm["final_summary"]
            print(
                f"- {name}: passes={algorithm['passes_completed']} first_contact={summary['first_contact_time_s']} "
                f"max_contact={summary['max_total_contact_force_mn']:.6g} MN "
                f"max_penetration={summary['max_penetration_m']:.6g} m"
            )
        print(f"Convergence pass: {report['time_step_convergence'].get('pass')}")


if __name__ == "__main__":
    main()
