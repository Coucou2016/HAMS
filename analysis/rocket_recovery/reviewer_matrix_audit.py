"""Inspect archived coefficients before any reciprocal symmetrization."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from .common import parse_hydrostar_rao


def matrix_checks(raw: np.ndarray, length_m: float) -> dict:
    if length_m <= 0 or raw.shape != (6, 6) or not np.isfinite(raw).all():
        raise ValueError("Require a finite 6x6 matrix and positive reference length")
    # Coordinates are [x,y,z,L*roll,L*pitch,L*yaw]; conjugate forces preserve work.
    scale = np.array([1, 1, 1, 1 / length_m, 1 / length_m, 1 / length_m])
    scaled = raw * scale[:, None] * scale[None, :]
    norm = float(np.linalg.norm(scaled, "fro"))
    antisymmetric = float(np.linalg.norm(scaled - scaled.T, "fro"))
    symmetric = (scaled + scaled.T) / 2
    eig = np.linalg.eigvalsh(symmetric)
    active = np.linalg.eigvalsh(symmetric[np.ix_([2, 3, 4], [2, 3, 4])])
    magnitude = float(np.max(np.abs(eig)))
    return {"raw_reciprocity_relative_frobenius": antisymmetric / norm if norm else 0.0,
            "scaled_symmetric_eigenvalues": eig.tolist(),
            "active_scaled_symmetric_eigenvalues": active.tolist(),
            "relative_minimum_eigenvalue": float(eig[0]) / magnitude if magnitude else 0.0,
            "pairs": [{"i": i + 1, "j": j + 1, "raw_ij": float(raw[i, j]),
                       "raw_ji": float(raw[j, i]), "absolute_difference": float(abs(raw[i, j] - raw[j, i]))}
                      for i in range(6) for j in range(i + 1, 6)]}


def audit(case: Path, length_m: float) -> dict:
    sources, results = [], {}
    for prefix in ("AddedMass", "WaveDamping"):
        frequencies, matrices = None, None
        for i in range(6):
            for j in range(6):
                path = case / "Output" / "Hydrostar_format" / f"{prefix}_{i+1}{j+1}.rao"
                parsed = parse_hydrostar_rao(path)
                axis = np.array([row["frequency"] for row in parsed["rows"]])
                if frequencies is None:
                    frequencies, matrices = axis, np.zeros((len(axis), 6, 6))
                if not np.array_equal(frequencies, axis):
                    raise ValueError(f"Frequency mismatch: {path}")
                matrices[:, i, j] = [row["amplitudes"][0] for row in parsed["rows"]]
                sources.append({"path": path.as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        rows = [{"frequency_rad_s": float(w), **matrix_checks(m, length_m)} for w, m in zip(frequencies, matrices)]
        results[prefix] = {"maximum_raw_reciprocity_relative_frobenius": max(r["raw_reciprocity_relative_frobenius"] for r in rows), "rows": rows}
    return {"case": case.as_posix(), "reference_length_m": length_m,
            "scaling": "Work-preserving coordinates [x,y,z,L*roll,L*pitch,L*yaw]; scaled matrix D*M*D, D=diag(1,1,1,1/L,1/L,1/L).",
            "scope": "Raw reciprocity and symmetric-part eigenvalues. Added mass need not be positive semidefinite at every frequency. Nonnegative damping alone does not establish consistency of A and B or full coupled-model passivity.",
            "sources": sources, "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, default=Path("RocketRecoveryCases/Barge_120x50/validation/hydrodynamic_runs/medium_local025_high5"))
    parser.add_argument("--length", type=float, default=120.0)
    parser.add_argument("--out", type=Path, default=Path("analysis/diagnostics/reviewer-matrix-audit.json"))
    args = parser.parse_args()
    result = audit(args.case, args.length)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v["maximum_raw_reciprocity_relative_frobenius"] for k, v in result["results"].items()}))


if __name__ == "__main__":
    main()
