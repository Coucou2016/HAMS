from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from .leg_mechanism_data_contract import ADAMS_GATE, CONTRACT_JSON, TEMPLATE_JSON
    from .leg_mechanism_data_validator import flatten_values, is_missing, source_is_ready
except ImportError:
    from common import ROOT, ROCKET_CASES_DIR, VISUALIZATION_DIR, read_json, write_json
    from leg_mechanism_data_contract import ADAMS_GATE, CONTRACT_JSON, TEMPLATE_JSON
    from leg_mechanism_data_validator import flatten_values, is_missing, source_is_ready


CASE_ROOT = ROCKET_CASES_DIR / "Chrono_LeggedRecovery"
VALIDATION_JSON = CASE_ROOT / "leg-mechanism-data-validation.json"
BUILDER_JSON = CASE_ROOT / "real-leg-mechanism-builder-gate.json"
RUNTIME_JSON = CASE_ROOT / "chrono-real-leg-mechanism-report-data.json"

GAP_JSON = CASE_ROOT / "leg-mechanism-gap-tracker.json"
GAP_MD = ROOT / "docs" / "leg-mechanism-gap-tracker.md"
GAP_JS = VISUALIZATION_DIR / "leg-mechanism-gap-tracker-data.js"


SOURCE_MATRIX: list[dict[str, Any]] = [
    {
        "source_id": "Thies_2022",
        "local_files": [
            "海上平台火箭回收文献/P3_Thies_2022.md",
            "海上平台火箭回收文献/P3_Thies_2022.pdf",
        ],
        "usable_data": [
            "火箭高度、直径、着陆质量、质心和惯量",
            "四腿 tripod 总体构型",
            "B/T/K 高度、PB/PT/PK 长度、33 deg 主腿角、51 deg 斜撑角",
            "名义触地速度、触地动能、无摩擦名义工况",
            "缓冲器线性刚度/阻尼、表格结果中的行程/力/喷管间隙",
            "Figure 4/5 可数字化缓冲器力-行程/力-速度曲线",
        ],
        "cannot_fill_strict_fields": [
            "四条腿在火箭体坐标系内的完整 B/T/K/P 三维 marker 坐标",
            "真实 CAD/Adams 坐标系原点、轴向和 HAMS 甲板坐标转换",
            "每个铰链的 joint type、joint axis、限位和约束图",
            "主支柱、斜撑、足垫、缓冲器壳体/活塞/锁紧件的质量、质心和惯量",
            "伸缩缓冲器内部拓扑、真实 stroke limit、回弹/伸出行为和锁紧硬件",
        ],
        "strict_gate_use": "primary_scale_validation_only",
        "notes": "适合作为支腿量级和缓冲曲线基准；不足以直接生成 Adams 等价 Chrono 机构。",
    },
    {
        "source_id": "Yue_2022",
        "local_files": [
            "海上平台火箭回收文献/P4_Yue_2022.md",
            "海上平台火箭回收文献/P4_Yue_2022.pdf",
        ],
        "usable_data": [
            "准三维 2-2 / 1-2-1 对称着陆建模方式",
            "主支柱力、辅助支柱力、缓冲器行程、加速度的仿真/试验对比指标",
            "非线性接触和液体弹簧缓冲器验证思路",
        ],
        "cannot_fill_strict_fields": [
            "该文是另一缩比/准三维模型，不是 Thies/RETALT 真实 CAD 数据",
            "不能直接填入当前 Thies-based B/T/K/P marker 和质量惯量字段",
            "不能替代浮动甲板 HAMS/Cummins 数据",
        ],
        "strict_gate_use": "future_validation_targets",
        "notes": "适合后续增加支腿试验级对比，但不能和 Thies 参数混用后声称真实机构。",
    },
    {
        "source_id": "Li_2025",
        "local_files": [
            "海上平台火箭回收文献/P5_Li_2025_Aerospace.md",
            "海上平台火箭回收文献/P5_Li_2025_Aerospace.pdf",
        ],
        "usable_data": [
            "四腿机构、主支柱、两根辅助支柱、足垫和液气弹簧的建模拓扑描述",
            "另一设计的质量/惯量表",
            "接触刚度、阻尼、接触半径、接触指数、静/动摩擦系数",
            "柔性-刚体耦合和发动机关机后残余推力建模思路",
        ],
        "cannot_fill_strict_fields": [
            "这是另一火箭/支腿设计，不能直接填入 Thies/RETALT 机构几何",
            "不能与 Thies 几何混合后作为同一真实机构的质量惯量",
            "不包含浮式平台水动力或海上甲板运动数据",
        ],
        "strict_gate_use": "alternate_design_or_contact_reference",
        "notes": "可作为接触参数和未来柔性支腿路线参考；若采用，需要建立独立 Li-based config。",
    },
    {
        "source_id": "Wang_2023",
        "local_files": [
            "海上平台火箭回收文献/海上火箭回收过程中船舶耦合运动响应分析_王智.md",
            "海上平台火箭回收文献/P2_WangZhi_2023_ShipSciTech.pdf",
        ],
        "usable_data": [
            "JONSWAP 谱 Hs=1.75 m、Tp=4.5 s、gamma=3、浪向 135 deg",
            "31 s 喷流载荷时程构造和最终约 20400 kN 的垂向载荷量级",
            "165 m x 40 m x 5 m 驳船、四点悬链线系泊、偏心落点响应量级",
            "静水/波浪中 heave/roll/pitch 响应文字指标",
        ],
        "cannot_fill_strict_fields": [
            "没有火箭四腿结构模型",
            "没有足垫接触、缓冲器、摩擦、锁紧或火箭刚体动力学",
            "没有 HAMS/Chrono 真实支腿机构所需 CAD/Adams 数据",
        ],
        "strict_gate_use": "platform_wave_plume_validation",
        "notes": "用于 HAMS/Cummins 平台和喷流外载验证，不用于填真实支腿机构 gate。",
    },
    {
        "source_id": "Nargolkar_2025",
        "local_files": [
            "海上平台火箭回收文献/065002_1_2.0002061.md",
            "海上平台火箭回收文献/065002_1_2.0002061.pdf",
        ],
        "usable_data": [
            "HAMS 势流到 Cummins 时域记忆力再到火箭等效梁/弹簧耦合的主链路",
            "箱形驳船和 MARMAC 302 几何/质量参数",
            "中心/偏心着陆和不同速度的耦合响应对比",
        ],
        "cannot_fill_strict_fields": [
            "该文使用等效弹簧耦合，不是四腿接触模型",
            "没有铰链、足垫、缓冲器曲线、摩擦或锁紧硬件",
            "不能作为 Adams 等价支腿机构数据来源",
        ],
        "strict_gate_use": "hydro_structural_coupling_benchmark",
        "notes": "主复现基准仍有效，但其接触接口必须由 Chrono 支腿模型替换。",
    },
]


CSV_MAPPING = {
    "coordinate_system": {
        "csv_file": "coordinate_system.csv",
        "needed_source": "CAD/Adams frame export or author frame metadata",
        "priority": "P0",
    },
    "azimuths": {
        "csv_file": "leg_azimuths.csv",
        "needed_source": "CAD/Adams leg layout export or published four-leg azimuth table",
        "priority": "P0",
    },
    "marker_coordinates": {
        "csv_file": "marker_coordinates.csv",
        "needed_source": "CAD/Adams marker export for B/T/K/P in a declared rocket body frame",
        "priority": "P0",
    },
    "constraint_topology": {
        "csv_file": "constraint_topology.csv",
        "needed_source": "Adams constraint graph, CAD mate definitions, or author topology table",
        "priority": "P0",
    },
    "body_properties": {
        "csv_file": "body_properties.csv",
        "needed_source": "CAD mass-property export or validated component mass budget",
        "priority": "P0",
    },
    "buffer_lock": {
        "csv_file": "buffer_lock.csv",
        "needed_source": "absorber hardware specification, force-law table, stroke/rebound data, and lock hardware data",
        "priority": "P1",
    },
    "unknown": {
        "csv_file": "manual_review",
        "needed_source": "manual review",
        "priority": "P2",
    },
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT).as_posix())
    except ValueError:
        return str(path.as_posix())


def read_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return read_json(path)


def classify_path(path: str) -> str:
    if path.startswith("coordinate_system."):
        return "coordinate_system"
    if path.endswith(".azimuth_deg") or ".azimuth_deg" in path:
        return "azimuths"
    if ".adams_equivalent_geometry." in path:
        return "marker_coordinates"
    if ".constraint_topology." in path:
        return "constraint_topology"
    if ".body_properties." in path:
        return "body_properties"
    if path.startswith("buffer_law.") or path.startswith("lock_hardware."):
        return "buffer_lock"
    return "unknown"


def current_papers_can_fill_strict_field(path: str) -> bool:
    # The currently supplied papers provide useful scale/validation values but do not provide
    # source-ready B/T/K/P 3D markers, CAD mass properties, joint axes, absorber topology, or lock hardware.
    # Keep this explicit so the strict gate cannot be satisfied by reusing proxy assumptions.
    return False


def make_gap_row(row: dict[str, Any]) -> dict[str, Any]:
    field_class = classify_path(row["path"])
    mapping = CSV_MAPPING[field_class]
    return {
        "path": row["path"],
        "unit": row.get("unit"),
        "value": row.get("value"),
        "source_category": row.get("source_category"),
        "source_detail": row.get("source_detail"),
        "field_class": field_class,
        "csv_file": mapping["csv_file"],
        "needed_source": mapping["needed_source"],
        "priority": mapping["priority"],
        "current_papers_can_fill_without_new_assumption": current_papers_can_fill_strict_field(row["path"]),
    }


def build_report() -> dict[str, Any]:
    template = read_optional_json(TEMPLATE_JSON)
    contract = read_optional_json(CONTRACT_JSON)
    validation = read_optional_json(VALIDATION_JSON)
    builder = read_optional_json(BUILDER_JSON)
    runtime = read_optional_json(RUNTIME_JSON)

    rows = flatten_values(template) if template else []
    adams_rows = [row for row in rows if ADAMS_GATE in row.get("required_for", [])]
    blocking_rows = [
        row
        for row in adams_rows
        if is_missing(row.get("value")) or not source_is_ready(row, allow_synthetic=False)
    ]
    gap_rows = [make_gap_row(row) for row in blocking_rows]

    by_class = Counter(row["field_class"] for row in gap_rows)
    by_csv = Counter(row["csv_file"] for row in gap_rows)
    by_source = Counter(row.get("source_category") for row in blocking_rows)
    ready_rows = [row for row in adams_rows if source_is_ready(row, allow_synthetic=False) and not is_missing(row.get("value"))]
    ready_by_source = Counter(row.get("source_category") for row in ready_rows)

    action_plan = [
        {
            "order": 1,
            "id": "export_frames_and_markers",
            "target_csv": ["coordinate_system.csv", "leg_azimuths.csv", "marker_coordinates.csv"],
            "acceptance": "validator coordinate_system and geometry_closure checks pass in strict_real_data mode",
            "why": "没有统一坐标系和 B/T/K/P marker，Chrono 中杆件闭合方向、支腿高度和足垫位置都无法证明。",
        },
        {
            "order": 2,
            "id": "export_constraint_graph",
            "target_csv": ["constraint_topology.csv"],
            "acceptance": "validator constraint_topology check passes and every slider axis is unit length",
            "why": "真实铰链类型、轴向、限位和伸缩副决定机构自由度，不能从 PB/PT/PK 长度反推。",
        },
        {
            "order": 3,
            "id": "export_mass_properties",
            "target_csv": ["body_properties.csv"],
            "acceptance": "validator body_mass_inertia check passes for main strut, auxiliary struts and footpad of every leg",
            "why": "Chrono 刚体杆件会参与冲击和反弹，质量/惯量不能继续使用占位值。",
        },
        {
            "order": 4,
            "id": "fill_absorber_and_lock_hardware",
            "target_csv": ["buffer_lock.csv"],
            "acceptance": "validator buffer_law and lock_hardware checks pass or lock hardware is explicitly moved to a separate platform-side model",
            "why": "Thies 给出了可数字化曲线和结果量级，但没有完整 stroke limit、伸出/回弹规则和锁紧硬件。",
        },
        {
            "order": 5,
            "id": "rerun_strict_gate_and_runtime",
            "target_csv": ["all"],
            "acceptance": "validator ready=true, builder writes Input/chrono_real_leg_mechanism_config.json, runtime gate runs strict config",
            "why": "只有这个链路通过后，才允许把模型标为真实机构分支，而不是 Stage 3A 代理。",
        },
    ]

    strict_blocking_count = (
        validation.get("summary", {}).get("blocking_field_count")
        if validation
        else len(blocking_rows)
    )
    strict_ready = bool(validation.get("ready")) if validation else False
    builder_status = builder.get("overall_status") if builder else "missing_report"
    runtime_status = runtime.get("overall_status") if runtime else "missing_report"

    return {
        "report_id": "ChronoRealLegMechanismGapTracker",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overall_status": "blocked_pending_real_mechanism_data" if not strict_ready else "ready_for_real_mechanism_build",
        "conclusion": (
            "当前论文和 Markdown 可支撑平台水动力、喷流载荷、缓冲器曲线和支腿量级验证，"
            "但不能填满 Adams 等价 Chrono 支腿所需的真实 CAD/Adams 机构字段。"
        ),
        "inputs": {
            "template_json": {"path": rel(TEMPLATE_JSON), "exists": TEMPLATE_JSON.exists()},
            "contract_json": {"path": rel(CONTRACT_JSON), "exists": CONTRACT_JSON.exists()},
            "validation_json": {"path": rel(VALIDATION_JSON), "exists": VALIDATION_JSON.exists()},
            "builder_json": {"path": rel(BUILDER_JSON), "exists": BUILDER_JSON.exists()},
            "runtime_json": {"path": rel(RUNTIME_JSON), "exists": RUNTIME_JSON.exists()},
        },
        "current_gate": {
            "strict_validation_ready": strict_ready,
            "strict_validation_blocking_field_count": strict_blocking_count,
            "builder_status": builder_status,
            "runtime_status": runtime_status,
            "production_real_config_exists": (CASE_ROOT / "Input" / "chrono_real_leg_mechanism_config.json").exists(),
        },
        "summary": {
            "adams_required_field_count": len(adams_rows),
            "strict_ready_field_count": len(ready_rows),
            "strict_blocking_field_count": len(blocking_rows),
            "strict_blocking_field_count_from_validator": strict_blocking_count,
            "current_papers_can_fill_blocking_field_count": sum(
                1 for row in gap_rows if row["current_papers_can_fill_without_new_assumption"]
            ),
            "ready_source_category_counts": dict(sorted(ready_by_source.items())),
            "blocking_source_category_counts": dict(sorted(by_source.items())),
            "blocking_field_class_counts": dict(sorted(by_class.items())),
            "blocking_csv_file_counts": dict(sorted(by_csv.items())),
        },
        "source_matrix": SOURCE_MATRIX,
        "blocking_fields": gap_rows,
        "csv_mapping": CSV_MAPPING,
        "action_plan": action_plan,
        "commands": [
            r".\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_importer.py import --source-dir .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_import_schema",
            r".\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_validator.py report --input .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_data_imported.json",
            r".\.tools\chrono-env\python.exe .\analysis\rocket_recovery\real_leg_mechanism_builder.py report --input .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_data_imported.json",
            r".\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_real_leg_mechanism_recovery.py report",
        ],
        "contract_status": contract.get("overall_status") if contract else "missing_report",
    }


def escape_table(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|")


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Chrono Real Leg Mechanism Gap Tracker",
        "",
        f"- Overall status: `{report['overall_status']}`",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Strict validation ready: `{report['current_gate']['strict_validation_ready']}`",
        f"- Blocking fields: `{summary['strict_blocking_field_count_from_validator']}`",
        f"- Current papers can fill blocking fields without new assumption: `{summary['current_papers_can_fill_blocking_field_count']}`",
        "",
        "## Conclusion",
        "",
        report["conclusion"],
        "",
        "No current paper/PDF/Markdown in the workspace provides the full 3D hinge-marker, constraint-topology, mass-property, absorber-topology, and lock-hardware data required to pass the strict real-leg gate.",
        "",
        "## Source Matrix",
        "",
        "| Source | Useful Data | Cannot Fill | Gate Use |",
        "| --- | --- | --- | --- |",
    ]
    for row in report["source_matrix"]:
        useful = "<br>".join(escape_table(item) for item in row["usable_data"])
        missing = "<br>".join(escape_table(item) for item in row["cannot_fill_strict_fields"])
        lines.append(f"| `{row['source_id']}` | {useful} | {missing} | `{row['strict_gate_use']}` |")

    lines.extend(
        [
            "",
            "## Blocking Field Classes",
            "",
            "| Class | Count | CSV | Needed Source |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for field_class, mapping in report["csv_mapping"].items():
        count = summary["blocking_field_class_counts"].get(field_class, 0)
        lines.append(
            f"| `{field_class}` | {count} | `{mapping['csv_file']}` | {escape_table(mapping['needed_source'])} |"
        )

    lines.extend(["", "## Action Plan", ""])
    for row in report["action_plan"]:
        target = ", ".join(f"`{item}`" for item in row["target_csv"])
        lines.append(f"{row['order']}. `{row['id']}` -> {target}: {row['acceptance']}")

    lines.extend(
        [
            "",
            "## Top Blocking Fields",
            "",
            "| Path | Source | CSV | Needed Source |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in report["blocking_fields"][:120]:
        lines.append(
            f"| `{row['path']}` | `{escape_table(row['source_category'])}` | `{row['csv_file']}` | {escape_table(row['needed_source'])} |"
        )
    if len(report["blocking_fields"]) > 120:
        lines.append(f"| ... | ... | ... | {len(report['blocking_fields']) - 120} more rows in JSON |")

    lines.extend(["", "## Commands", ""])
    lines.append("```powershell")
    lines.extend(report["commands"])
    lines.append("```")
    GAP_MD.parent.mkdir(parents=True, exist_ok=True)
    GAP_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_js(report: dict[str, Any]) -> None:
    GAP_JS.parent.mkdir(parents=True, exist_ok=True)
    GAP_JS.write_text(
        "window.LEG_MECHANISM_GAP_TRACKER = "
        + json.dumps(report, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Track real-data gaps blocking an Adams-equivalent Chrono landing-leg mechanism.")
    parser.add_argument("command", choices=["report", "json"], nargs="?", default="report")
    args = parser.parse_args()

    report = build_report()
    write_json(GAP_JSON, report)
    write_markdown(report)
    write_js(report)

    print(f"Overall: {report['overall_status']}")
    print(f"Strict ready: {report['current_gate']['strict_validation_ready']}")
    print(f"Blocking fields: {report['summary']['strict_blocking_field_count_from_validator']}")
    print(f"Current papers can fill blocking fields: {report['summary']['current_papers_can_fill_blocking_field_count']}")
    print(f"Gap JSON: {GAP_JSON}")
    print(f"Gap MD: {GAP_MD}")
    print(f"Gap JS: {GAP_JS}")
    if args.command == "report":
        print("Open: http://127.0.0.1:8765/leg-mechanism-gap-tracker.html")


if __name__ == "__main__":
    main()
