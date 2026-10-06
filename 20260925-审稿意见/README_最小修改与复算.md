# 候选修正与最小复算

这是2026-09-26审查生成的候选代码。原始59项测试及新增15项解析测试共74项通过。**没有运行修正后的完整PyChrono接触算例**。禁止把测试通过写成完整模型已验证。

## 1. 在副本安装，不覆盖原归档

以下示例使用Linux/macOS终端。Windows可用相同Python命令，将路径替换成实际路径。`REPO`应指向解压后直接包含`SourceCode`、`analysis`和`RocketRecoveryCases`的根目录；不是压缩包路径。

```bash
export REPO=/absolute/path/to/HAMS_working_copy
export REVIEW=/absolute/path/to/HAMS_review_20260926
python "$REVIEW/code_patch/apply_patch.py" --repo "$REPO"
# 确认全部SHA通过后才执行：
python "$REVIEW/code_patch/apply_patch.py" --repo "$REPO" --apply
```

默认仅预检。`--apply`会创建`.review_20260926_backup`，再安装三份修改模块和一份新增工具模块。哈希不符、目标新增文件已存在或备份目录已存在时停止。已有本地修改时请依据`review_candidate.patch`人工合并，不绕过哈希检查。回滚时用备份恢复三个原模块，并删除本补丁新增的`review_integrity.py`；保留本次输出供比较。

## 2. 已实现的变化

| 模块 | 修改 |
|---|---|
| `review_integrity.py` | 惯量换轴；参考构型质量/质心/惯量分配；甲板姿态与角速度；六分量守恒重采样；同点功率；全记录写出、哈希和防覆盖 |
| `chrono_leg_model.py` | 修正文献惯量轴向；甲板尺寸、高度、姿态与速度一致；新增投影法向力及脚垫运动学；保留旧Fz字段但澄清定义 |
| `chrono_two_way_recovery.py` | 修改主程序实际调用的传力函数；关于运动平台参考点组装力矩；记录源/目标冲量差 |
| `chrono_same_platform_multibody.py` | 主配置分配组合惯量；禁用错误功/能量代理；每轮保留原始节点；统一自适应反馈；独立输出目录；复用重复工况 |

并非完整重写所有旧研究分支。特别是旧的低维`chrono_revision_study`实验配置不因本补丁自动成为受审定的全尺寸接触模型。后续应以`chrono_same_platform_multibody`为论文主入口，明确其他脚本仅作历史或子模型用途。

## 3. 执行已有测试与新增测试

本次已执行环境为Python3.13.5、NumPy2.3.5。解析测试不依赖真实Chrono积分；不提供包含未知兼容组合的伪“锁定环境”。先在已有科学Python环境安装实际缺少的`numpy scipy pytest`，保存真实版本。

```bash
cd "$REPO"
export PYTHONPATH="$REPO${PYTHONPATH:+:$PYTHONPATH}"
python -m pytest analysis/rocket_recovery/test_*.py \
  "$REVIEW/code_patch/test_review_integrity.py" -q
```

预期与本次相同源码对应为74项通过。更换依赖后出现差异应记录，不应修改断言以追求通过。`CertTest/test_cert.py`是另一路水动力认证，不混入上述74项统计。

## 4. 真实PyChrono环境

官方安装页： https://api.projectchrono.org/pychrono_installation.html 。推荐独立conda环境，从`projectchrono`官方渠道选择实际可用的发行版/构建，并核对Python兼容性。归档中的旧环境提示不是已随包交付的运行环境；不要直接把提示中的版本组合当作已验证锁文件。不要安装名称相似但不是Project Chrono绑定的软件包。

在能运行原算例的作者环境优先执行本补丁，保存：

```bash
python -c "import sys,numpy; import pychrono; print(sys.version); print(numpy.__version__); print(pychrono.__file__); print(getattr(pychrono,'CHRONO_VERSION','inspect installed package metadata'))"
conda list --explicit > environment-conda-explicit.txt
python -m pip freeze > environment-pip-freeze.txt
```

非conda环境记录对应构建方式即可。环境清单不能仅包含Python库而遗漏Chrono二进制版本、安装来源和编译选项。

## 5. 最小重算顺序

```bash
cd "$REPO"
# 先检查主工况。它仍使用自适应反馈，但跳过局部收敛组：
python -m analysis.rocket_recovery.chrono_same_platform_multibody --skip-convergence \
  > chrono-main-review.log 2>&1
```

输出写到新目录`RocketRecoveryCases/Chrono_LeggedRecovery_Review20260926`。先检查质量/惯量、甲板基准、接触力符号、每轮原始历史、传递冲量和闭合状态。候选代码禁止覆盖已存在的原始文件，所以完整重算前须**重命名封存**刚完成的整个新目录，再运行：

```bash
mv RocketRecoveryCases/Chrono_LeggedRecovery_Review20260926 \
   RocketRecoveryCases/Chrono_LeggedRecovery_Review20260926_main_only
python -m analysis.rocket_recovery.chrono_same_platform_multibody \
  > chrono-complete-review.log 2>&1
```

第二条完整运行会重新执行主工况及原论文的步长/刚度组，不会把主工况检查输出假装复用为完整组。目标封存目录已存在时另用唯一名称，不覆盖。主工况20s、局部比较10s，统一最少2次、最多8次反馈及原2%阈值；各组比较相同时间窗。达到最大反馈次数未闭合即失败。

### 必须人工审查的运行结果

1. 惯量轴向正确；参考构型总质量61288kg及所声明总质心/惯量闭合。脚垫代理假设不等于真实CAD。
2. 水动力甲板120×50m、z=3m与碰撞面一致；接触正压力朝向正确，局部法向与世界Fz分列。
3. 原始时刻覆盖整个积分区间，没有只写压缩节点。新保存字段是全部**已记录**积分节点，并不保证求解器所有内部接触对信息均已输出。
4. 六分量传递冲量差在同覆盖区间内接近浮点精度；仍需检查平台步长响应精度。守恒重采样不证明功守恒。
5. 每个工况实际达到反馈标准。步长比较的力、行程、穿透、时间跨度分别报告；峰值力收敛不能替代事件时序收敛。
6. `coupling_work_audit.available=false`不是错误变成零，而是缺少独立接触对信息。不允许用null填0后宣称能量守恒。
7. 表4、图6、正文及摘要只能从同一次修正后输出生成。在真实结果产生前，不删除工作稿中的“pre-correction/pending”状态说明。

## 6. 复算本次已经执行的独立检查

这部分在**原始未打补丁副本**运行，用于重现本次审查的旧结果检查。输出选择新目录，避免覆盖交付证据。

```bash
python "$REVIEW/review_tools/run_independent_checks.py" \
  --repo /path/to/untouched_original --out /path/to/new_checks --wave-seeds 1000
```

包括三组Yang ODE、一次Y0参数拟合、旧轨迹审查、平台单侧重放及单个海况1000条记录。它不运行修正后的Chrono、不重算全部63海况、不重做128次多起点拟合。

重新编译HAMS后，在本次证据中相应算例目录的**副本**执行：

```bash
cd "$REPO/SourceCode"
make clean
make FC=gfortran MODE=repro -j1
export OMP_NUM_THREADS=2
export OPENBLAS_NUM_THREADS=1
cd /path/to/copied_evidence/fresh_cylinder
"$REPO/SourceCode/hams" > cylinder.log 2>&1
cd /path/to/copied_evidence/fresh_medium_anchors
"$REPO/SourceCode/hams" > medium_anchors.log 2>&1
python "$REVIEW/review_tools/compare_fresh_hams.py" \
  --repo /path/to/untouched_original --evidence /path/to/copied_evidence \
  --binary "$REPO/SourceCode/hams"
```

每个算例目录随包含`Input`。其中中等网格输入只保留本次五频点、七浪向；不能据此宣称细网格和完整频谱已经完成。比较程序比较Hydrostar .rao，不等同于原认证的所有输出格式。

## 7. 暂未实现/暂未关闭

真实PyChrono执行及API兼容性；接触对级独立功率/能量闭合；Cylinder基准差异归因；主峰细网格补算；FD/TD复阻抗稳态一致性；修正后图6和表4。英文全文只是诚实标明这些状态，并未用新数字填补未知结果。
