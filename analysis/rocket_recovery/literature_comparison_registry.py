from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
except ImportError:
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
REGISTRY_JSON = CASE_ROOT / "literature-comparison-registry.json"
REGISTRY_MD = ROOT / "docs" / "literature-comparison-registry.md"
REGISTRY_JS = VISUALIZATION_DIR / "literature-comparison-registry-data.js"

NARGOLKAR_REPORT = ROCKET_CASES_DIR / "Paper_Nargolkar_2025" / "nargolkar-2025-report-data.json"
WANG_REPORT = ROCKET_CASES_DIR / "Paper_WangZhi_2023" / "wang-2023-report-data.json"
LEG_CONTACT_REPORT = ROCKET_CASES_DIR / "Stage3_LandingLegContact" / "landing-leg-contact-envelope.json"
CHRONO_STAGE3_REPORT = CASE_ROOT / "chrono-stage3-tripod-report-data.json"
CHRONO_LOCK_TWO_WAY_REPORT = CASE_ROOT / "chrono-stage3-lock-two-way-report-data.json"
THIES_BUFFER_CURVES = CASE_ROOT / "validation" / "thies_absorber_curves" / "thies-buffer-curves.json"
CHRONO_THIES_BUFFER_REPORT = CASE_ROOT / "chrono-stage3-thies-buffer-report-data.json"
YANG_REPORT = ROCKET_CASES_DIR / "Paper_Yang_2026" / "yang-2026-evidence-report.json"
YANG_REFERENCE = ROCKET_CASES_DIR / "Paper_Yang_2026" / "reference" / "yang-2026-published.json"
YANG_DIGITIZED = ROCKET_CASES_DIR / "Paper_Yang_2026" / "reference" / "digitized" / "yang-2026-fig09-11-digitization.json"

PAPER_MD = {
    "nargolkar_2025": Path("海上平台火箭回收文献") / "065002_1_2.0002061.md",
    "wang_2023": Path("海上平台火箭回收文献") / "海上火箭回收过程中船舶耦合运动响应分析_王智.md",
    "thies_2022": Path("海上平台火箭回收文献") / "P3_Thies_2022.md",
    "yue_2022": Path("海上平台火箭回收文献") / "P4_Yue_2022.md",
    "li_2025": Path("海上平台火箭回收文献") / "P5_Li_2025_Aerospace.md",
    "wang_actuators_2023": Path("海上平台火箭回收文献") / "P6_Wang_2023_Actuators.md",
    "xie_2025": Path("海上平台火箭回收文献") / "P7_Xie_2025.md",
    "yang_2026": Path("新论文参考写作论文") / "Analysis+of+Sea-Based+Landing+Dynamics+of+Reusable+Landing+Vehicle+Considering+Mechanism+Flexibility.md",
}

PAPER_PDF = {
    "nargolkar_2025": Path("海上平台火箭回收文献") / "065002_1_2.0002061.pdf",
    "wang_2023": Path("海上平台火箭回收文献") / "P2_WangZhi_2023_ShipSciTech.pdf",
    "thies_2022": Path("海上平台火箭回收文献") / "P3_Thies_2022.pdf",
    "yue_2022": Path("海上平台火箭回收文献") / "P4_Yue_2022.pdf",
    "li_2025": Path("海上平台火箭回收文献") / "P5_Li_2025_Aerospace.pdf",
    "wang_actuators_2023": Path("海上平台火箭回收文献") / "P6_Wang_2023_Actuators.pdf",
    "xie_2025": Path("海上平台火箭回收文献") / "P7_Xie_2025.pdf",
    "yang_2026": Path("新论文参考写作论文") / "Analysis+of+Sea-Based+Landing+Dynamics+of+Reusable+Landing+Vehicle+Considering+Mechanism+Flexibility.pdf",
}

RESPONSE_UNITS = {
    "barge_surge_m": "m",
    "barge_heave_m": "m",
    "barge_pitch_rad": "rad",
    "rlv_transverse_m": "m",
    "rlv_axial_m": "m",
    "rlv_rotation_rad": "rad",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return read_json(path)


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def error_metrics(paper_value: Any, computed_value: Any) -> dict[str, Any]:
    if not finite_number(paper_value) or not finite_number(computed_value):
        return {}
    paper = float(paper_value)
    computed = float(computed_value)
    scale = max(abs(paper), 1.0e-12)
    return {
        "abs_error": abs(computed - paper),
        "relative_error": abs(computed - paper) / scale,
    }


def source_paths(paper_id: str) -> dict[str, Any]:
    md = ROOT / PAPER_MD[paper_id]
    pdf = ROOT / PAPER_PDF[paper_id]
    return {
        "markdown": rel(md),
        "markdown_exists": md.exists(),
        "pdf": rel(pdf),
        "pdf_exists": pdf.exists(),
    }


def add_missing_artifact(entries: list[dict[str, Any]], report_name: str, path: Path) -> None:
    entries.append(
        {
            "id": f"missing_artifact_{report_name}",
            "paper_id": "multi",
            "category": "missing_artifact",
            "comparison_level": "none",
            "reproduction_status": "missing",
            "model_component": "artifact",
            "paper_data_source": {},
            "computed_data_source": {"report_json": rel(path), "exists": path.exists()},
            "blocking_reason": "The prerequisite report has not been generated yet.",
            "required_action": f"Run the producer script for {report_name}.",
        }
    )


def add_yang_entries(
    entries: list[dict[str, Any]],
    report: dict[str, Any],
    reference: dict[str, Any],
    digitized: dict[str, Any],
) -> None:
    if not report or not reference:
        add_missing_artifact(entries, "yang_2026", YANG_REPORT)
        return

    audit_by_key = {
        (row["condition_id"], row["metric"]): row
        for row in report["table_2_audit"]["rows"]
    }
    for source in reference["table_2"]:
        audit = audit_by_key[(source["condition_id"], source["metric"])]
        for branch in ("flexible", "rigid"):
            printed_error = float(source[f"{branch}_error_percent_printed"])
            recomputed_error = float(audit["recomputed"][f"{branch}_error_percent"])
            entry_id = f"yang_2026_{source['condition_id']}_{source['metric']}_{branch}"
            entries.append(
                {
                    "id": entry_id,
                    "paper_id": "yang_2026",
                    "paper_title": reference["paper"]["title"],
                    "category": "published_scalar_consistency_audit",
                    "comparison_level": "publication_internal_consistency",
                    "reproduction_status": "internally_consistent" if audit["internally_consistent"] else "publication_inconsistency",
                    "model_component": "Yang 2026 evidence layer",
                    "paper_data_source": {
                        **source_paths("yang_2026"),
                        "table": "Table 2",
                        "source_extract_method": "Direct transcription from the supplied PDF; cross-checked against the PDF rendering.",
                    },
                    "computed_data_source": {
                        "report_json": rel(YANG_REPORT),
                        "method": "Recompute abs(model-test)/abs(test) from the printed scalar values.",
                    },
                    "metric": f"{source['condition_id']} {source['metric']} {branch} printed error",
                    "unit": "%",
                    "paper_value": printed_error,
                    "computed_value": recomputed_error,
                    "error_metrics": error_metrics(printed_error, recomputed_error),
                    "limitations": [source.get("note")] if source.get("note") else [],
                }
            )

    for metric, unit in [
        ("peak_vertical_acceleration_g", "g"),
        ("maximum_main_strut_load_n", "N"),
        ("maximum_buffer_stroke_m", "m"),
        ("minimum_stability_margin_m", "m"),
    ]:
        entries.append(
            {
                "id": f"yang_2026_sea_{metric}",
                "paper_id": "yang_2026",
                "paper_title": reference["paper"]["title"],
                "category": "published_validation_target",
                "comparison_level": "published_scalar_pending_model",
                "reproduction_status": "not_reproduced_model_pending",
                "model_component": "future HAMS/Cummins + Chrono sea-landing case",
                "paper_data_source": {
                    **source_paths("yang_2026"),
                    "section_or_figure": "Section 4.4 / Figure 17",
                    "source_extract_method": "Direct scalar value from the supplied paper text.",
                },
                "computed_data_source": {"report_json": rel(YANG_REPORT), "current_model_status": "evidence and deck-filter layer implemented; landing model pending"},
                "metric": metric,
                "unit": unit,
                "paper_value": reference["sea_case"][metric],
                "computed_value": None,
                "error_metrics": {},
                "limitations": ["The paper does not publish the unique ADAMS/Abaqus parameter set or white-noise realization."],
            }
        )

    if digitized:
        for curve in digitized.get("curves", []):
            quality = curve["quality"]
            entries.append(
                {
                    "id": f"yang_2026_{curve['id']}",
                    "paper_id": "yang_2026",
                    "paper_title": reference["paper"]["title"],
                    "category": "digitized_reference_curve",
                    "comparison_level": "digitized_curve_pending_model",
                    "reproduction_status": "digitized_pending_model_comparison",
                    "model_component": "four-leg landing validation",
                    "paper_data_source": {
                        **source_paths("yang_2026"),
                        "figure": curve["figure"],
                        "curve": "red dashed Test curve",
                        "axis_box_px": curve["axis_box_px"],
                        "source_image_sha256": digitized["source_image_sha256"],
                        "source_extract_method": digitized["method"],
                    },
                    "computed_data_source": {
                        "digitized_csv": curve["csv"],
                        "sampled_columns": quality["sampled_columns"],
                        "column_coverage_fraction": quality["column_coverage_fraction"],
                        "model_comparison": "pending",
                    },
                    "metric": curve["metric"],
                    "unit": curve["unit"],
                    "paper_value": quality["published_peak"],
                    "computed_value": quality["digitized_peak"],
                    "error_metrics": error_metrics(quality["published_peak"], quality["digitized_peak"]),
                    "limitations": curve["limitations"],
                }
            )
    else:
        entries.append(
            {
                "id": "yang_2026_fig9_11_time_histories",
                "paper_id": "yang_2026",
                "paper_title": reference["paper"]["title"],
                "category": "missing_curve",
                "comparison_level": "not_available_for_pointwise_reproduction",
                "reproduction_status": "not_reproduced_curve_not_digitized",
                "model_component": "four-leg landing validation",
                "paper_data_source": {**source_paths("yang_2026"), "figure": "Figures 9-11"},
                "computed_data_source": {},
                "metric": "acceleration, main-strut load and buffer-stroke histories",
                "unit": "mixed",
                "paper_value": None,
                "computed_value": None,
                "error_metrics": {},
                "blocking_reason": "The visible raster curves have not yet been converted to machine-readable samples.",
                "required_action": "Digitize Figures 9-11 with axis and color provenance before pointwise comparison.",
                "limitations": ["Scalar targets are available, but curve-shape agreement is not yet measured."],
            }
        )

    entries.append(
            {
                "id": "yang_2026_fig17_sea_time_histories",
                "paper_id": "yang_2026",
                "paper_title": reference["paper"]["title"],
                "category": "missing_curve",
                "comparison_level": "not_available_for_pointwise_reproduction",
                "reproduction_status": "not_reproduced_unknown_random_realization",
                "model_component": "prescribed-deck sea landing",
                "paper_data_source": {**source_paths("yang_2026"), "figure": "Figure 17"},
                "computed_data_source": {"report_json": rel(YANG_REPORT)},
                "metric": "sea-landing acceleration, load, stroke and stability histories",
                "unit": "mixed",
                "paper_value": None,
                "computed_value": None,
                "error_metrics": {},
                "blocking_reason": "The paper omits the white-noise normalization and seed, so the plotted realization is not uniquely reproducible.",
                "required_action": "Digitize Figure 17 for shape comparison and compare stochastic statistics rather than claiming a pointwise random-trace reproduction.",
                "limitations": ["The published transfer functions are implemented exactly; the random realization is not author-identical."],
            }
    )


def add_nargolkar_entries(entries: list[dict[str, Any]], narg: dict[str, Any]) -> None:
    if not narg:
        add_missing_artifact(entries, "nargolkar_2025", NARGOLKAR_REPORT)
        return

    digitized = narg.get("paper_time_digitized", {})
    comparisons = narg.get("paper_time_comparison", {})
    digitization_method = digitized.get("method", "not recorded")
    comparison_method = comparisons.get("method", "not recorded")
    comp_cases = comparisons.get("cases", {})

    for case_id, velocities in digitized.get("cases", {}).items():
        for velocity, responses in velocities.items():
            for response_id, curve in responses.items():
                comp = comp_cases.get(case_id, {}).get(velocity, {}).get(response_id, {})
                compared = comp.get("status") == "compared"
                entry = {
                    "id": f"nargolkar_2025_{case_id}_{velocity}_{response_id}",
                    "paper_id": "nargolkar_2025",
                    "paper_title": "Coupled hydrodynamic-structural analysis on reusable launch vehicle landing on barge",
                    "category": "digitized_time_curve",
                    "comparison_level": "pointwise_digitized_curve" if compared else "digitized_curve_gap",
                    "reproduction_status": "pointwise_compared" if compared else f"not_pointwise_compared:{comp.get('status', 'missing_comparison')}",
                    "model_component": "HAMS/Cummins platform + equivalent RLV structure",
                    "paper_data_source": {
                        **source_paths("nargolkar_2025"),
                        "figure": curve.get("figure"),
                        "legend": curve.get("legend"),
                        "family": curve.get("family"),
                        "axis_box_px": curve.get("axis_box_px"),
                        "axis_time_range_s": curve.get("axis_time_range_s"),
                        "axis_value_range": curve.get("axis_value_range"),
                        "digitization_method": digitization_method,
                        "digitization_note": curve.get("digitization_note"),
                        "quality": curve.get("quality"),
                        "quality_note": curve.get("quality_note"),
                        "paper_point_count": curve.get("point_count"),
                    },
                    "computed_data_source": {
                        "report_json": rel(NARGOLKAR_REPORT),
                        "case_id": case_id,
                        "touchdown_velocity_m_s": float(velocity),
                        "response_id": response_id,
                        "comparison_method": comparison_method,
                    },
                    "metric": response_id,
                    "unit": RESPONSE_UNITS.get(response_id, "unknown"),
                    "time_range_s": comp.get("time_range_s"),
                    "n_points": comp.get("n_points"),
                    "error_metrics": {
                        key: comp.get(key)
                        for key in [
                            "rmse",
                            "normalized_rmse_vs_paper_peak",
                            "mean_error",
                            "correlation",
                            "paper_peak_abs",
                            "our_peak_abs",
                            "peak_ratio_our_over_paper",
                        ]
                        if key in comp
                    },
                    "limitations": [
                        "Digitized from raster figure, not original author data.",
                        "Only the visible 0..3 s figure interval is compared.",
                    ],
                }
                if not compared:
                    entry["blocking_reason"] = comp.get("paper_quality_note") or comp.get("reason") or "No usable comparison row was generated."
                    entry["required_action"] = "Improve digitization coverage or add author-provided numeric curve data."
                entries.append(entry)

    paper_audit = narg.get("paper_audit", {})
    for idx, row in enumerate(paper_audit.get("numeric_comparisons", []), start=1):
        paper_value = row.get("source")
        computed_value = row.get("implemented")
        entries.append(
            {
                "id": f"nargolkar_2025_table_value_{idx:03d}",
                "paper_id": "nargolkar_2025",
                "paper_title": "Coupled hydrodynamic-structural analysis on reusable launch vehicle landing on barge",
                "category": "paper_table_value",
                "comparison_level": "table_value_exactness",
                "reproduction_status": f"table_{row.get('status', 'unknown')}",
                "model_component": "input parameter",
                "paper_data_source": {
                    **source_paths("nargolkar_2025"),
                    "table_or_source": row.get("label"),
                    "source_extract_method": "Markdown table parser",
                    "source_cell": row.get("source_cell"),
                },
                "computed_data_source": {
                    "report_json": rel(NARGOLKAR_REPORT),
                    "implemented_field": row.get("label"),
                },
                "metric": row.get("label"),
                "unit": row.get("unit"),
                "paper_value": paper_value,
                "computed_value": computed_value,
                "error_metrics": error_metrics(paper_value, computed_value)
                or {"abs_error": row.get("abs_error"), "relative_error": row.get("relative_error")},
                "limitations": ["Parameter-table match only; not a dynamic response curve."],
            }
        )


def add_wang_entries(entries: list[dict[str, Any]], wang: dict[str, Any]) -> None:
    if not wang:
        add_missing_artifact(entries, "wang_2023", WANG_REPORT)
        return

    for row in wang.get("comparison", []):
        entries.append(
            {
                "id": f"wang_2023_{row.get('id')}",
                "paper_id": "wang_2023",
                "paper_title": "海上火箭回收过程中船舶耦合运动响应分析",
                "category": "published_text_indicator",
                "comparison_level": "scalar_text_indicator",
                "reproduction_status": "surrogate_scale_compared",
                "model_component": "wave/plume/platform Cummins response",
                "paper_data_source": {
                    **source_paths("wang_2023"),
                    "section_or_figure": row.get("source"),
                    "source_extract_method": "Manual text extraction from supplied Markdown; original AQWA/STAR-CCM+ curves are not machine-readable.",
                },
                "computed_data_source": {
                    "report_json": rel(WANG_REPORT),
                    "case_id": row.get("case"),
                    "environment": row.get("environment"),
                    "metric": row.get("metric"),
                    "method": "Open HAMS/Cummins surrogate using published principal dimensions, JONSWAP sea state, and text-described plume load.",
                },
                "metric": row.get("metric"),
                "unit": row.get("unit"),
                "paper_value": row.get("paper_value"),
                "computed_value": row.get("computed_value"),
                "error_metrics": {
                    "abs_error": row.get("abs_error"),
                    "relative_error": row.get("relative_error"),
                },
                "limitations": [
                    "Reference-only quantity because the AQWA hull mesh, mooring mechanical properties and STAR-CCM+ time samples are not published.",
                    "This does not claim point-by-point reproduction of Figures 8-10.",
                ],
            }
        )

    plume = (wang.get("config") or {}).get("plume_load", {})
    if plume:
        entries.append(
            {
                "id": "wang_2023_plume_plateau_text_value",
                "paper_id": "wang_2023",
                "paper_title": "海上火箭回收过程中船舶耦合运动响应分析",
                "category": "paper_text_load_value",
                "comparison_level": "model_input_from_text",
                "reproduction_status": "implemented_as_input",
                "model_component": "plume load",
                "paper_data_source": {
                    **source_paths("wang_2023"),
                    "section_or_figure": "Section 3.1.3 and Figure 6 description",
                    "source_extract_method": "Text value extraction; full oscillatory CFD trace absent.",
                },
                "computed_data_source": {
                    "report_json": rel(WANG_REPORT),
                    "implemented_field": "config.plume_load.plateau_n",
                },
                "metric": "plume_plateau_force",
                "unit": "N",
                "paper_value": 20_400_000.0,
                "computed_value": plume.get("plateau_n"),
                "error_metrics": error_metrics(20_400_000.0, plume.get("plateau_n")),
                "limitations": [
                    "The 506-510 s segment is treated as the text-stated 20,400 kN plateau; the CFD oscillatory trace is registered as a missing curve.",
                ],
            }
        )


def add_thies_entries(entries: list[dict[str, Any]], leg_report: dict[str, Any], stage3: dict[str, Any]) -> None:
    if not leg_report:
        add_missing_artifact(entries, "landing_leg_contact", LEG_CONTACT_REPORT)
    if not stage3:
        add_missing_artifact(entries, "chrono_stage3_tripod", CHRONO_STAGE3_REPORT)

    for row in leg_report.get("comparison", []) if leg_report else []:
        entries.append(
            {
                "id": f"thies_2022_{row.get('id')}",
                "paper_id": "thies_2022",
                "paper_title": "Investigation of the landing dynamics of a reusable launch vehicle and derivation of dimension loading for the landing leg",
                "category": "paper_table_value",
                "comparison_level": "table_value_exactness",
                "reproduction_status": "computed_from_paper_inputs",
                "model_component": "touchdown energy",
                "paper_data_source": {
                    **source_paths("thies_2022"),
                    "table_or_source": row.get("source"),
                    "source_extract_method": "Table values from supplied Markdown plus formula 0.5*m*v^2.",
                },
                "computed_data_source": {
                    "report_json": rel(LEG_CONTACT_REPORT),
                    "method": "Independent kinetic-energy recomputation from mass and nominal vertical velocity.",
                },
                "metric": row.get("id"),
                "unit": row.get("unit"),
                "paper_value": row.get("paper_value"),
                "computed_value": row.get("computed_value"),
                "error_metrics": {
                    "abs_error": row.get("abs_error"),
                    "relative_error": row.get("relative_error"),
                },
                "limitations": ["This validates the input scale, not Adams force-time curves."],
            }
        )

    cfg = (stage3.get("config") or {}) if stage3 else {}
    legs = cfg.get("legs", {})
    rocket = cfg.get("rocket", {})
    sim = ((stage3.get("simulations") or {}).get("calm_center") or {}) if stage3 else {}
    summary = sim.get("summary", {})
    thies_targets = [
        (
            "thies_touchdown_vertical_velocity",
            "Table 6 / Table 7",
            "touchdown_vertical_velocity",
            "m/s",
            5.0,
            rocket.get("touchdown_vertical_velocity_m_s"),
            "input_value",
        ),
        (
            "thies_table8_damper_deformation",
            "Table 8",
            "max_leg_stroke",
            "m",
            0.420,
            summary.get("max_leg_stroke_m"),
            "surrogate_scale_check",
        ),
        (
            "thies_table8_leg_force_magnitude",
            "Table 8",
            "max_leg_contact_force",
            "kN",
            902.0,
            summary.get("max_leg_contact_force_kn"),
            "surrogate_scale_check",
        ),
        (
            "thies_table8_spring_damper_force",
            "Table 8",
            "max_leg_tsda_force",
            "kN",
            935.0,
            summary.get("max_leg_tsda_force_kn"),
            "surrogate_scale_check",
        ),
        (
            "thies_table8_nozzle_clearance",
            "Table 8",
            "final_nozzle_clearance",
            "m",
            0.570,
            summary.get("final_nozzle_clearance_m"),
            "surrogate_scale_check",
        ),
        (
            "thies_table3_required_nozzle_clearance",
            "Table 3",
            "required_nozzle_clearance",
            "m",
            0.5475,
            rocket.get("nozzle_clearance_required_m"),
            "input_value",
        ),
        (
            "thies_table10_damper_stiffness",
            "Table 10",
            "damper_stiffness",
            "N/m",
            2_600_000.0,
            legs.get("damper_stiffness_n_m"),
            "input_value",
        ),
        (
            "thies_table10_damper_damping",
            "Table 10",
            "damper_damping",
            "N*s/m",
            1_300_000.0,
            legs.get("damper_damping_ns_m"),
            "input_value",
        ),
    ]
    for entry_id, table, metric, unit, paper_value, computed_value, level in thies_targets:
        entries.append(
            {
                "id": entry_id,
                "paper_id": "thies_2022",
                "paper_title": "Investigation of the landing dynamics of a reusable launch vehicle and derivation of dimension loading for the landing leg",
                "category": "paper_table_or_scale_value",
                "comparison_level": level,
                "reproduction_status": "implemented_input" if level == "input_value" else "proxy_result_compared_to_adams_table",
                "model_component": "Chrono landing-leg proxy",
                "paper_data_source": {
                    **source_paths("thies_2022"),
                    "table_or_source": table,
                    "source_extract_method": "Manual table extraction from supplied Markdown.",
                },
                "computed_data_source": {
                    "report_json": rel(CHRONO_STAGE3_REPORT),
                    "case_id": "calm_center",
                    "field": metric,
                },
                "metric": metric,
                "unit": unit,
                "paper_value": paper_value,
                "computed_value": computed_value,
                "error_metrics": error_metrics(paper_value, computed_value),
                "limitations": [
                    "Stage 3A is a Chrono tripod proxy, not the published MSC Adams model.",
                    "Large differences here are calibration signals, not hidden failures.",
                ]
                if level != "input_value"
                else ["Input value traceability check."],
            }
        )


def add_thies_digitized_buffer_entries(entries: list[dict[str, Any]], curves: dict[str, Any], chrono_report: dict[str, Any]) -> None:
    if not curves:
        return
    law = curves.get("chrono_buffer_law", {})
    report_law = (((chrono_report.get("config") or {}).get("legs") or {}).get("nonlinear_buffer_law") or {}) if chrono_report else {}
    simulated = bool(chrono_report.get("simulations")) and report_law.get("type") == "compression_only_table"
    for curve_id, curve in (curves.get("curves") or {}).items():
        if curve_id == "spring_force_stroke":
            metric = "absorber_spring_force_stroke"
            unit = "N versus m"
            points = law.get("force_stroke_points", [])
            range_key = "stroke_m"
        else:
            metric = "absorber_damper_force_velocity"
            unit = "N versus m/s"
            points = law.get("force_velocity_points", [])
            range_key = "velocity_m_s"
        entries.append(
            {
                "id": f"thies_2022_digitized_{curve_id}",
                "paper_id": "thies_2022",
                "paper_title": "Investigation of the landing dynamics of a reusable launch vehicle and derivation of dimension loading for the landing leg",
                "category": "digitized_buffer_curve",
                "comparison_level": "digitized_curve_table_input",
                "reproduction_status": "implemented_in_chrono_table_law" if simulated else "digitized_not_yet_simulated",
                "model_component": "Chrono main-buffer TSDA force law",
                "paper_data_source": {
                    **source_paths("thies_2022"),
                    "figure": curve.get("figure"),
                    "caption": curve.get("caption"),
                    "crop_png": curve.get("crop_png"),
                    "axis_calibration": curve.get("axis_calibration"),
                    "source_extract_method": law.get("digitization", {}).get("method"),
                    "quality": curve.get("quality"),
                    "coverage_ratio": curve.get("coverage_ratio"),
                },
                "computed_data_source": {
                    "curve_json": rel(THIES_BUFFER_CURVES),
                    "chrono_report_json": rel(CHRONO_THIES_BUFFER_REPORT),
                    "law_type": report_law.get("type"),
                    "simulated_cases": list((chrono_report.get("simulations") or {}).keys()),
                },
                "metric": metric,
                "unit": unit,
                "paper_value": None,
                "computed_value": None,
                "n_points": len(points),
                "range": curve.get("range", {}).get(range_key),
                "error_metrics": {},
                "limitations": [
                    "Digitized from the visible raster PDF figure, not original Adams/absorber author data.",
                    "Hard-stop values outside the digitized Figure 4 range remain numerical guards.",
                ],
            }
        )

    if simulated and chrono_report.get("simulations", {}).get("calm_center"):
        summary = chrono_report["simulations"]["calm_center"]["summary"]
        paper_value = 935.0
        computed_value = summary.get("max_leg_tsda_force_kn")
        entries.append(
            {
                "id": "thies_2022_digitized_buffer_table8_force_check",
                "paper_id": "thies_2022",
                "paper_title": "Investigation of the landing dynamics of a reusable launch vehicle and derivation of dimension loading for the landing leg",
                "category": "digitized_buffer_scale_check",
                "comparison_level": "table_value_scale_check_with_digitized_law",
                "reproduction_status": "digitized_law_simulated_and_compared",
                "model_component": "Chrono main-buffer TSDA force law",
                "paper_data_source": {
                    **source_paths("thies_2022"),
                    "table_or_source": "Table 8 spring damper force magnitude",
                    "figure": "Figures 4-5",
                    "source_extract_method": "Table 8 scalar plus Figure 4/5 digitized force law.",
                },
                "computed_data_source": {
                    "chrono_report_json": rel(CHRONO_THIES_BUFFER_REPORT),
                    "case_id": "calm_center",
                    "field": "summary.max_leg_tsda_force_kn",
                },
                "metric": "max_leg_tsda_force",
                "unit": "kN",
                "paper_value": paper_value,
                "computed_value": computed_value,
                "error_metrics": error_metrics(paper_value, computed_value),
                "limitations": [
                    "This is a scalar force-scale check, not an Adams Figure 9 time-history reproduction.",
                ],
            }
        )


def add_published_error_band_entries(entries: list[dict[str, Any]], leg_report: dict[str, Any]) -> None:
    literature = leg_report.get("literature_inputs", {}) if leg_report else {}

    yue = literature.get("yue_2022", {})
    for metric, value in (yue.get("reported_validation_ranges") or {}).items():
        entries.append(
            {
                "id": f"yue_2022_reported_error_band_{metric}",
                "paper_id": "yue_2022",
                "paper_title": "Modeling and experimental validation of vertical landing reusable launch vehicle under symmetric landing conditions",
                "category": "published_error_band",
                "comparison_level": "literature_validation_context",
                "reproduction_status": "not_reproduced_reference_band_only",
                "model_component": "future four-leg validation",
                "paper_data_source": {
                    **source_paths("yue_2022"),
                    "section_or_figure": "Section 5 / Figure 19 text",
                    "source_extract_method": "Text extraction from supplied Markdown.",
                },
                "computed_data_source": {
                    "report_json": rel(LEG_CONTACT_REPORT),
                    "current_model_status": "not yet calibrated to Yue experiment.",
                },
                "metric": metric,
                "unit": "reported_percent_or_text_range",
                "paper_value": value,
                "computed_value": None,
                "error_metrics": {},
                "limitations": ["Used as a future validation band only; no Yue time-history curve has been digitized."],
            }
        )

    wang = literature.get("wang_actuators_2023", {})
    for metric, value in (wang.get("reported_errors") or {}).items():
        unit = "m/s^2" if metric.endswith("_m_s2") else "fraction"
        entries.append(
            {
                "id": f"wang_actuators_2023_reported_metric_{metric}",
                "paper_id": "wang_actuators_2023",
                "paper_title": "The Impact Modeling and Experimental Verification of a Launch Vehicle with Crushing-Type Landing Gear",
                "category": "published_error_or_experiment_metric",
                "comparison_level": "literature_validation_context",
                "reproduction_status": "not_reproduced_reference_metric_only",
                "model_component": "future contact-state validation",
                "paper_data_source": {
                    **source_paths("wang_actuators_2023"),
                    "section_or_figure": "Reported validation metrics in supplied Markdown",
                    "source_extract_method": "Text extraction from supplied Markdown.",
                },
                "computed_data_source": {
                    "report_json": rel(LEG_CONTACT_REPORT),
                    "current_model_status": "not yet calibrated to crushing-gear experiment.",
                },
                "metric": metric,
                "unit": unit,
                "paper_value": value,
                "computed_value": None,
                "error_metrics": {},
                "limitations": ["Crushing gear is a different mechanism; retained as future state-machine validation context."],
            }
        )


def add_missing_curve_gaps(entries: list[dict[str, Any]], *, thies_buffer_curves_available: bool) -> None:
    gaps = [
        {
            "id": "wang_2023_fig6_plume_load_trace",
            "paper_id": "wang_2023",
            "figure": "Figure 6",
            "metric": "plume_load_time_history",
            "unit": "N",
            "reason": "The paper/Markdown provides text values and qualitative trend, but no machine-readable CFD time samples.",
            "required_action": "Digitize Figure 6 or obtain author-provided STAR-CCM+ load samples.",
        },
        {
            "id": "wang_2023_fig8_10_motion_curves",
            "paper_id": "wang_2023",
            "figure": "Figures 8-10",
            "metric": "heave_roll_pitch_time_histories",
            "unit": "m/deg",
            "reason": "Only selected peak values are available from text; full AQWA time histories are not machine-readable.",
            "required_action": "Digitize Figures 8-10 or obtain AQWA output time histories.",
        },
        {
            "id": "thies_2022_fig4_5_absorber_curves",
            "paper_id": "thies_2022",
            "figure": "Figures 4-5",
            "metric": "absorber_force_stroke_and_force_velocity",
            "unit": "N/m and N*s/m equivalent curve",
            "reason": "The supplied Markdown contains captions and qualitative description, not point data for the nonlinear absorber curves.",
            "required_action": "Digitize Figures 4-5 or obtain the absorber property tables used in Adams.",
        },
        {
            "id": "thies_2022_fig9_10_adams_time_curves",
            "paper_id": "thies_2022",
            "figure": "Figures 9-10",
            "metric": "leg_force_damper_force_stroke_nozzle_clearance_time_histories",
            "unit": "kN/m/mm",
            "reason": "Current data has Table 8 scalar results, but not the Adams time-history curves.",
            "required_action": "Digitize Figures 9-10 or obtain Adams output data.",
        },
        {
            "id": "yue_2022_force_stroke_acceleration_curves",
            "paper_id": "yue_2022",
            "figure": "Figures 7-19",
            "metric": "experimental_and_simulated_force_stroke_acceleration_time_histories",
            "unit": "N/mm/m/s^2",
            "reason": "The Markdown records several peak values and error ranges, but not pointwise experimental curves.",
            "required_action": "Digitize the relevant figures before using Yue as a pointwise validation target.",
        },
        {
            "id": "li_2025_hydropneumatic_spring_tables",
            "paper_id": "li_2025",
            "figure": "hydropneumatic spring force curves / Akima fitted measured data",
            "metric": "force_stroke_force_velocity",
            "unit": "N",
            "reason": "The paper describes Akima fitting from measured motions/forces, but the supplied Markdown does not expose the measured table.",
            "required_action": "Add measured/digitized force-stroke and force-velocity tables to the Chrono buffer config.",
        },
    ]

    for gap in gaps:
        if gap["id"] == "thies_2022_fig4_5_absorber_curves" and thies_buffer_curves_available:
            continue
        entries.append(
            {
                "id": gap["id"],
                "paper_id": gap["paper_id"],
                "category": "missing_curve",
                "comparison_level": "not_available_for_pointwise_reproduction",
                "reproduction_status": "not_reproduced_missing_machine_readable_data",
                "model_component": "validation data",
                "paper_data_source": {
                    **source_paths(gap["paper_id"]),
                    "figure": gap["figure"],
                    "source_extract_method": "Gap identified from supplied Markdown/PDF inventory.",
                },
                "computed_data_source": {},
                "metric": gap["metric"],
                "unit": gap["unit"],
                "paper_value": None,
                "computed_value": None,
                "error_metrics": {},
                "blocking_reason": gap["reason"],
                "required_action": gap["required_action"],
                "limitations": ["This entry prevents unsupported claims of pointwise reproduction."],
            }
        )


def metadata_complete(entries: list[dict[str, Any]]) -> dict[str, Any]:
    missing: list[dict[str, str]] = []
    for entry in entries:
        category = entry.get("category")
        if category in {"missing_artifact"}:
            missing.append({"id": entry.get("id", ""), "field": "artifact", "reason": entry.get("blocking_reason", "")})
            continue
        paper_source = entry.get("paper_data_source") or {}
        if not paper_source:
            missing.append({"id": entry.get("id", ""), "field": "paper_data_source", "reason": "missing"})
        if category != "missing_curve" and not entry.get("unit"):
            missing.append({"id": entry.get("id", ""), "field": "unit", "reason": "missing"})
        if category != "missing_curve" and not entry.get("comparison_level"):
            missing.append({"id": entry.get("id", ""), "field": "comparison_level", "reason": "missing"})
        if category != "missing_curve" and finite_number(entry.get("paper_value")) and finite_number(entry.get("computed_value")) and not entry.get("error_metrics"):
            missing.append({"id": entry.get("id", ""), "field": "error_metrics", "reason": "numeric comparison lacks error metrics"})
        if category == "missing_curve" and (not entry.get("blocking_reason") or not entry.get("required_action")):
            missing.append({"id": entry.get("id", ""), "field": "gap_metadata", "reason": "missing blocking reason or required action"})
    return {"pass": not missing, "missing": missing}


def build_registry() -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    yang_report = optional_json(YANG_REPORT)
    yang_reference = optional_json(YANG_REFERENCE)
    yang_digitized = optional_json(YANG_DIGITIZED)
    narg = optional_json(NARGOLKAR_REPORT)
    wang = optional_json(WANG_REPORT)
    leg_report = optional_json(LEG_CONTACT_REPORT)
    stage3 = optional_json(CHRONO_STAGE3_REPORT)
    lock_two_way = optional_json(CHRONO_LOCK_TWO_WAY_REPORT)
    thies_buffer_curves = optional_json(THIES_BUFFER_CURVES)
    thies_buffer_report = optional_json(CHRONO_THIES_BUFFER_REPORT)

    add_yang_entries(entries, yang_report, yang_reference, yang_digitized)
    add_nargolkar_entries(entries, narg)
    add_wang_entries(entries, wang)
    add_thies_entries(entries, leg_report, stage3)
    add_thies_digitized_buffer_entries(entries, thies_buffer_curves, thies_buffer_report)
    add_published_error_band_entries(entries, leg_report)
    add_missing_curve_gaps(entries, thies_buffer_curves_available=bool((thies_buffer_curves.get("validation") or {}).get("pass")))

    categories: dict[str, int] = {}
    statuses: dict[str, int] = {}
    papers: dict[str, int] = {}
    for entry in entries:
        categories[entry["category"]] = categories.get(entry["category"], 0) + 1
        statuses[entry["reproduction_status"]] = statuses.get(entry["reproduction_status"], 0) + 1
        papers[entry["paper_id"]] = papers.get(entry["paper_id"], 0) + 1

    meta = metadata_complete(entries)
    pointwise = [entry for entry in entries if entry.get("comparison_level") == "pointwise_digitized_curve" and entry.get("reproduction_status") == "pointwise_compared"]
    wang_text = [entry for entry in entries if entry.get("paper_id") == "wang_2023" and entry.get("category") == "published_text_indicator"]
    thies_scale = [entry for entry in entries if entry.get("paper_id") == "thies_2022" and entry.get("comparison_level") in {"table_value_exactness", "surrogate_scale_check", "input_value"}]
    digitized_buffer = [entry for entry in entries if entry.get("category") == "digitized_buffer_curve" and entry.get("reproduction_status") == "implemented_in_chrono_table_law"]
    missing_curves = [entry for entry in entries if entry.get("category") == "missing_curve"]

    summary = {
        "total_entries": len(entries),
        "by_category": dict(sorted(categories.items())),
        "by_reproduction_status": dict(sorted(statuses.items())),
        "by_paper": dict(sorted(papers.items())),
        "pointwise_digitized_curve_count": len(pointwise),
        "wang_text_indicator_count": len(wang_text),
        "thies_table_or_scale_count": len(thies_scale),
        "thies_digitized_buffer_curve_count": len(digitized_buffer),
        "missing_curve_count": len(missing_curves),
        "metadata_complete_for_current_entries": bool(meta["pass"]),
        "metadata_gap_count": len(meta["missing"]),
        "available_comparisons_covered": bool(pointwise and wang_text and thies_scale and digitized_buffer),
        "status": "available_data_registered" if meta["pass"] and pointwise and wang_text and thies_scale and digitized_buffer else "incomplete",
    }

    return {
        "registry_id": "HAMS_Chrono_RocketRecovery_LiteratureComparisonRegistry",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": {
            "purpose": "Central registry of all current paper comparisons, digitized curves, text indicators, table values and missing source-data gaps.",
            "claim_boundary": "Pointwise reproduction is currently claimed only where source curves are digitized. Text/table indicators are scale checks. Missing curves are explicitly registered as gaps.",
        },
        "source_reports": {
            "yang_2026": {"path": rel(YANG_REPORT), "exists": YANG_REPORT.exists()},
            "yang_2026_digitized": {"path": rel(YANG_DIGITIZED), "exists": YANG_DIGITIZED.exists()},
            "nargolkar_2025": {"path": rel(NARGOLKAR_REPORT), "exists": NARGOLKAR_REPORT.exists()},
            "wang_2023": {"path": rel(WANG_REPORT), "exists": WANG_REPORT.exists()},
            "landing_leg_contact": {"path": rel(LEG_CONTACT_REPORT), "exists": LEG_CONTACT_REPORT.exists()},
            "chrono_stage3_tripod": {"path": rel(CHRONO_STAGE3_REPORT), "exists": CHRONO_STAGE3_REPORT.exists()},
            "chrono_stage3_lock_two_way": {"path": rel(CHRONO_LOCK_TWO_WAY_REPORT), "exists": CHRONO_LOCK_TWO_WAY_REPORT.exists()},
            "thies_buffer_curves": {"path": rel(THIES_BUFFER_CURVES), "exists": THIES_BUFFER_CURVES.exists()},
            "chrono_stage3_thies_buffer": {"path": rel(CHRONO_THIES_BUFFER_REPORT), "exists": CHRONO_THIES_BUFFER_REPORT.exists()},
        },
        "summary": summary,
        "metadata_check": meta,
        "entries": entries,
        "gaps": missing_curves + [entry for entry in entries if entry.get("category") == "missing_artifact"],
        "not_claimed": [
            "Yang 2026 ADAMS/Abaqus time histories are not claimed as reproduced until the landing model is identified on the simultaneous case and independently validated on 1-2-1 and 2-2.",
            "Yang 2026 Figure 17 is a random realization with unpublished white-noise normalization and seed; only filter equations and stochastic metrics can be reproduced uniquely.",
            "Wang 2023 AQWA/STAR-CCM+ curves are not pointwise reproduced until the curves are digitized or author data is available.",
            "Thies 2022 Adams force/stroke/nozzle time histories are not pointwise reproduced until Figures 9-10 or original Adams outputs are digitized.",
            "Yue/Li/Wang Actuators data are validation context only; current Chrono model has not been calibrated to those experiments.",
        ],
    }


def write_registry_markdown(registry: dict[str, Any]) -> None:
    summary = registry["summary"]
    lines = [
        "# Literature Comparison Registry",
        "",
        f"- Generated UTC: `{registry['generated_utc']}`",
        f"- Status: `{summary['status']}`",
        f"- Entries: `{summary['total_entries']}`",
        f"- Pointwise digitized curves: `{summary['pointwise_digitized_curve_count']}`",
        f"- Wang text indicators: `{summary['wang_text_indicator_count']}`",
        f"- Thies table/scale entries: `{summary['thies_table_or_scale_count']}`",
        f"- Thies digitized buffer curves: `{summary['thies_digitized_buffer_curve_count']}`",
        f"- Missing curve gaps: `{summary['missing_curve_count']}`",
        f"- Metadata complete: `{summary['metadata_complete_for_current_entries']}`",
        "",
        "## Claim Boundary",
        "",
        registry["scope"]["claim_boundary"],
        "",
        "## Current Comparison Entries",
        "",
        "| Paper | ID | Category | Level | Status | Metric | Unit | Paper | Computed | Error |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in registry["entries"]:
        if entry["category"] == "missing_curve":
            continue
        error = entry.get("error_metrics") or {}
        if "relative_error" in error and error["relative_error"] is not None:
            error_text = f"rel={float(error['relative_error']):.4g}"
        elif "normalized_rmse_vs_paper_peak" in error and error["normalized_rmse_vs_paper_peak"] is not None:
            error_text = f"nRMSE={float(error['normalized_rmse_vs_paper_peak']):.4g}"
        else:
            error_text = ""
        lines.append(
            "| {paper} | `{id}` | {category} | {level} | {status} | {metric} | {unit} | {paper_value} | {computed_value} | {error} |".format(
                paper=entry.get("paper_id", ""),
                id=entry.get("id", ""),
                category=entry.get("category", ""),
                level=entry.get("comparison_level", ""),
                status=entry.get("reproduction_status", ""),
                metric=str(entry.get("metric", "")).replace("|", "\\|"),
                unit=str(entry.get("unit", "")).replace("|", "\\|"),
                paper_value=str(entry.get("paper_value", "")).replace("|", "\\|"),
                computed_value=str(entry.get("computed_value", "")).replace("|", "\\|"),
                error=error_text,
            )
        )

    lines.extend(["", "## Missing Curves", "", "| Paper | ID | Figure | Metric | Required Action |", "| --- | --- | --- | --- | --- |"])
    for gap in registry["gaps"]:
        paper_source = gap.get("paper_data_source") or {}
        lines.append(
            "| {paper} | `{id}` | {figure} | {metric} | {action} |".format(
                paper=gap.get("paper_id", ""),
                id=gap.get("id", ""),
                figure=str(paper_source.get("figure", "")).replace("|", "\\|"),
                metric=str(gap.get("metric", "")).replace("|", "\\|"),
                action=str(gap.get("required_action", "")).replace("|", "\\|"),
            )
        )
    lines.extend(["", "## Not Claimed", ""])
    for item in registry["not_claimed"]:
        lines.append(f"- {item}")

    REGISTRY_MD.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_registry_js(registry: dict[str, Any]) -> None:
    REGISTRY_JS.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_JS.write_text(
        "window.LITERATURE_COMPARISON_REGISTRY = "
        + json.dumps(registry, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the paper comparison metadata registry for the HAMS/Cummins + Chrono workflow.")
    parser.add_argument("command", choices=["registry", "report"], nargs="?", default="registry")
    args = parser.parse_args()
    registry = build_registry()
    write_json(REGISTRY_JSON, registry)
    write_registry_markdown(registry)
    write_registry_js(registry)
    print(f"Registry status: {registry['summary']['status']}")
    print(f"Entries: {registry['summary']['total_entries']}")
    print(f"Pointwise digitized curves: {registry['summary']['pointwise_digitized_curve_count']}")
    print(f"Missing curve gaps: {registry['summary']['missing_curve_count']}")
    print(f"Registry JSON: {REGISTRY_JSON}")
    print(f"Registry MD: {REGISTRY_MD}")
    print(f"Registry JS: {REGISTRY_JS}")
    if args.command == "report":
        print("Open: http://127.0.0.1:8765/literature-comparison-registry.html")


if __name__ == "__main__":
    main()
