from __future__ import annotations

import argparse
import copy
import json
import math
from typing import Any

import numpy as np

try:
    from .chrono_leg_model import (
        ChronoOneWayLegModel,
        ChronoUnavailableError,
        DeckMotion,
        chrono_environment_report,
        default_leg_model_config,
        leg_positions_from_config,
    )
    from .common import ROCKET_CASES_DIR, VISUALIZATION_DIR, parse_hydrostar_rao, read_json, write_json
except ImportError:
    from chrono_leg_model import (
        ChronoOneWayLegModel,
        ChronoUnavailableError,
        DeckMotion,
        chrono_environment_report,
        default_leg_model_config,
        leg_positions_from_config,
    )
    from common import ROCKET_CASES_DIR, VISUALIZATION_DIR, parse_hydrostar_rao, read_json, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
WANG_ROOT = ROCKET_CASES_DIR / "Paper_WangZhi_2023"
WANG_RESPONSE = WANG_ROOT / "Output" / "RocketRecovery" / "wang-2023-response.json"
WANG_SELF_CHECK = WANG_ROOT / "validation" / "wang-self-check.json"
REPORT_JS = VISUALIZATION_DIR / "chrono-two-way-data.js"
CONTRACT_JS = VISUALIZATION_DIR / "chrono-two-way-contract-data.js"
PROGRESS_LOG = CASE_ROOT / "validation" / "chrono-two-way-progress.log"

STAGE2_CASES = ["calm_center", "wave_center", "wave_bow_15m", "wave_port_15m"]
DOF_IDS = [3, 4, 5]
DOF_NAMES = ["heave_m", "roll_rad", "pitch_rad"]
DOF_IDS_6DOF = [1, 2, 3, 4, 5, 6]
DOF_NAMES_6DOF = ["surge_m", "sway_m", "heave_m", "roll_rad", "pitch_rad", "yaw_rad"]


def log_progress(message: str) -> None:
    PROGRESS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with PROGRESS_LOG.open("a", encoding="utf-8") as handle:
        handle.write(message + "\n")
    print(message, flush=True)


def ensure_dirs() -> None:
    for path in [
        CASE_ROOT,
        CASE_ROOT / "Input",
        CASE_ROOT / "Output" / "RocketRecovery",
        CASE_ROOT / "validation",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def make_time_grid(start_s: float, end_s: float, dt_s: float) -> np.ndarray:
    start = float(start_s)
    end = float(end_s)
    step = float(dt_s)
    if not math.isfinite(start) or not math.isfinite(end) or not math.isfinite(step) or step <= 0.0:
        raise ValueError("Time-grid bounds must be finite and dt_s must be positive.")
    span = end - start
    if span < 0.0:
        raise ValueError("Time-grid end must not be earlier than start.")
    count_float = span / step
    count = int(round(count_float))
    if not math.isclose(count_float, count, rel_tol=1.0e-10, abs_tol=1.0e-12):
        raise ValueError(f"Time interval {span:g} is not an integer multiple of dt_s={step:g}.")
    # linspace makes the requested physical end time exact.  Repeated addition
    # with arange can leave the last sample a few ulps short of the endpoint.
    return np.linspace(start, end, count + 1, dtype=float)


def quadrature_weights(omega: np.ndarray) -> np.ndarray:
    if len(omega) == 1:
        return np.array([2.0 / math.pi], dtype=float)
    weights = np.zeros_like(omega, dtype=float)
    weights[0] = 0.5 * (omega[1] - omega[0])
    weights[-1] = 0.5 * (omega[-1] - omega[-2])
    for idx in range(1, len(omega) - 1):
        weights[idx] = 0.5 * (omega[idx + 1] - omega[idx - 1])
    return (2.0 / math.pi) * weights


def inverse_3x3(matrix: np.ndarray) -> np.ndarray:
    a, b, c = float(matrix[0, 0]), float(matrix[0, 1]), float(matrix[0, 2])
    d, e, f = float(matrix[1, 0]), float(matrix[1, 1]), float(matrix[1, 2])
    g, h, i = float(matrix[2, 0]), float(matrix[2, 1]), float(matrix[2, 2])
    co00 = e * i - f * h
    co01 = -(d * i - f * g)
    co02 = d * h - e * g
    co10 = -(b * i - c * h)
    co11 = a * i - c * g
    co12 = -(a * h - b * g)
    co20 = b * f - c * e
    co21 = -(a * f - c * d)
    co22 = a * e - b * d
    det = a * co00 + b * co01 + c * co02
    if abs(det) < 1.0e-24:
        raise ValueError("Singular 3x3 platform mass matrix.")
    return np.array(
        [
            [co00, co10, co20],
            [co01, co11, co21],
            [co02, co12, co22],
        ],
        dtype=float,
    ) / det


def matvec3(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    return np.array(
        [
            float(matrix[0, 0]) * float(vector[0]) + float(matrix[0, 1]) * float(vector[1]) + float(matrix[0, 2]) * float(vector[2]),
            float(matrix[1, 0]) * float(vector[0]) + float(matrix[1, 1]) * float(vector[1]) + float(matrix[1, 2]) * float(vector[2]),
            float(matrix[2, 0]) * float(vector[0]) + float(matrix[2, 1]) * float(vector[1]) + float(matrix[2, 2]) * float(vector[2]),
        ],
        dtype=float,
    )


def matrix_vector_product(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=float)
    vector = np.asarray(vector, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != len(vector):
        raise ValueError("Matrix/vector dimensions do not match.")
    return np.array(
        [sum(float(matrix[row, col]) * float(vector[col]) for col in range(matrix.shape[1])) for row in range(matrix.shape[0])],
        dtype=float,
    )


def inverse_square_matrix(matrix: np.ndarray) -> np.ndarray:
    source = np.asarray(matrix, dtype=float)
    if source.ndim != 2 or source.shape[0] != source.shape[1]:
        raise ValueError("Matrix must be square.")
    size = source.shape[0]
    work = source.copy()
    inverse = np.eye(size, dtype=float)
    row_scale = np.max(np.abs(work), axis=1)
    if np.any(row_scale <= 0.0):
        raise ValueError("Singular platform mass matrix: a row has zero scale.")

    for column in range(size):
        pivot_row = max(
            range(column, size),
            key=lambda row: abs(float(work[row, column])) / float(row_scale[row]),
        )
        pivot = float(work[pivot_row, column])
        if abs(pivot) <= np.finfo(float).eps * float(row_scale[pivot_row]) * size:
            raise ValueError("Singular platform mass matrix during scaled-pivot elimination.")
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
            if factor == 0.0:
                continue
            work[row, :] -= factor * work[column, :]
            inverse[row, :] -= factor * inverse[column, :]

    residual = np.zeros_like(source)
    for row in range(size):
        for column in range(size):
            residual[row, column] = sum(float(source[row, k]) * float(inverse[k, column]) for k in range(size))
            if row == column:
                residual[row, column] -= 1.0
    max_residual = float(np.max(np.abs(residual)))
    if not math.isfinite(max_residual) or max_residual > 1.0e-8:
        raise ValueError(f"Platform mass inverse residual is too large: {max_residual:.3e}.")
    return inverse


def extract_real_matrix_series(
    case_dir: Any,
    prefix: str,
    dof_ids: list[int] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    selected_dofs = dof_ids or DOF_IDS
    ndof = len(selected_dofs)
    omega_ref: np.ndarray | None = None
    matrices: list[np.ndarray] | None = None
    hydro_dir = case_dir / "Output" / "Hydrostar_format"
    for a, i in enumerate(selected_dofs):
        for b, j in enumerate(selected_dofs):
            parsed = parse_hydrostar_rao(hydro_dir / f"{prefix}_{i}{j}.rao")
            omega = np.array([row["frequency"] for row in parsed["rows"]], dtype=float)
            values = np.array([row["amplitudes"][0] for row in parsed["rows"]], dtype=float)
            if omega_ref is None:
                omega_ref = omega
                matrices = [np.zeros((ndof, ndof), dtype=float) for _ in omega]
            if not np.allclose(omega_ref, omega):
                values = np.interp(omega_ref, omega, values)
            assert matrices is not None
            for k, value in enumerate(values):
                matrices[k][a, b] = value
    assert omega_ref is not None and matrices is not None
    symmetric = [0.5 * (matrix + matrix.T) for matrix in matrices]
    return omega_ref, np.stack(symmetric, axis=0)


def load_wang_response() -> dict[str, Any]:
    if not WANG_RESPONSE.exists():
        raise FileNotFoundError(f"Missing Wang response file: {WANG_RESPONSE}. Run wang_2023.py report first.")
    return read_json(WANG_RESPONSE)


def load_cummins_matrices(wang: dict[str, Any]) -> dict[str, Any]:
    hydro = wang["hydrodynamic_sample"]
    omega, radiation = extract_real_matrix_series(WANG_ROOT, "WaveDamping")
    omega_ref = np.array(hydro["omega_rad_s"], dtype=float)
    if not np.allclose(omega, omega_ref):
        raise ValueError("Wang response and HAMS WaveDamping frequency grids differ.")
    rigid = np.array(hydro["rigid_mass_3dof"], dtype=float)
    a_inf = np.array(hydro["added_mass_infinite_3dof"], dtype=float)
    return {
        "omega_rad_s": omega,
        "radiation_damping": radiation,
        "radiation_weights": quadrature_weights(omega),
        "rigid_mass": rigid,
        "a_inf": a_inf,
        "mass": rigid + a_inf,
        "restoring": np.array(hydro["restoring_3dof"], dtype=float),
        "linear_damping": np.array(hydro["linear_damping_3dof"], dtype=float),
    }


def load_cummins_matrices_6dof(wang: dict[str, Any]) -> dict[str, Any]:
    if not WANG_SELF_CHECK.exists():
        raise FileNotFoundError(f"Missing Wang hydrostatic self-check: {WANG_SELF_CHECK}")
    self_check = read_json(WANG_SELF_CHECK)
    hydrostatic = self_check["hydrostatic"]
    omega, radiation = extract_real_matrix_series(WANG_ROOT, "WaveDamping", DOF_IDS_6DOF)
    omega_added, added = extract_real_matrix_series(WANG_ROOT, "AddedMass", DOF_IDS_6DOF)
    if not np.allclose(omega, omega_added):
        raise ValueError("Wang HAMS AddedMass and WaveDamping frequency grids differ.")
    hydro = wang["hydrodynamic_sample"]
    omega_ref = np.array(hydro["omega_rad_s"], dtype=float)
    if not np.allclose(omega, omega_ref):
        raise ValueError("Wang response and HAMS 6DOF frequency grids differ.")
    rigid = np.array(hydrostatic["body_mass_matrix"], dtype=float)
    restoring = np.array(hydrostatic["hydrostatic_restoring_matrix"], dtype=float)
    a_inf = added[-1]
    linear_damping = np.zeros((6, 6), dtype=float)
    reduced_indices = [2, 3, 4]
    reduced_damping = np.array(hydro["linear_damping_3dof"], dtype=float)
    linear_damping[np.ix_(reduced_indices, reduced_indices)] = reduced_damping
    return {
        "dof_ids": DOF_IDS_6DOF,
        "dof_names": DOF_NAMES_6DOF,
        "omega_rad_s": omega,
        "radiation_damping": radiation,
        "radiation_weights": quadrature_weights(omega),
        "rigid_mass": rigid,
        "a_inf": a_inf,
        "mass": rigid + a_inf,
        "restoring": restoring,
        "linear_damping": linear_damping,
        "model_boundary": {
            "baseline_dofs": ["heave_m", "roll_rad", "pitch_rad"],
            "leg_increment_dofs": DOF_NAMES_6DOF,
            "zero_baseline_dofs": ["surge_m", "sway_m", "yaw_rad"],
            "horizontal_restoring_source": "none_unpublished_in_wang_2023",
            "horizontal_linear_damping_source": "none_unpublished_in_wang_2023",
            "radiation_source": "local_HAMS_full_6x6",
            "a_inf_source": f"highest_computed_frequency_{float(omega[-1]):g}_rad_s_estimate",
            "mass_inverse_solver": "scaled_partial_pivot_Gauss_Jordan_with_1e-8_identity_residual_gate",
            "mass_inverse_solver_reason": "numpy.linalg.inv hangs in the isolated PyChrono environment; the local solver is deterministic and unit-tested in both Python environments.",
        },
    }


def baseline_arrays(wang: dict[str, Any], case_id: str, time_s: np.ndarray) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    sim = wang["simulations"][case_id]
    raw_time = np.array(sim["time_s"], dtype=float)
    q = np.column_stack(
        [
            np.interp(time_s, raw_time, np.array(sim["responses"]["heave_m"], dtype=float)),
            np.interp(time_s, raw_time, np.array(sim["responses"]["roll_rad"], dtype=float)),
            np.interp(time_s, raw_time, np.array(sim["responses"]["pitch_rad"], dtype=float)),
        ]
    )
    qd = np.column_stack(
        [
            np.interp(time_s, raw_time, np.array(sim["velocities"]["heave_m_s"], dtype=float)),
            np.interp(time_s, raw_time, np.array(sim["velocities"]["roll_rad_s"], dtype=float)),
            np.interp(time_s, raw_time, np.array(sim["velocities"]["pitch_rad_s"], dtype=float)),
        ]
    )
    return sim, q, qd


def baseline_arrays_6dof(wang: dict[str, Any], case_id: str, time_s: np.ndarray) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    sim, reduced_q, reduced_qd = baseline_arrays(wang, case_id, time_s)
    q = np.zeros((len(time_s), 6), dtype=float)
    qd = np.zeros((len(time_s), 6), dtype=float)
    q[:, 2:5] = reduced_q
    qd[:, 2:5] = reduced_qd
    return sim, q, qd


def deck_motion_from_arrays(time_s: np.ndarray, q: np.ndarray, qd: np.ndarray, offset: dict[str, Any]) -> DeckMotion:
    zeros = np.zeros_like(time_s)
    return DeckMotion(
        time_s=time_s,
        heave_m=q[:, 0],
        roll_rad=q[:, 1],
        pitch_rad=q[:, 2],
        heave_m_s=qd[:, 0],
        roll_rad_s=qd[:, 1],
        pitch_rad_s=qd[:, 2],
        surge_m=zeros,
        sway_m=zeros,
        yaw_rad=zeros,
        surge_m_s=zeros,
        sway_m_s=zeros,
        yaw_rad_s=zeros,
        offset_x_m=float(offset["x"]),
        offset_y_m=float(offset["y"]),
    )


def deck_motion_from_arrays_6dof(time_s: np.ndarray, q: np.ndarray, qd: np.ndarray, offset: dict[str, Any]) -> DeckMotion:
    if q.shape[1] != 6 or qd.shape[1] != 6:
        raise ValueError("6DOF deck motion requires q and qd arrays with six columns.")
    return DeckMotion(
        time_s=time_s,
        surge_m=q[:, 0],
        sway_m=q[:, 1],
        heave_m=q[:, 2],
        roll_rad=q[:, 3],
        pitch_rad=q[:, 4],
        yaw_rad=q[:, 5],
        surge_m_s=qd[:, 0],
        sway_m_s=qd[:, 1],
        heave_m_s=qd[:, 2],
        roll_rad_s=qd[:, 3],
        pitch_rad_s=qd[:, 4],
        yaw_rad_s=qd[:, 5],
        offset_x_m=float(offset["x"]),
        offset_y_m=float(offset["y"]),
    )


def deck_motion_from_wang_raw(wang: dict[str, Any], case_id: str) -> DeckMotion:
    sim = wang["simulations"][case_id]
    time_s = np.array(sim["time_s"], dtype=float)
    zeros = np.zeros_like(time_s)
    return DeckMotion(
        time_s=time_s,
        heave_m=np.array(sim["responses"]["heave_m"], dtype=float),
        roll_rad=np.array(sim["responses"]["roll_rad"], dtype=float),
        pitch_rad=np.array(sim["responses"]["pitch_rad"], dtype=float),
        heave_m_s=np.array(sim["velocities"]["heave_m_s"], dtype=float),
        roll_rad_s=np.array(sim["velocities"]["roll_rad_s"], dtype=float),
        pitch_rad_s=np.array(sim["velocities"]["pitch_rad_s"], dtype=float),
        surge_m=np.array(sim["responses"].get("surge_m", zeros), dtype=float),
        sway_m=np.array(sim["responses"].get("sway_m", zeros), dtype=float),
        yaw_rad=np.array(sim["responses"].get("yaw_rad", zeros), dtype=float),
        surge_m_s=np.array(sim["velocities"].get("surge_m_s", zeros), dtype=float),
        sway_m_s=np.array(sim["velocities"].get("sway_m_s", zeros), dtype=float),
        yaw_rad_s=np.array(sim["velocities"].get("yaw_rad_s", zeros), dtype=float),
        offset_x_m=float(sim["offset"]["x"]),
        offset_y_m=float(sim["offset"]["y"]),
    )


def values_to_named_series(time_s: np.ndarray, q: np.ndarray, qd: np.ndarray) -> dict[str, Any]:
    return {
        "time_s": time_s.tolist(),
        "responses": {
            "heave_m": q[:, 0].tolist(),
            "roll_rad": q[:, 1].tolist(),
            "pitch_rad": q[:, 2].tolist(),
            "roll_deg": np.degrees(q[:, 1]).tolist(),
            "pitch_deg": np.degrees(q[:, 2]).tolist(),
        },
        "velocities": {
            "heave_m_s": qd[:, 0].tolist(),
            "roll_rad_s": qd[:, 1].tolist(),
            "pitch_rad_s": qd[:, 2].tolist(),
        },
    }


def peak_summary(q: np.ndarray, qd: np.ndarray) -> dict[str, float]:
    return {
        "heave_peak_m": float(np.max(np.abs(q[:, 0]))),
        "roll_peak_deg": float(np.max(np.abs(np.degrees(q[:, 1])))),
        "pitch_peak_deg": float(np.max(np.abs(np.degrees(q[:, 2])))),
        "heave_rms_m": float(math.sqrt(np.mean(q[:, 0] ** 2))),
        "roll_rms_deg": float(math.sqrt(np.mean(np.degrees(q[:, 1]) ** 2))),
        "pitch_rms_deg": float(math.sqrt(np.mean(np.degrees(q[:, 2]) ** 2))),
        "heave_velocity_peak_m_s": float(np.max(np.abs(qd[:, 0]))),
        "roll_rate_peak_deg_s": float(np.max(np.abs(np.degrees(qd[:, 1])))),
        "pitch_rate_peak_deg_s": float(np.max(np.abs(np.degrees(qd[:, 2])))),
    }


def values_to_named_series_6dof(time_s: np.ndarray, q: np.ndarray, qd: np.ndarray) -> dict[str, Any]:
    if q.shape[1] != 6 or qd.shape[1] != 6:
        raise ValueError("6DOF result serialization requires q and qd arrays with six columns.")
    return {
        "time_s": time_s.tolist(),
        "responses": {
            "surge_m": q[:, 0].tolist(),
            "sway_m": q[:, 1].tolist(),
            "heave_m": q[:, 2].tolist(),
            "roll_rad": q[:, 3].tolist(),
            "pitch_rad": q[:, 4].tolist(),
            "yaw_rad": q[:, 5].tolist(),
            "roll_deg": np.degrees(q[:, 3]).tolist(),
            "pitch_deg": np.degrees(q[:, 4]).tolist(),
            "yaw_deg": np.degrees(q[:, 5]).tolist(),
        },
        "velocities": {
            "surge_m_s": qd[:, 0].tolist(),
            "sway_m_s": qd[:, 1].tolist(),
            "heave_m_s": qd[:, 2].tolist(),
            "roll_rad_s": qd[:, 3].tolist(),
            "pitch_rad_s": qd[:, 4].tolist(),
            "yaw_rad_s": qd[:, 5].tolist(),
        },
    }


def peak_summary_6dof(q: np.ndarray, qd: np.ndarray) -> dict[str, float]:
    if q.shape[1] != 6 or qd.shape[1] != 6:
        raise ValueError("6DOF peak summary requires q and qd arrays with six columns.")
    return {
        "surge_peak_m": float(np.max(np.abs(q[:, 0]))),
        "sway_peak_m": float(np.max(np.abs(q[:, 1]))),
        "heave_peak_m": float(np.max(np.abs(q[:, 2]))),
        "roll_peak_deg": float(np.max(np.abs(np.degrees(q[:, 3])))),
        "pitch_peak_deg": float(np.max(np.abs(np.degrees(q[:, 4])))),
        "yaw_peak_deg": float(np.max(np.abs(np.degrees(q[:, 5])))),
        "surge_rms_m": float(math.sqrt(np.mean(q[:, 0] ** 2))),
        "sway_rms_m": float(math.sqrt(np.mean(q[:, 1] ** 2))),
        "heave_rms_m": float(math.sqrt(np.mean(q[:, 2] ** 2))),
        "roll_rms_deg": float(math.sqrt(np.mean(np.degrees(q[:, 3]) ** 2))),
        "pitch_rms_deg": float(math.sqrt(np.mean(np.degrees(q[:, 4]) ** 2))),
        "yaw_rms_deg": float(math.sqrt(np.mean(np.degrees(q[:, 5]) ** 2))),
        "surge_velocity_peak_m_s": float(np.max(np.abs(qd[:, 0]))),
        "sway_velocity_peak_m_s": float(np.max(np.abs(qd[:, 1]))),
        "heave_velocity_peak_m_s": float(np.max(np.abs(qd[:, 2]))),
        "roll_rate_peak_deg_s": float(np.max(np.abs(np.degrees(qd[:, 3])))),
        "pitch_rate_peak_deg_s": float(np.max(np.abs(np.degrees(qd[:, 4])))),
        "yaw_rate_peak_deg_s": float(np.max(np.abs(np.degrees(qd[:, 5])))),
    }


def _named_series_arrays_6dof(series: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    time_s = np.asarray(series["time_s"], dtype=float)
    response_names = ["surge_m", "sway_m", "heave_m", "roll_rad", "pitch_rad", "yaw_rad"]
    velocity_names = ["surge_m_s", "sway_m_s", "heave_m_s", "roll_rad_s", "pitch_rad_s", "yaw_rad_s"]
    q = np.column_stack([np.asarray(series["responses"][name], dtype=float) for name in response_names])
    qd = np.column_stack([np.asarray(series["velocities"][name], dtype=float) for name in velocity_names])
    if time_s.ndim != 1 or len(time_s) == 0 or q.shape != (len(time_s), 6) or qd.shape != (len(time_s), 6):
        raise ValueError("A named 6DOF series must contain six response and six velocity arrays on one time axis.")
    if np.any(np.diff(time_s) <= 0.0):
        raise ValueError("A named 6DOF series time axis must be strictly increasing.")
    return time_s, q, qd


def _interpolate_matrix(time_s: np.ndarray, values: np.ndarray, target_time_s: np.ndarray) -> np.ndarray:
    return np.column_stack([np.interp(target_time_s, time_s, values[:, column]) for column in range(values.shape[1])])


def compare_time_step_series_6dof(
    coarse_series: dict[str, Any],
    fine_series: dict[str, Any],
    tolerance: float = 0.10,
) -> dict[str, Any]:
    """Compare two responses on one common physical time grid.

    A peak taken on each solver's native output grid can change when an event
    moves by one integration step.  The convergence metric therefore uses the
    union of both sampled grids over their shared physical interval.  Native
    peaks remain available to the caller as a separate diagnostic.
    """
    coarse_time, coarse_q, coarse_qd = _named_series_arrays_6dof(coarse_series)
    fine_time, fine_q, fine_qd = _named_series_arrays_6dof(fine_series)
    start = max(float(coarse_time[0]), float(fine_time[0]))
    end = min(float(coarse_time[-1]), float(fine_time[-1]))
    if end <= start:
        raise ValueError("Coarse and fine responses do not share a positive physical time interval.")
    coarse_mask = (coarse_time >= start) & (coarse_time <= end)
    fine_mask = (fine_time >= start) & (fine_time <= end)
    comparison_time = np.unique(
        np.concatenate([coarse_time[coarse_mask], fine_time[fine_mask], np.array([start, end], dtype=float)])
    )
    coarse_q_common = _interpolate_matrix(coarse_time, coarse_q, comparison_time)
    coarse_qd_common = _interpolate_matrix(coarse_time, coarse_qd, comparison_time)
    fine_q_common = _interpolate_matrix(fine_time, fine_q, comparison_time)
    fine_qd_common = _interpolate_matrix(fine_time, fine_qd, comparison_time)
    coarse_summary = peak_summary_6dof(coarse_q_common, coarse_qd_common)
    fine_summary = peak_summary_6dof(fine_q_common, fine_qd_common)
    metric_names = [
        "surge_peak_m",
        "sway_peak_m",
        "heave_peak_m",
        "roll_peak_deg",
        "pitch_peak_deg",
        "yaw_peak_deg",
    ]
    checks = []
    passed = True
    for name in metric_names:
        coarse_value = float(coarse_summary[name])
        fine_value = float(fine_summary[name])
        relative = abs(fine_value - coarse_value) / max(abs(fine_value), abs(coarse_value), 1.0e-12)
        row_pass = relative <= tolerance
        checks.append(
            {
                "metric": name,
                "coarse": coarse_value,
                "fine": fine_value,
                "relative_difference": relative,
                "pass": row_pass,
            }
        )
        passed = passed and row_pass
    return {
        "definition": "Peak and velocity comparison after linear interpolation onto the union of coarse and fine sample times within the shared physical interval.",
        "time_start_s": float(start),
        "time_end_s": float(end),
        "sample_count": int(len(comparison_time)),
        "coarse_summary_on_common_grid": coarse_summary,
        "fine_summary_on_common_grid": fine_summary,
        "tolerance": float(tolerance),
        "checks": checks,
        "pass": bool(passed),
    }


def solve_cummins_leg_correction(
    matrices: dict[str, Any],
    time_s: np.ndarray,
    external_force: np.ndarray,
    dt_s: float,
) -> dict[str, Any]:
    mass = np.asarray(matrices["mass"], dtype=float)
    if mass.ndim != 2 or mass.shape[0] != mass.shape[1]:
        raise ValueError("Cummins mass matrix must be square.")
    ndof = mass.shape[0]
    external_force = np.asarray(external_force, dtype=float)
    if external_force.shape != (len(time_s), ndof):
        raise ValueError(f"External force shape must be ({len(time_s)}, {ndof}), got {external_force.shape}.")
    if np.max(np.abs(external_force)) == 0.0:
        zeros = np.zeros((len(time_s), ndof), dtype=float)
        return {"q": zeros.copy(), "qd": zeros.copy(), "memory_force": zeros.copy(), "dt_s": dt_s}

    omega = matrices["omega_rad_s"]
    radiation = matrices["radiation_damping"]
    radiation_weights = matrices["radiation_weights"]
    mass_inv = inverse_square_matrix(mass)
    memory_count = len(omega)
    y = np.zeros(2 * ndof + 2 * memory_count * ndof, dtype=float)
    q_hist = np.zeros((len(time_s), ndof), dtype=float)
    qd_hist = np.zeros((len(time_s), ndof), dtype=float)
    memory_force_hist = np.zeros((len(time_s), ndof), dtype=float)

    def rhs(state: np.ndarray, external_force: np.ndarray) -> np.ndarray:
        q = state[:ndof]
        qd = state[ndof : 2 * ndof]
        memory = state[2 * ndof :].reshape(2, memory_count, ndof)
        cos_state = memory[0]
        sin_state = memory[1]
        memory_force = np.einsum("k,kij,kj->i", radiation_weights, radiation, cos_state)
        force = external_force.copy()
        force -= matrix_vector_product(matrices["linear_damping"], qd)
        force -= matrix_vector_product(matrices["restoring"], q)
        force -= memory_force
        qdd = matrix_vector_product(mass_inv, force)
        cos_dot = qd[None, :] - omega[:, None] * sin_state
        sin_dot = omega[:, None] * cos_state
        return np.concatenate([qd, qdd, cos_dot.reshape(-1), sin_dot.reshape(-1)])

    for idx, t_abs in enumerate(time_s):
        q_hist[idx, :] = y[:ndof]
        qd_hist[idx, :] = y[ndof : 2 * ndof]
        memory = y[2 * ndof :].reshape(2, memory_count, ndof)
        memory_force_hist[idx, :] = np.einsum("k,kij,kj->i", radiation_weights, radiation, memory[0])
        if idx == len(time_s) - 1:
            break
        h = float(time_s[idx + 1] - t_abs)
        force_0 = external_force[idx, :]
        force_1 = external_force[idx + 1, :]
        force_half = 0.5 * (force_0 + force_1)
        k1 = rhs(y, force_0)
        k2 = rhs(y + 0.5 * h * k1, force_half)
        k3 = rhs(y + 0.5 * h * k2, force_half)
        k4 = rhs(y + h * k3, force_1)
        y = y + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return {"q": q_hist, "qd": qd_hist, "memory_force": memory_force_hist, "dt_s": dt_s}


def generalized_leg_force_from_chrono(sim: dict[str, Any], target_time_s: np.ndarray, include_lock_reaction: bool = False) -> dict[str, Any]:
    chrono_time = np.array(sim["time_s"], dtype=float)
    fleg_samples = np.zeros((len(chrono_time), 3), dtype=float)
    contact_sum = np.zeros((len(chrono_time), 3), dtype=float)
    horizontal_samples = np.zeros((len(chrono_time), 2), dtype=float)
    for leg_id, xyz in sim["forces"]["leg_contact_force_xyz_n"].items():
        cf_x = np.array(xyz["x"], dtype=float)
        cf_y = np.array(xyz["y"], dtype=float)
        cf_z = np.array(xyz["z"], dtype=float)
        px = np.array(sim["feet"]["position_m"][leg_id]["x_m"], dtype=float)
        py = np.array(sim["feet"]["position_m"][leg_id]["y_m"], dtype=float)
        platform_fz = -cf_z
        fleg_samples[:, 0] += platform_fz
        fleg_samples[:, 1] += py * platform_fz
        fleg_samples[:, 2] += -px * platform_fz
        contact_sum[:, 0] += cf_z
        contact_sum[:, 1] += py * cf_z
        contact_sum[:, 2] += px * cf_z
        horizontal_samples[:, 0] += cf_x
        horizontal_samples[:, 1] += cf_y
    contact_platform_samples = fleg_samples.copy()
    lock_samples = np.zeros((len(chrono_time), 3), dtype=float)
    lock_reaction = sim.get("forces", {}).get("lock_reaction_force_xyz_n")
    lock_torque = sim.get("forces", {}).get("lock_reaction_torque_xyz_nm")
    lock_point = sim.get("mechanism", {}).get("lock_point_position_m")
    if include_lock_reaction and lock_reaction and lock_torque and lock_point:
        fr_x = np.array(lock_reaction["x"], dtype=float)
        fr_y = np.array(lock_reaction["y"], dtype=float)
        fr_z = np.array(lock_reaction["z"], dtype=float)
        tr_x = np.array(lock_torque["x"], dtype=float)
        tr_y = np.array(lock_torque["y"], dtype=float)
        px = np.array(lock_point["x_m"], dtype=float)
        py = np.array(lock_point["y_m"], dtype=float)
        pz = np.array(lock_point["z_m"], dtype=float)
        platform_fx = -fr_x
        platform_fy = -fr_y
        platform_fz = -fr_z
        platform_tx = -tr_x
        platform_ty = -tr_y
        lock_samples[:, 0] = platform_fz
        lock_samples[:, 1] = py * platform_fz - pz * platform_fy + platform_tx
        lock_samples[:, 2] = pz * platform_fx - px * platform_fz + platform_ty
        fleg_samples += lock_samples
    residual = {
        "max_vertical_action_reaction_residual_n": float(np.max(np.abs(contact_platform_samples[:, 0] + contact_sum[:, 0]))) if len(chrono_time) else 0.0,
        "max_roll_moment_residual_nm": float(np.max(np.abs(contact_platform_samples[:, 1] + contact_sum[:, 1]))) if len(chrono_time) else 0.0,
        "max_pitch_moment_residual_nm": float(np.max(np.abs(contact_platform_samples[:, 2] - contact_sum[:, 2]))) if len(chrono_time) else 0.0,
        "max_omitted_horizontal_contact_force_n": float(np.max(np.sqrt(horizontal_samples[:, 0] ** 2 + horizontal_samples[:, 1] ** 2))) if len(chrono_time) else 0.0,
        "lock_reaction_included": bool(include_lock_reaction and lock_reaction and lock_torque and lock_point),
        "max_lock_vertical_platform_force_n": float(np.max(np.abs(lock_samples[:, 0]))) if len(chrono_time) else 0.0,
        "max_lock_roll_platform_moment_nm": float(np.max(np.abs(lock_samples[:, 1]))) if len(chrono_time) else 0.0,
        "max_lock_pitch_platform_moment_nm": float(np.max(np.abs(lock_samples[:, 2]))) if len(chrono_time) else 0.0,
        "sign_convention": "Chrono contact and lock reactions are forces on rocket/footpad. Platform generalized load uses the equal and opposite load.",
    }


def _deck_normal_from_rpy(sim: dict[str, Any], sample_count: int) -> np.ndarray:
    deck = sim.get("deck", {})
    roll = np.asarray(deck.get("roll_rad", np.zeros(sample_count)), dtype=float)
    pitch = np.asarray(deck.get("pitch_rad", np.zeros(sample_count)), dtype=float)
    yaw = np.asarray(deck.get("yaw_rad", np.zeros(sample_count)), dtype=float)
    if len(roll) != sample_count or len(pitch) != sample_count or len(yaw) != sample_count:
        raise ValueError("Chrono deck rotation arrays must match the force sample count.")
    cr = np.cos(0.5 * roll)
    sr = np.sin(0.5 * roll)
    cp = np.cos(0.5 * pitch)
    sp = np.sin(0.5 * pitch)
    cy = np.cos(0.5 * yaw)
    sy = np.sin(0.5 * yaw)
    qw = cr * cp * cy - sr * sp * sy
    qx = sr * cp * cy + cr * sp * sy
    qy = cr * sp * cy - sr * cp * sy
    qz = cr * cp * sy + sr * sp * cy
    normal = np.column_stack(
        [
            2.0 * (qx * qz + qw * qy),
            2.0 * (qy * qz - qw * qx),
            1.0 - 2.0 * (qx**2 + qy**2),
        ]
    )
    norm = np.linalg.norm(normal, axis=1)
    normal /= np.maximum(norm[:, None], 1.0e-12)
    return normal


def generalized_leg_force_from_chrono_6dof(
    sim: dict[str, Any],
    target_time_s: np.ndarray,
    include_lock_reaction: bool = False,
    footpad_radius_m: float = 0.0,
) -> dict[str, Any]:
    chrono_time = np.asarray(sim["time_s"], dtype=float)
    sample_count = len(chrono_time)
    platform_samples = np.zeros((sample_count, 6), dtype=float)
    rocket_samples = np.zeros((sample_count, 6), dtype=float)
    contact_platform_samples = np.zeros((sample_count, 6), dtype=float)
    contact_rocket_samples = np.zeros((sample_count, 6), dtype=float)
    deck_normal = _deck_normal_from_rpy(sim, sample_count)

    for leg_id, xyz in sim["forces"]["leg_contact_force_xyz_n"].items():
        rocket_force = np.column_stack(
            [
                np.asarray(xyz["x"], dtype=float),
                np.asarray(xyz["y"], dtype=float),
                np.asarray(xyz["z"], dtype=float),
            ]
        )
        position = np.column_stack(
            [
                np.asarray(sim["feet"]["position_m"][leg_id]["x_m"], dtype=float),
                np.asarray(sim["feet"]["position_m"][leg_id]["y_m"], dtype=float),
                np.asarray(sim["feet"]["position_m"][leg_id]["z_m"], dtype=float),
            ]
        )
        if len(rocket_force) != sample_count or len(position) != sample_count:
            raise ValueError(f"Chrono force and position arrays for {leg_id} must match time_s.")
        contact_point = position - max(float(footpad_radius_m), 0.0) * deck_normal
        platform_force = -rocket_force
        rocket_moment = np.cross(contact_point, rocket_force)
        platform_moment = np.cross(contact_point, platform_force)
        rocket_generalized = np.column_stack([rocket_force, rocket_moment])
        platform_generalized = np.column_stack([platform_force, platform_moment])
        contact_rocket_samples += rocket_generalized
        contact_platform_samples += platform_generalized
        rocket_samples += rocket_generalized
        platform_samples += platform_generalized

    lock_samples = np.zeros((sample_count, 6), dtype=float)
    lock_rocket_samples = np.zeros((sample_count, 6), dtype=float)
    lock_reaction = sim.get("forces", {}).get("lock_reaction_force_xyz_n")
    lock_torque = sim.get("forces", {}).get("lock_reaction_torque_xyz_nm")
    lock_point = sim.get("mechanism", {}).get("lock_point_position_m")
    lock_available = bool(include_lock_reaction and lock_reaction and lock_torque and lock_point)
    if lock_available:
        rocket_force = np.column_stack(
            [
                np.asarray(lock_reaction["x"], dtype=float),
                np.asarray(lock_reaction["y"], dtype=float),
                np.asarray(lock_reaction["z"], dtype=float),
            ]
        )
        rocket_torque = np.column_stack(
            [
                np.asarray(lock_torque["x"], dtype=float),
                np.asarray(lock_torque["y"], dtype=float),
                np.asarray(lock_torque["z"], dtype=float),
            ]
        )
        position = np.column_stack(
            [
                np.asarray(lock_point["x_m"], dtype=float),
                np.asarray(lock_point["y_m"], dtype=float),
                np.asarray(lock_point["z_m"], dtype=float),
            ]
        )
        if len(rocket_force) != sample_count or len(rocket_torque) != sample_count or len(position) != sample_count:
            raise ValueError("Chrono lock force, torque and point arrays must match time_s.")
        platform_force = -rocket_force
        platform_torque = -rocket_torque
        rocket_moment = np.cross(position, rocket_force) + rocket_torque
        platform_moment = np.cross(position, platform_force) + platform_torque
        lock_rocket_samples = np.column_stack([rocket_force, rocket_moment])
        lock_samples = np.column_stack([platform_force, platform_moment])
        rocket_samples += lock_rocket_samples
        platform_samples += lock_samples

    residual = platform_samples + rocket_samples
    force_residual = np.max(np.abs(residual[:, :3]), axis=0) if sample_count else np.zeros(3)
    moment_residual = np.max(np.abs(residual[:, 3:]), axis=0) if sample_count else np.zeros(3)
    horizontal_contact = np.linalg.norm(contact_platform_samples[:, :2], axis=1) if sample_count else np.zeros(0)
    audit = {
        "max_surge_action_reaction_residual_n": float(force_residual[0]),
        "max_sway_action_reaction_residual_n": float(force_residual[1]),
        "max_vertical_action_reaction_residual_n": float(force_residual[2]),
        "max_roll_moment_residual_nm": float(moment_residual[0]),
        "max_pitch_moment_residual_nm": float(moment_residual[1]),
        "max_yaw_moment_residual_nm": float(moment_residual[2]),
        "max_omitted_horizontal_contact_force_n": 0.0,
        "max_horizontal_contact_force_fed_back_n": float(np.max(horizontal_contact)) if sample_count else 0.0,
        "horizontal_force_feedback_included": True,
        "lock_reaction_included": lock_available,
        "max_lock_vertical_platform_force_n": float(np.max(np.abs(lock_samples[:, 2]))) if sample_count else 0.0,
        "max_lock_roll_platform_moment_nm": float(np.max(np.abs(lock_samples[:, 3]))) if sample_count else 0.0,
        "max_lock_pitch_platform_moment_nm": float(np.max(np.abs(lock_samples[:, 4]))) if sample_count else 0.0,
        "max_lock_yaw_platform_moment_nm": float(np.max(np.abs(lock_samples[:, 5]))) if sample_count else 0.0,
        "contact_application_point": "Chrono spherical footpad center minus radius along the prescribed deck normal.",
        "coordinate_frame": "Chrono world axes aligned with the HAMS reference axes; moments are about XR=(0,0,0).",
        "sign_convention": "Chrono contact and lock reactions act on the rocket/footpads. Platform generalized load is the equal and opposite [Fx,Fy,Fz,Mx,My,Mz].",
    }
    target = np.column_stack(
        [np.interp(target_time_s, chrono_time, platform_samples[:, column]) for column in range(6)]
    )
    return {
        "time_s": target_time_s,
        "values_6dof": target,
        "samples_time_s": chrono_time,
        "samples_6dof": platform_samples,
        "force_audit": audit,
        "summary": {
            "max_surge_platform_force_mn": float(np.max(np.abs(platform_samples[:, 0])) / 1.0e6) if sample_count else 0.0,
            "max_sway_platform_force_mn": float(np.max(np.abs(platform_samples[:, 1])) / 1.0e6) if sample_count else 0.0,
            "max_downward_platform_force_mn": float(np.max(np.abs(np.minimum(platform_samples[:, 2], 0.0))) / 1.0e6) if sample_count else 0.0,
            "max_roll_moment_mnm": float(np.max(np.abs(platform_samples[:, 3])) / 1.0e6) if sample_count else 0.0,
            "max_pitch_moment_mnm": float(np.max(np.abs(platform_samples[:, 4])) / 1.0e6) if sample_count else 0.0,
            "max_yaw_moment_mnm": float(np.max(np.abs(platform_samples[:, 5])) / 1.0e6) if sample_count else 0.0,
            "max_lock_vertical_platform_force_mn": audit["max_lock_vertical_platform_force_n"] / 1.0e6,
            "max_lock_roll_platform_moment_mnm": audit["max_lock_roll_platform_moment_nm"] / 1.0e6,
            "max_lock_pitch_platform_moment_mnm": audit["max_lock_pitch_platform_moment_nm"] / 1.0e6,
            "max_lock_yaw_platform_moment_mnm": audit["max_lock_yaw_platform_moment_nm"] / 1.0e6,
        },
    }


def leg_force_series_for_json(time_s: np.ndarray, values: np.ndarray) -> dict[str, Any]:
    return {
        "time_s": time_s.tolist(),
        "force_heave_n": values[:, 0].tolist(),
        "moment_roll_nm": values[:, 1].tolist(),
        "moment_pitch_nm": values[:, 2].tolist(),
    }


def leg_force_series_for_json_6dof(time_s: np.ndarray, values: np.ndarray) -> dict[str, Any]:
    if values.shape[1] != 6:
        raise ValueError("6DOF generalized force serialization requires six columns.")
    return {
        "time_s": time_s.tolist(),
        "force_surge_n": values[:, 0].tolist(),
        "force_sway_n": values[:, 1].tolist(),
        "force_heave_n": values[:, 2].tolist(),
        "moment_roll_nm": values[:, 3].tolist(),
        "moment_pitch_nm": values[:, 4].tolist(),
        "moment_yaw_nm": values[:, 5].tolist(),
    }


def rocket_energy_diagnostic(config: dict[str, Any], chrono_sim: dict[str, Any]) -> dict[str, Any]:
    rocket = config["rocket"]
    mass = float(rocket["landing_mass_kg"])
    inertia = rocket["inertia_kg_m2"]
    vz = np.array(chrono_sim["rocket"]["vertical_velocity_m_s"], dtype=float)
    roll_rate = np.array(chrono_sim["rocket"]["roll_rate_rad_s"], dtype=float)
    pitch_rate = np.array(chrono_sim["rocket"]["pitch_rate_rad_s"], dtype=float)
    yaw_rate = np.array(chrono_sim["rocket"]["yaw_rate_rad_s"], dtype=float)
    kinetic = (
        0.5 * mass * vz**2
        + 0.5 * float(inertia["roll_x"]) * roll_rate**2
        + 0.5 * float(inertia["pitch_y"]) * pitch_rate**2
        + 0.5 * float(inertia["yaw_z"]) * yaw_rate**2
    )
    initial = float(kinetic[0] / 1000.0) if len(kinetic) else 0.0
    final = float(kinetic[-1] / 1000.0) if len(kinetic) else 0.0
    peak_after_contact = float(np.max(kinetic) / 1000.0) if len(kinetic) else 0.0
    return {
        "initial_kinetic_energy_kj": initial,
        "final_kinetic_energy_kj": final,
        "peak_kinetic_energy_kj": peak_after_contact,
        "final_over_initial": final / initial if initial > 0.0 else None,
        "trend": "diagnostic_only_includes_rocket_vertical_and_rotational_kinetic_energy",
        "kinetic_energy_decreased": bool(initial > 0.0 and final < initial),
        "status": "incomplete_energy_budget",
        "pass": None,
        "missing_terms": ["horizontal kinetic energy", "potential and elastic energy", "platform and radiation energy", "external work and dissipation"],
    }


def run_chrono(config: dict[str, Any], motion: DeckMotion, label: str) -> dict[str, Any]:
    log_progress(f"Running PyChrono two-way source case: {label}")
    return ChronoOneWayLegModel(config, motion).run()


def run_feedback_case(
    case_id: str,
    config: dict[str, Any],
    wang: dict[str, Any],
    matrices: dict[str, Any],
    iterations: int,
    coupling_dt_s: float,
) -> dict[str, Any]:
    start = float(config["solver"]["start_s"])
    end = float(config["solver"]["end_s"])
    time_s = make_time_grid(start, end, coupling_dt_s)
    baseline_sim, q_base, qd_base = baseline_arrays(wang, case_id, time_s)
    offset = baseline_sim["offset"]
    current_q = q_base.copy()
    current_qd = qd_base.copy()
    current_motion = deck_motion_from_wang_raw(wang, case_id)
    zero_force = np.zeros((len(time_s), 3), dtype=float)
    zero_correction = solve_cummins_leg_correction(matrices, time_s, zero_force, coupling_dt_s)
    iteration_rows: list[dict[str, Any]] = []
    final_chrono: dict[str, Any] | None = None
    final_force = zero_force
    final_correction = zero_correction

    for iteration in range(1, iterations + 1):
        chrono_sim = run_chrono(config, current_motion, f"{case_id} iteration {iteration}/{iterations}")
        force = generalized_leg_force_from_chrono(chrono_sim, time_s)
        correction = solve_cummins_leg_correction(matrices, time_s, force["values_3dof"], coupling_dt_s)
        current_q = q_base + correction["q"]
        current_qd = qd_base + correction["qd"]
        current_motion = deck_motion_from_arrays(time_s, current_q, current_qd, offset)
        final_chrono = chrono_sim
        final_force = force["values_3dof"]
        final_correction = correction
        iteration_rows.append(
            {
                "iteration": iteration,
                "chrono_summary": chrono_sim["summary"],
                "leg_force_summary": force["summary"],
                "force_audit": force["force_audit"],
                "platform_delta_summary": peak_summary(correction["q"], correction["qd"]),
                "rocket_energy": rocket_energy_diagnostic(config, chrono_sim),
            }
        )

    assert final_chrono is not None
    no_leg_max = float(np.max(np.abs(zero_correction["q"])))
    baseline_summary = peak_summary(q_base, qd_base)
    feedback_summary = peak_summary(current_q, current_qd)
    delta_summary = peak_summary(current_q - q_base, current_qd - qd_base)
    return {
        "id": case_id,
        "environment": baseline_sim["environment"],
        "offset": offset,
        "with_wave": baseline_sim["with_wave"],
        "with_plume": baseline_sim["with_plume"],
        "iterations_requested": iterations,
        "coupling_dt_s": coupling_dt_s,
        "baseline": {**values_to_named_series(time_s, q_base, qd_base), "summary": baseline_summary},
        "with_leg_feedback": {**values_to_named_series(time_s, current_q, current_qd), "summary": feedback_summary},
        "leg_induced_delta": {**values_to_named_series(time_s, current_q - q_base, current_qd - qd_base), "summary": delta_summary},
        "leg_generalized_force": leg_force_series_for_json(time_s, final_force),
        "final_iteration_chrono": final_chrono,
        "iterations": iteration_rows,
        "validation": {
            "no_leg_degeneracy": {
                "max_abs_zero_force_correction": no_leg_max,
                "pass": no_leg_max < 1.0e-12,
            },
            "force_reciprocity": iteration_rows[-1]["force_audit"],
            "rocket_energy": iteration_rows[-1]["rocket_energy"],
        },
    }


def compare_peak_change(case_result: dict[str, Any]) -> dict[str, Any]:
    base = case_result["baseline"]["summary"]
    coupled = case_result["with_leg_feedback"]["summary"]
    induced = case_result["leg_induced_delta"]["summary"]
    return {
        "heave_peak_delta_m": coupled["heave_peak_m"] - base["heave_peak_m"],
        "roll_peak_delta_deg": coupled["roll_peak_deg"] - base["roll_peak_deg"],
        "pitch_peak_delta_deg": coupled["pitch_peak_deg"] - base["pitch_peak_deg"],
        "heave_peak_relative_delta": (coupled["heave_peak_m"] - base["heave_peak_m"]) / max(base["heave_peak_m"], 1.0e-12),
        "roll_peak_relative_delta": (coupled["roll_peak_deg"] - base["roll_peak_deg"]) / max(base["roll_peak_deg"], 1.0e-12),
        "pitch_peak_relative_delta": (coupled["pitch_peak_deg"] - base["pitch_peak_deg"]) / max(base["pitch_peak_deg"], 1.0e-12),
        "leg_induced_heave_peak_m": induced["heave_peak_m"],
        "leg_induced_roll_peak_deg": induced["roll_peak_deg"],
        "leg_induced_pitch_peak_deg": induced["pitch_peak_deg"],
    }


def run_time_step_convergence(
    case_id: str,
    base_config: dict[str, Any],
    wang: dict[str, Any],
    matrices: dict[str, Any],
    coupling_dt_s: float,
) -> dict[str, Any]:
    fine_config = copy.deepcopy(base_config)
    fine_config["solver"]["time_step_s"] = float(base_config["solver"]["time_step_s"]) * 0.5
    fine_config["solver"]["output_step_s"] = float(base_config["solver"]["output_step_s"])
    start = float(fine_config["solver"]["start_s"])
    end = float(fine_config["solver"]["end_s"])
    fine_time_s = make_time_grid(start, end, coupling_dt_s * 0.5)
    baseline_sim, q_base, qd_base = baseline_arrays(wang, case_id, fine_time_s)
    motion = deck_motion_from_wang_raw(wang, case_id)
    fine_chrono = run_chrono(fine_config, motion, f"{case_id} convergence half Chrono dt")
    fine_force = generalized_leg_force_from_chrono(fine_chrono, fine_time_s)
    fine_correction = solve_cummins_leg_correction(matrices, fine_time_s, fine_force["values_3dof"], coupling_dt_s * 0.5)
    fine_q = q_base + fine_correction["q"]
    fine_qd = qd_base + fine_correction["qd"]
    return {
        "case_id": case_id,
        "half_chrono_time_step_s": fine_config["solver"]["time_step_s"],
        "half_cummins_time_step_s": coupling_dt_s * 0.5,
        "chrono_summary": fine_chrono["summary"],
        "leg_force_summary": fine_force["summary"],
        "platform_summary": peak_summary(fine_q, fine_qd),
    }


def convergence_validation(reference: dict[str, Any], fine: dict[str, Any] | None) -> dict[str, Any]:
    if fine is None:
        return {"enabled": False, "pass": None}
    ref_chrono = reference["final_iteration_chrono"]["summary"]
    ref_platform = reference["with_leg_feedback"]["summary"]
    metrics = [
        ("max_leg_contact_force_kn", ref_chrono["max_leg_contact_force_kn"], fine["chrono_summary"]["max_leg_contact_force_kn"]),
        ("max_leg_stroke_m", ref_chrono["max_leg_stroke_m"], fine["chrono_summary"]["max_leg_stroke_m"]),
        ("heave_peak_m", ref_platform["heave_peak_m"], fine["platform_summary"]["heave_peak_m"]),
        ("roll_peak_deg", ref_platform["roll_peak_deg"], fine["platform_summary"]["roll_peak_deg"]),
        ("pitch_peak_deg", ref_platform["pitch_peak_deg"], fine["platform_summary"]["pitch_peak_deg"]),
    ]
    rows = []
    passed = True
    for name, coarse, fine_value in metrics:
        rel = abs(fine_value - coarse) / max(abs(fine_value), abs(coarse), 1.0e-12)
        ok = rel <= 0.10
        rows.append({"metric": name, "coarse": coarse, "fine": fine_value, "relative_difference": rel, "pass": ok})
        passed = passed and ok
    return {
        "enabled": True,
        "case_id": fine["case_id"],
        "tolerance": 0.10,
        "checks": rows,
        "pass": passed,
    }


def build_validation(simulations: dict[str, Any], convergence: dict[str, Any] | None) -> dict[str, Any]:
    force_checks = {}
    energy_checks = {}
    no_leg_checks = {}
    peak_changes = {}
    all_force_pass = True
    all_no_leg_pass = True
    for case_id, sim in simulations.items():
        force = sim["validation"]["force_reciprocity"]
        force_pass = (
            force["max_vertical_action_reaction_residual_n"] < 1.0e-6
            and force["max_roll_moment_residual_nm"] < 1.0e-4
            and force["max_pitch_moment_residual_nm"] < 1.0e-4
        )
        no_leg_pass = bool(sim["validation"]["no_leg_degeneracy"]["pass"])
        force_checks[case_id] = {**force, "pass": force_pass}
        energy_checks[case_id] = {**sim["validation"]["rocket_energy"], "pass": None, "status": "incomplete_energy_budget"}
        no_leg_checks[case_id] = sim["validation"]["no_leg_degeneracy"]
        peak_changes[case_id] = compare_peak_change(sim)
        all_force_pass = all_force_pass and force_pass
        all_no_leg_pass = all_no_leg_pass and no_leg_pass
    bow_change = abs(peak_changes.get("wave_bow_15m", {}).get("leg_induced_pitch_peak_deg", 0.0))
    port_change = abs(peak_changes.get("wave_port_15m", {}).get("leg_induced_roll_peak_deg", 0.0))
    eccentric_response = {
        "wave_bow_15m_pitch_peak_delta_deg": bow_change,
        "wave_port_15m_roll_peak_delta_deg": port_change,
        "threshold_deg": 1.0e-3,
        "pass": bow_change > 1.0e-3 and port_change > 1.0e-3,
    }
    return {
        "rhs_composition": {
            "form": "q_total = q_Wang(F_wave + F_plume) + delta_q(F_leg)",
            "equivalent_linear_equation": "(M + A_inf) qdd + C qd + K q + F_memory = F_wave + F_plume + F_leg",
            "no_leg_degeneracy_pass": all_no_leg_pass,
        },
        "force_reciprocity": {"cases": force_checks, "pass": all_force_pass},
        "energy_diagnostic": {"cases": energy_checks, "pass": None, "status": "incomplete_energy_budget"},
        "eccentric_response": eccentric_response,
        "time_step_convergence": convergence_validation(
            simulations[convergence["case_id"]] if convergence and convergence.get("case_id") in simulations else {},
            convergence,
        ),
        "peak_changes": peak_changes,
    }


def build_contract() -> dict[str, Any]:
    config = default_leg_model_config()
    return {
        "case_id": "Chrono_LeggedRecovery_TwoWayContract",
        "status": "interface_contract",
        "environment": chrono_environment_report(),
        "purpose": "Define the two-way Chrono <-> HAMS/Cummins force contract for the Stage 2 loose-coupling solver.",
        "platform_equation": {
            "dofs": ["heave", "roll", "pitch"],
            "coordinates": "z up; roll about +x; pitch about +y; generalized force vector [Fz, Mx, My]",
            "equation": "(M + A_inf) qdd + C qd + K q + F_memory = F_wave + F_plume + F_leg",
            "implemented_stage2_form": "q_total = q_Wang(F_wave + F_plume) + delta_q(F_leg), using linear superposition over the published Wang/HAMS baseline.",
        },
        "chrono_to_platform_force": {
            "input_from_chrono": [
                "per-footpad contact force in global frame",
                "per-footpad contact point in global frame",
                "per-footpad slip velocity and contact state",
            ],
            "mapping": [
                "F_contact is the force on the rocket/footpad.",
                "F_leg_z = sum(-F_contact_z_on_rocket)",
                "M_leg_x = sum(y_deck * -F_contact_z_on_rocket)",
                "M_leg_y = sum(-x_deck * -F_contact_z_on_rocket)",
            ],
            "sign_audit": "A positive upward Chrono contact force on the rocket becomes a negative vertical generalized force on the platform.",
        },
        "coupling_algorithm": [
            "Use Wang 2023 HAMS/Cummins response as the F_wave + F_plume baseline.",
            "Run Chrono on the current deck motion to obtain four-foot contact forces.",
            "Map Chrono contact reactions to F_leg generalized platform load.",
            "Solve a Cummins correction equation with zero initial correction and F_leg as the only new load.",
            "Repeat the loose-coupling pass when iterations > 1.",
        ],
        "acceptance_checks": {
            "force_reciprocity": "sum(platform generalized deck reaction) + sum(Chrono rocket contact action) must be zero within numerical tolerance after coordinate mapping.",
            "degeneration": "F_leg disabled must produce zero correction and therefore match Wang 2023 baseline exactly on the Stage 2 grid.",
            "eccentric_response": "Port/bow offset cases must alter roll/pitch relative to baseline.",
            "energy": "Rocket kinetic energy diagnostic should decay after touchdown because contact damping/friction/buffer remove energy.",
            "time_step_convergence": "The default report reruns the selected convergence case with half Chrono dt and half Cummins dt.",
        },
        "config": config,
        "leg_positions": leg_positions_from_config(config),
    }


def write_contract_js(data: dict[str, Any]) -> None:
    CONTRACT_JS.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT_JS.write_text(
        "window.CHRONO_TWO_WAY_CONTRACT_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {CONTRACT_JS}")


def write_report_js(report: dict[str, Any]) -> None:
    REPORT_JS.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JS.write_text(
        "window.CHRONO_TWO_WAY_DATA = " + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {REPORT_JS}")


def build_report(
    cases: list[str],
    iterations: int,
    coupling_dt_s: float,
    run_convergence: bool,
    convergence_case: str,
) -> dict[str, Any]:
    ensure_dirs()
    PROGRESS_LOG.write_text("", encoding="utf-8")
    log_progress("Loading Chrono leg configuration...")
    config = default_leg_model_config()
    log_progress("Checking PyChrono environment...")
    env = chrono_environment_report()
    if not env["available"]:
        write_json(CASE_ROOT / "validation" / "chrono-env-check.json", env)
        raise ChronoUnavailableError(json.dumps(env, ensure_ascii=False, indent=2))
    log_progress("Loading Wang 2023 HAMS/Cummins baseline...")
    wang = load_wang_response()
    log_progress("Loading HAMS radiation damping matrices...")
    matrices = load_cummins_matrices(wang)
    simulations = {}
    for case_id in cases:
        log_progress(f"Building two-way loose-coupling case: {case_id}")
        simulations[case_id] = run_feedback_case(case_id, config, wang, matrices, iterations, coupling_dt_s)
    convergence = None
    if run_convergence and convergence_case in simulations:
        log_progress(f"Running time-step convergence check: {convergence_case}")
        convergence = run_time_step_convergence(convergence_case, config, wang, matrices, coupling_dt_s)
    report = {
        "case_id": "Chrono_LeggedRecovery_TwoWay",
        "title": "Two-way loose coupling: HAMS/Cummins platform response with Chrono leg-reaction feedback",
        "status": "simulated",
        "environment": env,
        "coupling": {
            "mode": "two_way_loose_linear_correction",
            "platform_source": str(WANG_RESPONSE),
            "platform_solver": "HAMS/Cummins Wang 2023 surrogate plus Cummins F_leg correction",
            "leg_solver": "Project Chrono / PyChrono",
            "fallback_to_handwritten_contact": False,
            "rhs": "F_wave + F_plume from Wang baseline; F_leg from Chrono contact force mapped into Cummins correction.",
            "limitations": [
                "This is loose coupling by iteration, not a monolithic strong stepper.",
                "Only heave/roll/pitch platform DOFs are fed back in Stage 2.",
                "Horizontal footpad contact forces are audited but not injected because the reduced platform model omits surge/sway/yaw.",
            ],
        },
        "config": config,
        "leg_positions": leg_positions_from_config(config),
        "hydrodynamic_sample": {
            "omega_rad_s": matrices["omega_rad_s"].tolist(),
            "mass_3dof": matrices["mass"].tolist(),
            "a_inf_3dof": matrices["a_inf"].tolist(),
            "rigid_mass_3dof": matrices["rigid_mass"].tolist(),
            "restoring_3dof": matrices["restoring"].tolist(),
            "linear_damping_3dof": matrices["linear_damping"].tolist(),
        },
        "simulations": simulations,
        "validation": build_validation(simulations, convergence),
        "acceptance_scope": {
            "stage_2_done": [
                "Chrono contact force is mapped to platform generalized loads.",
                "Cummins correction equation includes F_leg and preserves Wang F_wave + F_plume baseline by linear superposition.",
                "Four requested cases are generated when selected.",
                "No fallback to integrated_recovery_model.contact_forces.",
            ],
            "not_claimed": [
                "full six-DOF platform feedback",
                "strong monolithic Chrono/Cummins co-simulation",
                "Adams-equivalent real tripod linkage",
                "validated nonlinear hydraulic or hydropneumatic buffer law",
            ],
        },
    }
    write_json(CASE_ROOT / "chrono-two-way-report-data.json", report)
    write_json(CASE_ROOT / "Output" / "RocketRecovery" / "chrono-two-way-response.json", report)
    write_report_js(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Project Chrono to HAMS/Cummins two-way loose coupling.")
    parser.add_argument("command", choices=["contract", "check", "run", "report"], nargs="?", default="check")
    parser.add_argument("--case", action="append", choices=STAGE2_CASES, help="Run/check one case. Can be repeated.")
    parser.add_argument("--iterations", type=int, default=1, help="Loose-coupling iterations per case.")
    parser.add_argument("--coupling-dt", type=float, default=0.01, help="Cummins correction and report grid time step.")
    parser.add_argument("--skip-convergence", action="store_true", help="Skip the half-time-step convergence rerun.")
    parser.add_argument("--convergence-case", choices=STAGE2_CASES, default="wave_port_15m")
    args = parser.parse_args()

    if args.command == "contract":
        data = build_contract()
        write_json(CASE_ROOT / "chrono-two-way-contract.json", data)
        write_contract_js(data)
        print(f"Status: {data['status']}")
        print(f"Chrono available: {data['environment']['available']}")
        print(f"Report: {CASE_ROOT / 'chrono-two-way-contract.json'}")
        return

    cases = args.case or STAGE2_CASES
    if args.command == "check":
        env = chrono_environment_report()
        ensure_dirs()
        write_json(CASE_ROOT / "validation" / "chrono-two-way-env-check.json", env)
        print(f"Chrono available: {env['available']}")
        print(f"Report: {CASE_ROOT / 'validation' / 'chrono-two-way-env-check.json'}")
        return

    try:
        report = build_report(
            cases=cases,
            iterations=max(1, args.iterations),
            coupling_dt_s=args.coupling_dt,
            run_convergence=not args.skip_convergence,
            convergence_case=args.convergence_case,
        )
    except ChronoUnavailableError as exc:
        print(exc)
        raise SystemExit(2)
    print(f"Status: {report['status']}")
    print(f"Cases: {', '.join(cases)}")
    print(f"Report: {CASE_ROOT / 'chrono-two-way-report-data.json'}")


if __name__ == "__main__":
    main()
