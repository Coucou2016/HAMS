from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat

try:
    from .common import ROOT, read_json, write_json
except ImportError:
    from common import ROOT, read_json, write_json


PAPER_DIR = ROOT / "paper" / "yang_2026_extension"
MANUSCRIPT = PAPER_DIR / "manuscript.md"
REPORT = PAPER_DIR / "research-integrity-audit.json"
MARKDOWN = PAPER_DIR / "RESEARCH_INTEGRITY_AUDIT_CN.md"

YANG_REPORT = ROOT / "RocketRecoveryCases" / "Paper_Yang_2026" / "identified_landing_model" / "yang-2026-identified-landing-report.json"
YANG_IDENT = ROOT / "RocketRecoveryCases" / "Paper_Yang_2026" / "identified_landing_model" / "yang-2026-identifiability-report.json"
YANG_DIGITIZED = ROOT / "RocketRecoveryCases" / "Paper_Yang_2026" / "reference" / "digitized" / "yang-2026-fig09-11-digitization.json"
BARGE_CONFIG = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "platform_config.json"
BARGE_SELF_CHECK = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "validation" / "barge-self-check.json"
HYDRO_REPORT = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "validation" / "barge-hydrodynamic-convergence.json"
BARGE_RAO = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "Output" / "RocketRecovery" / "deck-point-rao-medium.json"
WAVE_REPORT = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "Output" / "RocketRecovery" / "wave-sensitivity-revision-600s.json"
DURATION_REPORT = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "Output" / "RocketRecovery" / "wave-duration-sensitivity.json"
THIES_CURVES = ROOT / "RocketRecoveryCases" / "Chrono_LeggedRecovery" / "validation" / "thies_absorber_curves" / "thies-buffer-curves.json"
CHRONO_REPORT = ROOT / "RocketRecoveryCases" / "Chrono_LeggedRecovery" / "chrono-same-platform-multibody-report.json"
CHRONO_RESPONSE = ROOT / "RocketRecoveryCases" / "Chrono_LeggedRecovery" / "Output" / "RocketRecovery" / "chrono-same-platform-multibody-response.json"
COMPANION_REPORT = ROOT / "RocketRecoveryCases" / "Chrono_LeggedRecovery" / "chrono-revision-study-report.json"
CERT_DIAGNOSTIC = ROOT / "analysis" / "diagnostics" / "hams-cert-root-cause.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def file_record(path: Path, evidence_class: str, role: str) -> dict[str, Any]:
    out: dict[str, Any] = {
        "path": rel(path),
        "evidence_class": evidence_class,
        "role": role,
        "exists": path.is_file(),
    }
    if path.is_file():
        stat = path.stat()
        out.update({"bytes": stat.st_size, "sha256": digest(path)})
    return out


def finite_tree(value: Any) -> bool:
    if isinstance(value, dict):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, list):
        return all(finite_tree(item) for item in value)
    if isinstance(value, float):
        return math.isfinite(value)
    return True


def figure_record(stem: str, role: str, sources: list[Path]) -> dict[str, Any]:
    png = PAPER_DIR / "figures" / f"{stem}.png"
    svg = PAPER_DIR / "figures" / f"{stem}.svg"
    out: dict[str, Any] = {
        "id": stem,
        "role": role,
        "sources": [rel(path) for path in sources],
        "png": rel(png),
        "svg": rel(svg),
        "checks": {},
    }
    if png.is_file():
        with Image.open(png) as image:
            rgb = image.convert("RGB")
            extrema = ImageStat.Stat(rgb).extrema
            width, height = image.size
        out["checks"].update(
            {
                "png_exists": True,
                "width_px": width,
                "height_px": height,
                "minimum_dimension_at_least_1800_px": min(width, height) >= 1800,
                "nonblank": any(high > low for low, high in extrema),
                "sha256": digest(png),
            }
        )
    else:
        out["checks"]["png_exists"] = False
    if svg.is_file():
        text = svg.read_text(encoding="utf-8", errors="replace")
        out["checks"].update(
            {
                "svg_exists": True,
                "svg_contains_times_new_roman": "Times New Roman" in text,
                "svg_sha256": digest(svg),
            }
        )
    else:
        out["checks"]["svg_exists"] = False
    return out


def maximum_wave_case(wave: dict[str, Any], metric: str) -> dict[str, Any]:
    return max(wave["cases"], key=lambda row: float(row["statistics"][metric]["p95"]))


def duration_value(duration: dict[str, Any], sea: str, metric: str, seconds: int) -> float:
    row = next(item for item in duration["duration_comparison"][sea][metric] if int(item["duration_s"]) == seconds)
    return float(row["p95"])


def build_report() -> dict[str, Any]:
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    yang = read_json(YANG_REPORT)
    ident = read_json(YANG_IDENT)
    hydro = read_json(HYDRO_REPORT)
    rao = read_json(BARGE_RAO)
    wave = read_json(WAVE_REPORT)
    duration = read_json(DURATION_REPORT)
    chrono = read_json(CHRONO_REPORT)
    cert = read_json(CERT_DIAGNOSTIC)

    center = next(point for point in rao["points"] if point["id"] == "landing_center")
    heave = max(center["rows"], key=lambda row: float(row["displacement_m"]["z"]["amp"]))
    center_wave = maximum_wave_case(wave, "landing_center.max_abs_vertical_velocity_m_s")
    feet_wave = maximum_wave_case(wave, "four_feet.max_vertical_velocity_span_m_s")
    tilt_wave = maximum_wave_case(wave, "platform.max_tilt_deg")
    valid_cases = sum(bool(row["linear_validity"]["pass"]) for row in wave["cases"])
    final_contact = chrono["iterative_run"]["final_contact_summary"]
    final_platform = chrono["iterative_run"]["final_platform_summary"]
    energy = chrono["algorithms"]["four_pass_platform_update"]["platform_energy"]

    reference_pdf = next(ROOT.rglob("Analysis+of+Sea-Based+Landing+Dynamics+of+Reusable+Landing+Vehicle+Considering+Mechanism+Flexibility.pdf"), None)
    reference_md = next(ROOT.rglob("Analysis+of+Sea-Based+Landing+Dynamics+of+Reusable+Landing+Vehicle+Considering+Mechanism+Flexibility.md"), None)
    nargolkar_pdf = ROOT / "海上平台火箭回收文献" / "065002_1_2.0002061.pdf"
    thies_pdf = ROOT / "海上平台火箭回收文献" / "P3_Thies_2022.pdf"
    wang_pdf = ROOT / "海上平台火箭回收文献" / "P2_WangZhi_2023_ShipSciTech.pdf"

    evidence_files: list[dict[str, Any]] = []
    if reference_pdf:
        evidence_files.append(file_record(reference_pdf, "reference_source", "Yang et al. paper"))
    if reference_md:
        evidence_files.append(file_record(reference_md, "reference_source", "Yang et al. extracted text"))
    evidence_files.extend(
        [
            file_record(nargolkar_pdf, "reference_source", "Nargolkar and Vijayan paper"),
            file_record(thies_pdf, "reference_source", "Thies landing-leg paper"),
            file_record(wang_pdf, "reference_source", "Wang plume/platform paper"),
            file_record(YANG_DIGITIZED, "reference_target", "Digitized published test traces"),
            file_record(THIES_CURVES, "reference_target", "Digitized absorber curves and axis calibration"),
            file_record(BARGE_CONFIG, "present_input", "Parameterized barge input"),
            file_record(BARGE_SELF_CHECK, "present_calculation", "Analytic mesh and hydrostatic self-check"),
            file_record(HYDRO_REPORT, "present_calculation", "Hydrodynamic refinement, A-infinity and IRF checks"),
            file_record(BARGE_RAO, "present_calculation", "Medium-grid local deck response operators"),
            file_record(WAVE_REPORT, "present_calculation", "1000-realization random-wave calculation"),
            file_record(DURATION_REPORT, "present_calculation", "600/1200/1800 s duration sensitivity"),
            file_record(YANG_REPORT, "present_calculation", "Reduced-model comparison"),
            file_record(YANG_IDENT, "present_calculation", "128-start identifiability analysis"),
            file_record(CHRONO_REPORT, "present_calculation_with_labelled_proxies", "Same-platform four-pass multibody report"),
            file_record(CHRONO_RESPONSE, "present_calculation_with_labelled_proxies", "Full same-platform response history"),
            file_record(COMPANION_REPORT, "present_code_verification", "Independent smooth-law energy/code companion"),
            file_record(CERT_DIAGNOSTIC, "failed_external_regression", "Official four-case comparator diagnostic; no validation credit"),
            file_record(MANUSCRIPT, "present_manuscript", "Submission manuscript source"),
        ]
    )

    code_names = [
        "generate_barge_case.py",
        "barge_hydrodynamic_convergence.py",
        "deck_point_rao.py",
        "barge_wave_sensitivity.py",
        "barge_wave_duration_sensitivity.py",
        "yang_2026_landing_identification.py",
        "yang_2026_identifiability.py",
        "thies_buffer_digitization.py",
        "chrono_leg_model.py",
        "chrono_same_platform_multibody.py",
        "yang_2026_figures.py",
        "paper_integrity_audit.py",
    ]
    code_files = [
        file_record(ROOT / "analysis" / "rocket_recovery" / name, "present_code", "Executable analysis source")
        for name in code_names
    ]

    figures = [
        figure_record("fig01-coupled-framework", "Implemented theoretical data flow", [ROOT / "analysis" / "rocket_recovery" / "yang_2026_figures.py"]),
        figure_record("fig02-barge-geometry-mesh", "Present geometry and two deck-point layouts", [BARGE_CONFIG]),
        figure_record("fig03-yang-identified-landing-comparison", "Digitized reference versus present reduced-model calculation", [YANG_DIGITIZED, YANG_REPORT, YANG_IDENT]),
        figure_record("fig04-platform-hydrodynamic-response", "Present hydrodynamic and refinement calculations", [HYDRO_REPORT, BARGE_RAO]),
        figure_record("fig05-random-wave-deck-statistics", "Present 1000-realization statistics and validity flags", [WAVE_REPORT, DURATION_REPORT]),
        figure_record("fig06-partitioned-contact-feedback", "Present same-platform multibody response and numerical sensitivity", [CHRONO_REPORT, CHRONO_RESPONSE]),
        figure_record("figS01-yang-identifiability", "Present multi-start identifiability result", [YANG_IDENT]),
        figure_record("figS02-yang-deck-filter-reproduction", "Supplementary transfer-function reconstruction", [ROOT / "RocketRecoveryCases" / "Paper_Yang_2026" / "yang-2026-evidence-report.json"]),
    ]

    claims = [
        {"id": "yang_stroke_peak", "literal": "within 4.1%", "value": max(100 * float(yang["comparisons"][case]["metrics"]["stroke_m"]["peak_relative_error"]) for case in yang["comparisons"]), "source": rel(YANG_REPORT), "pointer": "/comparisons/*/metrics/stroke_m/peak_relative_error"},
        {"id": "yang_near_optimal", "literal": "127 of 128", "value": [ident["convergence"]["near_optimal_count"], ident["convergence"]["total_starts"]], "source": rel(YANG_IDENT), "pointer": "/convergence"},
        {"id": "medium_heave_rao", "literal": "1.113 m/m", "value": float(heave["displacement_m"]["z"]["amp"]), "source": rel(BARGE_RAO), "pointer": "/points[id=landing_center]/rows/*/displacement_m/z/amp"},
        {"id": "mesh_medium_fine", "literal": "5.88%", "value": 100 * float(hydro["acceptance"]["pair_checks"][1]["maximum_selected_relative_change"]), "source": rel(HYDRO_REPORT), "pointer": "/acceptance/pair_checks/1"},
        {"id": "center_p95", "literal": "1.570 m/s", "value": float(center_wave["statistics"]["landing_center.max_abs_vertical_velocity_m_s"]["p95"]), "source": rel(WAVE_REPORT), "pointer": "/cases/*/statistics/landing_center.max_abs_vertical_velocity_m_s/p95"},
        {"id": "actual_feet_p95", "literal": "1.591 m/s", "value": float(feet_wave["statistics"]["four_feet.max_vertical_velocity_span_m_s"]["p95"]), "source": rel(WAVE_REPORT), "pointer": "/cases/*/statistics/four_feet.max_vertical_velocity_span_m_s/p95"},
        {"id": "valid_cases", "literal": "41 of 63", "value": [valid_cases, len(wave["cases"])], "source": rel(WAVE_REPORT), "pointer": "/cases/*/linear_validity/pass"},
        {"id": "touchdown_span_production", "literal": "0.229 s", "value": float(final_contact["contact_state"]["touchdown_span_s"]), "source": rel(CHRONO_REPORT), "pointer": "/iterative_run/final_contact_summary/contact_state/touchdown_span_s"},
        {"id": "production_peak_force", "literal": "5.006 MN", "value": float(final_contact["max_leg_contact_force_kn"]) / 1000, "source": rel(CHRONO_REPORT), "pointer": "/iterative_run/final_contact_summary/max_leg_contact_force_kn"},
        {"id": "platform_energy_residual", "literal": "-6.43e-6", "value": float(energy["platform_energy_residual_relative"]), "source": rel(CHRONO_REPORT), "pointer": "/algorithms/four_pass_platform_update/platform_energy/platform_energy_residual_relative"},
        {"id": "cert_file_failures", "literal": "157 file-level failures", "value": {name: int(case["comparison"]["failed_files"]) for name, case in cert["cases"].items()}, "source": rel(CERT_DIAGNOSTIC), "pointer": "/cases/*/comparison/failed_files"},
    ]
    for claim in claims:
        claim["literal_present"] = claim["literal"] in manuscript

    forbidden_old_literals = ["1.128 m/m", "1.505 m/s", "2.435 m/s", "0.148 m", "2.678 MN", "100 realizations", "one-pass correction"]
    style_checks = {
        "forbidden_old_literals": {item: item in manuscript for item in forbidden_old_literals},
        "explicit_product_chain_label_present": "HAMS-Cummins-Chrono" in manuscript,
        "em_dash_count": manuscript.count("—"),
        "template_phrases": {phrase: phrase.lower() in manuscript.lower() for phrase in ["This paper presents", "The present work", "It is important to note"]},
    }

    limitations = [
        {"severity": "high", "item": "Repository certification regression", "evidence": "The registered four-case comparator reports 157 failed output files (65/13/7/72 by case).", "claim_boundary": "No solver-certification or hydrodynamic-benchmark pass is claimed; cause remains unresolved."},
        {"severity": "high", "item": "Hydrodynamic mesh refinement", "evidence": "Medium-to-fine maximum selected change is 5.88%, above the 5% criterion.", "claim_boundary": "Medium-grid RAOs are reported as sampled case-study results, not mesh-converged predictions."},
        {"severity": "high", "item": "Linear free-surface validity", "evidence": f"Only {valid_cases}/63 random-wave cases pass tilt and deck-edge criteria; worst P95 tilt is {float(tilt_wave['statistics']['platform.max_tilt_deg']['p95']):.2f} deg.", "claim_boundary": "Failed conditions are screens for nonlinear analysis, not operational predictions."},
        {"severity": "high", "item": "Contact numerical convergence", "evidence": "Time-step convergence and contact-stiffness regularization both fail for local force/stroke/touchdown metrics.", "claim_boundary": "No contact peak is qualified as a design load."},
        {"severity": "high", "item": "Stable standing", "evidence": "Final vertical speed and angular rate exceed the diagnostic thresholds.", "claim_boundary": "The simulated interval demonstrates contact dynamics, not a completed stable landing."},
        {"severity": "medium", "item": "Reduced-model identifiability", "evidence": "127/128 starts are near-optimal and parameters are strongly correlated.", "claim_boundary": "Yang curves support response comparison, not unique physical parameter recovery."},
        {"severity": "medium", "item": "Horizontal platform closure", "evidence": "Fx, Fy and Mz are calculated but not injected because horizontal restoring is absent.", "claim_boundary": "Feedback is restricted to heave, roll and pitch."},
        {"severity": "medium", "item": "Literature-derived full-scale inputs", "evidence": "Vehicle geometry and absorber curves are proxies digitized from public literature; azimuths and component inertia allocation remain declared assumptions.", "claim_boundary": "The full-scale calculation is a proof of concept, not a reproduction of proprietary vehicle data."},
    ]

    files_ok = all(item["exists"] for item in evidence_files + code_files)
    claims_ok = all(item["literal_present"] for item in claims)
    figures_ok = all(
        item["checks"].get("png_exists")
        and item["checks"].get("svg_exists")
        and item["checks"].get("nonblank")
        and item["checks"].get("minimum_dimension_at_least_1800_px")
        and item["checks"].get("svg_contains_times_new_roman")
        for item in figures
    )
    stale_ok = not any(style_checks["forbidden_old_literals"].values())
    report = {
        "audit_id": "SeaLandingPaper-ResearchIntegrity-Audit-v2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_WITH_DECLARED_LIMITATIONS" if files_ok and claims_ok and figures_ok and stale_ok else "FAIL",
        "classification": {
            "present_calculation": "Output produced in this project from executable code.",
            "reference_target": "Published value or digitized curve used only for labelled comparison/input.",
            "proxy_or_assumption": "Input introduced because open literature does not supply vehicle data; it cannot support an exact-reproduction claim.",
        },
        "checks": {"evidence_files_exist": files_ok, "protected_claims_present": claims_ok, "figures_pass_mechanical_checks": figures_ok, "old_literals_removed": stale_ok, "all_loaded_numeric_trees_finite": all(finite_tree(value) for value in [yang, ident, hydro, rao, wave, duration, chrono])},
        "current_results": {
            "medium_heave_rao_m_per_m": float(heave["displacement_m"]["z"]["amp"]),
            "hydrodynamic_acceptance": hydro["acceptance"],
            "random_wave_acceptance": wave["acceptance"],
            "random_wave_valid_case_count": valid_cases,
            "random_wave_case_count": len(wave["cases"]),
            "duration_center_p95_m_s": {
                "Hs3_Tp8": {str(seconds): duration_value(duration, "Hs3_Tp8", "landing_center.max_abs_vertical_velocity_m_s", seconds) for seconds in [600, 1200, 1800]},
                "Hs3_Tp10": {str(seconds): duration_value(duration, "Hs3_Tp10", "landing_center.max_abs_vertical_velocity_m_s", seconds) for seconds in [600, 1200, 1800]},
            },
            "coupling_iteration_pass": chrono["coupling_iteration_convergence"]["pass"],
            "contact_time_step_pass": chrono["time_step_convergence"]["pass"],
            "contact_load_prediction_qualified": chrono["contact_regularization_sensitivity"]["load_prediction_qualified"],
            "stable_standing_pass": final_contact["stable_standing_diagnostic"]["all_flags_true"],
            "final_platform_summary": final_platform,
        },
        "claim_registry": claims,
        "evidence_files": evidence_files,
        "code_files": code_files,
        "figures": figures,
        "style_checks": style_checks,
        "declared_limitations": limitations,
    }
    return report


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return lines


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# 海上回收着陆论文真实性准确性与完整性审查",
        "",
        f"**审查编号：** `{report['audit_id']}`  ",
        f"**生成时间（UTC）：** `{report['generated_utc']}`  ",
        f"**机器审查结论：** `{report['status']}`",
        "",
        "## 1. 审查原则",
        "",
        "本审查把本项目重新计算的数据、文献对照数据和因公开资料不足而采用的代理输入分开记录。文献曲线只能作为带标签的对照或输入，不能写成本文计算结果；代理几何、数字化缓冲器曲线和数值接触参数不能用于声称复现了原作者的专有模型。任何未通过的数值判据均保留为限制，不以图形平滑或叙述判断改写为通过。",
        "",
        "## 2. 总体结论",
        "",
        "当前正文已切换到最新的中等网格水动力、1000 组随机波、实际 6.926 m 四足布局和同一平台四次耦合输出。旧版 1.128 m/m、1.505 m/s、2.435 m/s、2.678 MN 和 0.148 m 等数字均已移除。正文没有把计算未通过项包装为验证成功：仓库四案例认证比较出现 157 个文件级失败，水动力网格判据未通过，22 个随机波工况超出线性适用边界，接触时间步与刚度正则化未通过，526 s 时稳定站立诊断也未通过。",
        "",
        "## 3. 关键结果与证据边界",
        "",
    ]
    lines += markdown_table(
        ["项目", "机器结果", "正文解释"],
        [
            ["中等网格垂荡 RAO", f"{report['current_results']['medium_heave_rao_m_per_m']:.6f} m/m", "离散频率样本峰值；未称网格收敛"],
            ["网格判据", report["current_results"]["hydrodynamic_acceptance"]["status"], "medium-to-fine 最大选定变化 5.88%，阈值 5%"],
            ["随机波线性有效", f"{report['current_results']['random_wave_valid_case_count']}/{report['current_results']['random_wave_case_count']}", "失效工况不作作业海况或成功率结论"],
            ["耦合迭代", str(report["current_results"]["coupling_iteration_pass"]), "四次固定点的最后一次更新满足 2%"],
            ["接触时间步", str(report["current_results"]["contact_time_step_pass"]), "峰值力、行程和触地时序不同时收敛"],
            ["接触载荷资格", str(report["current_results"]["contact_load_prediction_qualified"]), "不得作为真实型号设计载荷"],
            ["稳定站立", str(report["current_results"]["stable_standing_pass"]), "动画只能描述当前 20 s 接触过程"],
        ],
    )
    lines += ["", "## 4. 正文数值锁定", ""]
    lines += markdown_table(
        ["声明", "正文字面值", "机器值", "来源", "存在"],
        [[item["id"], f"`{item['literal']}`", json.dumps(item["value"], ensure_ascii=False), f"`{item['source']}`", "是" if item["literal_present"] else "否"] for item in report["claim_registry"]],
    )
    lines += ["", "## 5. 文件溯源", ""]
    lines += markdown_table(
        ["文件", "类别", "用途", "存在", "SHA-256 前缀"],
        [[f"`{item['path']}`", item["evidence_class"], item["role"], "是" if item["exists"] else "否", item.get("sha256", "")[:16]] for item in report["evidence_files"]],
    )
    lines += ["", "## 6. 图件审查", "", "全部图件由同一脚本基于机器输出生成，采用 SciencePlots `science/no-latex` 风格、Times New Roman 字体，并同时输出 600 dpi PNG 和可编辑 SVG。文献曲线使用灰黑虚线，本文计算使用彩色实线。图形不经办公软件手工移动数据点。", ""]
    lines += markdown_table(
        ["图件", "用途", "像素", "TNR", "SHA-256 前缀"],
        [[item["id"], item["role"], f"{item['checks'].get('width_px')} x {item['checks'].get('height_px')}", "是" if item["checks"].get("svg_contains_times_new_roman") else "否", item["checks"].get("sha256", "")[:16]] for item in report["figures"]],
    )
    lines += ["", "## 7. 未解决问题及结论约束", ""]
    lines += markdown_table(
        ["严重度", "项目", "证据", "结论约束"],
        [[item["severity"], item["item"], item["evidence"], item["claim_boundary"]] for item in report["declared_limitations"]],
    )
    lines += [
        "",
        "## 8. 可重复执行命令",
        "",
        "```powershell",
        "python .\\analysis\\rocket_recovery\\barge_hydrodynamic_convergence.py --execute",
        "python .\\analysis\\rocket_recovery\\deck_point_rao.py --case .\\RocketRecoveryCases\\Barge_120x50",
        "python .\\analysis\\rocket_recovery\\barge_wave_sensitivity.py report",
        "python .\\analysis\\rocket_recovery\\barge_wave_duration_sensitivity.py report",
        "python .\\analysis\\rocket_recovery\\yang_2026_identifiability.py report",
        "python .\\analysis\\rocket_recovery\\chrono_same_platform_multibody.py report",
        "python .\\analysis\\rocket_recovery\\yang_2026_figures.py",
        "python .\\analysis\\rocket_recovery\\paper_integrity_audit.py report",
        "```",
        "",
        "## 9. 审查结论",
        "",
        "`PASS_WITH_DECLARED_LIMITATIONS` 表示数字、来源、代码、图件和正文限定语之间已建立可追溯关系，不表示所有数值模型均通过验证。现阶段能够支持的是理论接口、实现可重复性、局部甲板运动机制和同一平台反馈演示；不能支持真实型号支腿载荷、着陆成功率、允许海况或全六自由度动力定位闭环。",
        "",
    ]
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")


def report_command() -> dict[str, Any]:
    report = build_report()
    write_json(REPORT, report)
    write_markdown(report)
    print(json.dumps({"status": report["status"], "report": rel(REPORT), "markdown": rel(MARKDOWN), "checks": report["checks"]}, ensure_ascii=False, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the manuscript evidence and integrity audit.")
    parser.add_argument("command", nargs="?", default="report", choices=["report"])
    parser.parse_args()
    result = report_command()
    if result["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
