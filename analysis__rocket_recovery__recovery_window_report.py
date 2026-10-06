from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, VISUALIZATION_DIR, parse_pnl, read_json, resolve_case, write_json
    from .deck_point_rao import build_deck_point_rao
    from .sea_state_response import build_sea_state_response
except ImportError:
    from common import ROOT, VISUALIZATION_DIR, parse_pnl, read_json, resolve_case, write_json
    from deck_point_rao import build_deck_point_rao
    from sea_state_response import build_sea_state_response


CERT_CASES = ["Cylinder", "DeepCwind", "HywindSpar", "Moonpool"]


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def mesh_to_three(mesh: dict[str, Any]) -> dict[str, Any]:
    vertices = [coord for node in mesh["nodes"] for coord in node]
    triangles: list[int] = []
    edges: list[int] = []
    for panel in mesh["panels"]:
        face = [index - 1 for index in panel]
        if len(face) == 3:
            triangles.extend(face)
        elif len(face) == 4:
            triangles.extend([face[0], face[1], face[2], face[0], face[2], face[3]])
        else:
            for i in range(1, len(face) - 1):
                triangles.extend([face[0], face[i], face[i + 1]])
        for i, a in enumerate(face):
            edges.extend([a, face[(i + 1) % len(face)]])
    return {
        "rawNodes": mesh["raw_nodes"],
        "rawPanels": mesh["raw_panels"],
        "vertices": vertices,
        "triangles": triangles,
        "edges": edges,
    }


def circular_angle_error_deg(truth: float, actual: float) -> float:
    diff = abs(actual - truth) % 360.0
    return min(diff, 360.0 - diff)


def compare_token(
    truth: str,
    actual: str,
    *,
    is_phase: bool = False,
    phase_amplitude: float | None = None,
) -> tuple[bool, float | None, float | None]:
    try:
        truth_value = float(truth.replace("D", "E").replace("d", "E"))
        actual_value = float(actual.replace("D", "E").replace("d", "E"))
    except ValueError:
        return truth == actual, None, None
    if math.isnan(truth_value) and math.isnan(actual_value):
        return True, 0.0, 0.0
    abs_error = abs(actual_value - truth_value)
    if is_phase:
        phase_error = circular_angle_error_deg(truth_value, actual_value)
        if phase_amplitude is not None and phase_amplitude < 1.0e-8:
            return True, phase_error, 0.0
        return phase_error <= 2.0, phase_error, phase_error / 180.0
    if truth_value != 0.0:
        rel_error = abs_error / abs(truth_value)
    else:
        rel_error = 0.0 if abs_error == 0.0 else math.inf
    return math.isclose(truth_value, actual_value, rel_tol=1.0e-1, abs_tol=1.0e-6), abs_error, rel_error


def phase_context(relative: Path, truth_tokens: list[str], actual_tokens: list[str], token_index: int, nbheading: int | None) -> tuple[bool, float | None]:
    suffix = relative.suffix.lower()
    name = relative.name
    idx = token_index - 1
    if suffix == ".rao" and nbheading and len(truth_tokens) >= 1 + 2 * nbheading:
        phase_start = 1 + nbheading
        phase_end = 1 + 2 * nbheading
        if phase_start <= idx < phase_end:
            amp_index = 1 + (idx - phase_start)
            try:
                truth_amp = float(truth_tokens[amp_index].replace("D", "E").replace("d", "E"))
                actual_amp = float(actual_tokens[amp_index].replace("D", "E").replace("d", "E"))
            except ValueError:
                return True, None
            return True, max(abs(truth_amp), abs(actual_amp))
    if name in {"Buoy.4", "Buoy.6p"} and len(truth_tokens) >= 7 and idx == 4:
        try:
            truth_amp = float(truth_tokens[3].replace("D", "E").replace("d", "E"))
            actual_amp = float(actual_tokens[3].replace("D", "E").replace("d", "E"))
        except ValueError:
            return True, None
        return True, max(abs(truth_amp), abs(actual_amp))
    return False, None


def benchmark_regression() -> dict[str, Any]:
    cert_root = ROOT / "CertTest"
    cases = []
    all_passed = True
    global_max_rel = 0.0
    global_max_abs = 0.0

    for cert in CERT_CASES:
        truth_dir = cert_root / cert / "Output_Benchmark"
        actual_dir = cert_root / cert / "Output"
        files = sorted(path for path in truth_dir.rglob("*") if path.is_file())
        case_result = {
            "case": cert,
            "files_checked": 0,
            "numeric_values_checked": 0,
            "text_values_checked": 0,
            "max_relative_error": 0.0,
            "max_absolute_error": 0.0,
            "failures": [],
            "passed": True,
        }

        for truth_path in files:
            relative = truth_path.relative_to(truth_dir)
            actual_path = actual_dir / relative
            if not actual_path.exists():
                case_result["failures"].append({"file": relative.as_posix(), "reason": "missing actual file"})
                case_result["passed"] = False
                continue
            truth_lines = truth_path.read_text(errors="replace").splitlines()
            actual_lines = actual_path.read_text(errors="replace").splitlines()
            nbheading = None
            case_result["files_checked"] += 1
            if len(truth_lines) != len(actual_lines):
                case_result["failures"].append(
                    {"file": relative.as_posix(), "reason": "line count differs", "truth": len(truth_lines), "actual": len(actual_lines)}
                )
                case_result["passed"] = False
                continue
            for line_index, (truth_line, actual_line) in enumerate(zip(truth_lines, actual_lines), start=1):
                if truth_line.strip().startswith("#NBHEADING"):
                    numbers = [token for token in truth_line.split() if token.lstrip("+-").isdigit()]
                    if numbers:
                        nbheading = int(numbers[-1])
                truth_tokens = truth_line.split()
                actual_tokens = actual_line.split()
                if len(truth_tokens) != len(actual_tokens):
                    case_result["failures"].append({"file": relative.as_posix(), "line": line_index, "reason": "token count differs"})
                    case_result["passed"] = False
                    continue
                for token_index, (truth_token, actual_token) in enumerate(zip(truth_tokens, actual_tokens), start=1):
                    is_phase, phase_amplitude = phase_context(relative, truth_tokens, actual_tokens, token_index, nbheading)
                    ok, abs_error, rel_error = compare_token(
                        truth_token,
                        actual_token,
                        is_phase=is_phase,
                        phase_amplitude=phase_amplitude,
                    )
                    if abs_error is None:
                        case_result["text_values_checked"] += 1
                    else:
                        case_result["numeric_values_checked"] += 1
                        case_result["max_absolute_error"] = max(case_result["max_absolute_error"], abs_error)
                        global_max_abs = max(global_max_abs, abs_error)
                        if math.isfinite(rel_error):
                            case_result["max_relative_error"] = max(case_result["max_relative_error"], rel_error)
                            global_max_rel = max(global_max_rel, rel_error)
                    if not ok and len(case_result["failures"]) < 25:
                        case_result["failures"].append(
                            {
                                "file": relative.as_posix(),
                                "line": line_index,
                                "token": token_index,
                                "truth": truth_token,
                                "actual": actual_token,
                                "abs_error": abs_error,
                                "rel_error": rel_error,
                            }
                        )
                        case_result["passed"] = False
        all_passed = all_passed and case_result["passed"]
        cases.append(case_result)

    return {
        "passed": all_passed,
        "cases": cases,
        "max_relative_error": global_max_rel,
        "max_absolute_error": global_max_abs,
    }


def report_validation(case_dir: Path, deck_rao: dict[str, Any], sea_response: dict[str, Any]) -> dict[str, Any]:
    config = read_json(case_dir / "platform_config.json")
    expected_freq_count = int(round((config["frequency"]["max_rad_s"] - config["frequency"]["min_rad_s"]) / config["frequency"]["step_rad_s"])) + 1
    expected_heading_count = len(config["headings_deg"])
    checks = [
        {
            "id": "deck_rao_frequency_count",
            "expected": expected_freq_count,
            "actual": len(deck_rao["frequencies_rad_s"]),
            "passed": len(deck_rao["frequencies_rad_s"]) == expected_freq_count,
        },
        {
            "id": "deck_rao_heading_count",
            "expected": expected_heading_count,
            "actual": len(deck_rao["headings_deg"]),
            "passed": len(deck_rao["headings_deg"]) == expected_heading_count,
        },
        {
            "id": "deck_point_count",
            "expected": len(config["deck_points"]),
            "actual": len(deck_rao["points"]),
            "passed": len(deck_rao["points"]) == len(config["deck_points"]),
        },
        {
            "id": "sea_state_count",
            "expected": len(config["sea_states"]),
            "actual": len(sea_response["summary"]),
            "passed": len(sea_response["summary"]) == len(config["sea_states"]),
        },
    ]
    return {"passed": all(check["passed"] for check in checks), "checks": checks}


def build_report(case_dir: Path) -> dict[str, Any]:
    deck_rao = build_deck_point_rao(case_dir)
    deck_path = case_dir / "Output" / "RocketRecovery" / "deck-point-rao.json"
    write_json(deck_path, deck_rao)

    sea_response = build_sea_state_response(case_dir, deck_path)
    sea_path = case_dir / "Output" / "RocketRecovery" / "sea-state-response.json"
    write_json(sea_path, sea_response)

    benchmark = benchmark_regression()
    write_json(case_dir / "validation" / "benchmark-regression.json", benchmark)

    self_check_path = case_dir / "validation" / "barge-self-check.json"
    self_check = read_json(self_check_path) if self_check_path.exists() else {"passed": False, "checks": []}
    validation = report_validation(case_dir, deck_rao, sea_response)
    write_json(case_dir / "validation" / "report-validation.json", validation)

    hull = parse_pnl(case_dir / "Input" / "HullMesh.pnl")
    waterplane = parse_pnl(case_dir / "Input" / "WaterplaneMesh.pnl")
    data = {
        "case": read_json(case_dir / "platform_config.json"),
        "paths": {
            "case_dir": rel(case_dir),
            "deck_rao": rel(deck_path),
            "sea_response": rel(sea_path),
            "self_check": rel(self_check_path),
            "benchmark_regression": rel(case_dir / "validation" / "benchmark-regression.json"),
        },
        "mesh": {
            "hull": mesh_to_three(hull),
            "waterplane": mesh_to_three(waterplane),
        },
        "deckRao": deck_rao,
        "seaResponse": sea_response,
        "validation": {
            "bargeSelfCheck": self_check,
            "benchmarkRegression": benchmark,
            "reportValidation": validation,
        },
    }
    return data


def write_visualization_data(data: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "window.ROCKET_RECOVERY_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the rocket recovery landing-leg HTML report data.")
    parser.add_argument("--case", default="Barge_120x50", help="Case name under RocketRecoveryCases or an explicit path.")
    parser.add_argument("--out", default=str(VISUALIZATION_DIR / "rocket-recovery-data.js"), help="Output JavaScript data file.")
    args = parser.parse_args()

    case_dir = resolve_case(args.case)
    data = build_report(case_dir)
    out = Path(args.out)
    write_visualization_data(data, out)
    print(f"Wrote {out}")
    print(f"Case: {data['case']['case_id']}")
    print(f"Benchmark regression passed: {data['validation']['benchmarkRegression']['passed']}")
    print(f"Barge self-check passed: {data['validation']['bargeSelfCheck']['passed']}")
    print(f"Report validation passed: {data['validation']['reportValidation']['passed']}")


if __name__ == "__main__":
    main()
