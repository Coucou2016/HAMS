# Nargolkar & Vijayan 2025 驳船触地耦合响应复现记录

对应论文：`海上平台火箭回收文献/065002_1_2.0002061.pdf`

## 复现目标

复现论文中 reusable launch vehicle landing on barge 的四个公开工况：

- Box Barge center landing
- Box Barge 5 m offset landing
- MARMAC 302 center landing
- MARMAC 302 30 m offset landing

实现策略与本项目火箭回收路线一致：HAMS 核心不改，只生成驳船湿表面网格并求频域水动力；触地、火箭等效梁和中心/偏心对照放在外部 Python 时域模块。

## 已采用的论文参数

几何和质量参数采用论文表 1：

- Box Barge：`L=44 m`，`B=4 m`，`depth=4 m`，`draft=2 m`，barge mass `260800 kg`，RLV mass `100000 kg`，RLV height `22 m`
- MARMAC 302：`L=91.44 m`，`B=30.48 m`，`depth=6.0198 m`，`draft=2.9718 m`，barge mass `7129486 kg`，RLV mass `20000 kg`，RLV height `40.9 m`

结构参数采用论文表 2 的 stiffness 和 equivalent mass。严格模式不按正文目标频率反算质量，因为表 2 中 Box Barge 的部分 stiffness/mass 与打印的 `10 Hz` 不一致：

- Box transverse：表中 `K=7.85e5 N/m`、`M=48.03 kg`，反推约 `20.35 Hz`，不是 `10 Hz`
- Box rotational：表中 `K=6.12e7 Nm/rad`、`M=704.47 kg`，反推约 `46.91 Hz`，不是 `10 Hz`
- MARMAC transverse/rotational/axial 与 `10/10/30 Hz` 基本一致

偏心工况采用论文表 3 的 COM 输入：

- Box offset：`COM X=1.3858 m`，`COM Z=-0.0238 m`
- MARMAC offset：`COM X=0.0839 m`，`COM Z=-0.0025 m`

## 外部耦合模型

广义坐标为：

```text
q = [barge_surge, barge_heave, barge_pitch, rlv_transverse, rlv_axial, rlv_rotation]
```

接触相对位移使用小角度线性变换：

```text
r_transverse = rlv_transverse - barge_surge - deck_z * barge_pitch
r_axial      = rlv_axial - barge_heave + offset_x * barge_pitch
r_rotation   = rlv_rotation - barge_pitch
```

写成矩阵：

```text
r = H q
K_contact_global = H.T K_contact H
```

时域方程为：

```text
(M_barge + A_inf) qdd + convolution(K_rad, qd_barge) + (K_hydro + H.T K_contact H) q = 0
```

其中 `A_inf` 用 HAMS 已计算最高频率处的 added mass 近似；`K_rad(t)` 由 HAMS 的 `WaveDamping_ij.rao` 按论文式 Ogilvie 关系生成：

```text
K_ij(t) = 2/pi integral B_ij(w) cos(w t) dw
```

代码中没有用直接历史求和，而是把余弦积分离散成状态空间记忆项：

```text
c_k_dot = v_barge - w_k s_k
s_k_dot = w_k c_k
F_memory = sum_k weight_k B(w_k) c_k
```

论文未给 structural damping、contact damping、mooring stiffness 数值，当前严格模式将这些未公开经验项设为 `0`。

## 当前对照结果

触地速度 `2.0 m/s` 下的趋势对照：

| 工况 | Barge heave peak | Barge pitch peak | RLV axial peak | RLV transverse peak | 论文趋势 |
| --- | ---: | ---: | ---: | ---: | --- |
| Box center | `1.75e-2 m` | `~0 rad` | `2.78e-2 m` | `~0 m` | 中心着陆不激发 pitch |
| Box offset 5 m | `1.71e-2 m` | `5.19e-4 rad` | `2.98e-2 m` | `1.21e-3 m` | 偏心引入 heave-pitch 和横向响应 |
| MARMAC center | `4.53e-4 m` | `~0 rad` | `1.11e-2 m` | `~0 m` | 中心着陆不激发 pitch |
| MARMAC offset 30 m | `4.53e-4 m` | `2.30e-5 rad` | `1.17e-2 m` | `9.89e-5 m` | 偏心引入 heave-pitch 和横向响应 |

MARMAC 302 的船体 heave 峰值约为 Box Barge 的 `1/39`，pitch 也低一个数量级以上。因此在相同 `Motion Scale` 下，MARMAC302 看起来明显“没那么动”是当前计算结果和论文图 10 文字解释共同支持的现象，不是坐标方向或船体姿态映射错误。

## 论文曲线叠图

当前报告页已对论文 Figure 9(a) 和 Figure 10(a) 的时间响应曲线做栅格图像数字化：

- 页面 Time Response 中，实线为本项目 HAMS/Cummins 外部时域计算结果，虚线为论文图像数字化曲线。
- 只在 `0..3 s` 对比，因为论文时间响应图的横轴范围为 `0..3 s`。
- 数字化采用手动坐标轴标定和 RGB 阈值取线；低覆盖曲线会被标记为 `low_coverage` 并跳过叠图，避免把坐标轴、图例或重叠零线误作为论文数据。
- 对通过质量检查的曲线，报告页显示 `RMSE`、论文峰值、本计算峰值和峰值比。
- 论文 Figure 9(b)/10(b) 的频域图暂不叠加论文虚线；它们是对数 y 轴、曲线接近坐标线且有明显栅格噪声。当前页面下方频谱图只显示本项目计算结果。

需要注意：这仍然不是作者原始数据文件。它是基于用户提供论文图片的可审计数字化对比，所以可以作为复现进度检查，但不应当作为最终误差认证。

## 论文数据审计

`analysis/rocket_recovery/nargolkar_2025.py report` 会从 Markdown 文件解析论文三张表并生成 `paper_audit`：

- 表 1/2/3 共 `40` 个数值对照项，当前全部 `MATCH`
- 表 2 的 stiffness/mass/frequency 内部一致性检查中，Box Barge transverse 和 rotational 为 `CHECK`
- 未公开但影响逐点复现的项被列入 `unresolved`

报告页中的 trend checks：

- Center landing keeps pitch nearly unexcited：`MATCH`
- Offset landing increases pitch and RLV transverse response：`MATCH`

## 动画解释

HTML 动画分两段：

- `t=-2..0 s`：按所选 touchdown velocity 做恒速下降的运动学预演，只用于说明火箭从上方接近甲板；论文没有给下降段 GNC/气动/推力轨迹。
- `t=0..10 s`：使用 HAMS 水动力 + 外部 Cummins 时域耦合模型求得的响应时程 `q(t)`，显示驳船 heave/pitch/surge 和 RLV transverse/axial/rotation。

页面默认不循环，播放到 `t=10 s` 停止。`Motion Scale` 是可视化放大倍率，不改变结果数据。

## 已生成文件

- 生成/仿真脚本：`analysis/rocket_recovery/nargolkar_2025.py`
- 四个 HAMS 工况：`RocketRecoveryCases/Paper_Nargolkar_2025/*`
- 完整时程结果：`RocketRecoveryCases/Paper_Nargolkar_2025/*/Output/RocketRecovery/nargolkar-touchdown-response.json`
- 汇总报告数据：`RocketRecoveryCases/Paper_Nargolkar_2025/nargolkar-2025-report-data.json`
- HTML 数据：`visualization/nargolkar-2025-data.js`
- HTML 页面：`visualization/nargolkar-2025.html`
- 论文数据审计：`RocketRecoveryCases/Paper_Nargolkar_2025/nargolkar-2025-report-data.json` 中的 `paper_audit`

## 运行命令

```powershell
python .\analysis\rocket_recovery\nargolkar_2025.py generate
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\RocketRecoveryCases\Paper_Nargolkar_2025\BoxBarge_Center
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\RocketRecoveryCases\Paper_Nargolkar_2025\BoxBarge_Offset5m
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\RocketRecoveryCases\Paper_Nargolkar_2025\MARMAC302_Center
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\RocketRecoveryCases\Paper_Nargolkar_2025\MARMAC302_Offset30m
python .\analysis\rocket_recovery\nargolkar_2025.py simulate
python .\analysis\rocket_recovery\nargolkar_2025.py report
```

打开：

```text
http://127.0.0.1:8765/nargolkar-2025.html
```

## 尚未等同于原论文的部分

- 论文未公开 MATLAB 源码、网格、触地脉冲/冲击律、mooring stiffness 和数值曲线数据；当前无法做逐点误差对比。
- `A_inf` 只能用 HAMS 当前最高频 `4.0 rad/s` 的 added mass 近似，因为论文没有给更高频截断或 `A_inf` 处理方式。
- MARMAC 302 的 trapezoidal approximation 只可由论文表 1 推断；当前用 mass-matched trapezoidal prism 生成湿表面。
- 若要进一步逼近论文图 9/10，应优先补：作者原始时程/频谱数据、作者同款 Ogilvie retardation kernel 离散方式、初始速度/冲击接触律、未公开阻尼和 mooring 输入。
