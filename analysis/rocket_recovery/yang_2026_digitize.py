from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

try:
    from .common import ROOT, ROCKET_CASES_DIR, write_json
except ImportError:
    from common import ROOT, ROCKET_CASES_DIR, write_json


CASE_DIR = ROCKET_CASES_DIR / "Paper_Yang_2026"
DEFAULT_IMAGE = CASE_DIR / "reference" / "renders" / "yang-2026-page-07-160dpi.png"
OUTPUT_DIR = CASE_DIR / "reference" / "digitized"


PLOTS: list[dict[str, Any]] = [
    {
        "id": "fig09_acceleration_test",
        "figure": "Figure 9(a)",
        "condition_id": "Y0_simultaneous",
        "metric": "rocket_vertical_acceleration_mm_s2",
        "box_px": [249, 850, 502, 1052],
        "x_range": [0.0, 1.5],
        "y_range": [-20000.0, 40000.0],
        "published_peak": 2.91 * 9.80665 * 1000.0,
        "unit": "mm/s^2",
    },
    {
        "id": "fig09_main_strut_load_test",
        "figure": "Figure 9(b)",
        "condition_id": "Y0_simultaneous",
        "metric": "main_strut_load_n",
        "box_px": [607, 850, 860, 1052],
        "x_range": [0.0, 2.0],
        "y_range": [0.0, 120000.0],
        "published_peak": 98800.0,
        "unit": "N",
    },
    {
        "id": "fig09_buffer_stroke_test",
        "figure": "Figure 9(c)",
        "condition_id": "Y0_simultaneous",
        "metric": "buffer_stroke_mm",
        "box_px": [934, 850, 1187, 1052],
        "x_range": [0.0, 2.0],
        "y_range": [0.0, 140.0],
        "published_peak": 99.8,
        "unit": "mm",
    },
    {
        "id": "fig10_acceleration_test",
        "figure": "Figure 10(a)",
        "condition_id": "Y1_1-2-1",
        "metric": "rocket_vertical_acceleration_mm_s2",
        "box_px": [249, 1174, 502, 1376],
        "x_range": [0.0, 1.5],
        "y_range": [-20000.0, 30000.0],
        "published_peak": 2.27 * 9.80665 * 1000.0,
        "unit": "mm/s^2",
    },
    {
        "id": "fig10_main_strut_load_test",
        "figure": "Figure 10(b)",
        "condition_id": "Y1_1-2-1",
        "metric": "main_strut_load_n",
        "box_px": [607, 1174, 860, 1376],
        "x_range": [0.0, 2.0],
        "y_range": [0.0, 120000.0],
        "published_peak": 115000.0,
        "unit": "N",
        "published_peak_note": "Probable correction of the printed 0.115 x 10^5 N anomaly; not a strict target.",
    },
    {
        "id": "fig10_buffer_stroke_test",
        "figure": "Figure 10(c)",
        "condition_id": "Y1_1-2-1",
        "metric": "buffer_stroke_mm",
        "box_px": [934, 1174, 1187, 1376],
        "x_range": [0.0, 4.0],
        "y_range": [0.0, 140.0],
        "published_peak": 127.9,
        "unit": "mm",
    },
    {
        "id": "fig11_acceleration_test",
        "figure": "Figure 11(a)",
        "condition_id": "Y2_2-2",
        "metric": "rocket_vertical_acceleration_mm_s2",
        "box_px": [249, 1503, 502, 1705],
        "x_range": [0.0, 1.5],
        "y_range": [-20000.0, 40000.0],
        "published_peak": 2.95 * 9.80665 * 1000.0,
        "unit": "mm/s^2",
    },
    {
        "id": "fig11_main_strut_load_test",
        "figure": "Figure 11(b)",
        "condition_id": "Y2_2-2",
        "metric": "main_strut_load_n",
        "box_px": [607, 1503, 860, 1705],
        "x_range": [0.0, 2.0],
        "y_range": [0.0, 120000.0],
        "published_peak": 114100.0,
        "unit": "N",
    },
    {
        "id": "fig11_buffer_stroke_test",
        "figure": "Figure 11(c)",
        "condition_id": "Y2_2-2",
        "metric": "buffer_stroke_mm",
        "box_px": [934, 1503, 1187, 1705],
        "x_range": [0.0, 4.0],
        "y_range": [0.0, 140.0],
        "published_peak": 119.9,
        "unit": "mm",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def red_curve_mask(rgb: np.ndarray) -> np.ndarray:
    red = rgb[:, :, 0].astype(int)
    green = rgb[:, :, 1].astype(int)
    blue = rgb[:, :, 2].astype(int)
    return (red >= 145) & (red - green >= 45) & (red - blue >= 35) & (green <= 190)


def digitize_plot(image: np.ndarray, config: dict[str, Any]) -> dict[str, Any]:
    x0, y0, x1, y1 = [int(value) for value in config["box_px"]]
    crop = image[y0 : y1 + 1, x0 : x1 + 1]
    mask = red_curve_mask(crop)
    height, width = mask.shape

    legend_x_start = int(round(0.55 * width))
    legend_y_end = int(round(0.33 * height))
    mask[:legend_y_end, legend_x_start:] = False

    rows: list[dict[str, float]] = []
    for local_x in range(width):
        candidates = np.flatnonzero(mask[:, local_x])
        if not len(candidates):
            continue
        local_y = float(np.median(candidates))
        time_s = float(config["x_range"][0]) + local_x / max(width - 1, 1) * (
            float(config["x_range"][1]) - float(config["x_range"][0])
        )
        value = float(config["y_range"][1]) - local_y / max(height - 1, 1) * (
            float(config["y_range"][1]) - float(config["y_range"][0])
        )
        rows.append(
            {
                "x_pixel": float(x0 + local_x),
                "y_pixel": float(y0 + local_y),
                "time_s": time_s,
                "value": value,
            }
        )

    if not rows:
        raise ValueError(f"No red curve pixels found for {config['id']}")
    values = np.asarray([row["value"] for row in rows], dtype=float)
    peak = float(np.max(values))
    published_peak = float(config["published_peak"])
    return {
        "config": config,
        "rows": rows,
        "quality": {
            "sampled_columns": len(rows),
            "plot_columns": width,
            "column_coverage_fraction": len(rows) / width,
            "digitized_peak": peak,
            "published_peak": published_peak,
            "peak_relative_difference": abs(peak - published_peak) / max(abs(published_peak), 1.0e-15),
            "status": "raster_digitization_requires_visual_review",
        },
    }


def write_curve_csv(result: dict[str, Any], output_dir: Path) -> Path:
    path = output_dir / f"{result['config']['id']}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["x_pixel", "y_pixel", "time_s", "value"])
        writer.writeheader()
        writer.writerows(result["rows"])
    return path


def build_digitization(image_path: Path, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    image = np.asarray(Image.open(image_path).convert("RGB"))
    curves: list[dict[str, Any]] = []
    for config in PLOTS:
        result = digitize_plot(image, config)
        csv_path = write_curve_csv(result, output_dir)
        curves.append(
            {
                "id": config["id"],
                "figure": config["figure"],
                "condition_id": config["condition_id"],
                "metric": config["metric"],
                "unit": config["unit"],
                "csv": str(csv_path.relative_to(ROOT).as_posix()),
                "axis_box_px": config["box_px"],
                "x_range": config["x_range"],
                "y_range": config["y_range"],
                "curve_color": "red dashed Test curve",
                "quality": result["quality"],
                "limitations": [
                    "Raster color extraction, not author-provided samples.",
                    "Dashed-curve gaps are preserved; no interpolation is written to the source CSV.",
                    "Axis boxes were calibrated on the 160 dpi PDF render and require visual review.",
                ],
            }
        )
    report = {
        "paper_id": "yang_2026",
        "source_image": str(image_path.relative_to(ROOT).as_posix()),
        "source_image_sha256": sha256(image_path),
        "source_image_size_px": [int(image.shape[1]), int(image.shape[0])],
        "render": {"pdf_page": 7, "dpi": 160, "renderer": "Poppler pdftoppm"},
        "method": "Threshold red pixels, remove the in-plot legend region, and map retained pixel centers through the printed linear axes.",
        "curves": curves,
    }
    write_json(output_dir / "yang-2026-fig09-11-digitization.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Digitize the red experimental curves in Yang et al. 2026 Figures 9-11.")
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    report = build_digitization(args.image.resolve(), args.output.resolve())
    print(f"Digitized curves: {len(report['curves'])}")
    for curve in report["curves"]:
        quality = curve["quality"]
        print(
            f"{curve['id']}: coverage={quality['column_coverage_fraction']:.3f}, "
            f"peak_difference={quality['peak_relative_difference']:.3f}"
        )


if __name__ == "__main__":
    main()
