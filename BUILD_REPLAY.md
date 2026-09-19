# HAMS build replay

日期：2026-07-28  
路径：`E:\Projects\20260728-HAMS`

## 实际搭建的本地环境

- 本地 MSYS2：`.tools\msys64`
- Fortran 编译器：GNU Fortran 16.1.0, MSYS2 MinGW64
- 构建工具：GNU Make 4.4.1
- 数值库：MSYS2 MinGW64 `liblapack` / `libblas`
- Python：`E:\Miniconda3\python.exe`
- 可视化：项目内 `visualization\viewer.html`，本地 vendored Three.js r128，另有 matplotlib PNG 快照

## 关键修正

1. `SourceCode\makefile` 保持仓库原样；`local-tools\Build-HAMS.ps1` 显式调用 `make OS=Windows_NT FC=gfortran`，让 MSYS2 bash 进入原 makefile 已有的 Windows 分支并生成 `libhams.dll`。
2. 该 E 盘文件系统对 MSYS2 某些链接创建不完整，`ld.exe` 缺失但 `ld.bfd.exe` 存在。`local-tools\Build-HAMS.ps1` 会在本地 `.tools` 内自动复制 `ld.bfd.exe` 为 `ld.exe`。
3. `local-tools\Run-HAMS.ps1` 已改为默认运行 `SourceCode\hams.exe`，不再默认使用 `Bin\HAMS_x64.exe`。

## 复盘命令

重新编译：

```powershell
cd E:\Projects\20260728-HAMS
powershell -ExecutionPolicy Bypass -File .\local-tools\Build-HAMS.ps1
```

运行两个已验证案例：

```powershell
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\CertTest\Cylinder
powershell -ExecutionPolicy Bypass -File .\local-tools\Run-HAMS.ps1 -CaseDir .\CertTest\DeepCwind
```

两次运行均完成并输出：

```text
Congratulations! Your computation completes successfully.
```

## 可视化复盘

生成可视化数据和 PNG：

```powershell
python .\visualization\generate_mesh_viewer.py
python .\visualization\render_mesh_snapshots.py
python .\visualization\generate_case_reports.py
```

启动本地交互式查看器：

```powershell
cd E:\Projects\20260728-HAMS\visualization
python -m http.server 8765 --bind 127.0.0.1
```

查看器地址：

```text
http://127.0.0.1:8765/viewer.html
http://127.0.0.1:8765/results.html
```

静态快照：

```text
visualization\snapshots\hams-mesh-overview.png
visualization\snapshots\cylinder-mesh.png
visualization\snapshots\deepcwind-mesh.png
visualization\snapshots\hywindspar-mesh.png
visualization\snapshots\moonpool-mesh.png
```

结果页当前包含两个完整运行过的案例：`Cylinder` 和 `DeepCwind`。页面读取各自 `Output\Hydrostar_format` 下的 `.rao` 文件，按浪向展示 Added Mass、Radiation Damping、Wave Excitation 和 Motion RAO。

## 回归检查说明

仓库自带 `CertTest\test_cert.py` 在当前 Python 版本下会因为 `unittest.makeSuite` 不存在而失败。使用兼容脚本做 NaN 处理后，输出文件能够生成，但新编译版与仓库基准并非逐项完全一致，部分数值超过仓库脚本中近似比较的 10% 相对容差。这个差异需要按编译器、优化参数和 HAMS 数值设置进一步分析；不影响本次确认的“本机源码编译成功并能运行案例”。

2026-08-15 已完成四个案例的全量本机重算和工具链追查。详细证据、可声明范围和未通过结论见 `docs/hams-certtest-toolchain-diagnosis.md`。
