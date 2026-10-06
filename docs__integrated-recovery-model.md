# 综合火箭海上平台着陆模型实现记录

对应入口：

- `analysis/rocket_recovery/integrated_recovery_model.py`
- `visualization/integrated-recovery.html`

## 目标

这一阶段把前三个已实现模块串成一个可运行的外部时域模型：

```text
HAMS 势流水动力
-> Cummins/Ogilvie 时域记忆力
-> Wang 2023 JONSWAP 不规则波和喷流载荷
-> Nargolkar 2025 火箭等效梁模态
-> Thies 2022 四腿触地、缓冲和接触状态
```

HAMS 核心仍不改。HAMS 只提供 heave/roll/pitch 频域水动力、静水恢复和一阶波浪激励；所有火箭、喷流、波浪合成、Cummins 记忆项和支腿接触都在外部 Python 模块完成。

## 已接入的公开数据

王智等 2023：

- 回收平台主尺度 `165 m x 40 m x draft 5 m`
- 平台质量 `22000 t`
- JONSWAP `Hs=1.75 m`、`Tp=4.5 s`、`gamma=3`
- 浪向 `135 deg`
- 喷流载荷分段时刻：`480 s` 点火、`506 s` 垂直下降、`510 s` 着陆、`511 s` 关机消散
- 喷流平台载荷 `20400 kN`

Thies 2022：

- RETALT1 着陆质量 `61288 kg`
- 名义触地垂向速度 `5 m/s`
- 触地速度包络 `1..15 m/s`
- 平台/箭体入射角包络 `0..10 deg`
- 四条着陆腿，腿长 `8.1 m`，静态腿角 `33 deg`
- 触地动能 `766 kJ`
- 参考缓冲器变形 `0.42 m`
- 参考支腿力 `902 kN`
- 参考弹簧-阻尼器力 `935 kN`

Nargolkar & Vijayan 2025：

- MARMAC 302 等效火箭轴向模态：`K=2.95e8 N/m`，`M_eq=8307.97 kg`
- 等效转动/弯曲模态：`K=1.50e6 Nm/rad`，`M_eq=381.08 kg`
- 轴向目标频率 `30 Hz`，弯曲/转动目标频率 `10 Hz`

## 当前动力学方程

平台保留三个自由度：

```text
q_p = [heave, roll, pitch]
```

平台时域方程为：

```text
(M + A_inf) qdd
+ C_linear qd
+ K_hydro q
+ F_memory(qd)
= F_wave + F_plume + F_leg
```

其中 `F_memory` 由 HAMS 辐射阻尼 `B(w)` 离散成 Ogilvie/Cummins 记忆状态：

```text
c_k_dot = qd - w_k s_k
s_k_dot = w_k c_k
F_memory = sum_k weight_k B(w_k)c_k
```

火箭刚体保留：

```text
q_r = [z_CG, roll, pitch]
```

火箭等效梁保留：

```text
q_b = [axial, flex_roll, flex_pitch]
```

四个足点采用对称方位：

```text
azimuth = [45, 135, 225, 315] deg
r_foot = 8.1 cos(33 deg) = 6.793 m
```

足端和甲板局部高度均使用小角度变换：

```text
z_deck = heave + roll*y - pitch*x
z_foot = z_CG - z_CG_from_base + axial + (roll + flex_roll)y - (pitch + flex_pitch)x
stroke = max(0, z_deck - z_foot)
```

接触力为单向压缩弹簧-阻尼模型，并用 Thies 表 8 的参考力和参考行程做限幅/硬止挡基准：

```text
F_i = k stroke_i + c stroke_rate_i,  stroke_i > 0
F_i = 0,                           stroke_i <= 0
```

代码中阻尼项用 `tanh` 平滑，避免固定步长 RK4 在接触切换瞬间出现非物理数值尖峰。

## 当前计算结果

命令：

```powershell
python .\analysis\rocket_recovery\integrated_recovery_model.py report
```

输出：

- `RocketRecoveryCases/Integrated_LeggedRecovery/Output/RocketRecovery/integrated-recovery-full.json`
- `RocketRecoveryCases/Integrated_LeggedRecovery/integrated-recovery-report-data.json`
- `visualization/integrated-recovery-data.js`

四个工况摘要：

| Case | First contact | All legs contact | Max leg force | Max stroke | Final vertical velocity | Final contacts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `calm_center` | `510.000 s` | `510.002 s` | `1870 kN` | `0.497 m` | `+2.192 m/s` | `0` |
| `wave_center` | `510.000 s` | `510.008 s` | `1870 kN` | `0.506 m` | `-1.045 m/s` | `0` |
| `wave_bow_15m` | `510.000 s` | `510.014 s` | `1870 kN` | `0.509 m` | `-2.311 m/s` | `2` |
| `wave_port_15m` | `510.000 s` | `510.010 s` | `1870 kN` | `0.515 m` | `-0.346 m/s` | `4` |

这个结果说明：当前降阶接触模型已经能显示四腿依次触地、缓冲压缩、反弹/再接触和平台反馈；但它还没有着陆锁紧、主动 GNC、真实侧向摩擦和真实非线性缓冲器，所以多数工况不会自然稳定停放。动画中的持续振荡或反弹不是浏览器动画循环伪造，而是当前方程积分出来的时域状态。

## 文献对照

| 指标 | 文献值 | 当前计算 | 说明 |
| --- | ---: | ---: | --- |
| Thies 触地动能 | `766 kJ` | `766.1 kJ` | 由公开质量和 `5 m/s` 直接复算 |
| Thies 缓冲器变形 | `0.42 m` | `0.506 m` | 不同平台和降阶接触律，只做量级/趋势对照 |
| Thies 支腿力 | `902 kN` | `1870 kN` | 当前使用参考力限幅和硬止挡，不是 Adams 逐点复现 |
| Wang 波浪 + 船长偏心 pitch peak | `0.267 deg` | `0.165 deg` | 综合模型包含 510 s 后火箭接触反馈，不等同 Wang 平台单向载荷模型 |
| Wang 波浪 + 船宽偏心 roll peak | `2.898 deg` | `2.139 deg` | 数量级和趋势一致，仍受 AQWA/STAR 缺参限制 |

## 可视化

打开：

```text
http://127.0.0.1:8765/integrated-recovery.html
```

页面包含：

- 船体网格、甲板、火箭本体、四条支腿和四个足垫
- 接触足垫颜色状态
- `506..526 s` 动画时间轴
- 平台 heave/roll/pitch、火箭 CG 高度、垂向速度、总接触力、单腿接触力、缓冲器行程、梁模态响应曲线
- 与 Wang/Thies 公开指标的同页对照表
- 已实现模块和公开缺参清单

## 不能伪造的缺口

下面这些不是代码工作量问题，而是公开文件没有给出可唯一确定的数据：

- Wang 2023 的 STAR-CCM+ 喷流高分辨率时历数据
- Wang 2023 的 AQWA 工程、二阶波浪力和完整悬链线系泊参数
- Thies 2022 的 MSC Adams 模型、四腿精确方位、关节约束、真实非线性力-行程/力-速度表
- 触地后的火箭主动控制、发动机关机策略、着陆锁紧和侧向摩擦模型

因此当前应表述为：

```text
开源 HAMS/Cummins 外部综合模型已经实现；
能和公开文献指标做数量级/趋势对照；
但还不是商业软件原模型或实验数据的逐点复现。
```
