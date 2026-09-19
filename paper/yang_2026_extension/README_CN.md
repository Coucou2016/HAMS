# 杨少斐 2026 主参考论文复现说明

## 当前定位

本目录用于形成英文论文：

> Open-source Coupled Hydrodynamic-Multibody Simulation of Four-Leg Reusable Launch Vehicle Landing on a Floating Barge

主参考是杨少斐等 2026 年《考虑机构柔性的可重复使用运载器海上着陆动力学分析》。水动力与冲击平台验证分别参考 Nargolkar 2025、王智 2023 和 Xie 2025，四腿接触验证补充参考 Yue 2022 和 Thies 2022。

## 已完成且可复算

1. 杨论文 Table 1、Table 2、海上工况、设计限值和甲板滤波器已经转成机器可读 JSON。
2. 油液阻尼、气体弹簧、机械限位和足垫法向接触公式已经直接编码并有单元测试。
3. 杨论文 Figure 9-11 的 9 条红色试验曲线已经从 PDF 原页数字化为 CSV。
4. 数字化数据保留 PDF 页码、160 dpi 渲染信息、像素坐标框、源图 SHA-256 和曲线颜色规则。
5. 杨论文海况 5 的 heave/pitch 传递函数已经实现，可用固定白噪声定义和随机种子生成可复算的新时历。
6. 七组论文图由代码生成，不使用手工修改的数据副本。
7. 杨论文证据已经并入全项目文献对比注册表。
8. 已建立公开两自由度四腿辨识模型：仅用同时触地工况拟合，以冻结参数预测 1-2-1 和 2-2。
9. 三种触地顺序均正确产生；三组行程峰值误差不超过 4.0%，载荷峰值误差为 6.7% 到 18.7%。
10. 加速度峰值仍低估 29.2% 到 51.9%，严格曲线验收为 `PARTIAL`；正文已如实写入这一结果。
11. 已完成 9 个 JONSWAP 海况、7 个浪向、5 个甲板点、每组合 100 个 600 s 随机相位种子的 HAMS 甲板运动统计；该层明确限定为线性波频筛选，不冒充耦合着陆成功概率。

## 已发现的原论文数据问题

- 公式 (11) 印刷为 `H = v/(2g)`，量纲不成立；物理上应为 `H = v^2/(2g)`。
- Table 2 的 1-2-1 试验主支柱载荷印刷为 `0.115 x 10^5 N`，与同表模型值和百分比不相容。
- Table 2 若干印刷误差百分比不能由表内模型值和试验值重新计算得到。
- 由印刷标量计算，海上相对陆上 1-2-1 工况的增幅为：加速度约 16.26%、主支柱载荷约 12.18%、行程约 12.76%。正文和结论对 12.3%/12.8% 的指标归属存在不一致。

上述问题均保留原始值和审计结果，不静默修正。

## 尚未完成，禁止提前宣称

1. 尚未形成杨论文 ADAMS/Abaqus 模型的等价 Chrono 复现；原文缺少完整几何、惯量、关节、缓冲器和柔性模态数据。
2. 当前辨识模型是公开降阶模型，不是未公开机构的反演复制品；观测映射系数不得解释为真实连杆传动比。
3. 尚未将杨 5.2 t 基准模型接入 HAMS/Cummins 双向平台反馈。
4. HAMS 官方旧 benchmark 在当前 GNU 构建下只有 HywindSpar 完整通过，其余算例存在编译器/数值结果差异，不能写成官方回归全部通过。
5. 当前带锁紧代理的 Chrono 分支接触力和行程尚未满足半步长收敛；不带锁紧的 Stage 3 双向分支更稳定，应作为论文数值主线。
6. 当前松耦合最终回放未达到固定点闭合，不能宣称强耦合收敛。
7. Figure 17 的白噪声归一化和随机种子未公开，不能宣称逐点复现原随机时历。

## 一键复盘

在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-Yang2026-PaperPipeline.ps1
```

该命令依次完成：

- 公开数据和算术审计；
- 甲板滤波器确定性时历生成；
- PDF 第 7 页重新渲染；
- Figure 9-11 曲线数字化；
- 同时触地辨识及冻结参数预测；
- 论文图生成；
- 文献注册表更新；
- HAMS/Chrono 基础工具与杨模块单元测试。

生成论文 DOCX、PDF 并刷新真实性与总验收审计：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Build-SeaLanding-Paper.ps1
```

默认复用已经完成的 HAMS/Cummins/Chrono 计算，只重算杨论文证据链、图表和审计。需要从 HAMS 编译与各动力学算例开始重新计算时，显式增加 `-FullRecompute`；该模式运行时间明显更长。

## 关键输出

- `manuscript.md`：英文论文唯一正文源。
- `Coupled_Hydrodynamic_FourLeg_Sea_Landing_Manuscript.docx`：由正文源和代码图表自动生成的 Word 工作稿。
- `Coupled_Hydrodynamic_FourLeg_Sea_Landing_Manuscript.pdf`：经 Microsoft Word 固定格式导出的版面审阅稿。
- `Research_Integrity_Audit_CN_TheoryFramework.docx/.pdf`：独立真实性、准确性、完整性审查文档；其中保留实现软件与代理参数的可追溯记录，但不把软件组合写作论文理论框架。
- `figures/`：代码生成的 PNG/SVG 论文图。
- `../../RocketRecoveryCases/Paper_Yang_2026/reference/yang-2026-published.json`：公开数据原始登记。
- `../../RocketRecoveryCases/Paper_Yang_2026/yang-2026-evidence-report.json`：数据一致性和甲板滤波报告。
- `../../RocketRecoveryCases/Paper_Yang_2026/reference/digitized/`：数字化 CSV 和元数据。
- `../../RocketRecoveryCases/Paper_Yang_2026/identified_landing_model/`：辨识报告和三工况逐点 CSV。
- `../../RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/wave-sensitivity.json`：HAMS 甲板点随机波统计完整样本与分位数。
- `../../RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/wave-sensitivity-summary.csv`：63 个海况-浪向组合的统计汇总。
- `IMPLEMENTATION_PLAN_CN.md`：论文落地路线、验收条件和声明边界。

## 下一实施门

下一阶段将公开辨识模型作为基准观测层接入 Chrono。先使用无锁紧分支完成接触时步收敛，再接入 HAMS/Cummins 固定点迭代。任何无法从论文获得的几何或机构参数继续保持 `identified`/`proxy` 标签，不用于 Adams 等价性声明。
