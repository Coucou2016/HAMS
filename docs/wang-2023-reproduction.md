# 王智等 2023 喷流-波浪-平台响应复现记录

对应论文：`海上平台火箭回收文献/P2_WangZhi_2023_ShipSciTech.pdf`

## 复现目标

这一步用于推进第二阶段：

```text
Nargolkar 水动力-结构触地基准
-> 王智 2023 JONSWAP 波浪 + 喷流载荷 + 平台 heave/roll/pitch 响应
-> 后续再接 Thies/Yue 四腿接触与缓冲器
```

当前仍不改 HAMS 核心。HAMS 只提供势流频域附加质量、辐射阻尼和一阶波浪激励；喷流载荷、JONSWAP 不规则波和 Cummins 时域响应在 `analysis/rocket_recovery/wang_2023.py` 外部完成。

## 已采用的论文公开参数

船体表 1：

- 总长 `165.0 m`
- 型宽 `40.0 m`
- 设计吃水 `5.0 m`
- 载重量/质量输入 `22000 t`
- 重心位置 `(70.5, 0, -2.32) m`
- 惯性半径：roll `13.5 m`，pitch `38.8 m`，yaw `40.3 m`

系泊与海况：

- 4 根悬链线系泊缆，对称 45 deg 布置
- 每根缆长 `820 m`
- JONSWAP 谱：`Hs=1.75 m`，`Tp=4.5 s`，`gamma=3`
- 浪向 `135 deg`

喷流载荷：

- 480 s 着陆点火
- 506 s 进入垂直下降
- 510 s 着陆
- 511 s 关机载荷消散
- 载荷平台值约 `20400 kN`
- 分段表达式采用论文式 (7)；其中 `506..510 s` 的 `Fp` 没有机器可读数据，当前按论文文字用 `20400 kN` 平台值表示，不加入人为振荡。

## 当前模型

广义坐标为：

```text
q = [heave, roll, pitch]
```

外部时域方程为：

```text
(M + A_inf) qdd
+ C qd
+ K_hydro q
+ integral K_rad(t-tau) qd(tau) dtau
= F_wave(t) + F_plume(t)
```

喷流在落点 `(x, y)` 处对平台施加：

```text
Fz = -F_T
Mx = y Fz
My = -x Fz
```

不规则波通过 HAMS `Excitation_3/4/5.rao` 和 JONSWAP 谱合成一条确定性时历，随机相位种子固定为 `2023`，保证可复算。

## 当前对照结果

| 论文指标 | 论文值 | 当前 HAMS/Cummins 值 | 相对误差 |
| --- | ---: | ---: | ---: |
| 静水，沿船长 15 m 偏心，pitch peak | `0.25 deg` | `0.124 deg` | `50.6%` |
| 静水，沿船宽 15 m 偏心，roll peak | `2.858 deg` | `2.056 deg` | `28.1%` |
| 波浪，沿船长 15 m 偏心，pitch peak | `0.267 deg` | `0.165 deg` | `38.2%` |
| 波浪，沿船宽 15 m 偏心，roll peak | `2.898 deg` | `2.139 deg` | `26.2%` |
| 波浪，中心喷流对 heave 的影响 | `0.41 m` | `0.321 m` | `21.8%` |

结论：当前结果与论文在数量级和趋势上对齐，但还不是 AQWA/STAR-CCM+ 原模型逐点复现。

## 为什么还不能完全一致

- 论文未公开 AQWA 船体面元和真实 hull offsets；当前用公开主尺度和质量匹配梯形湿表面重新生成 HAMS 网格。
- 论文 AQWA 面元数为 `13367`，当前 HAMS 湿表面为 `1292` 面元，优先保证本机可快速复算。
- 论文有二阶波浪力，当前只用 HAMS 一阶波浪激励。
- 论文有悬链线系泊，但没有缆径、湿重、轴向刚度、锚点、导缆孔、预张力等参数；当前不插入伪造的线性系泊刚度。
- 论文 Figure 6 的 CFD 喷流振荡曲线没有机器可读数据；当前中段采用论文文字给出的 `20400 kN` 平台载荷。

## 已生成文件

- 脚本：`analysis/rocket_recovery/wang_2023.py`
- HAMS 工况：`RocketRecoveryCases/Paper_WangZhi_2023`
- 完整时程：`RocketRecoveryCases/Paper_WangZhi_2023/Output/RocketRecovery/wang-2023-response.json`
- 报告数据：`RocketRecoveryCases/Paper_WangZhi_2023/wang-2023-report-data.json`
- HTML 数据：`visualization/wang-2023-data.js`
- HTML 页面：`visualization/wang-2023.html`

## 运行命令

```powershell
python .\analysis\rocket_recovery\wang_2023.py generate
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\RocketRecoveryCases\Paper_WangZhi_2023
python .\analysis\rocket_recovery\wang_2023.py simulate
python .\analysis\rocket_recovery\wang_2023.py report
```

打开：

```text
http://127.0.0.1:8765/wang-2023.html
```
