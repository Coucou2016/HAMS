from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ROCKET_CASES_DIR = ROOT / "RocketRecoveryCases"
VISUALIZATION_DIR = ROOT / "visualization"

RHO = 1025.0
G = 9.80665

NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[DEde][-+]?\d+)?|NaN")


def resolve_case(case: str | Path) -> Path:
    path = Path(case)
    if path.is_absolute() or len(path.parts) > 1:
        return path.resolve()
    return (ROCKET_CASES_DIR / path).resolve()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_number(token: str) -> float:
    token = token.replace("D", "E").replace("d", "E")
    if token.lower() == "nan":
        return math.nan
    return float(token)


def numeric_tokens(line: str) -> list[str]:
    return NUMBER_RE.findall(line)


def fortran_float(value: float) -> str:
    return f"{value:.8E}".replace("E", "D")


def ensure_case_output_dirs(case_dir: Path) -> None:
    for subdir in [
        case_dir / "Input",
        case_dir / "Output" / "Hams_format",
        case_dir / "Output" / "Hydrostar_format",
        case_dir / "Output" / "Wamit_format",
        case_dir / "validation",
    ]:
        subdir.mkdir(parents=True, exist_ok=True)


def write_pnl(
    path: Path,
    title: str,
    nodes: list[tuple[float, float, float]],
    panels: list[list[int]],
    x_symmetry: int = 0,
    y_symmetry: int = 0,
) -> None:
    lines = [
        f"    --------------{title}---------------",
        "",
        "    # Number of Panels, Nodes, X-Symmetry and Y-Symmetry",
        f"{len(panels):12d}{len(nodes):12d}{x_symmetry:12d}{y_symmetry:12d}",
        "",
        "    #Start Definition of Node Coordinates     ! node_number   x   y   z",
    ]
    for idx, (x, y, z) in enumerate(nodes, start=1):
        lines.append(f"{idx:5d}{x:18.6f}{y:18.6f}{z:18.6f}")

    lines.extend(["    #End Definition of Node Coordinates", "", "    #Start Definition of Node Relations"])
    for idx, panel in enumerate(panels, start=1):
        indices = "".join(f"{node:10d}" for node in panel)
        lines.append(f"{idx:5d}{len(panel):5d}{indices}")

    lines.extend(["   #End Definition of Node Relations", "", f"    --------------End {title}---------------", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_pnl(path: Path) -> dict[str, Any]:
    lines = path.read_text(errors="replace").splitlines()

    header = None
    for line in lines:
        toks = numeric_tokens(line)
        if len(toks) < 4:
            continue
        vals = [int(float(tok)) for tok in toks[:4]]
        if vals[0] > 0 and vals[1] > 0:
            header = vals
            break
    if header is None:
        raise ValueError(f"Cannot find mesh header in {path}")

    panel_count, node_count, x_sym, y_sym = header
    node_marker = "Start Definition of Node Coordinates"
    panel_marker = "Start Definition of Node Relations"
    node_start = next(i + 1 for i, line in enumerate(lines) if node_marker in line)
    panel_start = next(i + 1 for i, line in enumerate(lines) if panel_marker in line)

    nodes: list[tuple[float, float, float]] = []
    i = node_start
    while len(nodes) < node_count and i < len(lines):
        toks = numeric_tokens(lines[i])
        if len(toks) >= 4:
            nodes.append((parse_number(toks[1]), parse_number(toks[2]), parse_number(toks[3])))
        i += 1

    panels: list[list[int]] = []
    i = panel_start
    while len(panels) < panel_count and i < len(lines):
        toks = numeric_tokens(lines[i])
        if len(toks) >= 5:
            n = int(float(toks[1]))
            panels.append([int(float(tok)) for tok in toks[2 : 2 + n]])
        i += 1

    if len(nodes) != node_count or len(panels) != panel_count:
        raise ValueError(f"Incomplete mesh in {path}: {len(nodes)}/{node_count} nodes, {len(panels)}/{panel_count} panels")

    return {
        "raw_nodes": node_count,
        "raw_panels": panel_count,
        "x_symmetry": x_sym,
        "y_symmetry": y_sym,
        "nodes": nodes,
        "panels": panels,
    }


def parse_hydrostar_rao(path: Path) -> dict[str, Any]:
    headings: list[float] = []
    metadata: dict[str, str] = {}
    rows: list[dict[str, Any]] = []
    in_rows = False

    for line in path.read_text(errors="replace").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#RAOTYPE"):
            metadata["type"] = stripped.split(":", 1)[-1].strip()
            continue
        if stripped.startswith("#COMPONENT"):
            metadata["component"] = stripped.split(":", 1)[-1].strip()
            continue
        if stripped.startswith("#UNIT"):
            metadata["unit"] = stripped.split(":", 1)[-1].strip()
            continue
        if stripped.startswith("#HEADING"):
            headings = [parse_number(token) for token in numeric_tokens(stripped)]
            continue
        if stripped.startswith("#---"):
            in_rows = True
            continue
        if stripped.startswith("#END"):
            break
        if not in_rows or stripped.startswith("#"):
            continue

        values = [parse_number(token) for token in numeric_tokens(stripped)]
        n = len(headings)
        if n == 0 or len(values) < 1 + 2 * n:
            continue
        frequency = values[0]
        if not math.isfinite(frequency) or frequency < 0.0:
            continue
        amplitudes = values[1 : 1 + n]
        phases = values[1 + n : 1 + 2 * n]
        rows.append({"frequency": frequency, "amplitudes": amplitudes, "phases_deg": phases})

    return {"headings": headings, "metadata": metadata, "rows": rows}


def hams_amp_phase_to_complex(amplitude: float, phase_deg: float) -> complex:
    phase = math.radians(phase_deg)
    return complex(-amplitude * math.sin(phase), -amplitude * math.cos(phase))


def complex_to_amp_phase(value: complex) -> tuple[float, float]:
    amplitude = abs(value)
    if amplitude == 0.0:
        return 0.0, 0.0
    phase = math.degrees(math.atan2(-value.real, -value.imag))
    if phase < 0.0:
        phase += 360.0
    return amplitude, phase


def read_motion_raos(case_dir: Path) -> dict[str, Any]:
    hydro_dir = case_dir / "Output" / "Hydrostar_format"
    dof_values: dict[str, dict[tuple[float, float], complex]] = {}
    frequencies: list[float] = []
    headings: list[float] = []
    metadata: dict[str, Any] = {}

    for dof in range(1, 7):
        path = hydro_dir / f"Motion_{dof}.rao"
        parsed = parse_hydrostar_rao(path)
        if not headings:
            headings = parsed["headings"]
        metadata[str(dof)] = parsed["metadata"]
        table: dict[tuple[float, float], complex] = {}
        for row in parsed["rows"]:
            frequency = row["frequency"]
            if frequency not in frequencies:
                frequencies.append(frequency)
            for heading, amplitude, phase in zip(headings, row["amplitudes"], row["phases_deg"]):
                table[(frequency, heading)] = hams_amp_phase_to_complex(amplitude, phase)
        dof_values[str(dof)] = table

    return {
        "frequencies": sorted(frequencies),
        "headings": headings,
        "dofs": dof_values,
        "metadata": metadata,
    }


def trapezoid_integral(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    total = 0.0
    for i in range(1, len(xs)):
        total += 0.5 * (ys[i - 1] + ys[i]) * (xs[i] - xs[i - 1])
    return total
