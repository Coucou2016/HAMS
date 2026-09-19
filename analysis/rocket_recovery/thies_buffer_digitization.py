from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json
except ImportError:
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, write_json


PDFDEPS = ROOT / ".tools" / "pdfdeps"
if PDFDEPS.exists():
    sys.path.insert(0, str(PDFDEPS))

try:
    import fitz  # type: ignore
except ImportError as exc:  # pragma: no cover - depends on local setup
    raise SystemExit(
        "PyMuPDF is required for PDF figure rendering. Install it into the project-local target with: "
        "python -m pip install --target .\\.tools\\pdfdeps PyMuPDF"
    ) from exc


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
OUT_DIR = CASE_ROOT / "validation" / "thies_absorber_curves"
CURVES_JSON = OUT_DIR / "thies-buffer-curves.json"
CURVES_JS = VISUALIZATION_DIR / "thies-buffer-curves-data.js"
PDF_PATH = ROOT / "海上平台火箭回收文献" / "P3_Thies_2022.pdf"
MD_PATH = ROOT / "海上平台火箭回收文献" / "P3_Thies_2022.md"


FIGURE_SPECS: dict[str, dict[str, Any]] = {
    "spring_force_stroke": {
        "figure": "Figure 4",
        "caption": "Spring property of the absorbers",
        "image_block_index_on_page": 1,
        "crop_png": "thies_fig4_spring_property.png",
        "curve_color": "blue",
        "plot_px": {"left": 119, "right": 666, "top": 25, "bottom": 431},
        "axis_x": {"label": "Displacement", "unit": "mm", "min": -400.0, "max": 0.0},
        "axis_y": {"label": "Force", "unit": "kN", "min": -300.0, "max": 0.0},
        "positive_x_key": "stroke_m",
        "positive_x_scale": 0.001,
    },
    "damper_force_velocity": {
        "figure": "Figure 5",
        "caption": "Damper property of the absorbers",
        "image_block_index_on_page": 2,
        "crop_png": "thies_fig5_damper_property.png",
        "curve_color": "red",
        "plot_px": {"left": 144, "right": 658, "top": 27, "bottom": 432},
        "axis_x": {"label": "Velocity", "unit": "m/s", "min": -2.5, "max": 0.0},
        "axis_y": {"label": "Force", "unit": "kN", "min": -1000.0, "max": 0.0},
        "positive_x_key": "velocity_m_s",
        "positive_x_scale": 1.0,
    },
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def render_figure_crops(scale: float = 3.0) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF_PATH)
    page_index = 6
    page = doc[page_index]
    blocks = [block for block in page.get_text("dict")["blocks"] if block.get("type") == 1]
    blocks = sorted(blocks, key=lambda block: (block["bbox"][1], block["bbox"][0]))
    crops: dict[str, Any] = {}
    for curve_id, spec in FIGURE_SPECS.items():
        block = blocks[int(spec["image_block_index_on_page"])]
        rect = fitz.Rect(block["bbox"])
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=rect, alpha=False)
        out_png = OUT_DIR / spec["crop_png"]
        public_png = VISUALIZATION_DIR / spec["crop_png"]
        pix.save(out_png)
        public_png.parent.mkdir(parents=True, exist_ok=True)
        pix.save(public_png)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].copy()
        crops[curve_id] = {
            "path": out_png,
            "public_path": public_png,
            "array": arr,
            "pdf_bbox": [float(v) for v in block["bbox"]],
            "pixel_size": [int(pix.width), int(pix.height)],
        }
    return crops


def curve_mask(rgb: np.ndarray, color: str) -> np.ndarray:
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    if color == "blue":
        return (b > 150) & (g > 100) & (r < 150) & (b > r + 35)
    if color == "red":
        return (r > 180) & (g < 100) & (b < 100) & (r > g + 80)
    raise ValueError(f"Unsupported curve color: {color}")


def pixel_to_axis_value(pixel: float, lo_px: float, hi_px: float, lo_value: float, hi_value: float) -> float:
    return lo_value + (pixel - lo_px) / max(hi_px - lo_px, 1.0e-12) * (hi_value - lo_value)


def digitize_curve(rgb: np.ndarray, spec: dict[str, Any], resample_points: int = 100) -> dict[str, Any]:
    mask = curve_mask(rgb, spec["curve_color"])
    plot = spec["plot_px"]
    left = int(plot["left"])
    right = int(plot["right"])
    top = int(plot["top"])
    bottom = int(plot["bottom"])
    x_axis = spec["axis_x"]
    y_axis = spec["axis_y"]
    raw_points: list[dict[str, float]] = []
    for px in range(left, right + 1):
        ys = np.where(mask[top : bottom + 1, px])[0]
        if len(ys) == 0:
            continue
        py = float(np.median(ys) + top)
        source_x = pixel_to_axis_value(px, left, right, float(x_axis["min"]), float(x_axis["max"]))
        source_force = pixel_to_axis_value(py, top, bottom, float(y_axis["max"]), float(y_axis["min"]))
        positive_x = max(0.0, -source_x * float(spec["positive_x_scale"]))
        positive_force_n = max(0.0, -source_force * 1000.0)
        raw_points.append(
            {
                "pixel_x": float(px),
                "pixel_y": py,
                "source_x": source_x,
                "source_force_kN": source_force,
                spec["positive_x_key"]: positive_x,
                "force_n": positive_force_n,
            }
        )

    if len(raw_points) < 10:
        raise ValueError(f"Too few curve pixels digitized for {spec['figure']}: {len(raw_points)}")

    x_key = spec["positive_x_key"]
    raw_points = sorted(raw_points, key=lambda row: row[x_key])
    xs = np.array([row[x_key] for row in raw_points], dtype=float)
    forces = np.array([row["force_n"] for row in raw_points], dtype=float)
    max_x = float(np.max(xs))
    grid = np.linspace(0.0, max_x, resample_points)
    source_force = np.interp(grid, xs, forces)
    source_force[0] = 0.0
    table_points = [{x_key: float(x), "force_n": float(max(force, 0.0))} for x, force in zip(grid, source_force)]
    coverage = len(raw_points) / max(right - left + 1, 1)
    return {
        "figure": spec["figure"],
        "caption": spec["caption"],
        "axis_calibration": {
            "plot_px": spec["plot_px"],
            "axis_x": spec["axis_x"],
            "axis_y": spec["axis_y"],
            "positive_convention": f"{x_key}=max(0,-source_x) and force_n=max(0,-force_kN*1000)",
        },
        "mask_rule": spec["curve_color"],
        "raw_point_count": len(raw_points),
        "resampled_point_count": len(table_points),
        "coverage_ratio": coverage,
        "raw_points": raw_points,
        "table_points": table_points,
        "range": {
            x_key: [float(grid[0]), float(grid[-1])],
            "force_n": [float(np.min(source_force)), float(np.max(source_force))],
        },
        "quality": "ok" if coverage > 0.35 else "check",
    }


def build_digitized_curves() -> dict[str, Any]:
    crops = render_figure_crops()
    curves: dict[str, Any] = {}
    for curve_id, spec in FIGURE_SPECS.items():
        curve = digitize_curve(crops[curve_id]["array"], spec)
        curve["crop_png"] = rel(crops[curve_id]["path"])
        curve["crop_png_public"] = crops[curve_id]["public_path"].name
        curve["pdf_bbox"] = crops[curve_id]["pdf_bbox"]
        curve["pixel_size"] = crops[curve_id]["pixel_size"]
        curves[curve_id] = curve

    spring = curves["spring_force_stroke"]
    damper = curves["damper_force_velocity"]
    stroke_limit = float(spring["range"]["stroke_m"][1])
    law = {
        "source": "Thies 2022 Figures 4 and 5 digitized from supplied PDF page 7.",
        "type": "compression_only_table",
        "supported_types": [
            "compression_only_bilinear_with_hard_stop",
            "compression_only_table",
        ],
        "table_interface_note": "Spring and damper curves are digitized from raster PDF figures; hard stop remains only a numerical guard beyond the digitized stroke range.",
        "linear_stiffness_n_m": None,
        "linear_damping_ns_m": None,
        "stroke_limit_m": stroke_limit,
        "hard_stop_stiffness_n_m": 200_000_000.0,
        "hard_stop_damping_ns_m": 10_000_000.0,
        "force_stroke_points": spring["table_points"],
        "force_velocity_points": damper["table_points"],
        "no_tension": True,
        "digitization": {
            "source_pdf": rel(PDF_PATH),
            "source_markdown": rel(MD_PATH),
            "source_page": 7,
            "method": "PyMuPDF page rendering, manual axis calibration, color-threshold curve extraction, and linear resampling.",
            "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "curve_ids": ["spring_force_stroke", "damper_force_velocity"],
            "force_sign_convention": "Thies plots compression as negative force/displacement/velocity; Chrono table stores compression and resisting force as positive values.",
            "hard_stop_note": "The hard-stop terms are not digitized paper data; they are a numerical guard outside the digitized range.",
        },
    }
    return {
        "case_id": "Thies_2022_DigitizedAbsorberCurves",
        "status": "digitized",
        "source": {
            "pdf": rel(PDF_PATH),
            "pdf_exists": PDF_PATH.exists(),
            "markdown": rel(MD_PATH),
            "markdown_exists": MD_PATH.exists(),
            "figures": ["Figure 4", "Figure 5"],
        },
        "claim_boundary": (
            "These are digitized curves from the visible PDF figures, not original author data. "
            "They are suitable for an auditable open Chrono table-law input, not for claiming exact Adams source-data recovery."
        ),
        "curves": curves,
        "chrono_buffer_law": law,
        "validation": {
            "curves_present": bool(law["force_stroke_points"]) and bool(law["force_velocity_points"]),
            "spring_quality": spring["quality"],
            "damper_quality": damper["quality"],
            "pass": bool(law["force_stroke_points"]) and bool(law["force_velocity_points"]) and spring["quality"] == "ok" and damper["quality"] == "ok",
        },
    }


def write_report_js(data: dict[str, Any]) -> None:
    CURVES_JS.parent.mkdir(parents=True, exist_ok=True)
    CURVES_JS.write_text(
        "window.THIES_BUFFER_CURVES = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Digitize Thies 2022 absorber spring/damper curves from PDF Figures 4 and 5.")
    parser.add_argument("command", choices=["digitize", "report"], nargs="?", default="digitize")
    _args = parser.parse_args()
    data = build_digitized_curves()
    write_json(CURVES_JSON, data)
    write_report_js(data)
    print(f"Status: {data['status']}")
    print(f"Validation pass: {data['validation']['pass']}")
    print(f"Spring points: {len(data['chrono_buffer_law']['force_stroke_points'])}")
    print(f"Damper points: {len(data['chrono_buffer_law']['force_velocity_points'])}")
    print(f"JSON: {CURVES_JSON}")
    print(f"JS: {CURVES_JS}")


if __name__ == "__main__":
    main()
