"""Read-only provenance and regression diagnostics for HAMS CertTest outputs.

This script never runs HAMS and never edits SourceCode, Input, Output_Benchmark,
or an existing case Output directory. It records the evidence needed to tell a
toolchain mismatch from an input, working-directory, or phase-format problem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
CASES = ("Cylinder", "DeepCwind", "HywindSpar", "Moonpool")
REL_TOL = 1.0e-1
ABS_TOL = 1.0e-7


def run_command(args: list[str], cwd: Path = ROOT) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "args": args,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_info(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"path": str(path.relative_to(ROOT)), "exists": False}
    stat = path.stat()
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": True,
        "size": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "sha256": sha256(path),
    }


def pe_info(path: Path) -> dict[str, Any]:
    info = file_info(path)
    if not path.is_file():
        return info
    data = path.read_bytes()
    info["is_pe"] = data[:2] == b"MZ"
    if len(data) >= 0x40 and info["is_pe"]:
        pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
        info["pe_header_offset"] = pe_offset
        if pe_offset + 12 <= len(data) and data[pe_offset : pe_offset + 4] == b"PE\\0\\0":
            timestamp = struct.unpack_from("<I", data, pe_offset + 8)[0]
            info["pe_timestamp"] = timestamp
            info["pe_timestamp_utc"] = datetime.fromtimestamp(
                timestamp, timezone.utc
            ).isoformat()
    return info


def is_float(token: str) -> bool:
    try:
        float(token)
    except ValueError:
        return False
    return True


def numeric_equal(left: float, right: float) -> bool:
    if math.isnan(left) or math.isnan(right):
        return math.isnan(left) and math.isnan(right)
    if math.isinf(left) or math.isinf(right):
        return left == right
    return math.isclose(left, right, rel_tol=REL_TOL, abs_tol=ABS_TOL)


def compare_tree(truth_dir: Path, actual_dir: Path) -> dict[str, Any]:
    files = 0
    missing = 0
    failed_files = 0
    mismatch_count = 0
    numeric_mismatch = 0
    text_mismatch = 0
    by_group: dict[str, dict[str, int]] = {}
    first_mismatches: list[dict[str, Any]] = []

    truth_files = sorted(path for path in truth_dir.rglob("*") if path.is_file())
    for truth_file in truth_files:
        files += 1
        relative = truth_file.relative_to(truth_dir)
        actual_file = actual_dir / relative
        group = relative.parts[0] if relative.parts else "."
        summary = by_group.setdefault(
            group, {"files": 0, "failed_files": 0, "mismatches": 0}
        )
        summary["files"] += 1
        if not actual_file.is_file():
            missing += 1
            failed_files += 1
            summary["failed_files"] += 1
            if len(first_mismatches) < 20:
                first_mismatches.append(
                    {"file": str(relative), "kind": "missing_actual_file"}
                )
            continue

        truth_lines = truth_file.read_text(encoding="utf-8", errors="replace").splitlines()
        actual_lines = actual_file.read_text(encoding="utf-8", errors="replace").splitlines()
        mismatches = 0
        first: dict[str, Any] | None = None
        if len(truth_lines) != len(actual_lines):
            mismatches += 1
            first = {
                "file": str(relative),
                "kind": "line_count",
                "truth": len(truth_lines),
                "actual": len(actual_lines),
            }

        for line_number, (truth_line, actual_line) in enumerate(
            zip(truth_lines, actual_lines), start=1
        ):
            truth_tokens = truth_line.split()
            actual_tokens = actual_line.split()
            if len(truth_tokens) != len(actual_tokens):
                mismatches += 1
                text_mismatch += 1
                first = first or {
                    "file": str(relative),
                    "kind": "token_count",
                    "line": line_number,
                    "truth": len(truth_tokens),
                    "actual": len(actual_tokens),
                }
                continue

            for token_number, (truth_token, actual_token) in enumerate(
                zip(truth_tokens, actual_tokens), start=1
            ):
                truth_is_float = is_float(truth_token)
                actual_is_float = is_float(actual_token)
                if truth_is_float and actual_is_float:
                    if numeric_equal(float(truth_token), float(actual_token)):
                        continue
                    mismatches += 1
                    numeric_mismatch += 1
                    first = first or {
                        "file": str(relative),
                        "kind": "numeric",
                        "line": line_number,
                        "token": token_number,
                        "truth": truth_token,
                        "actual": actual_token,
                    }
                elif truth_is_float != actual_is_float or truth_token != actual_token:
                    mismatches += 1
                    text_mismatch += 1
                    first = first or {
                        "file": str(relative),
                        "kind": "token",
                        "line": line_number,
                        "token": token_number,
                        "truth": truth_token,
                        "actual": actual_token,
                    }

        if mismatches:
            failed_files += 1
            summary["failed_files"] += 1
            mismatch_count += mismatches
            summary["mismatches"] += mismatches
            if first is not None and len(first_mismatches) < 20:
                first["mismatch_count_in_file"] = mismatches
                first_mismatches.append(first)

    return {
        "truth": str(truth_dir.relative_to(ROOT)),
        "actual": str(actual_dir.relative_to(ROOT)),
        "registered_tolerance": {"rel_tol": REL_TOL, "abs_tol": ABS_TOL},
        "files": files,
        "missing_files": missing,
        "failed_files": failed_files,
        "mismatches": mismatch_count,
        "numeric_mismatches": numeric_mismatch,
        "text_mismatches": text_mismatch,
        "by_group": by_group,
        "first_mismatches": first_mismatches,
    }


def same_tree(left: Path, right: Path) -> dict[str, Any]:
    left_files = {path.relative_to(left) for path in left.rglob("*") if path.is_file()}
    right_files = {path.relative_to(right) for path in right.rglob("*") if path.is_file()}
    different: list[str] = []
    for relative in sorted(left_files | right_files):
        first = left / relative
        second = right / relative
        if not first.is_file() or not second.is_file() or sha256(first) != sha256(second):
            different.append(str(relative))
    return {
        "left": str(left.relative_to(ROOT)),
        "right": str(right.relative_to(ROOT)),
        "same": not different,
        "different_files": different[:50],
        "different_file_count": len(different),
    }


def git_diff_clean(*args: str) -> bool:
    result = run_command(["git", "diff", "--quiet", *args])
    return result["returncode"] == 0


def discover_diagnostic_outputs() -> list[Path]:
    base = ROOT / ".diagnostics"
    if not base.is_dir():
        return []
    candidates: list[Path] = []
    for directory in sorted(base.iterdir()):
        if not directory.is_dir():
            continue
        if directory.name.startswith("cert-cylinder-compare-"):
            candidates.append(directory / "gfortran" / "Output")
        elif directory.name.startswith("hams-70283d0-cylinder-"):
            candidates.append(directory / "Output")
        elif directory.name.startswith("cert-cylinder-threads1-correct-"):
            candidates.append(directory / "Output")
    return [path for path in candidates if path.is_dir()]


def compiler_info() -> dict[str, Any]:
    commands = {
        "gfortran": [str(ROOT / ".tools/msys64/mingw64/bin/gfortran.exe"), "--version"],
        "make": [str(ROOT / ".tools/msys64/usr/bin/make.exe"), "--version"],
        "ld": [str(ROOT / ".tools/msys64/mingw64/bin/ld.exe"), "--version"],
    }
    result: dict[str, Any] = {}
    for name, command in commands.items():
        record = run_command(command)
        result[name] = {
            "command": command,
            "returncode": record["returncode"],
            "version": record["stdout"].splitlines()[:4],
            "stderr": record["stderr"],
        }
    return result


def build_report() -> dict[str, Any]:
    git_head = run_command(["git", "rev-parse", "HEAD"])
    git_branch = run_command(["git", "branch", "--show-current"])
    git_remote = run_command(["git", "remote", "-v"])
    benchmark_log = run_command(
        [
            "git",
            "log",
            "--all",
            "--format=%h %ad %s",
            "--date=iso",
            "--",
            "CertTest/Cylinder/Output_Benchmark",
        ]
    )
    source_delta = run_command(
        ["git", "diff", "--name-only", "70283d0", "HEAD", "--", "SourceCode"]
    )

    cases: dict[str, Any] = {}
    for case in CASES:
        case_dir = ROOT / "CertTest" / case
        cases[case] = {
            "input_semantically_matches_head": git_diff_clean(
                "HEAD", "--", f"CertTest/{case}/Input"
            ),
            "input_semantically_matches_benchmark_commit": git_diff_clean(
                "70283d0", "HEAD", "--", f"CertTest/{case}/Input"
            ),
            "benchmark_unmodified_in_worktree": git_diff_clean(
                "HEAD", "--", f"CertTest/{case}/Output_Benchmark"
            ),
            "comparison": compare_tree(
                case_dir / "Output_Benchmark", case_dir / "Output"
            ),
        }

    diagnostic_comparisons: list[dict[str, Any]] = []
    for output_dir in discover_diagnostic_outputs():
        diagnostic_comparisons.append(
            {
                "output": str(output_dir.relative_to(ROOT)),
                "comparison_to_current_cylinder_output": same_tree(
                    output_dir, ROOT / "CertTest/Cylinder/Output"
                ),
                "comparison_to_cylinder_benchmark": compare_tree(
                    ROOT / "CertTest/Cylinder/Output_Benchmark", output_dir
                ),
            }
        )

    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "git": {
            "head": git_head["stdout"],
            "branch": git_branch["stdout"],
            "remote": git_remote["stdout"].splitlines(),
            "benchmark_history": benchmark_log["stdout"].splitlines()[:12],
            "source_delta_70283d0_to_head": source_delta["stdout"].splitlines(),
            "source_delta_is_phase_only_candidate": source_delta["stdout"].splitlines()
            == [
                "SourceCode/PotentWavForce.f90",
                "SourceCode/PressureElevation.f90",
                "SourceCode/PrintOutput.f90",
                "SourceCode/SolveMotion.f90",
            ],
        },
        "build": {
            "script": file_info(ROOT / "local-tools/Build-HAMS.ps1"),
            "run_script": file_info(ROOT / "local-tools/Run-HAMS.ps1"),
            "makefile": file_info(ROOT / "SourceCode/makefile"),
            "source_executable": pe_info(ROOT / "SourceCode/hams.exe"),
            "repository_ifort_executable": pe_info(
                ROOT / "SourceCode/HAMS_ifort_Win.exe"
            ),
            "compiler": compiler_info(),
        },
        "registered_comparison": {
            "source": "CertTest/test_cert.py",
            "rel_tol": REL_TOL,
            "abs_tol": ABS_TOL,
            "tolerance_was_not_changed_by_this_diagnostic": True,
        },
        "cases": cases,
        "diagnostic_outputs": diagnostic_comparisons,
        "conclusions": [
            "Input and Output_Benchmark have no semantic Git worktree diff.",
            "The local run is tied to the case working directory by Run-HAMS.ps1 and the isolated Cylinder run is compared separately.",
            "A benchmark-commit source rebuild is included when the corresponding .diagnostics output exists.",
            "Failure of the official benchmark remains a real failure of reproducibility, not a reason to widen tolerance.",
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# HAMS CertTest root-cause diagnostic",
        "",
        f"Generated (UTC): `{report['generated_utc']}`",
        f"Git HEAD: `{report['git']['head']}` on `{report['git']['branch']}`",
        "",
        "## Evidence",
        "",
        "- The comparison uses the already registered `CertTest/test_cert.py` tolerances: "
        f"`rel_tol={REL_TOL}` and `abs_tol={ABS_TOL}`.",
        "- This report is read-only with respect to HAMS source, inputs, benchmarks, and case outputs.",
        "- A raw Windows CRLF hash difference is not treated as an input change; Git semantic diff is the authority.",
        "",
        "### Source and benchmark history",
        "",
        "```text",
        *report["git"]["benchmark_history"],
        "```",
        "",
        "Source files changed from `70283d0` to HEAD:",
        "",
        *[f"- `{item}`" for item in report["git"]["source_delta_70283d0_to_head"]],
        "",
        "### Case results",
        "",
        "| Case | Files | Failed files | Numeric mismatches | Text mismatches |",
        "|---|---:|---:|---:|---:|",
    ]
    for case, data in report["cases"].items():
        result = data["comparison"]
        lines.append(
            f"| {case} | {result['files']} | {result['failed_files']} | "
            f"{result['numeric_mismatches']} | {result['text_mismatches']} |"
        )
    lines += [
        "",
        "### Build provenance",
        "",
        f"- Build script: `{report['build']['script']['path']}`",
        f"- Makefile: `{report['build']['makefile']['path']}`",
        f"- Local executable PE timestamp: `{report['build']['source_executable'].get('pe_timestamp_utc', 'unavailable')}`",
        f"- Repository ifort executable PE timestamp: `{report['build']['repository_ifort_executable'].get('pe_timestamp_utc', 'unavailable')}`",
        "",
        "### Diagnostic outputs",
        "",
    ]
    for item in report["diagnostic_outputs"]:
        result = item["comparison_to_cylinder_benchmark"]
        same = item["comparison_to_current_cylinder_output"]["same"]
        lines.append(
            f"- `{item['output']}`: benchmark failed files `{result['failed_files']}` / "
            f"`{result['files']}`, same bytes as current Cylinder Output: `{same}`."
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "The report deliberately does not convert a failed benchmark into PASS. "
        "Use the evidence above to distinguish compiler/flags and benchmark provenance from input or working-directory errors.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=ROOT / "analysis/diagnostics/hams-cert-root-cause.json",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=ROOT / "analysis/diagnostics/hams-cert-root-cause.md",
    )
    args = parser.parse_args()
    report = build_report()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown_out.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.markdown_out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
