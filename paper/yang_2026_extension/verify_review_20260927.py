"""Check delivery structure and published values without rerunning physics."""
from __future__ import annotations

import json
import math
import re

import pymupdf
from docx import Document
from PIL import Image, ImageDraw

from refine_review_20260927 import INPUT, OUTPUT, SOURCE_DOCX, sha, structural_record


def main() -> None:
    docx = OUTPUT / "HAMS_manuscript_refined_20260927.docx"
    pdf = OUTPUT / "HAMS_manuscript_refined_20260927.pdf"
    document = Document(docx)
    evidence = json.loads((INPUT / "independent_checks.json").read_text(encoding="utf-8"))
    numeric_checks = []
    table = document.tables[2]
    row_index = 1
    for case_id in ("Y0_simultaneous", "Y1_1-2-1", "Y2_2-2"):
        for channel in ("acceleration_up_m_s2", "strut_force_n", "stroke_m"):
            metrics = evidence["yang"]["cases"][case_id]["metrics"][channel]
            expected = [f"{metrics['normalized_rmse_vs_paper_peak']:.3f}",
                        f"{metrics['correlation']:.3f}",
                        f"{metrics['peak_relative_error'] * 100:.1f}%"]
            actual = [cell.text.strip() for cell in table.rows[row_index].cells[2:]]
            numeric_checks.append({"case": case_id, "channel": channel,
                                   "actual": actual, "evidence_rounded": expected, "matches": actual == expected})
            row_index += 1
    pdf_doc = pymupdf.open(pdf)
    page_records = []
    for page in pdf_doc:
        outside = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    bounds = pymupdf.Rect(span["bbox"])
                    if not (page.rect + (-1, -1, 1, 1)).contains(bounds):
                        outside.append(span["text"])
        page_records.append({"page": page.number + 1, "text_characters": len(page.get_text()),
                             "text_outside_page": outside})
    previews = OUTPUT / "visual_qa"
    previews.mkdir(exist_ok=True)
    for start in range(0, len(pdf_doc), 6):
        sheet = Image.new("RGB", (1080, 976), "#dddddd")
        draw = ImageDraw.Draw(sheet)
        for local, index in enumerate(range(start, min(start + 6, len(pdf_doc)))):
            pixmap = pdf_doc[index].get_pixmap(matrix=pymupdf.Matrix(0.55, 0.55), alpha=False)
            page_image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            x, y = (local % 3) * 360 + 10, (local // 3) * 488 + 28
            sheet.paste(page_image, (x, y))
            draw.text((x, y - 18), f"Page {index + 1}", fill="black")
        sheet.save(previews / f"overview-{start // 6 + 1}.png")
    report = {
        "scope": "Document preservation, supplied-evidence comparison, and PDF layout checks; no new physics execution.",
        "docx_sha256": sha(docx), "pdf_sha256": sha(pdf), "pdf_pages": len(pdf_doc),
        "structure_preserved": structural_record(SOURCE_DOCX) == structural_record(docx),
        "table3_against_supplied_independent_checks": numeric_checks,
        "page_checks": page_records,
        "all_checks_pass": all(row["matches"] for row in numeric_checks)
        and structural_record(SOURCE_DOCX) == structural_record(docx)
        and all(row["text_characters"] > 0 and not row["text_outside_page"] for row in page_records),
    }
    (OUTPUT / "delivery_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pages": len(pdf_doc), "table3_rows_checked": len(numeric_checks),
                      "all_checks_pass": report["all_checks_pass"]}))
    if not report["all_checks_pass"]:
        raise SystemExit("Delivery validation failed")


if __name__ == "__main__":
    main()
