from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    from .common import complex_to_amp_phase, read_json, read_motion_raos, resolve_case, write_json
except ImportError:
    from common import complex_to_amp_phase, read_json, read_motion_raos, resolve_case, write_json


COMPONENTS = {
    "displacement_m": ("x", "y", "z"),
    "velocity_m_s": ("x", "y", "z"),
    "angles_rad": ("roll", "pitch", "yaw"),
    "angle_rates_rad_s": ("roll", "pitch", "yaw"),
}


def value_record(value: complex) -> dict[str, float]:
    amp, phase = complex_to_amp_phase(value)
    return {
        "real": value.real,
        "imag": value.imag,
        "amp": amp,
        "phase_deg": phase,
    }


def transform_motion(dofs: dict[str, complex], point: list[float], frequency: float) -> dict[str, dict[str, complex]]:
    x, y, z = point
    surge = dofs["1"]
    sway = dofs["2"]
    heave = dofs["3"]
    roll = dofs["4"]
    pitch = dofs["5"]
    yaw = dofs["6"]

    displacement = {
        "x": surge + pitch * z - yaw * y,
        "y": sway + yaw * x - roll * z,
        "z": heave + roll * y - pitch * x,
    }
    velocity = {axis: 1j * frequency * value for axis, value in displacement.items()}
    angles = {"roll": roll, "pitch": pitch, "yaw": yaw}
    angle_rates = {axis: 1j * frequency * value for axis, value in angles.items()}
    return {
        "displacement_m": displacement,
        "velocity_m_s": velocity,
        "angles_rad": angles,
        "angle_rates_rad_s": angle_rates,
    }


def row_records(response: dict[str, dict[str, complex]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for group, axes in COMPONENTS.items():
        out[group] = {axis: value_record(response[group][axis]) for axis in axes}
    return out


def build_deck_point_rao(case_dir: Path) -> dict[str, Any]:
    config = read_json(case_dir / "platform_config.json")
    motion = read_motion_raos(case_dir)
    frequencies = motion["frequencies"]
    headings = motion["headings"]
    points = []

    for point in config["deck_points"]:
        position = [float(value) for value in point["position_m"]]
        rows = []
        for frequency in frequencies:
            for heading in headings:
                dofs = {dof: motion["dofs"][dof][(frequency, heading)] for dof in motion["dofs"]}
                transformed = transform_motion(dofs, position, frequency)
                rows.append(
                    {
                        "frequency_rad_s": frequency,
                        "heading_deg": heading,
                        **row_records(transformed),
                    }
                )
        points.append({"id": point["id"], "position_m": position, "rows": rows})

    return {
        "case_id": config["case_id"],
        "source_case": str(case_dir),
        "source_motion_files": "Output/Hydrostar_format/Motion_1..6.rao",
        "angular_motion_convention": "HAMS Hydrostar Motion_4..6 values are interpreted as radians per metre from raw DSPL.",
        "frequencies_rad_s": frequencies,
        "headings_deg": headings,
        "reference_point_m": config["reference_point_m"],
        "points": points,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Transform HAMS 6DOF motion RAOs to deck-point and landing-leg point RAOs.")
    parser.add_argument("--case", default="Barge_120x50", help="Case name under RocketRecoveryCases or an explicit path.")
    parser.add_argument("--out", default=None, help="Optional output JSON path.")
    args = parser.parse_args()

    case_dir = resolve_case(args.case)
    data = build_deck_point_rao(case_dir)
    out = Path(args.out) if args.out else case_dir / "Output" / "RocketRecovery" / "deck-point-rao.json"
    write_json(out, data)
    print(f"Wrote {out}")
    print(f"Points: {len(data['points'])}; frequencies: {len(data['frequencies_rad_s'])}; headings: {len(data['headings_deg'])}")


if __name__ == "__main__":
    main()
