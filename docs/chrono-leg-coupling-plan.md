# HAMS/Cummins + Chrono 着陆腿耦合目标与验收条件

## 总目标

建立一套开源、隔离、可复算的海上平台火箭着陆腿动力学模型：

```text
HAMS/Cummins: 平台频域水动力、时域记忆力、波浪/喷流/平台 6DOF 响应
Project Chrono/PyChrono: 火箭刚体/等效梁、四腿机构、足垫接触、缓冲、摩擦、滑移、再接触
```

核心原则：

- HAMS 只替代 AQWA 类势流水动力求解，不承担 Adams 类着陆腿多体接触动力学。
- Chrono 作为 Adams 的开源替代，用于接触、摩擦、铰链、缓冲器和刚柔多体动力学。
- 不修改 HAMS `SourceCode`，不修改系统 `PATH`，Chrono 安装在项目本地 `.tools/chrono-env`。
- 所有参数必须标注来源：文献公开值、现有计算输出、外部文件提取值或显式工程假设。

## 阶段 1：单向耦合

### 目标

HAMS/Cummins 先独立计算平台运动，Chrono 将甲板作为 prescribed moving body，火箭和四条着陆腿在运动甲板上落地。

输入：

- Wang 2023/HAMS-Cummins 生成的平台 heave、roll、pitch 时程。
- Thies 2022 的火箭质量、惯量、着陆速度、支腿几何和线性缓冲参数。
- Li 2025 或其他文献给出的接触刚度、阻尼、摩擦参数；若缺失必须显式标注为假设。

输出：

- 四个足垫的接触状态、接触时刻、法向接触力、切向摩擦力、滑移量。
- 四条支腿的缓冲行程、缓冲力、最大压缩、是否触及行程限位。
- 火箭质心位移/速度、姿态角/角速度、最终稳定状态。
- 甲板着陆点和四个足点处的位移、速度、倾角、角速度。
- HTML 动画展示完整落地过程，而不是循环振荡示意。

### 验收条件

| 项目 | 验收条件 |
| --- | --- |
| 环境隔离 | `.tools/chrono-env/python.exe` 可导入 `pychrono`、`numpy`；不依赖系统 Python、不改系统 PATH |
| HAMS 职责 | HAMS/Cummins 输出平台运动；代码中不把支腿接触力塞进 HAMS 源码 |
| Chrono 职责 | 着陆腿接触由 Chrono 求解；不调用旧的手写 `contact_forces()` 作为主计算结果 |
| 接触有效性 | 最小球-甲板接触自测通过：球不能穿透甲板，静止接触力接近自重 |
| 火箭不穿透 | 火箭落地后足垫不穿透甲板，支腿行程不出现非物理超大值 |
| 足垫约束 | 足垫不能靠无约束横向滑移逃避承载；最大滑移必须受摩擦/机构约束解释 |
| 静水中心落地 | 四腿接触时刻和峰值力近似对称，相对不平衡小于设定阈值 |
| 偏心/倾斜落地 | 四腿接触顺序、峰值力和火箭姿态随落点/甲板姿态发生可解释变化 |
| 文献对比 | Thies 触地动能、参考缓冲行程、参考支腿力在报告中列出并计算误差 |
| 可视化 | `visualization/chrono-recovery.html` 能显示落地动画、四腿状态、力/行程/滑移曲线和参数审计 |

## 阶段 2：双向耦合

### 目标

Chrono 每个时间步返回四足垫对甲板的接触反力和力矩，作为平台 Cummins 方程的外载荷：

```text
(M + A_inf) qdd + C qd + K q + F_memory = F_wave + F_plume + F_leg
```

当前阶段 2 的已实现降阶版本只回灌 heave/roll/pitch 三个自由度，因此实际使用：

```text
F_leg,3dof = [Fz, Mx, My]
```

其中：

```text
F_leg = [Fx, Fy, Fz, Mx, My, Mz]
M_leg = r_contact x F_contact
```

### 验收条件

| 项目 | 验收条件 |
| --- | --- |
| 退化一致性 | 关闭 `F_leg` 后，平台响应退化为原 Wang 2023/HAMS-Cummins 时程 |
| 作用反作用 | Chrono 给火箭的接触力与送入平台的反力大小相等、方向相反 |
| 力矩方向 | 中心落地力矩接近零；偏心落地激发正确方向的 roll/pitch 力矩 |
| 数值稳定 | 时间步减半后，峰值接触力、最大行程、平台峰值运动变化小于 10% |
| 能量审计 | 接触、摩擦、缓冲器耗能非负，不出现无约束能量增长 |
| 对比输出 | 同一图中给出 Wang 2023 无腿反力基线和 Chrono 腿反力反馈后的 heave/roll/pitch 响应 |

## 阶段 3：真实支腿机构和缓冲器

### 目标

将第一版 TSDA 等效支腿升级为更接近 Adams 的 Chrono 多体模型：

- 火箭刚体或等效梁。
- 四条支腿，每条包含主支柱、斜撑、铰链、足垫。
- 非线性液压/液气缓冲器力-行程-速度曲线。
- 足垫库仑/正则化摩擦、滑移、离地、再接触。
- 支腿锁紧、触地后稳定和喷管离地间隙检查。

### 分步目标

| 步骤 | 目标 | 当前范围 |
| --- | --- | --- |
| Stage 3A | 用 Chrono 建立 tripod 支腿计算代理 | 斜向主腿导向、非线性压缩缓冲、两根弹性斜撑、足垫接触、稳定锁紧诊断 |
| Stage 3B | 用真实铰链和刚性杆件替换弹性斜撑代理 | 已加入 `ChLinkDistance` 刚性斜撑代理，但单工况物理诊断失败；需要补齐真实铰点/运动学后才能验收 |
| Stage 3C | 用有限质量刚体杆件和球铰替换质量为零的距离约束 | 已加入圆柱杆件 + `ChLinkMateSpherical` 诊断分支；`calm_center` 可运行但物理诊断失败，证明不能用任意闭合杆件冒充 Adams/CAD 模型 |
| Stage 3-buffer | 用文献或试验曲线替换假设缓冲器 | 已从 Thies Figure 4/5 数字化 force-stroke/force-velocity 曲线并接入 `compression_only_table` |
| Stage 3-lock | 触地稳定后加入锁紧约束 | 已完成 `ChLinkMateFix` 火箭-甲板锁紧代理，四工况均实际触发锁紧 |
| Stage 3D | 将 Stage 3 支腿反力回灌 Cummins | 已完成 Stage 3A tripod 双向松耦合；已完成 Stage 3-lock 接触反力 + 锁紧约束反力双向松耦合；Stage 3B/3C 几何诊断分支因物理诊断失败不作为验收结果 |

### 验收条件

| 项目 | 验收条件 |
| --- | --- |
| 机构自由度 | 每条支腿的铰链、支柱和足垫相对运动由 Chrono 约束控制 |
| 缓冲器曲线 | 线性缓冲器可替换为表格/函数形式的非线性缓冲曲线 |
| 接触状态机 | 能记录首腿接触、四腿全接触、离地、再接触、锁紧完成时刻 |
| 稳定性指标 | 输出最大姿态角、角速度、支承多边形裕度、喷管最小间隙 |
| 文献对照 | 与 Thies/Yue/Li/Wang 等文献可获得结果逐项对比，无法直接对比的项明确说明原因 |

Stage 3A 的可验收边界：

- 主腿不再是阶段 1/2 的竖向导向，而是沿 Thies Table 4 主腿几何方向布置的 `ChLinkMatePrismatic`。
- 主缓冲器由 Chrono `ChLinkTSDA` 的非线性压缩-only force functor 计算，输出每条腿的力和行程；默认用双线性硬止挡代理，也支持后续切换为表格型力-行程/速度曲线。
- 每条腿包含两根从 T/K 附着点到足垫的弹性轴向斜撑，输出斜撑力和长度误差。
- 四工况均输出首腿接触、四腿全接触、每腿触地顺序、离地次数、再接触次数、最终接触数、足垫穿透、足垫滑移、支承裕度、喷管间隙、触地后稳定诊断和锁紧候选时刻。
- 报告页展示落地动画和曲线，但所有 OK/CHECK 只代表脚本级模型检查，不代表真实火箭着陆合格判定。

Stage 3A 不声明：

- 不声明复现 Thies 的完整 MSC Adams 模型。
- 不声明已经具备 CAD 精确 tripod 铰点、杆件质量和刚性杆约束。
- 不声明硬止挡、摩擦和缓冲曲线来自公开试验数据；缺失项必须保留为显式假设。
- 不声明已经完成 Chrono/Cummins 强耦合在线联合积分；目前完成的是 Stage 3A tripod 代理的双向松耦合线性修正。

Stage 3-lock 双向当前可验收边界：

- `chrono_stage3_lock_two_way_recovery.py` 使用 `tripod_actuated_lock_model_config()`，先由 Chrono 计算四腿接触、缓冲、摩擦和触地后锁紧，再把足垫接触反力与锁紧约束反力完整映射为平台 `F_leg,6dof=[Fx,Fy,Fz,Mx,My,Mz]`。
- 平台反馈使用本机 HAMS 6x6 附加质量、辐射阻尼和 Cummins 线性修正：`q_total = q_Wang,3dof(F_wave + F_plume) + delta_q_6dof(F_contact + F_lock)`，因此它是双向松耦合，不是 Chrono/Cummins 强耦合在线联合积分。
- 王智 2023 公开基线只包含 `heave/roll/pitch`。`surge/sway/yaw` 没有公开的波浪、系泊或 DP 输入，环境基线保持显式零值；新增三通道只代表 Chrono 反力驱动的无系泊增量诊断。
- 平台修正完成后再执行一次 Chrono 反馈甲板重放，网页动画使用该重放时历；报告同时公开下一轮反力对应的 closure residual。动画一致性通过不等于松耦合固定点已经收敛。
- 四个工况均已运行：`calm_center`、`wave_center`、`wave_bow_15m`、`wave_port_15m`。
- 当前验证结果：无腿退化、作用反作用、接触状态机、能量诊断、偏心响应、锁紧反馈和 `wave_port_15m` 半时间步收敛检查均为 OK。
- 关键量级：锁紧实际触发时间为 `514.769..520.097 s`；`wave_bow_15m` 腿反力与锁紧反力引起 pitch 峰值修正约 `0.00574 deg`；`wave_port_15m` 引起 roll 峰值修正约 `0.12414 deg`；半时间步收敛最大相对差约 `9.08%`，低于 `10%` 阈值。
- 锁紧机构使用 `ChLinkMateFix` 代理，只验证“稳定后固定约束反力反馈”的数值链路，不声明已复现真实夹持/固定硬件。

Stage 3B 当前诊断结论：

- 新增 `tripod_rigid_brace_model_config()` 和 `chrono_stage3b_rigid_recovery.py`，用 `ChLinkDistance` 表示两根定长斜撑。
- `calm_center` 单工况能运行，斜撑长度最大误差约 `5.5e-5 m`，说明刚性长度约束本身生效。
- 但该代理禁用主腿滑轨后出现足垫滑移约 `7.6 m`、最大接触穿透大于足垫半径、最终喷管间隙为负，物理诊断为 CHECK。
- 结论：在缺少 Thies/Adams 级别真实铰点坐标、杆件连接拓扑和锁定机构之前，不能把简单刚性斜撑代理作为可验收支腿模型。Stage 3B 文件保留为失败证据和后续接口，不作为最终结果。

Stage 3C 当前诊断结论：

- 新增 `tripod_rigid_body_link_model_config()` 和 `chrono_stage3c_rigid_body_link_recovery.py`，用有限质量 `ChBodyEasyCylinder` 圆柱杆件和两端 `ChLinkMateSpherical` 球铰表示 Thies 表 4 的 PT/KP 支撑杆。
- 主 B-to-foot 构件仍保持 `ChLinkTSDA` 非线性压缩缓冲器，因为论文没有公开伸缩缓冲器的多体拓扑、滑移副、壳体/活塞质量和铰点坐标。
- `calm_center` 可完成数值运行，但接触状态机和物理诊断未通过，出现过大滑移、过大杆长误差和喷管间隙失真。
- 结论：Stage 3C 证明 PyChrono 可以搭建有限质量杆件和球铰，但也证明没有真实铰点/拓扑数据时，简单刚体杆件闭合不能作为 Adams 替代结果。

真实支腿机构数据合同：

- 新增 `leg_mechanism_data_contract.py`，生成 `leg-mechanism-data-contract.json` 和可填写模板 `Input/leg_mechanism_data_template.json`。
- 合同把 Adams 等价 Chrono 支腿所需输入拆成坐标系、四腿方位、B/T/K/P 铰点坐标、约束拓扑、伸缩缓冲器拓扑、杆件质量惯量、足垫接触、锁紧硬件和验证曲线。
- 当前合同状态为 `incomplete_for_adams_equivalent_chrono_model`，这是有意保留的边界：没有 CAD/Adams 导出、作者数据或校准测量前，不允许把 Stage 3B/3C 调参成“通过”。

真实支腿机构数据导入：

- 新增 `leg_mechanism_data_importer.py`，生成 `Input/leg_mechanism_import_schema/*.csv`。
- 支持把 CAD/Adams/作者数据按 CSV 导入为 `Input/leg_mechanism_data_imported.json`，再交给 validator 和 builder gate。
- 默认 `report` 只写空 schema，不改当前模板；必须显式执行 `import --source-dir ...` 才会生成 imported 模板。
- 新增 `leg_mechanism_import_selftest.py`，生成一组合成四腿 CSV fixture，验证 `CSV -> imported template -> validator -> builder` 代码路径。该 fixture 只用于工具链自测，使用 `synthetic_test_fixture` 来源标签，不能作为论文复现或真实 CAD/Adams 数据。

真实支腿机构数据校验：

- 新增 `leg_mechanism_data_validator.py`，读取 `Input/leg_mechanism_data_template.json` 并生成 `leg-mechanism-data-validation.json`。
- validator 检查来源标签、必填字段、四腿 B/T/K/P 坐标、PB/PT/PK 几何闭合、约束拓扑、杆件质量惯量、缓冲器行程/伸缩行为和锁紧硬件。
- 当前 validator gate 为 `False`，因此后续真实机构分支必须继续被阻止；Stage 3A 仍是当前可运行代理模型。
- 默认严格模式拒绝 `synthetic_test_fixture`；只有显式 `--allow-synthetic` 的自测路径会接受该来源类别。

真实支腿机构数据缺口追踪：

- 新增 `leg_mechanism_gap_tracker.py`，读取合同、模板、validator、builder 和 runtime gate 输出。
- 该报告把每个 strict blocking field 映射到需要填写的 CSV、必须取得的数据来源，以及当前论文为什么不能直接填该字段。
- 当前结论是：Thies/Yue/Li/Wang/Nargolkar 可支撑量级验证、接触参数参考、平台水动力和缓冲器曲线数字化，但不能提供 Adams 等价机构所需的完整 CAD marker、约束拓扑、杆件质量惯量、伸缩缓冲器拓扑和锁紧硬件。
- 因此当前真实机构分支继续保持 blocked，这是正确状态，不应通过调参或 synthetic fixture 绕过。

真实支腿机构数据补齐包：

- 新增 `leg_mechanism_data_request_pack.py`，根据 gap tracker 的 120 个阻塞字段生成 `Input/leg_mechanism_data_request_pack`。
- 该目录包含 `field_tasks.csv`、`field_tasks.jsonl` 和按导入 schema 拆分的 `.todo.csv` 文件，用于向 CAD/Adams/作者数据源索取或整理数据。
- `.todo.csv` 文件故意不使用 importer 的正式文件名，避免空模板被误导入模型。
- 拿到真实数据后，应把完成的行复制到 `Input/leg_mechanism_import_schema/*.csv`，再执行 importer、validator、builder 和 runtime gate。
- 新增 `leg_mechanism_data_request_lint.py`，检查补齐包是否覆盖全部 120 个 blocking field、字段组是否与 importer schema 对齐、`.todo.csv` 是否保持未填状态、是否排除 synthetic/assumption 来源类别。

真实 Chrono 机构配置生成 gate：

- 新增 `real_leg_mechanism_builder.py`，在 validator 通过后才从模板生成 `Input/chrono_real_leg_mechanism_config.json`。
- 当前输出 `real-leg-mechanism-builder-gate.json`，状态为 `blocked_by_data_validation`，未写出可运行真实机构配置。
- 这个 gate 是从数据合同进入真实 Chrono 机构分支的唯一入口，避免绕过 validator 直接使用假设铰点或代理拓扑。
- builder 已支持 `--output`，用于把通过校验的数据写到显式目标路径。即使启用 `--allow-synthetic`，也不能把合成 fixture 写入正式 `Input/chrono_real_leg_mechanism_config.json`。

真实 Chrono 机构运行入口：

- 新增 `chrono_real_leg_mechanism_recovery.py`，作为未来真实支腿机构进入 Chrono 计算的正式命令入口。
- 当前默认读取 `Input/chrono_real_leg_mechanism_config.json`；该文件不存在时输出 `blocked_missing_real_config`。
- 如果显式传入 synthetic self-test config，该入口会因为 `synthetic_test_fixture` 来源标签而阻止运行。
- 新增 `chrono_real_leg_backend.py`，提供真实 config 到 PyChrono body、球铰和缓冲器 link 的通用装配适配器。
- 新增 `chrono_real_leg_backend_selftest.py`，用 synthetic config 执行 smoke assembly，当前能创建 18 个 body 和 28 个 link；该自测只证明 adapter 代码路径，不是落地轨迹仿真。
- 当前 runner 在严格真实配置存在且通过 gate 时才会调用后端 smoke assembly，不把 Stage 3A/3B/3C 代理拓扑自动当成真实机构后端。

## 当前本机状态

- 已在项目本地安装 Project Chrono/PyChrono：`.tools/chrono-env`。
- 已验证 `pychrono`、`ChSystemSMC`、`ChLinkTSDA` 和 `numpy` 可导入。
- 已修正 Chrono 系统初始化，显式启用 Bullet collision system 和 `SPARSE_LU` 求解器。
- 已完成最小球-甲板接触自测，接触力可正确平衡自重。
- 已将失败的自由足垫 + TSDA 模型替换为 `ChLinkMatePrismatic` 竖向导向足垫 + TSDA 缓冲器模型。
- 已完成阶段 1 四个工况计算：`calm_center`、`wave_center`、`wave_bow_15m`、`wave_port_15m`。
- 当前阶段 1 已通过脚本级检查：Thies 触地动能误差小于 1%，静水中心落地四腿峰值接触力不平衡约 0.37%，倾斜/偏心工况存在首腿先触地时序，最大接触穿透小于足垫半径。
- 已完成阶段 2 双向松耦合计算：Chrono 四腿接触力映射为平台 `F_leg,3dof=[Fz,Mx,My]`，再进入 Cummins 修正方程。
- 阶段 2 四工况已重新计算，输出 `chrono-two-way-response.json`、`chrono-two-way-data.js` 和 `chrono-two-way.html`。
- 阶段 2 当前验证结果：关闭腿力时零修正并退化回 Wang 基线；四工况作用反作用残差为 0；`wave_bow_15m` 腿反力引起 pitch 峰值修正约 0.0058 deg；`wave_port_15m` 腿反力引起 roll 峰值修正约 0.1192 deg；`wave_port_15m` 半步收敛检查全部小于 10%。
- 已完成 Stage 3A tripod 代理计算：斜向主腿导向、非线性压缩缓冲、两根弹性斜撑、接触状态机和锁紧候选诊断已接入 Chrono。
- Stage 3A 四工况已重新计算，输出 `chrono-stage3-tripod-response.json`、`chrono-stage3-tripod-data.js` 和 `chrono-stage3-tripod.html`。
- Stage 3A 当前验证结果：Thies 触地动能误差约 0.013%；接触状态机检查为 OK；四工况最终均保持四足接触；偏心横向工况首腿到四腿全接触间隔约 0.08 s；四工况均记录到离地/再接触事件；最大足垫滑移约 0.0397 m；最大主缓冲行程约 0.0464 m；最大斜撑轴向力约 656.6 kN；最小喷管间隙诊断值约 `0.425..0.496 m`；最终喷管间隙约 0.559 m；`wave_port_15m` 最大火箭 roll 约 3.748 deg。
- 已完成 Stage 3A tripod 双向松耦合：`ChronoTripodLegModel` 的四腿接触反力映射为平台 `F_leg,3dof=[Fz,Mx,My]`，进入 Cummins 修正方程。
- Stage 3A 双向四工况当前验证结果：关闭腿力时退化回 Wang 基线；四工况作用反作用检查为 OK；接触状态机检查为 OK；能量趋势检查为 OK；`wave_bow_15m` 腿反力引起 pitch 峰值修正约 0.0057 deg；`wave_port_15m` 腿反力引起 roll 峰值修正约 0.1241 deg；`wave_port_15m` 半时间步收敛最大相对差约 9.08%，小于 10%。
- 已完成 Stage 3 锁紧代理：稳定窗口满足后自动添加 `ChLinkMateFix` 火箭-甲板固定约束，输出 `chrono-stage3-lock-response.json`、`chrono-stage3-lock-data.js` 和 `chrono-stage3-lock.html`。
- Stage 3 锁紧四工况当前验证结果：锁紧执行检查为 OK；`calm_center` 实际锁紧 `514.769 s`；`wave_center` 实际锁紧 `518.095 s`；`wave_bow_15m` 实际锁紧 `514.785 s`；`wave_port_15m` 实际锁紧 `520.097 s`。
- 已完成 Stage 3 锁紧双向松耦合：足垫接触反力与锁紧约束反力共同映射为平台 `F_leg,6dof=[Fx,Fy,Fz,Mx,My,Mz]`，进入使用 HAMS 全 6x6 水动力矩阵的 Cummins 增量方程，输出 `chrono-stage3-lock-two-way-response.json`、`chrono-stage3-lock-two-way-data.js` 和 `chrono-stage3-lock-two-way.html`。
- Stage 3 锁紧双向四工况当前验证结果：关闭腿力时退化回 Wang 基线；四工况作用反作用检查为 OK；接触状态机检查为 OK；能量趋势检查为 OK；锁紧反馈检查为 OK；`wave_bow_15m` 接触和锁紧反力引起 pitch 峰值修正约 `0.00574 deg`；`wave_port_15m` 引起 roll 峰值修正约 `0.12414 deg`；`wave_port_15m` 半时间步收敛最大相对差约 `9.08%`，小于 `10%`。
- 已完成 Thies 2022 图 4/5 缓冲器曲线数字化：`thies_buffer_digitization.py report` 从 PDF 栅格图中提取力-行程和力-速度表，并生成 `thies-buffer-curves.json`、`thies-buffer-curves-data.js` 和 `thies-buffer-curves.html`。
- 已完成 Stage 3A Thies 数字化缓冲器分支：`chrono_stage3_thies_buffer_recovery.py report` 将上述曲线作为 Chrono `compression_only_table` 主缓冲器定律，输出 `chrono-stage3-thies-buffer-response.json` 和 `chrono-stage3-thies-buffer-data.js`。四工况最大主缓冲器力约 `936 kN`，与 Thies 表 8 的 `935 kN` 量级一致；最终喷管间隙约 `0.570 m`；但触地后稳定诊断未全部通过，原因是最终角速度超过当前 `0.25 deg/s` 稳定阈值。
- 已完成 Stage 3C 有限质量刚体杆件诊断分支：`chrono_stage3c_rigid_body_link_recovery.py report --case calm_center` 生成 `chrono-stage3c-rigid-body-link-report-data.json`、`chrono-stage3c-rigid-body-link-data.js` 和 `chrono-stage3c-rigid-body-link.html`。该分支能运行，但物理诊断失败，不作为验收模型。
- 已完成 Adams 等价支腿机构数据合同：`leg_mechanism_data_contract.py report` 生成 `leg-mechanism-data-contract.json`、`Input/leg_mechanism_data_template.json`、`docs/leg-mechanism-data-contract.md` 和 `leg-mechanism-contract.html`。该合同明确列出真实铰点、拓扑、伸缩缓冲器、杆件质量惯量、锁紧硬件和验证曲线的缺失项。
- 已完成 CAD/Adams 数据导入 schema：`leg_mechanism_data_importer.py report` 生成 `Input/leg_mechanism_import_schema`、`leg-mechanism-data-import-report.json`、`docs/leg-mechanism-data-import.md` 和 `leg-mechanism-import.html`。当前没有导入真实数据，模板未被覆盖。
- 已完成 CAD/Adams 数据导入自测：`leg_mechanism_import_selftest.py report` 生成合成 CSV fixture、`leg_mechanism_data_synthetic.json`、`synthetic-leg-import-validation.json`、`synthetic-real-leg-builder-gate.json`、`chrono_real_leg_mechanism_config.synthetic.json`、`docs/leg-mechanism-import-selftest.md` 和 `leg-mechanism-import-selftest.html`。该自测通过，但明确标记为 synthetic，不写正式真实机构配置。
- 已完成 Adams 等价支腿机构数据校验：`leg_mechanism_data_validator.py report` 生成 `leg-mechanism-data-validation.json`、`docs/leg-mechanism-data-validation.md` 和 `leg-mechanism-validation.html`。当前 gate 未通过，阻止把未填模板用于真实机构分支。
- 已完成真实 Chrono 机构配置生成 gate：`real_leg_mechanism_builder.py report` 生成 `real-leg-mechanism-builder-gate.json`、`docs/real-leg-mechanism-builder.md` 和 `real-leg-mechanism-builder.html`。当前状态为 `blocked_by_data_validation`，没有写出 `Input/chrono_real_leg_mechanism_config.json`。
- 已完成真实 Chrono 机构运行入口 gate：`chrono_real_leg_mechanism_recovery.py report` 生成 `chrono-real-leg-mechanism-report-data.json`、`docs/chrono-real-leg-mechanism.md` 和 `chrono-real-leg-mechanism.html`。当前状态为 `blocked_missing_real_config`，用于明确阻止缺失真实配置或 synthetic 配置进入正式运行。
- 已完成真实 Chrono 后端 synthetic smoke assembly：`chrono_real_leg_backend_selftest.py report` 生成 `chrono-real-leg-backend-selftest-report.json`、`docs/chrono-real-leg-backend-selftest.md` 和 `chrono-real-leg-backend-selftest.html`。该自测当前为 `PASS`，创建 18 个 body、28 个 link，但仅证明真实配置后端适配器能装配 PyChrono 对象。
- 已新增文献对比注册表：`literature_comparison_registry.py report` 生成 `literature-comparison-registry.json`、`docs/literature-comparison-registry.md` 和 `visualization/literature-comparison-registry.html`，统一记录论文数据来源、数字化方式、单位、误差指标和缺失曲线。
- 已新增最终验收审计：`final_acceptance_audit.py report` 会读取当前所有权威 JSON、HTML 和源码边界，生成 `final-acceptance-audit.json`、`docs/chrono-final-acceptance-audit.md` 和 `visualization/chrono-final-acceptance.html`。
- 当前最终验收审计结论：`incomplete`，`19 PASS / 1 PARTIAL / 0 CHECK / 0 MISSING`。全链路编排脚本已纳入 Thies 曲线数字化、Thies-buffer 分支、Stage 3C 诊断分支、支腿机构数据合同、CSV 导入 schema、CSV 导入自测、真实后端自测、validator、真实机构 builder gate 和真实机构 runtime gate，并通过 dry-run；Chrono `DeckMotion` 已扩展为 6DOF 位移/姿态/速度/角速度接口；Chrono 配置已生成逐参数 provenance 表，逐项标明 `paper/computed/engineering_assumption/implementation_setting/to_verify` 等来源类别。文献注册表当前收录 124 个条目，其中 Nargolkar 数字化逐点曲线 36 条、Wang 正文指标 5 项、Thies 表格/量级对比 9 项、Thies 数字化缓冲曲线 2 条，并把 5 类缺失曲线作为 gap 记录。剩余 PARTIAL 项为 Adams 等价铰链机构。
- 重要限制：阶段 2、Stage 3A 双向和 Stage 3 锁紧双向均是线性叠加的松耦合迭代，不是 Chrono/Cummins 强耦合在线联合积分；Stage 3A 是 tripod 计算代理，不是完整 Adams 等价多体铰链支腿；真实铰链杆件、实测非线性缓冲曲线和真实硬件锁紧机构仍需继续实现。

## 运行命令

创建或修复本地 Chrono 环境：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Create-ChronoEnv.ps1
```

运行单向耦合报告：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_one_way_recovery.py report
```

生成双向耦合接口合同：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_two_way_recovery.py contract
```

运行双向松耦合四工况报告：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_two_way_recovery.py report
```

运行 Stage 3A tripod 代理四工况报告：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_stage3_recovery.py report
```

运行 Stage 3A tripod 双向松耦合四工况报告：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_stage3_two_way_recovery.py report
```

运行 Stage 3 锁紧代理四工况报告：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_stage3_lock_recovery.py report
```

运行 Stage 3 锁紧代理双向松耦合四工况报告：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_stage3_lock_two_way_recovery.py report
```

数字化 Thies 2022 缓冲器曲线：

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

生成 Adams 等价支腿机构数据合同：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_contract.py report
```

生成 CAD/Adams 支腿机构数据导入 schema：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_importer.py report
```

运行合成 CSV 导入自测；该命令只写 `validation/synthetic_leg_import` 下的自测产物，不写正式真实机构配置：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_import_selftest.py report
```

运行真实配置到 PyChrono 后端的 synthetic smoke assembly 自测：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_real_leg_backend_selftest.py report
```

生成真实支腿机构数据缺口追踪报告：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_gap_tracker.py report
```

生成真实支腿机构数据补齐包：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_request_pack.py report
```

检查真实支腿机构数据补齐包：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_request_lint.py report
```

导入已填写的 CSV：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_importer.py import --source-dir .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_import_schema
```

校验 Adams 等价支腿机构数据：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_validator.py report
```

运行真实 Chrono 支腿机构配置生成 gate：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\real_leg_mechanism_builder.py report
```

运行真实 Chrono 支腿机构 runtime gate：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_real_leg_mechanism_recovery.py report
```

生成文献对比与曲线元数据注册表：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\literature_comparison_registry.py report
```

生成最终验收审计：

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\final_acceptance_audit.py report
```

一键编排完整链路：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-RocketRecoveryPipeline.ps1
```

只检查命令顺序，不重跑计算：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-RocketRecoveryPipeline.ps1 -DryRun
```

打开 Stage 2 报告页：

```text
http://127.0.0.1:8765/chrono-two-way.html
```

打开 Stage 3A 报告页：

```text
http://127.0.0.1:8765/chrono-stage3-tripod.html
```

打开 Stage 3A 双向反馈报告页：

```text
http://127.0.0.1:8765/chrono-stage3-two-way.html
```

打开 Stage 3 锁紧代理报告页：

```text
http://127.0.0.1:8765/chrono-stage3-lock.html
```

打开 Stage 3 锁紧双向反馈报告页：

```text
http://127.0.0.1:8765/chrono-stage3-lock-two-way.html
```

打开 Thies 缓冲器数字化曲线页：

```text
http://127.0.0.1:8765/thies-buffer-curves.html
```

打开 Stage 3A Thies 数字化缓冲器动画页：

```text
http://127.0.0.1:8765/chrono-stage3-thies-buffer.html
```

打开 Stage 3C 刚体杆件诊断页：

```text
http://127.0.0.1:8765/chrono-stage3c-rigid-body-link.html
```

打开支腿机构数据合同页：

```text
http://127.0.0.1:8765/leg-mechanism-contract.html
```

打开支腿机构数据导入页：

```text
http://127.0.0.1:8765/leg-mechanism-import.html
```

打开支腿机构数据校验页：

```text
http://127.0.0.1:8765/leg-mechanism-validation.html
```

打开真实支腿机构数据缺口追踪页：

```text
http://127.0.0.1:8765/leg-mechanism-gap-tracker.html
```

打开真实支腿机构数据补齐包页：

```text
http://127.0.0.1:8765/leg-mechanism-data-request-pack.html
```

打开真实支腿机构数据补齐包检查页：

```text
http://127.0.0.1:8765/leg-mechanism-data-request-lint.html
```

打开真实机构 builder gate 页：

```text
http://127.0.0.1:8765/real-leg-mechanism-builder.html
```

打开最终验收审计页：

```text
http://127.0.0.1:8765/chrono-final-acceptance.html
```

打开文献对比注册表页：

```text
http://127.0.0.1:8765/literature-comparison-registry.html
```
