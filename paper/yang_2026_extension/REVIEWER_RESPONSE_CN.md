# 审稿意见逐条回复与修改说明

**稿件：** A Partitioned Hydromechanical Framework for Four Leg Reusable Launch Vehicle Landing on a Floating Barge

**修改原则：** 本轮不是通过措辞弱化问题，而是先完成审稿人要求的重算，再按计算是否通过收缩结论。以下所称“解决”分为三类：`重算通过` 表示新增计算满足预设判据；`证据补齐` 表示模型定义和溯源已完整，但不等于获得实验验证；`结论收缩` 表示新增计算仍未通过，因此正文撤回相应定量资格并保留失败结果。

## 一、总体修改

感谢审稿人指出稿件在证据权重、平台一致性和接触可复现性方面的问题。修订稿已重新定位为可重复的数值框架与验证层级研究，而不是全尺寸着陆载荷或允许海况预测。摘要、方法、结果和结论均按同一边界改写。Yang 缩比试验只用于约化模型对照；矩形驳船用于水动力和甲板运动；61.288 t 算例只用于同一平台算子上的全尺度耦合演示。三者不再相互替代验证。

新增或重算的证据包括：三层水动力网格与局部频率加密、高频附加质量尾段、辐射记忆回代、1000 组非重复随机波与 bootstrap 区间、600/1200/1800 s 时长敏感性、实际四足坐标、线性适用性筛查、128 次多起点辨识、同一平台四次固定点耦合、三层接触时间步、三档接触刚度、完整六分量接触合力矩记账、质量闭合及平台能量平衡。

## 二、Major Issues

### Major 1：600 s 随机波可能是 62.83 s 周期重复

**处理：重算通过。** 水动力频率网格与随机波合成网格现已明确分开。RAO 从中等网格插值到独立合成网格，合成频率间隔约为 0.004995 rad/s，对应重复周期 1257.95 s，大于 600 s 记录。每个工况的 JSON 均记录频率间隔、重复周期、自相关诊断和“记录不覆盖重复周期”判据。Figure 5 已完全重算。

**正文修改：** Section 2.3 给出实际合成网格；Section 3.2 说明水动力与随机网格的不同作用；Section 4.3 不再沿用旧版 19 个频率直接合成的解释。

**证据：** `wave-sensitivity-revision-600s.json` 的 `frequency_grids`、`cases/*/periodicity` 和 `acceptance.checks.no_repeat_period_in_record`。

### Major 2：100 个 realization 不足以支持三位小数 P95

**处理：重算通过。** 每个海况-浪向组合现使用 1000 个 realization，63 个组合共 63,000 条记录。每个 realization 先计算 600 s 内最大值，再对这些最大值求 P95。P95 使用 2000 次 percentile bootstrap 给出 95% 置信区间。

**结果：** 最大中心垂向速度 P95 为 1.570 m/s，95% 区间为 1.553-1.598 m/s；最大实际四足速度差 P95 为 1.591 m/s，区间为 1.559-1.629 m/s。正文保留三位小数是为了与机器输出对应，同时紧邻报告区间，不再暗示无不确定性的精确值。

### Major 3：原 [±9,±9] m 点不是全尺寸车辆四足位置

**处理：重算通过。** 着陆统计改用半径 6.926 m、方位角 45/135/225/315 deg 的四足布局。方位角是明确标注的对称布局假设。原 [±9,±9] m 点保留为 generic deck probes，只用于展示旋转半径敏感性，不再称为 feet。

**正文修改：** Figure 2 同时区分两个布局；Figure 5、摘要、Section 4.3 和结论中的 four-foot 均指 6.926 m 布局。旧值 2.435 m/s 已删除。

### Major 4：大倾角结果超出线性势流适用边界

**处理：结论收缩。** 新增 5 deg P95 倾角和甲板边缘浸水双判据。63 个工况中仅 41 个通过。最大倾角及最大甲板浸水工况均标为 outside linear validity，不再作为有效海况预测。Figure 5 用叉号直接标出失效工况。

**结果：** 最大 P95 倾角 11.99 deg，最大 P95 甲板边缘浸水 2.712 m；这两个数字现在用于说明需要非线性水动力，而不是支持平台作业能力。

### Major 5：缺少 CG、惯量和水静力参数

**处理：证据补齐。** 新增 Table 1，报告质量、CG、关于 CG 的 Ixx/Iyy/Izz、K33/K44/K55、参考点和外加阻尼。43.05 million kg、CG=(0,0,-2) m、Ixx=9.3275 billion kg m2、Iyy=52.0188 billion kg m2、Izz=60.6288 billion kg m2。正文明确这些参数来自均质矩形质量模型，不是实船倾斜试验数据。

### Major 6：附加线性阻尼 C 未定义

**处理：证据补齐。** 方程改写为 Cext，正文明确所有报告算例均使用零 6 by 6 外加线性阻尼矩阵。频率相关辐射阻尼仍通过记忆核进入方程，与 Cext 区分。无经验粘性滚阻，因此滚转峰值不作实船预测。

### Major 7：A(2 rad/s) 不能直接代表 A-infinity

**处理：新增计算并限定。** 水动力计算扩展到 5 rad/s。A-infinity 使用 4-5 rad/s 最后五个附加质量矩阵的均值，仅称 finite-cutoff estimate。A33、A44、A55 尾段相对范围分别为 1.638%、0.220% 和 0.605%。

辐射记忆另用 0.2-2.0 rad/s 正半定频带。对角项有限频带回代 RMS 误差为 3.19%、6.51% 和 3.65%。3-5 rad/s 阻尼出现数值负特征值，因此不用于记忆核。修订稿没有声称完成数学意义上的无限频率收敛。

### Major 8：缺少网格和频率收敛

**处理：新增计算，但判据未通过，结论收缩。** 三层湿表面网格约为 512、2048 和 8192 panels。粗、中网格在 0.2-2.0 rad/s 采用 0.025 rad/s 局部网格，并计算至 5 rad/s；细网格计算 0.6、0.8、1.0 rad/s 锚点。预先规定的最大选定变化阈值为 5%。

**结果：** coarse-to-medium 为 15.46%，medium-to-fine 为 5.88%，均未通过。Figure 4 明示 FAIL。中等网格因包含全部七个浪向和密集频率而用于后续计算，但正文只称 medium-grid sampled results，并把 5.88% 作为剩余数值不确定性。没有用“接近 5%”把结果改判为收敛。

### Major 9：Wang 平台运动与本文平台算子可能混用

**处理：重算通过。** Figure 6 的波浪、喷流时序和接触反馈全部通过本文 120 m by 50 m by 7 m 平台的同一质量、水静力、附加质量、辐射阻尼和记忆算子求解。Wang 文献只提供喷流载荷的时间轮廓；没有导入或数字化 Wang 的 165 m 平台位移。喷流在本文平台的 (15,10) m 点施加，并在 510 s 触地时刻截断。

**正文修改：** 删除 “Wang-based platform history” 表述，改为 “Wang plume temporal profile applied through the present platform operator”。

### Major 10：单次弱反馈没有证明充分

**处理：重算通过。** 现在执行四次平台-着陆固定点更新。验收要求最后一次更新的平台轨迹、峰值力、行程、触地时间差和接触冲量均不超过 2%。第三到第四次更新的平台指标为 0.145%，峰值力小于 0.001%，行程小于 0.001%，触地时间差 0.87%，接触冲量 0.03%，满足判据。

**限定：** 该结果证明本算例在生产时间步上的界面迭代收敛，不等于单体求解，也不消除接触时间步不收敛问题。

### Major 11：完整 wrench 与实际三通道反馈不一致

**处理：证据补齐并改图。** 四足力被归并为完整 [Fx,Fy,Fz,Mx,My,Mz]，作用反作用残差为机器精度零。因本文平台没有系泊/DP 水平恢复，实际返回平台方程的通道仅为 Fz、Mx、My。Figure 1 已明确标注通道，不再泛称完整六自由度闭环。

**被忽略分量：** 峰值 Fx=0.424 MN、Fy=1.453 MN、Mz=7.593 MN m。它们并不小，因此正文没有以“小量”作为忽略理由，而是把缺少水平恢复模型列为后续必须补齐的边界。

### Major 12：100 MN/m、穿透量和接触力不自洽

**处理：公式查清、阻尼换算修正并重新计算。** 实际显式接触律为 Fn=max(0,kn*delta-meff*Gn*vn)。在该模式中输入 Gn 的单位为 1/s，求解器再乘接触对有效质量。修订算例从目标阻尼 cn=10,000 N s/m 和有效质量 79.998 kg 换算得到 Gn=125.003 1/s，不再把 10 MN s/m 当作直接线性阻尼。

**新增敏感性：** 最细 0.125 ms 时间步下，kn=100/250/500 MN/m 的峰值力为 6.432/8.718/8.999 MN，穿透量为 52.42/23.64/12.65 mm，行程为 73.60/84.91/94.16 mm，而总法向冲量约为 3.909 MN s。局部峰值与行程对正则化敏感，所以 `load_prediction_qualified=false`。旧版 0.148 m 与 2.678 MN 已删除。

## 三、其他数值与写作意见

### 接触时间步和虚假精度

新增 0.500、0.250、0.125 ms 三层时间步。最细两层之间峰值力变化 1.07%、穿透变化 4.90%，但行程变化 11.16%，触地时间差变化超过 300%。因此 Table 4 明确写“no row is designated converged”，Figure 6 的 0.5 ms 曲线只作为过程演示，正文不再把触地时间和行程写成已收敛设计量。

### 平台插值与载荷回传

0.01 s 平台状态用位置-速度一致的 piecewise cubic Hermite 方法插值到接触网格。细网格接触合力矩通过区间守恒平均返回平台网格。方法已写入 Section 2.5 和机器报告。

### Verification 与 validation

新增四级证据结构：Level 1 代码验证；Level 2 子模型验证；Level 3 文献趋势对照；Level 4 完整耦合验证。Level 4 当前没有公开全尺寸海上触地试验，因此明确为 unavailable。作用反作用、能量残差和网格检查统一称 verification，不再称 validation。

同时重新执行了仓库自带 `CertTest/test_cert.py`。在其相对误差 10%、绝对误差 (10^{-7}) 的既定阈值下，本机现有输出出现 157 个文件级失败：Cylinder 65、DeepCwind 13、HywindSpar 7、Moonpool 72。现有证据不足以确定差异来源，因此修订稿明确将该项列为 failed external regression check，不再写成“通过官方 benchmark”，也不从中取得任何 validation credit。独立诊断及逐文件差异保存在 `analysis/diagnostics/hams-cert-root-cause.json` 和同名 Markdown 文件中。

### Thies 缓冲器

不再使用单一线性弹簧-阻尼替代。已从 Thies Figure 4 和 Figure 5 数字化 force-stroke 与 force-velocity 曲线，并以表格插值作为 compression-only absorber 输入。数字化轴标定、原始点、重采样点和哈希保存在独立 JSON。超出图示行程的 hard stop 仍是数值保护，正文明确不是文献数据。

### 能量检查

新增平台能量账本。四次反馈结果的相对残差为 -6.43e-6。该检查验证平台方程中的波浪、喷流、接触、辐射功和机械能记账，不被表述为整套推进-车辆-接触系统的实验验证。

### 喷流和车辆推力一致性

Wang 喷流轮廓仅在触地前作为平台外载荷，510 s 后截断。车辆接近速度仍为 prescribed 5 m/s，且不求解对应发动机推力和 GNC。正文现明确该边界，不再暗示模拟了完整动力下降。

### Yang 参数辨识

新增 128 次 multi-start。128 次均成功，127 次落在最优目标 1% 以内，且多组参数相关系数绝对值大于 0.98。Figure S1 给出奇异值和相关矩阵；Figure 3 给出近最优响应包络。结论改为 practical non-identifiability，不再使用 validated parameter set。

### 文献与行文

Yang 文献已改为 Transactions of Nanjing University of Aeronautics and Astronautics, 43(2), 238-250，DOI 保持 10.16356/j.1005-1120.2026.02.006。Yue DOI 已补齐。Xie 的表述收缩为“采用辐射记忆平台模型并与试验运动响应比较”。Introduction 的创新点集中在局部甲板运动、独立四足状态和返回平台的接触力矩，不再以三个软件名称的组合充当理论贡献。

## 四、图件修改

Figure 1 明确三通道反馈和受约束水平自由度。Figure 2 区分实际四足和 generic deck probes。原 Figure 3 甲板滤波重构移到 Supplementary Figure S2。Figure 3 现在是 Yang 对照与不确定性包络。Figure 4 增加网格失败、有限截断 A-infinity 和记忆核回代。Figure 5 使用 1000 realizations、bootstrap 区间、实际四足、时长敏感性及线性失效叉号。Figure 6 同时展示四足状态、同一平台响应、固定点迭代、时间步和接触刚度敏感性。

全部图件由 `yang_2026_figures.py` 从机器结果生成，使用 SciencePlots、Times New Roman、600 dpi PNG 和可编辑 SVG。研究完整性文档锁定每张图的数据来源、像素尺寸和 SHA-256。

## 五、修订后的结论尺度

修订稿不再声称获得全尺寸支腿设计载荷、着陆成功率或允许海况。能够支持的结论是：局部甲板运动与平台参考点运动存在可计算差异；四足顺序接触会形成位置相关力矩；同一平台算子上的 selected-channel fixed-point feedback 可以收敛；公开试验曲线不足以唯一辨识着陆机构。水动力网格、强海况线性适用性、局部接触收敛和稳定站立均保留为未解决问题。

## 六、随修订稿提供的证据文件

| 文件 | 内容 |
|---|---|
| `manuscript.md` | 重写后的投稿正文 |
| `RESEARCH_INTEGRITY_AUDIT_CN.md` | 数值、文件、图件和限制的机器生成审查 |
| `research-integrity-audit.json` | 完整机器可读证据链与哈希 |
| `barge-hydrodynamic-convergence.json` | 三层网格、频率、A-infinity 和 IRF 检查 |
| `wave-sensitivity-revision-600s.json` | 63 工况、每工况 1000 realizations 和 bootstrap |
| `wave-duration-sensitivity.json` | 600/1200/1800 s 时长敏感性 |
| `yang-2026-identifiability-report.json` | 128 次多起点与预测包络 |
| `chrono-same-platform-multibody-report.json` | 同一平台四次耦合、时间步、刚度和能量检查 |
