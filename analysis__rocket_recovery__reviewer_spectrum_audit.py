"""Audit normalization using the archived production grid and computed samples."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from .sea_state_response import spectrum_band_audit


def audit(source: Path) -> dict:
    raw = source.read_bytes()
    report = json.loads(raw)
    omega = report["frequency_grids"]["random_synthesis"]["frequencies_rad_s"]
    comparison_bands = []
    for upper in (2.0, 5.0):
        grid = np.linspace(0.2, upper, round((upper - 0.2) / 0.001) + 1).tolist()
        for tp in (6.0, 8.0, 10.0):
            comparison_bands.append({"maximum_frequency_rad_s": upper, "tp_s": tp,
                                     **spectrum_band_audit(grid, 1.0, tp)})
    rows = []
    for case in report["cases"]:
        band = spectrum_band_audit(omega, case["hs_m"], case["tp_s"], case["gamma"])
        factor = band["full_to_band_response_scale"]
        metric = "landing_center.max_abs_vertical_velocity_m_s"
        values = np.asarray([sample[metric] for sample in case["samples"]])
        rows.append({"sea_state_id": case["sea_state_id"], "heading_deg": case["heading_deg"],
                     **band, "stored_sample_count": len(values),
                     "band_normalized_p95_velocity_m_s": float(np.quantile(values, 0.95)),
                     "full_normalized_in_band_p95_velocity_m_s": float(np.quantile(values * factor, 0.95))})
    return {"source": source.as_posix(), "source_sha256": hashlib.sha256(raw).hexdigest(),
            "frequency_min_rad_s": min(omega), "frequency_max_rad_s": max(omega),
            "method": "Exact linear rescaling of archived samples by sqrt(captured full-spectrum variance / target variance), with the same phases and transfer functions.",
            "scope": "Normalization sensitivity only. No response beyond the computed frequency band is supplied or inferred. This is not a new hydrodynamic or contact simulation.",
            "maximum_velocity_scale_change_fraction": max(abs(1 - r["full_to_band_response_scale"]) for r in rows),
            "comparison_bands": comparison_bands,
            "cases": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/wave-sensitivity-revision-600s.json"))
    parser.add_argument("--out", type=Path, default=Path("analysis/diagnostics/reviewer-spectrum-audit.json"))
    args = parser.parse_args()
    result = audit(args.source)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "cases"}, indent=2))


if __name__ == "__main__":
    main()
