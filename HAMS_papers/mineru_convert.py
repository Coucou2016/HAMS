#!/usr/bin/env python3
"""Batch convert HAMS papers PDFs to Markdown via MinerU API."""

from __future__ import annotations

import io
import json
import os
import sys
import time
import zipfile
from pathlib import Path

import requests

TOKEN = os.environ.get("MINERU_TOKEN", "").strip()
PDF_DIR = Path.cwd()
OUT_DIR = PDF_DIR / "md"
ZIP_DIR = PDF_DIR / "mineru_zips"

BATCH_URL = "https://mineru.net/api/v4/file-urls/batch"
RESULT_URL = "https://mineru.net/api/v4/extract-results/batch/{batch_id}"

POLL_INTERVAL = 15
POLL_TIMEOUT = 60 * 40  # 40 minutes


def headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }


def main() -> int:
    if not TOKEN:
        print("ERROR: set MINERU_TOKEN env var", file=sys.stderr)
        return 1

    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ZIP_DIR.mkdir(parents=True, exist_ok=True)

    files_meta = [{"name": p.name, "data_id": p.stem} for p in pdfs]
    payload = {
        "files": files_meta,
        "model_version": "vlm",
        "enable_formula": True,
        "enable_table": True,
        "language": "en",
    }

    print(f"Submitting {len(pdfs)} files to MinerU...")
    resp = requests.post(BATCH_URL, headers=headers(), json=payload, timeout=60)
    print("apply status:", resp.status_code)
    result = resp.json()
    print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
    if resp.status_code != 200 or result.get("code") != 0:
        print("Failed to apply upload URLs", file=sys.stderr)
        return 1

    batch_id = result["data"]["batch_id"]
    urls = result["data"]["file_urls"]
    print(f"batch_id={batch_id}")

    if len(urls) != len(pdfs):
        print(f"URL count mismatch: {len(urls)} vs {len(pdfs)}", file=sys.stderr)
        return 1

    for pdf, upload_url in zip(pdfs, urls):
        print(f"Uploading {pdf.name} ...")
        with pdf.open("rb") as f:
            up = requests.put(upload_url, data=f, timeout=600)
        if up.status_code not in (200, 201):
            print(f"  FAILED {pdf.name}: HTTP {up.status_code} {up.text[:300]}", file=sys.stderr)
            return 1
        print(f"  OK {pdf.name}")

    print("Waiting for parse results...")
    deadline = time.time() + POLL_TIMEOUT
    extract_results = []
    while time.time() < deadline:
        q = requests.get(RESULT_URL.format(batch_id=batch_id), headers=headers(), timeout=60)
        body = q.json()
        if q.status_code != 200 or body.get("code") != 0:
            print("poll error:", q.status_code, body)
            time.sleep(POLL_INTERVAL)
            continue

        extract_results = body["data"].get("extract_result") or []
        states = [item.get("state") for item in extract_results]
        print(f"  states={states}")

        terminal = {"done", "failed"}
        if extract_results and all(s in terminal for s in states):
            break
        time.sleep(POLL_INTERVAL)
    else:
        print("Polling timed out", file=sys.stderr)
        # still try to save whatever we have

    summary = []
    for item in extract_results:
        name = item.get("file_name") or item.get("data_id") or "unknown"
        state = item.get("state")
        data_id = item.get("data_id") or Path(name).stem
        print(f"Result: {name} state={state} err={item.get('err_msg','')}")

        if state != "done":
            summary.append({"file": name, "state": state, "err": item.get("err_msg")})
            continue

        zip_url = item["full_zip_url"]
        zip_path = ZIP_DIR / f"{data_id}.zip"
        print(f"  downloading zip -> {zip_path.name}")
        zr = requests.get(zip_url, timeout=300)
        zr.raise_for_status()
        zip_path.write_bytes(zr.content)

        md_out = OUT_DIR / f"{data_id}.md"
        with zipfile.ZipFile(io.BytesIO(zr.content)) as zf:
            # Prefer full.md at any nesting level
            md_name = None
            for n in zf.namelist():
                if n.endswith("full.md") or n.endswith("/full.md") or n == "full.md":
                    md_name = n
                    break
            if md_name is None:
                # fallback: any .md
                mds = [n for n in zf.namelist() if n.lower().endswith(".md")]
                md_name = mds[0] if mds else None
            if md_name is None:
                print(f"  No markdown in zip: {zf.namelist()[:20]}", file=sys.stderr)
                summary.append({"file": name, "state": "no_md"})
                continue
            md_bytes = zf.read(md_name)
            md_out.write_bytes(md_bytes)
            print(f"  wrote {md_out} ({len(md_bytes)} bytes)")

            # also extract images folder if present
            img_dir = OUT_DIR / f"{data_id}_images"
            for n in zf.namelist():
                if "/images/" in n.replace("\\", "/") or n.startswith("images/"):
                    rel = Path(n).name
                    if not rel:
                        continue
                    img_dir.mkdir(parents=True, exist_ok=True)
                    (img_dir / rel).write_bytes(zf.read(n))

        summary.append({"file": name, "state": "done", "md": str(md_out)})

    summary_path = OUT_DIR / "_conversion_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSummary written to {summary_path}")
    done = sum(1 for s in summary if s.get("state") == "done")
    print(f"Done: {done}/{len(summary)}")
    return 0 if done == len(pdfs) else 2


if __name__ == "__main__":
    raise SystemExit(main())
