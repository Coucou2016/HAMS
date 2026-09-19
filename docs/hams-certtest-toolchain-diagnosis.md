# HAMS CertTest Toolchain Diagnosis

## Status

- Local source build: **PASS**. `SourceCode/hams.exe` was built in this workspace and all four CertTest solvers exited with code 0.
- Official benchmark reproduction: **FAIL**. Fresh local outputs do not reproduce all repository `Output_Benchmark` files within the registered tolerances.
- HAMS rocket-recovery boundary: **unchanged**. `git diff -- SourceCode` is empty.

The specialized benchmark report at `RocketRecoveryCases/Barge_120x50/validation/benchmark-regression.json` passes HywindSpar but fails Cylinder, DeepCwind, and Moonpool. The repository test script also reports failures because it treats some near-zero phase changes as ordinary scalar differences.

## Evidence

- Current compiler: MSYS2 GNU Fortran 16.1.0.
- Current GNU flags from `SourceCode/makefile`: `-O3 -march=native -mtune=native -fopenmp -fdec-math` plus runtime checks.
- Repository Windows reference build: `ifort /Qmkl /O3 ... -openmp`, using Intel Fortran and MKL.
- Benchmark history: the main benchmark was added in commit `cd30183` on 2021-05-19 and later output conventions were updated through `70283d0` on 2023-03-11.
- Repository history already records commit `4e0e49d`: matching compiler options more closely still failed the relative-error checks.
- Rebuilding benchmark-era source with the current GNU toolchain produced Cylinder results close to the current-source GNU build, so recent source changes alone do not explain the mismatch.
- Differences occur in added mass, radiation damping, excitation, and response outputs. They are not only 0/180-degree phase conventions.

The old `SourceCode/HAMS_ifort_Win.exe` was tried only as a diagnostic. It stopped with `forrtl: severe (64): input conversion error` on the current Cylinder input and produced no comparable output. It is not used by the implemented workflow.

## Claim Boundary

Safe to claim:

- HAMS compiles from source and runs locally without depending on the repository's precompiled executable.
- Cylinder, DeepCwind, HywindSpar, and Moonpool were freshly solved by the local executable.

Not safe to claim:

- Exact reproduction of the repository's old benchmark values.
- Numerical equivalence between the current GNU/OpenMP build and the undocumented Intel/MKL environment that generated the benchmarks.

Resolving the remaining difference requires the original benchmark compiler provenance or a controlled Intel oneAPI/MKL rebuild. Benchmark files, solver inputs, and tolerances must not be changed merely to obtain a passing label.
