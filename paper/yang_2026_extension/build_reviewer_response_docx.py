from __future__ import annotations

from pathlib import Path

from build_integrity_audit_docx import build_document


PAPER_DIR = Path(__file__).resolve().parent
SOURCE = PAPER_DIR / "REVIEWER_RESPONSE_CN.md"
OUTPUT = PAPER_DIR / "Reviewer_Response_CN.docx"


if __name__ == "__main__":
    build_document(
        SOURCE,
        OUTPUT,
        "海上回收着陆论文 | 审稿意见逐条回复",
        "Point-by-point response to the numerical credibility review",
    )
