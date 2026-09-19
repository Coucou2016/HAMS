from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path

from generate_mesh_viewer import parse_pnl


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = Path(__file__).resolve().parent
NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[DEde][-+]?\d+)?|NaN")

DOF_LABELS = {
    "1": "Surge X",
    "2": "Sway Y",
    "3": "Heave Z",
    "4": "Roll Rx",
    "5": "Pitch Ry",
    "6": "Yaw Rz",
}

CASES = [
    {
        "name": "Cylinder",
        "slug": "cylinder",
        "case_dir": ROOT / "CertTest" / "Cylinder",
        "snapshot": "snapshots/cylinder-mesh.png",
        "summary": "规则垂直圆柱体算例，适合快速查看规则几何在不同浪向下的附加质量、阻尼、激励力和运动 RAO。",
    },
    {
        "name": "DeepCwind",
        "slug": "deepcwind",
        "case_dir": ROOT / "CertTest" / "DeepCwind",
        "snapshot": "snapshots/deepcwind-mesh.png",
        "summary": "DeepCwind / OC4 半潜式浮式风机平台算例，网格更复杂，用来查看工程型浮体在波浪频域中的响应。",
    },
]

GROUPS = [
    {
        "id": "addedMass",
        "title": "Added Mass Aii",
        "subtitle": "辐射问题得到的附加质量矩阵对角项，显示 6 自由度趋势。",
        "prefix": "AddedMass_",
        "items": ["11", "22", "33", "44", "55", "66"],
        "label_kind": "matrix",
        "y_label": "Amplitude",
    },
    {
        "id": "waveDamping",
        "title": "Radiation Damping Bii",
        "subtitle": "辐射阻尼矩阵对角项，随波频变化的能量耗散趋势。",
        "prefix": "WaveDamping_",
        "items": ["11", "22", "33", "44", "55", "66"],
        "label_kind": "matrix",
        "y_label": "Amplitude",
    },
    {
        "id": "excitation",
        "title": "Wave Excitation",
        "subtitle": "入射/绕射波引起的 6 自由度激励力与力矩幅值。",
        "prefix": "Excitation_",
        "items": ["1", "2", "3", "4", "5", "6"],
        "label_kind": "dof",
        "y_label": "Amplitude",
    },
    {
        "id": "motion",
        "title": "Motion RAO",
        "subtitle": "线性频域运动响应幅值，平移为 m/m，转动为 deg/m。",
        "prefix": "Motion_",
        "items": ["1", "2", "3", "4", "5", "6"],
        "label_kind": "dof",
        "y_label": "RAO amplitude",
    },
]


def parse_number(token: str) -> float:
    token = token.replace("D", "E").replace("d", "E")
    if token.lower() == "nan":
        return math.nan
    return float(token)


def finite_or_none(value: float) -> float | None:
    return value if math.isfinite(value) else None


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_control_file(path: Path) -> dict:
    values: dict[str, str | int | float] = {}
    text = path.read_text(errors="replace").splitlines()
    keys = {
        "waterdepth": "waterDepth",
        "input_frequency_type": "inputFrequencyType",
        "output_frequency_type": "outputFrequencyType",
        "number_of_frequencies": "configuredFrequencyCount",
        "minimum_frequency_wmin": "minimumFrequency",
        "frequency_step": "frequencyStep",
        "number_of_headings": "configuredHeadingCount",
        "minimum_heading": "minimumHeading",
        "heading_step": "headingStep",
        "number of threads": "threads",
    }

    for line in text:
        clean = line.split("#", 1)[0].strip()
        if not clean:
            continue
        lower = clean.lower()
        for needle, key in keys.items():
            if not lower.startswith(needle):
                continue
            match = NUMBER_RE.search(clean)
            if not match:
                continue
            number = parse_number(match.group(0))
            if key in {"configuredFrequencyCount", "configuredHeadingCount", "threads"}:
                values[key] = abs(int(number))
            else:
                values[key] = number

    depth = values.get("waterDepth")
    if isinstance(depth, (int, float)) and depth < 0:
        values["waterDepthLabel"] = "Inf."
    elif isinstance(depth, (int, float)):
        values["waterDepthLabel"] = f"{depth:g} m"

    return values


def parse_rao(path: Path) -> dict:
    headings: list[float] = []
    metadata: dict[str, str] = {}
    rows: list[dict] = []
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
            headings = [parse_number(token) for token in NUMBER_RE.findall(stripped)]
            continue
        if stripped.startswith("#---"):
            in_rows = True
            continue
        if stripped.startswith("#END"):
            break
        if not in_rows or stripped.startswith("#"):
            continue

        values = [parse_number(token) for token in NUMBER_RE.findall(stripped)]
        if not headings or len(values) < 1 + len(headings):
            continue

        x_value = values[0]
        if not math.isfinite(x_value) or x_value < 0:
            continue

        n = len(headings)
        amplitudes = [finite_or_none(value) for value in values[1 : 1 + n]]
        phases = [finite_or_none(value) for value in values[1 + n : 1 + 2 * n]]
        rows.append({"x": x_value, "amplitude": amplitudes, "phase": phases})

    return {
        "headings": headings,
        "metadata": metadata,
        "rows": rows,
    }


def series_label(item: str, kind: str) -> str:
    if kind == "matrix":
        return f"{item} {DOF_LABELS[item[0]]}"
    return f"{item} {DOF_LABELS[item]}"


def build_group(case_dir: Path, group: dict) -> dict:
    hydro_dir = case_dir / "Output" / "Hydrostar_format"
    series = []
    headings: list[float] = []

    for item in group["items"]:
        path = hydro_dir / f"{group['prefix']}{item}.rao"
        parsed = parse_rao(path)
        if not headings:
            headings = parsed["headings"]
        unit = parsed["metadata"].get("unit", "")
        label = series_label(item, group["label_kind"])
        if unit:
            label = f"{label} [{unit}]"
        series.append(
            {
                "id": item,
                "name": label,
                "unit": unit,
                "source": rel(path),
                "points": [
                    {"x": row["x"], "y": row["amplitude"]}
                    for row in parsed["rows"]
                ],
            }
        )

    return {
        "id": group["id"],
        "title": group["title"],
        "subtitle": group["subtitle"],
        "xLabel": "w (rad/s)",
        "yLabel": group["y_label"],
        "series": series,
        "headings": headings,
    }


def mesh_summary(case_dir: Path) -> dict:
    input_dir = case_dir / "Input"
    hull = parse_pnl(input_dir / "HullMesh.pnl")
    water = parse_pnl(input_dir / "WaterplaneMesh.pnl")
    return {
        "hullPanels": hull["raw_panels"],
        "hullNodes": hull["raw_nodes"],
        "waterPanels": water["raw_panels"],
        "waterNodes": water["raw_nodes"],
        "xSymmetry": hull["x_symmetry"],
        "ySymmetry": hull["y_symmetry"],
    }


def build_case(config: dict) -> dict:
    case_dir = config["case_dir"]
    groups = [build_group(case_dir, group) for group in GROUPS]
    headings = groups[-1]["headings"]
    frequencies = sorted(
        {
            point["x"]
            for group in groups
            for series in group["series"]
            for point in series["points"]
        }
    )

    return {
        "name": config["name"],
        "slug": config["slug"],
        "summary": config["summary"],
        "snapshot": config["snapshot"],
        "caseDir": rel(case_dir),
        "controlFile": rel(case_dir / "Input" / "ControlFile.in"),
        "outputDir": rel(case_dir / "Output"),
        "control": parse_control_file(case_dir / "Input" / "ControlFile.in"),
        "mesh": mesh_summary(case_dir),
        "headings": headings,
        "frequencies": frequencies,
        "groups": groups,
    }


def build_data() -> dict:
    return {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "cases": [build_case(config) for config in CASES],
    }


def main() -> None:
    out = OUT_DIR / "results-data.js"
    data = build_data()
    out.write_text(
        "window.HAMS_RESULTS_DATA = "
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    for case in data["cases"]:
        print(
            f"{case['name']}: headings={len(case['headings'])}; "
            f"frequencies={len(case['frequencies'])}; output={case['outputDir']}"
        )
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
