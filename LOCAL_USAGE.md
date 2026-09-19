# HAMS local source-build usage

本目录已经配置成一个可以在本机从源码重新编译、运行和可视化 HAMS 的本地工作区。

当前默认不使用 `Bin\HAMS_x64.exe`。运行脚本默认调用本机重新编译得到的：

```text
E:\Projects\20260728-HAMS\SourceCode\hams.exe
```

## 本地隔离原则

- 编译工具链放在 `E:\Projects\20260728-HAMS\.tools\msys64`。
- 不把 HAMS 或 gfortran 加入系统 `PATH`。
- 不安装系统服务。
- 不修改全局 Git 配置。
- 运行时只在当前 PowerShell 进程临时加入本地 MinGW DLL 路径。

## 重新编译

```powershell
cd E:\Projects\20260728-HAMS
powershell -ExecutionPolicy Bypass -File .\local-tools\Build-HAMS.ps1
```

快速检查，不清理对象文件：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Build-HAMS.ps1 -NoClean
```

编译产物：

```text
SourceCode\hams.exe
SourceCode\libhams.dll
```

## 运行案例

运行 `Cylinder`：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\CertTest\Cylinder
```

运行 `DeepCwind`：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\CertTest\DeepCwind
```

输出会写回每个案例自己的 `Output` 目录。

## 三维形体可视化

生成/刷新可视化数据：

```powershell
python .\visualization\generate_mesh_viewer.py
python .\visualization\render_mesh_snapshots.py
```

启动本地查看器：

```powershell
cd E:\Projects\20260728-HAMS\visualization
python -m http.server 8765 --bind 127.0.0.1
```

打开：

```text
http://127.0.0.1:8765/viewer.html
```

静态图片在：

```text
E:\Projects\20260728-HAMS\visualization\snapshots
```

`viewer.html` 可切换四个自带案例：`Cylinder`、`DeepCwind`、`HywindSpar`、`Moonpool`。

## 案例结果 HTML

运行案例后，生成/刷新 `Cylinder` 和 `DeepCwind` 的结果曲线数据：

```powershell
python .\visualization\generate_case_reports.py
```

打开：

```text
http://127.0.0.1:8765/results.html
```

`results.html` 会显示每个案例的三维网格快照，并可按浪向切换查看 Added Mass、Radiation Damping、Wave Excitation、Motion RAO 四类曲线。

## 火箭回收：矩形驳船着陆腿落甲板

生成矩形回收驳船案例：

```powershell
python .\analysis\rocket_recovery\generate_barge_case.py --case Barge_120x50
```

运行 HAMS：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\RocketRecoveryCases\Barge_120x50
```

生成甲板着陆点/四个支腿点 RAO、海况响应和网页数据：

```powershell
python .\analysis\rocket_recovery\deck_point_rao.py --case Barge_120x50
python .\analysis\rocket_recovery\sea_state_response.py --case Barge_120x50
python .\analysis\rocket_recovery\recovery_window_report.py --case Barge_120x50
```

打开：

```text
http://127.0.0.1:8765/rocket-recovery.html
```

第一版只输出甲板点运动、支腿点运动包络和海况统计；不做喷流、真实 GNC、支腿强度或着陆成败判定。

## 论文复现：Nargolkar & Vijayan 2025 驳船触地耦合响应

生成论文中的 Box Barge、MARMAC 302 以及中心/偏心着陆四个 HAMS 工况：

```powershell
python .\analysis\rocket_recovery\nargolkar_2025.py generate
```

逐个运行 HAMS：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\RocketRecoveryCases\Paper_Nargolkar_2025\BoxBarge_Center
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\RocketRecoveryCases\Paper_Nargolkar_2025\BoxBarge_Offset5m
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\RocketRecoveryCases\Paper_Nargolkar_2025\MARMAC302_Center
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\RocketRecoveryCases\Paper_Nargolkar_2025\MARMAC302_Offset30m
```

生成外部 3DOF 驳船 + 3DOF 等效火箭触地时域响应和网页数据：

```powershell
python .\analysis\rocket_recovery\nargolkar_2025.py simulate
python .\analysis\rocket_recovery\nargolkar_2025.py report
```

打开：

```text
http://127.0.0.1:8765/nargolkar-2025.html
```

这个复现层使用论文表 1/2/3 的公开参数，并把 HAMS 输出的附加质量和辐射阻尼接到外部时域模型中。论文没有公开 MATLAB 源码、触地冲击律、完整网格和曲线数字化数据，所以这里输出的是透明的参数匹配复现和趋势对照，不把它伪装成逐点完全一致的原作者曲线。

当前报告页包含论文表格数据审计和基于计算时程 `q(t)` 的 3D 着陆动画；结构等效质量采用论文表 2 打印的 `M_eq`，不按目标频率反算替换。外部时域模块使用 HAMS `WaveDamping_ij.rao` 构造 Cummins/Ogilvie 记忆项，未公开的结构阻尼、接触阻尼和系泊刚度严格设为 `0` 并在报告中列为未解析项。

## 论文推进：王智等 2023 喷流-波浪-平台响应

生成王智等 2023 论文中的 165 m x 40 m 回收船 HAMS 工况：

```powershell
python .\analysis\rocket_recovery\wang_2023.py generate
```

运行本机源码编译得到的 HAMS：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\RocketRecoveryCases\Paper_WangZhi_2023
```

生成静水/波浪、中心/偏心喷流载荷下的外部 Cummins 时域响应和网页数据：

```powershell
python .\analysis\rocket_recovery\wang_2023.py simulate
python .\analysis\rocket_recovery\wang_2023.py report
```

打开：

```text
http://127.0.0.1:8765/wang-2023.html
```

这个复现层使用论文公开的船体主尺度、质量、重心、惯性半径、4 根 820 m 系泊缆布置、JONSWAP `Hs=1.75 m / Tp=4.5 s / gamma=3 / heading=135 deg` 和 480-511 s 喷流载荷分段表达式。论文没有公开 STAR-CCM+ 喷流时历数据、AQWA 工程、二阶波浪力数据和悬链线缆参数，所以当前报告是 HAMS/Cummins 开源替代模型与论文文本指标的数量级对照，不把缺失数据伪造成原作者结果。

## 第三阶段：着陆腿接触入口包络

在王智 2023 的平台时域响应基础上，接入 Thies 2022 的 RETALT1 支腿几何和触地条件，生成触地入口量包络：

```powershell
python .\analysis\rocket_recovery\landing_leg_contact.py report
```

打开：

```text
http://127.0.0.1:8765/landing-leg-contact.html
```

输出文件：

```text
RocketRecoveryCases\Stage3_LandingLegContact\landing-leg-contact-envelope.json
visualization\landing-leg-contact-data.js
docs\landing-leg-contact-stage3.md
```

这一层只计算甲板倾角、四腿足迹高度差、首腿提前接触时间、足迹垂向速度和相对闭合速度，并与 Thies 表 6 的 `10 deg` 倾角包络和 `1..15 m/s` 触地速度包络对照。由于 Thies 未公开完整 Adams 模型、四腿精确方位、非线性力-行程和力-速度函数，这一页不输出支腿结构载荷复现曲线。

## 综合模型：水动力 + 波浪/喷流 + 等效梁 + 四腿接触

在 Wang 2023 HAMS/Cummins 平台响应基础上，接入 Nargolkar 2025 等效梁模态和 Thies 2022 四腿单向压缩接触模型，生成完整触地后的时域响应：

```powershell
python .\analysis\rocket_recovery\integrated_recovery_model.py report
```

打开：

```text
http://127.0.0.1:8765/integrated-recovery.html
```

输出文件：

```text
RocketRecoveryCases\Integrated_LeggedRecovery\Output\RocketRecovery\integrated-recovery-full.json
RocketRecoveryCases\Integrated_LeggedRecovery\integrated-recovery-report-data.json
visualization\integrated-recovery-data.js
docs\integrated-recovery-model.md
```

这一层已经串联 HAMS 势流水动力、Cummins/Ogilvie 记忆项、JONSWAP 不规则波、王智论文喷流载荷、火箭刚体、Nargolkar 等效梁和四个支腿的独立接触状态。由于公开文献没有给出 STAR-CCM+ 喷流机器数据、AQWA 工程、MSC Adams 模型、真实非线性缓冲器和着陆锁紧/GNC 参数，当前报告只声明开源降阶模型和公开指标的数量级/趋势对照，不声明商业软件原模型逐点复现。

## Chrono 路线：用开源多体动力学替代 Adams

HAMS/Cummins 继续只负责平台波浪水动力；Project Chrono/PyChrono 负责火箭刚体、四腿、足垫接触、缓冲器和摩擦。

检查当前 Python 是否具备 PyChrono，并生成 Chrono 输入审计：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_one_way_recovery.py check
```

如果未安装 PyChrono，使用项目本地 prefix 创建隔离环境：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Create-ChronoEnv.ps1
```

安装完成后运行单向耦合 Chrono 计算：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_one_way_recovery.py report
```

写出双向耦合接口契约：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_two_way_recovery.py contract
```

运行双向松耦合四工况计算：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_two_way_recovery.py report
```

运行 Stage 3A tripod 支腿代理四工况计算：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_stage3_recovery.py report
```

运行 Stage 3A tripod 双向松耦合四工况计算：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_stage3_two_way_recovery.py report
```

运行 Stage 3 锁紧代理四工况计算：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_stage3_lock_recovery.py report
```

运行 Stage 3 锁紧代理双向松耦合四工况计算：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_stage3_lock_two_way_recovery.py report
```

该 Stage 3 锁紧分支把 Chrono 足垫接触力和锁紧约束反力完整映射为
`[Fx,Fy,Fz,Mx,My,Mz]`，使用本机 HAMS 生成的 6x6 附加质量与辐射阻尼矩阵计算
腿反力增量。王智 2023 公开基线仍只有 `heave/roll/pitch`；`surge/sway/yaw`
没有公开的波浪、系泊或 DP 输入，因此其环境基线保持显式零值，只把 Chrono 反力增量
作为无系泊诊断输出，不能据此声称已复现完整 6DOF 王智/AQWA 模型。

每个工况在完成平台修正后会额外执行一次 Chrono 反馈甲板重放，使网页动画与
`with_leg_feedback` 六自由度甲板时历完全一致，并报告下一轮反力对应的闭合残差。
默认 `--iterations 1 --relaxation 1.0` 表示一次不松弛的顺序松耦合；只有做显式
多轮迭代研究时才应使用例如 `--iterations 6 --relaxation 0.2`。报告中的闭合门槛
是数值求解设置，不是文献或火箭硬件判据。

从 Thies 2022 PDF 图 4/5 数字化缓冲器力-行程和力-速度曲线：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\thies_buffer_digitization.py report
```

运行 Stage 3A Thies 数字化缓冲器分支：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_stage3_thies_buffer_recovery.py report
```

运行 Stage 3B 刚性斜撑诊断分支：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_stage3b_rigid_recovery.py report --case calm_center
```

运行 Stage 3C 有限质量刚体杆件诊断分支：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_stage3c_rigid_body_link_recovery.py report --case calm_center
```

生成 Adams 等价 Chrono 支腿机构数据合同和可填写模板：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_contract.py report
```

生成 CAD/Adams/作者数据 CSV 导入 schema；该命令不修改当前模板：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_importer.py report
```

运行合成 CSV 导入自测；该命令只验证工具链，不代表真实支腿数据已经具备：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_import_selftest.py report
```

运行真实配置到 PyChrono 后端的 synthetic smoke assembly 自测；该命令不代表落地轨迹仿真：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_real_leg_backend_selftest.py report
```

用已填写的 CSV 导入生成单独的 imported 模板：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_importer.py import --source-dir .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_import_schema
```

校验可填写模板是否已经满足 Adams 等价 Chrono 支腿机构替换门槛：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_validator.py report
```

生成真实支腿机构数据缺口追踪报告，列出每个 blocking field 对应的 CSV 和必须获取的数据来源：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_gap_tracker.py report
```

生成真实支腿机构数据补齐包；该命令只写 `.todo.csv`，不修改正式导入 CSV：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_request_pack.py report
```

检查真实支腿机构数据补齐包是否覆盖全部 blocking field 且不会误导入：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_request_lint.py report
```

在校验通过后生成真实 Chrono 支腿机构配置；当前数据不足时只输出 blocked gate：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\real_leg_mechanism_builder.py report
```

运行真实 Chrono 支腿机构 runtime gate；当前缺少正式真实配置时只输出 blocked gate：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_real_leg_mechanism_recovery.py report
```

生成文献对比与曲线元数据注册表：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\literature_comparison_registry.py report
```

生成模型真实性审计，专门区分严格复现、图线数字化、代理模型和缺失真实数据：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\model_realism_audit.py report
```

生成当前完整目标的最终验收审计：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\final_acceptance_audit.py report
```

一键编排完整链路：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-RocketRecoveryPipeline.ps1
```

只检查完整链路命令顺序，不重跑计算：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-RocketRecoveryPipeline.ps1 -DryRun
```

打开：

```text
http://127.0.0.1:8765/chrono-final-acceptance.html
http://127.0.0.1:8765/model-realism-audit.html
http://127.0.0.1:8765/literature-comparison-registry.html
http://127.0.0.1:8765/chrono-recovery.html
http://127.0.0.1:8765/chrono-two-way.html
http://127.0.0.1:8765/chrono-stage3-tripod.html
http://127.0.0.1:8765/chrono-stage3-two-way.html
http://127.0.0.1:8765/chrono-stage3-lock.html
http://127.0.0.1:8765/chrono-stage3-lock-two-way.html
http://127.0.0.1:8765/thies-buffer-curves.html
http://127.0.0.1:8765/chrono-stage3-thies-buffer.html
http://127.0.0.1:8765/chrono-stage3c-rigid-body-link.html
http://127.0.0.1:8765/leg-mechanism-contract.html
http://127.0.0.1:8765/leg-mechanism-import.html
http://127.0.0.1:8765/leg-mechanism-import-selftest.html
http://127.0.0.1:8765/leg-mechanism-validation.html
http://127.0.0.1:8765/leg-mechanism-gap-tracker.html
http://127.0.0.1:8765/leg-mechanism-data-request-pack.html
http://127.0.0.1:8765/leg-mechanism-data-request-lint.html
http://127.0.0.1:8765/real-leg-mechanism-builder.html
http://127.0.0.1:8765/chrono-real-leg-backend-selftest.html
http://127.0.0.1:8765/chrono-real-leg-mechanism.html
```

输出文件：

```text
RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_model_config.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-one-way-report-data.json
RocketRecoveryCases\Chrono_LeggedRecovery\Output\RocketRecovery\chrono-one-way-response.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-two-way-contract.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-two-way-report-data.json
RocketRecoveryCases\Chrono_LeggedRecovery\Output\RocketRecovery\chrono-two-way-response.json
RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_model_config_stage3_tripod.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-stage3-tripod-report-data.json
RocketRecoveryCases\Chrono_LeggedRecovery\Output\RocketRecovery\chrono-stage3-tripod-response.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-stage3-two-way-report-data.json
RocketRecoveryCases\Chrono_LeggedRecovery\Output\RocketRecovery\chrono-stage3-two-way-response.json
RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_model_config_stage3_lock.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-stage3-lock-report-data.json
RocketRecoveryCases\Chrono_LeggedRecovery\Output\RocketRecovery\chrono-stage3-lock-response.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-stage3-lock-two-way-report-data.json
RocketRecoveryCases\Chrono_LeggedRecovery\Output\RocketRecovery\chrono-stage3-lock-two-way-response.json
RocketRecoveryCases\Chrono_LeggedRecovery\validation\thies_absorber_curves\thies-buffer-curves.json
RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_model_config_stage3_thies_buffer.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-stage3-thies-buffer-report-data.json
RocketRecoveryCases\Chrono_LeggedRecovery\Output\RocketRecovery\chrono-stage3-thies-buffer-response.json
RocketRecoveryCases\Chrono_LeggedRecovery\literature-comparison-registry.json
RocketRecoveryCases\Chrono_LeggedRecovery\model-realism-audit.json
RocketRecoveryCases\Chrono_LeggedRecovery\final-acceptance-audit.json
local-tools\Run-RocketRecoveryPipeline.ps1
RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_model_config_stage3b_rigid.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-stage3b-rigid-report-data.json
RocketRecoveryCases\Chrono_LeggedRecovery\Output\RocketRecovery\chrono-stage3b-rigid-response.json
RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_model_config_stage3c_rigid_body_link.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-stage3c-rigid-body-link-report-data.json
RocketRecoveryCases\Chrono_LeggedRecovery\Output\RocketRecovery\chrono-stage3c-rigid-body-link-response.json
RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_data_template.json
RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_import_schema
RocketRecoveryCases\Chrono_LeggedRecovery\leg-mechanism-data-contract.json
RocketRecoveryCases\Chrono_LeggedRecovery\leg-mechanism-data-import-report.json
RocketRecoveryCases\Chrono_LeggedRecovery\leg-mechanism-import-selftest-report.json
RocketRecoveryCases\Chrono_LeggedRecovery\validation\synthetic_leg_import
RocketRecoveryCases\Chrono_LeggedRecovery\leg-mechanism-data-validation.json
RocketRecoveryCases\Chrono_LeggedRecovery\leg-mechanism-gap-tracker.json
RocketRecoveryCases\Chrono_LeggedRecovery\leg-mechanism-data-request-pack.json
RocketRecoveryCases\Chrono_LeggedRecovery\leg-mechanism-data-request-lint.json
RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_data_request_pack
RocketRecoveryCases\Chrono_LeggedRecovery\real-leg-mechanism-builder-gate.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-real-leg-backend-selftest-report.json
RocketRecoveryCases\Chrono_LeggedRecovery\chrono-real-leg-mechanism-report-data.json
visualization\chrono-recovery-data.js
visualization\chrono-two-way-data.js
visualization\chrono-stage3-tripod-data.js
visualization\chrono-stage3-two-way-data.js
visualization\chrono-stage3-lock-data.js
visualization\chrono-stage3-lock-two-way-data.js
visualization\thies-buffer-curves-data.js
visualization\chrono-stage3-thies-buffer-data.js
visualization\literature-comparison-registry-data.js
visualization\model-realism-audit-data.js
visualization\chrono-final-acceptance-data.js
visualization\chrono-stage3b-rigid-data.js
visualization\chrono-stage3c-rigid-body-link-data.js
visualization\leg-mechanism-contract-data.js
visualization\leg-mechanism-import-data.js
visualization\leg-mechanism-import-selftest-data.js
visualization\leg-mechanism-validation-data.js
visualization\leg-mechanism-gap-tracker-data.js
visualization\leg-mechanism-data-request-pack-data.js
visualization\leg-mechanism-data-request-lint-data.js
visualization\real-leg-mechanism-builder-data.js
visualization\chrono-real-leg-backend-selftest-data.js
visualization\chrono-real-leg-mechanism-data.js
visualization\chrono-final-acceptance.html
visualization\model-realism-audit.html
visualization\literature-comparison-registry.html
visualization\thies-buffer-curves.html
visualization\chrono-stage3-thies-buffer.html
visualization\chrono-stage3c-rigid-body-link.html
visualization\leg-mechanism-contract.html
visualization\leg-mechanism-import.html
visualization\leg-mechanism-validation.html
visualization\leg-mechanism-gap-tracker.html
visualization\leg-mechanism-data-request-pack.html
visualization\leg-mechanism-data-request-lint.html
visualization\real-leg-mechanism-builder.html
visualization\chrono-recovery.html
visualization\chrono-two-way.html
visualization\chrono-stage3-tripod.html
visualization\chrono-stage3-two-way.html
visualization\chrono-stage3-lock.html
visualization\chrono-stage3-lock-two-way.html
docs\chrono-leg-coupling-plan.md
docs\literature-comparison-registry.md
docs\model-realism-audit.md
docs\chrono-final-acceptance-audit.md
docs\leg-mechanism-data-contract.md
docs\leg-mechanism-data-import.md
docs\leg-mechanism-import-selftest.md
docs\leg-mechanism-data-validation.md
docs\leg-mechanism-gap-tracker.md
docs\leg-mechanism-data-request-pack.md
docs\leg-mechanism-data-request-lint.md
docs\real-leg-mechanism-builder.md
docs\chrono-real-leg-backend-selftest.md
docs\chrono-real-leg-mechanism.md
```

注意：Chrono 路线不会回退到 `integrated_recovery_model.py` 中旧的手写 `contact_forces()`。如果 PyChrono 不可用，脚本会生成环境检查并停止真实多体计算。

新增真实支腿机构数据缺口追踪器：`leg_mechanism_gap_tracker.py` 会把每个 strict blocking field 映射到对应 CSV、必须获取的数据来源，并明确当前 Thies/Yue/Li/Wang/Nargolkar 论文不能直接补齐真实 CAD/Adams 机构字段。它已经接入 `Run-RocketRecoveryPipeline.ps1` 和最终验收审计。

新增真实支腿机构数据补齐包：`leg_mechanism_data_request_pack.py` 根据缺口追踪器生成 `Input/leg_mechanism_data_request_pack/*.todo.csv`、`field_tasks.csv` 和 `field_tasks.jsonl`。这些文件是数据采集清单，不会被 importer 自动读取，也不会改变当前仿真输入。

新增真实支腿机构数据补齐包检查：`leg_mechanism_data_request_lint.py` 当前 9/9 通过，确认补齐包覆盖全部 120 个 blocking field，marker 坐标按 B/T/K/P 行正确折叠，`.todo.csv` 不会和正式 importer 文件名冲突。

## 2026-08-15 真实性更新

- Stage 3 锁紧双向模块现将 Chrono 接触和锁紧反力完整映射为 `[Fx,Fy,Fz,Mx,My,Mz]`，通过本地 HAMS 全 `6x6` 附加质量和辐射阻尼矩阵计算支腿引起的平台增量；Wang 波浪/喷流基线仍只有 heave/roll/pitch。
- 已修正 Chrono 碰撞甲板的 pitch 符号，使其与 `DeckMotion.deck_z = heave + roll*y - pitch*x` 一致；Chrono 时间轴现用整数步号覆盖配置起止端点，最终动画和广义力均来自同一次反馈甲板重放。
- 该模块仍是松耦合。固定点残差和 6DOF 半时间步收敛必须以最新报告为准，未通过时不得称为强耦合收敛。
- 本机编译 HAMS 的四个 CertTest 求解均正常结束，但仓库旧 benchmark 未全部复现。工具链证据见 `docs/hams-certtest-toolchain-diagnosis.md`。
- 最终状态以 `docs/model-realism-audit.md` 和 `docs/chrono-final-acceptance-audit.md` 为准。下面的长段落保留为早期阶段历史快照，不再代表当前验收结论。

## 历史状态快照

当前本机状态：`.tools\chrono-env` 已安装 `pychrono=10.0.0`、`numpy` 和项目本地 PDF 数字化依赖，并已通过最小球-甲板接触自测。阶段 1 已从失败的自由足垫 + TSDA 模型改为 `ChLinkMatePrismatic` 竖向导向足垫 + TSDA 缓冲器模型，四个工况均可重新运行并生成动画数据。Chrono `DeckMotion` 已扩展为 6DOF 位移/姿态/速度/角速度接口；Wang 2023 源数据没有的 `surge/sway/yaw` 当前作为显式零填充字段进入适配器。阶段 2 已完成线性叠加式双向松耦合：Chrono 四腿接触力映射为平台 `F_leg,3dof=[Fz,Mx,My]`，进入 Cummins 修正方程，并生成 Wang 基线与腿反力反馈响应对比。Stage 3A 已完成 tripod 支腿代理：斜向主腿导向、非线性压缩缓冲、两根弹性斜撑、足垫接触、喷管间隙诊断、接触状态机、触地后稳定诊断和锁紧候选诊断均由 Chrono 计算。Stage 3A tripod 反力也已接入双向松耦合并通过四工况、作用反作用、接触状态机、能量趋势、偏心响应和半时间步收敛检查。Stage 3 锁紧代理已完成四工况计算，稳定窗口满足后实际添加 `ChLinkMateFix` 火箭-甲板固定约束，实际锁紧时间为 `514.769..520.097 s`。Stage 3 锁紧双向松耦合也已完成四工况计算，足垫接触反力与锁紧约束反力共同映射回 Cummins，当前无腿退化、作用反作用、接触状态机、能量诊断、偏心响应、锁紧反馈和半时间步收敛检查均为 OK。Thies 2022 图 4/5 的缓冲器力-行程、力-速度曲线已从 PDF 栅格图数字化并接入 `compression_only_table` 分支，当前四工况均已计算；最大主缓冲器力约 `936 kN`，与 Thies 表 8 的 `935 kN` 量级一致，最终喷管间隙约 `0.570 m`，但四工况触地后稳定诊断未全部通过，主要原因是最终角速度超过当前 `0.25 deg/s` 稳定阈值。Stage 3B 刚性斜撑诊断分支可运行但物理诊断未通过；Stage 3C 已新增有限质量圆柱杆件 + 球铰诊断分支，`calm_center` 能跑完但同样未通过接触和物理诊断，明确显示缺少真实铰点、伸缩缓冲拓扑和锁定机构时，简单刚体杆件闭合模型会发散或产生不可接受结果。新增 `leg_mechanism_data_contract.py`，输出 Adams 等价 Chrono 支腿机构所需的铰点、拓扑、杆件质量惯量、伸缩缓冲器和锁紧硬件数据合同，以及可填写模板 `leg_mechanism_data_template.json`；新增 `leg_mechanism_data_importer.py` 和 `leg_mechanism_import_selftest.py`，分别提供真实 CAD/Adams CSV 导入入口和 synthetic 非生产自测路径；新增 `leg_mechanism_data_validator.py`，对该模板执行来源标签、必填字段、几何闭合、约束拓扑、质量惯量、缓冲器和锁紧硬件 gate 校验，默认严格模式仍拒绝 synthetic；新增 `real_leg_mechanism_builder.py`，只有当 validator 在严格真实数据下通过时才生成正式 `chrono_real_leg_mechanism_config.json`，当前输出 `blocked_by_data_validation`，没有写出正式真实机构配置；新增 `chrono_real_leg_backend.py` 和 `chrono_real_leg_backend_selftest.py`，将真实 config 结构映射到 PyChrono body、球铰和缓冲器 link，synthetic smoke assembly 当前创建 18 个 body、28 个 link；新增 `chrono_real_leg_mechanism_recovery.py`，作为真实支腿机构 runtime gate，当前因正式配置缺失输出 `blocked_missing_real_config`，并会拒绝 synthetic 自测配置进入正式运行。Chrono 配置已自动生成逐参数 provenance 表，逐项标明论文值、计算值、工程假设和实现设置。文献对比注册表当前收录 124 个条目，其中 Nargolkar 数字化逐点曲线 36 条、Wang 正文指标 5 项、Thies 表格/量级对比 9 项、Thies 数字化缓冲曲线 2 条，并把 5 类缺失曲线作为 gap 记录。`Run-RocketRecoveryPipeline.ps1` 已纳入 Thies 曲线数字化、Thies-buffer 分支、Stage 3C 诊断分支、支腿机构数据合同、CSV 导入 schema、CSV 导入自测、真实后端自测、validator、真实机构 builder gate 和真实机构 runtime gate，并通过 `-DryRun` 检查命令顺序。最终验收审计当前总状态为 `incomplete`，`19 PASS / 1 PARTIAL / 0 CHECK / 0 MISSING`；唯一剩余 PARTIAL 是 Adams 等价真实铰链杆件几何。该模型仍不是完整 Adams 等价 tripod 铰链支腿。
