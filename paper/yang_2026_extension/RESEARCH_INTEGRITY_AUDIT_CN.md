# 海上回收着陆论文真实性准确性与完整性审查

**审查编号：** `SeaLandingPaper-ResearchIntegrity-Audit-v2`  
**生成时间（UTC）：** `2026-09-05T07:35:59.117394+00:00`  
**机器审查结论：** `PASS_WITH_DECLARED_LIMITATIONS`

## 1. 审查原则

本审查把本项目重新计算的数据、文献对照数据和因公开资料不足而采用的代理输入分开记录。文献曲线只能作为带标签的对照或输入，不能写成本文计算结果；代理几何、数字化缓冲器曲线和数值接触参数不能用于声称复现了原作者的专有模型。任何未通过的数值判据均保留为限制，不以图形平滑或叙述判断改写为通过。

## 2. 总体结论

当前正文已切换到最新的中等网格水动力、1000 组随机波、实际 6.926 m 四足布局和同一平台四次耦合输出。旧版 1.128 m/m、1.505 m/s、2.435 m/s、2.678 MN 和 0.148 m 等数字均已移除。正文没有把计算未通过项包装为验证成功：仓库四案例认证比较出现 157 个文件级失败，水动力网格判据未通过，22 个随机波工况超出线性适用边界，接触时间步与刚度正则化未通过，526 s 时稳定站立诊断也未通过。

## 3. 关键结果与证据边界

| 项目 | 机器结果 | 正文解释 |
|---|---|---|
| 中等网格垂荡 RAO | 1.113483 m/m | 离散频率样本峰值；未称网格收敛 |
| 网格判据 | FAIL | medium-to-fine 最大选定变化 5.88%，阈值 5% |
| 随机波线性有效 | 41/63 | 失效工况不作作业海况或成功率结论 |
| 耦合迭代 | True | 四次固定点的最后一次更新满足 2% |
| 接触时间步 | False | 峰值力、行程和触地时序不同时收敛 |
| 接触载荷资格 | False | 不得作为真实型号设计载荷 |
| 稳定站立 | False | 动画只能描述当前 20 s 接触过程 |

## 4. 正文数值锁定

| 声明 | 正文字面值 | 机器值 | 来源 | 存在 |
|---|---|---|---|---|
| yang_stroke_peak | `within 4.1%` | 4.024010180541493 | `RocketRecoveryCases/Paper_Yang_2026/identified_landing_model/yang-2026-identified-landing-report.json` | 是 |
| yang_near_optimal | `127 of 128` | [127, 128] | `RocketRecoveryCases/Paper_Yang_2026/identified_landing_model/yang-2026-identifiability-report.json` | 是 |
| medium_heave_rao | `1.113 m/m` | 1.113483 | `RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/deck-point-rao-medium.json` | 是 |
| mesh_medium_fine | `5.88%` | 5.879837438854719 | `RocketRecoveryCases/Barge_120x50/validation/barge-hydrodynamic-convergence.json` | 是 |
| center_p95 | `1.570 m/s` | 1.570142137428662 | `RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/wave-sensitivity-revision-600s.json` | 是 |
| actual_feet_p95 | `1.591 m/s` | 1.5912185953541447 | `RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/wave-sensitivity-revision-600s.json` | 是 |
| valid_cases | `41 of 63` | [41, 63] | `RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/wave-sensitivity-revision-600s.json` | 是 |
| touchdown_span_production | `0.229 s` | 0.228999999999985 | `RocketRecoveryCases/Chrono_LeggedRecovery/chrono-same-platform-multibody-report.json` | 是 |
| production_peak_force | `5.006 MN` | 5.006461513957208 | `RocketRecoveryCases/Chrono_LeggedRecovery/chrono-same-platform-multibody-report.json` | 是 |
| platform_energy_residual | `-6.43e-6` | -6.432821992171707e-06 | `RocketRecoveryCases/Chrono_LeggedRecovery/chrono-same-platform-multibody-report.json` | 是 |
| cert_file_failures | `157 file-level failures` | {"Cylinder": 65, "DeepCwind": 13, "HywindSpar": 7, "Moonpool": 72} | `analysis/diagnostics/hams-cert-root-cause.json` | 是 |

## 5. 文件溯源

| 文件 | 类别 | 用途 | 存在 | SHA-256 前缀 |
|---|---|---|---|---|
| `新论文参考写作论文/Analysis+of+Sea-Based+Landing+Dynamics+of+Reusable+Landing+Vehicle+Considering+Mechanism+Flexibility.pdf` | reference_source | Yang et al. paper | 是 | e7949d55dea5a5d9 |
| `新论文参考写作论文/Analysis+of+Sea-Based+Landing+Dynamics+of+Reusable+Landing+Vehicle+Considering+Mechanism+Flexibility.md` | reference_source | Yang et al. extracted text | 是 | 3939e6f442f1738d |
| `海上平台火箭回收文献/065002_1_2.0002061.pdf` | reference_source | Nargolkar and Vijayan paper | 是 | f9ba2eb6197a8ad7 |
| `海上平台火箭回收文献/P3_Thies_2022.pdf` | reference_source | Thies landing-leg paper | 是 | 98d22ac4d4995872 |
| `海上平台火箭回收文献/P2_WangZhi_2023_ShipSciTech.pdf` | reference_source | Wang plume/platform paper | 是 | afd1269bd8d00a75 |
| `RocketRecoveryCases/Paper_Yang_2026/reference/digitized/yang-2026-fig09-11-digitization.json` | reference_target | Digitized published test traces | 是 | 309fb9da09933f8c |
| `RocketRecoveryCases/Chrono_LeggedRecovery/validation/thies_absorber_curves/thies-buffer-curves.json` | reference_target | Digitized absorber curves and axis calibration | 是 | e4971045da507e89 |
| `RocketRecoveryCases/Barge_120x50/platform_config.json` | present_input | Parameterized barge input | 是 | 50f90e7fbd6f1f1b |
| `RocketRecoveryCases/Barge_120x50/validation/barge-self-check.json` | present_calculation | Analytic mesh and hydrostatic self-check | 是 | 06359d8905263bfc |
| `RocketRecoveryCases/Barge_120x50/validation/barge-hydrodynamic-convergence.json` | present_calculation | Hydrodynamic refinement, A-infinity and IRF checks | 是 | 69304f742c7bf2ca |
| `RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/deck-point-rao-medium.json` | present_calculation | Medium-grid local deck response operators | 是 | 61091ab1919a2593 |
| `RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/wave-sensitivity-revision-600s.json` | present_calculation | 1000-realization random-wave calculation | 是 | 5519de6bbc861e8c |
| `RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/wave-duration-sensitivity.json` | present_calculation | 600/1200/1800 s duration sensitivity | 是 | 4392ba5f0490553f |
| `RocketRecoveryCases/Paper_Yang_2026/identified_landing_model/yang-2026-identified-landing-report.json` | present_calculation | Reduced-model comparison | 是 | da1f143fe0d4051e |
| `RocketRecoveryCases/Paper_Yang_2026/identified_landing_model/yang-2026-identifiability-report.json` | present_calculation | 128-start identifiability analysis | 是 | 98f77e5b97f6558a |
| `RocketRecoveryCases/Chrono_LeggedRecovery/chrono-same-platform-multibody-report.json` | present_calculation_with_labelled_proxies | Same-platform four-pass multibody report | 是 | 868e066a08d712f2 |
| `RocketRecoveryCases/Chrono_LeggedRecovery/Output/RocketRecovery/chrono-same-platform-multibody-response.json` | present_calculation_with_labelled_proxies | Full same-platform response history | 是 | eb6546558296c4ee |
| `RocketRecoveryCases/Chrono_LeggedRecovery/chrono-revision-study-report.json` | present_code_verification | Independent smooth-law energy/code companion | 是 | 0954aa98bbbee771 |
| `analysis/diagnostics/hams-cert-root-cause.json` | failed_external_regression | Official four-case comparator diagnostic; no validation credit | 是 | 03d9bb625c5540f2 |
| `paper/yang_2026_extension/manuscript.md` | present_manuscript | Submission manuscript source | 是 | 83d4f469b23f9cc2 |

## 6. 图件审查

全部图件由同一脚本基于机器输出生成，采用 SciencePlots `science/no-latex` 风格、Times New Roman 字体，并同时输出 600 dpi PNG 和可编辑 SVG。文献曲线使用灰黑虚线，本文计算使用彩色实线。图形不经办公软件手工移动数据点。

| 图件 | 用途 | 像素 | TNR | SHA-256 前缀 |
|---|---|---|---|---|
| fig01-coupled-framework | Implemented theoretical data flow | 4299 x 2019 | 是 | 0bd63483100ef73a |
| fig02-barge-geometry-mesh | Present geometry and two deck-point layouts | 4029 x 2257 | 是 | 6b271ae6b1f9f857 |
| fig03-yang-identified-landing-comparison | Digitized reference versus present reduced-model calculation | 4296 x 3399 | 是 | 0a5197c871668851 |
| fig04-platform-hydrodynamic-response | Present hydrodynamic and refinement calculations | 4299 x 2799 | 是 | db83a3110b4e5a39 |
| fig05-random-wave-deck-statistics | Present 1000-realization statistics and validity flags | 4299 x 2799 | 是 | 66f2168bdcafca5c |
| fig06-partitioned-contact-feedback | Present same-platform multibody response and numerical sensitivity | 4299 x 4719 | 是 | b4d06de4475e7e77 |
| figS01-yang-identifiability | Present multi-start identifiability result | 4303 x 1869 | 是 | 495d07339611b49b |
| figS02-yang-deck-filter-reproduction | Supplementary transfer-function reconstruction | 4299 x 2769 | 是 | a68a77a375f853a7 |

## 7. 未解决问题及结论约束

| 严重度 | 项目 | 证据 | 结论约束 |
|---|---|---|---|
| high | Repository certification regression | The registered four-case comparator reports 157 failed output files (65/13/7/72 by case). | No solver-certification or hydrodynamic-benchmark pass is claimed; cause remains unresolved. |
| high | Hydrodynamic mesh refinement | Medium-to-fine maximum selected change is 5.88%, above the 5% criterion. | Medium-grid RAOs are reported as sampled case-study results, not mesh-converged predictions. |
| high | Linear free-surface validity | Only 41/63 random-wave cases pass tilt and deck-edge criteria; worst P95 tilt is 11.99 deg. | Failed conditions are screens for nonlinear analysis, not operational predictions. |
| high | Contact numerical convergence | Time-step convergence and contact-stiffness regularization both fail for local force/stroke/touchdown metrics. | No contact peak is qualified as a design load. |
| high | Stable standing | Final vertical speed and angular rate exceed the diagnostic thresholds. | The simulated interval demonstrates contact dynamics, not a completed stable landing. |
| medium | Reduced-model identifiability | 127/128 starts are near-optimal and parameters are strongly correlated. | Yang curves support response comparison, not unique physical parameter recovery. |
| medium | Horizontal platform closure | Fx, Fy and Mz are calculated but not injected because horizontal restoring is absent. | Feedback is restricted to heave, roll and pitch. |
| medium | Literature-derived full-scale inputs | Vehicle geometry and absorber curves are proxies digitized from public literature; azimuths and component inertia allocation remain declared assumptions. | The full-scale calculation is a proof of concept, not a reproduction of proprietary vehicle data. |

## 8. 可重复执行命令

```powershell
python .\analysis\rocket_recovery\barge_hydrodynamic_convergence.py --execute
python .\analysis\rocket_recovery\deck_point_rao.py --case .\RocketRecoveryCases\Barge_120x50
python .\analysis\rocket_recovery\barge_wave_sensitivity.py report
python .\analysis\rocket_recovery\barge_wave_duration_sensitivity.py report
python .\analysis\rocket_recovery\yang_2026_identifiability.py report
python .\analysis\rocket_recovery\chrono_same_platform_multibody.py report
python .\analysis\rocket_recovery\yang_2026_figures.py
python .\analysis\rocket_recovery\paper_integrity_audit.py report
```

## 9. 审查结论

`PASS_WITH_DECLARED_LIMITATIONS` 表示数字、来源、代码、图件和正文限定语之间已建立可追溯关系，不表示所有数值模型均通过验证。现阶段能够支持的是理论接口、实现可重复性、局部甲板运动机制和同一平台反馈演示；不能支持真实型号支腿载荷、着陆成功率、允许海况或全六自由度动力定位闭环。
