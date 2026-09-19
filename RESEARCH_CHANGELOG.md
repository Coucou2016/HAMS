# Research Change Log

## 2026-09-19 Public reproducibility snapshot

* Prepared the complete sea-landing research workspace for public cross-review in `Coucou2016/HAMS`.
* Added a repository manifest that distinguishes research evidence from replaceable workstation caches and records licensing boundaries.
* Included source, rebuilt executables, build and run logs, certification outputs, case meshes, full numerical histories, literature inputs, visualizations, paper sources, final documents, and machine-readable audits.
* Retained all known failed checks and numerical limitations instead of replacing them with qualitative pass statements.

## Work represented by this snapshot

* Rebuilt HAMS locally from source with an isolated local toolchain and documented the replay procedure.
* Regenerated the Cylinder, DeepCwind, HywindSpar, and Moonpool certification outputs and recorded the unresolved comparator failures.
* Added a parameterized 120 m by 50 m rectangular recovery-barge case, local deck-point response operators, mesh refinement checks, finite-cutoff added-mass diagnostics, and radiation-memory reconstruction.
* Added 63 JONSWAP sea-state and heading combinations with 1000 realizations per condition, bootstrap intervals, record-duration sensitivity, and a linear-validity screen.
* Implemented independent four-foot contact states, nonlinear tabulated absorbers, frictional multibody landing dynamics, action-reaction accounting, selected-channel platform feedback, and coupling-iteration diagnostics.
* Reproduced and compared published box-barge, MARMAC 302, plume-loading, and landing-mechanism results only where the source data were identifiable; digitized literature curves remain labelled reference observations.
* Reworked the paper around the governing hydrodynamic, time-domain, structural, contact, and partitioned-coupling theory rather than a chain of software product names.
* Rebuilt all paper figures with SciencePlots and Times New Roman, generated DOCX/PDF deliverables, and added a separate research-integrity audit and point-by-point reviewer response.

## Verification snapshot

* Rocket-recovery unit suite: 56 tests passed at the final paper build.
* Document package and PDF checks passed for the final manuscript, integrity audit, and reviewer response.
* The unresolved certification, mesh-refinement, contact-convergence, and stable-standing failures are listed in `RESEARCH_REPOSITORY_MANIFEST.md` and the integrity audit.
