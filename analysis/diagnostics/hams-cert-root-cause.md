# HAMS CertTest root-cause diagnostic

Generated (UTC): `2026-09-04T06:34:45.258250+00:00`
Git HEAD: `` on ``

## Evidence

- The comparison uses the already registered `CertTest/test_cert.py` tolerances: `rel_tol=0.1` and `abs_tol=1e-07`.
- This report is read-only with respect to HAMS source, inputs, benchmarks, and case outputs.
- A raw Windows CRLF hash difference is not treated as an input change; Git semantic diff is the authority.

### Source and benchmark history

```text
```

Source files changed from `70283d0` to HEAD:


### Case results

| Case | Files | Failed files | Numeric mismatches | Text mismatches |
|---|---:|---:|---:|---:|
| Cylinder | 108 | 65 | 9387 | 0 |
| DeepCwind | 108 | 13 | 54 | 0 |
| HywindSpar | 108 | 7 | 10 | 0 |
| Moonpool | 108 | 72 | 2618 | 0 |

### Build provenance

- Build script: `local-tools\Build-HAMS.ps1`
- Makefile: `SourceCode\makefile`
- Local executable PE timestamp: `unavailable`
- Repository ifort executable PE timestamp: `unavailable`

### Diagnostic outputs

- `.diagnostics\cert-cylinder-compare-20260815-210608\gfortran\Output`: benchmark failed files `108` / `108`, same bytes as current Cylinder Output: `False`.
- `.diagnostics\cert-cylinder-compare-20260815-210631\gfortran\Output`: benchmark failed files `65` / `108`, same bytes as current Cylinder Output: `True`.
- `.diagnostics\cert-cylinder-threads1-correct-20260815-212114\Output`: benchmark failed files `65` / `108`, same bytes as current Cylinder Output: `True`.
- `.diagnostics\hams-70283d0-cylinder-20260815-211309\Output`: benchmark failed files `65` / `108`, same bytes as current Cylinder Output: `True`.

## Interpretation

The report deliberately does not convert a failed benchmark into PASS. Use the evidence above to distinguish compiler/flags and benchmark provenance from input or working-directory errors.
