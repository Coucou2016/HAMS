from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

try:
    from .common import G, read_json, resolve_case, trapezoid_integral, write_json
except ImportError:
    from common import G, read_json, resolve_case, trapezoid_integral, write_json


def jonswap_spectrum(frequencies: list[float], hs_m: float, tp_s: float, gamma: float = 3.3) -> list[float]:
    wp = 2.0 * math.pi / tp_s
    raw = []
    for omega in frequencies:
        if omega <= 0.0:
            raw.append(0.0)
            continue
        sigma = 0.07 if omega <= wp else 0.09
        peak = math.exp(-((omega / wp - 1.0) ** 2) / (2.0 * sigma**2))
        value = G**2 * omega ** -5 * math.exp(-1.25 * (wp / omega) ** 4) * gamma**peak
        raw.append(value)

    current_m0 = trapezoid_integral(frequencies, raw)
    if current_m0 <= 0.0:
        return [0.0 for _ in frequencies]
    target_m0 = hs_m**2 / 16.0
    scale = target_m0 / current_m0
    return [value * scale for value in raw]


def spectrum_stats(frequencies: list[float], transfer_abs_squared: list[float], spectrum: list[float], duration_s: float) -> dict[str, float]:
    density = [h2 * s for h2, s in zip(transfer_abs_squared, spectrum)]
    m0 = trapezoid_integral(frequencies, density)
    m2 = trapezoid_integral(frequencies, [omega**2 * value for omega, value in zip(frequencies, density)])
    rms = math.sqrt(max(m0, 0.0))
    if m0 > 0.0 and m2 > 0.0:
        zero_crossing_period = 2.0 * math.pi * math.sqrt(m0 / m2)
        cycles = max(duration_s / zero_crossing_period, 1.0001)
        most_probable_max = rms * math.sqrt(2.0 * math.log(cycles))
    else:
        zero_crossing_period = 0.0
        most_probable_max = 0.0
    return {
        "rms": rms,
        "most_probable_max": most_probable_max,
        "m0": m0,
        "m2": m2,
        "zero_crossing_period_s": zero_crossing_period,
    }


def index_point_rows(deck_point: dict[str, Any]) -> dict[float, dict[float, dict[str, Any]]]:
    indexed: dict[float, dict[float, dict[str, Any]]] = {}
    for row in deck_point["rows"]:
        heading = float(row["heading_deg"])
        frequency = float(row["frequency_rad_s"])
        indexed.setdefault(heading, {})[frequency] = row
    return indexed


def amp_squared(row: dict[str, Any], group: str, axis: str) -> float:
    value = row[group][axis]["amp"]
    return value * value


def build_transfer_series(rows: dict[float, dict[str, Any]], frequencies: list[float], terms: list[tuple[str, str]]) -> list[float]:
    series = []
    for frequency in frequencies:
        row = rows[frequency]
        series.append(sum(amp_squared(row, group, axis) for group, axis in terms))
    return series


def build_sea_state_response(case_dir: Path, deck_rao_path: Path | None = None) -> dict[str, Any]:
    config = read_json(case_dir / "platform_config.json")
    deck_rao = read_json(deck_rao_path or (case_dir / "Output" / "RocketRecovery" / "deck-point-rao.json"))
    frequencies = [float(value) for value in deck_rao["frequencies_rad_s"]]
    headings = [float(value) for value in deck_rao["headings_deg"]]

    metrics = {
        "vertical_displacement_m": [("displacement_m", "z")],
        "vertical_velocity_m_s": [("velocity_m_s", "z")],
        "horizontal_displacement_m": [("displacement_m", "x"), ("displacement_m", "y")],
        "horizontal_velocity_m_s": [("velocity_m_s", "x"), ("velocity_m_s", "y")],
        "roll_rad": [("angles_rad", "roll")],
        "pitch_rad": [("angles_rad", "pitch")],
        "tilt_rad": [("angles_rad", "roll"), ("angles_rad", "pitch")],
        "roll_rate_rad_s": [("angle_rates_rad_s", "roll")],
        "pitch_rate_rad_s": [("angle_rates_rad_s", "pitch")],
        "tilt_rate_rad_s": [("angle_rates_rad_s", "roll"), ("angle_rates_rad_s", "pitch")],
    }

    points = []
    for point in deck_rao["points"]:
        indexed = index_point_rows(point)
        sea_states = []
        for sea_state in config["sea_states"]:
            spectrum = jonswap_spectrum(frequencies, sea_state["hs_m"], sea_state["tp_s"], sea_state.get("gamma", 3.3))
            heading_rows = []
            for heading in headings:
                rows = indexed[heading]
                metric_values = {}
                for metric, terms in metrics.items():
                    transfer = build_transfer_series(rows, frequencies, terms)
                    metric_values[metric] = spectrum_stats(frequencies, transfer, spectrum, sea_state.get("duration_s", 600.0))
                heading_rows.append({"heading_deg": heading, "metrics": metric_values})
            sea_states.append({"id": sea_state["id"], "definition": sea_state, "headings": heading_rows})
        points.append({"id": point["id"], "position_m": point["position_m"], "sea_states": sea_states})

    summary = []
    for sea_state in config["sea_states"]:
        worst = {"vertical_velocity_m_s": None, "tilt_rad": None, "horizontal_velocity_m_s": None}
        for point in points:
            state = next(item for item in point["sea_states"] if item["id"] == sea_state["id"])
            for heading_row in state["headings"]:
                for metric in worst:
                    value = heading_row["metrics"][metric]["most_probable_max"]
                    current = worst[metric]
                    if current is None or value > current["value"]:
                        worst[metric] = {
                            "value": value,
                            "point_id": point["id"],
                            "heading_deg": heading_row["heading_deg"],
                        }
        summary.append({"sea_state_id": sea_state["id"], "worst_mpm": worst})

    return {
        "case_id": config["case_id"],
        "source_deck_rao": str(deck_rao_path or (case_dir / "Output" / "RocketRecovery" / "deck-point-rao.json")),
        "spectrum": "JONSWAP scaled over the HAMS frequency grid to m0 = Hs^2/16.",
        "frequencies_rad_s": frequencies,
        "headings_deg": headings,
        "points": points,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert deck-point RAOs to sea-state response statistics.")
    parser.add_argument("--case", default="Barge_120x50", help="Case name under RocketRecoveryCases or an explicit path.")
    parser.add_argument("--deck-rao", default=None, help="Optional deck-point RAO JSON path.")
    parser.add_argument("--out", default=None, help="Optional output JSON path.")
    args = parser.parse_args()

    case_dir = resolve_case(args.case)
    data = build_sea_state_response(case_dir, Path(args.deck_rao) if args.deck_rao else None)
    out = Path(args.out) if args.out else case_dir / "Output" / "RocketRecovery" / "sea-state-response.json"
    write_json(out, data)
    print(f"Wrote {out}")
    print(f"Sea states: {len(data['summary'])}; points: {len(data['points'])}")


if __name__ == "__main__":
    main()
