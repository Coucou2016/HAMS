# Research Repository Manifest

This document describes the public reproducibility snapshot maintained in the `Coucou2016/HAMS` fork. Its purpose is to let another researcher or software agent inspect the complete evidence chain without relying on the original workstation.

## Included content

The commit includes all project-relevant files currently present in the workspace:

* `SourceCode`, `Compiling`, `MeshConverter`, `local-tools`, `Bin`: solver source, local build wrappers, compiler inputs, and rebuilt executables.
* `CertTest`: the four official certification cases, regenerated outputs, benchmark files, comparator, and the retained failed-comparison evidence.
* `analysis/rocket_recovery`: hydrodynamic convergence, deck-point transformation, stochastic-wave synthesis, time-domain radiation memory, landing-model identification, multibody coupling, figure generation, and tests.
* `RocketRecoveryCases`: case inputs, meshes, full result histories, JSON reports, validation records, and progress logs.
* `paper/yang_2026_extension`: manuscript sources, final DOCX/PDF files, reviewer response, integrity audit, figures, and document QA outputs.
* `visualization`: self-contained HTML/JavaScript reports, generated data, Three.js dependencies, and reviewed screenshots.
* `HAMS_papers`, `海上平台火箭回收文献`, `新论文参考写作论文`: the literature archive used during the study, including the supplied PDFs and Markdown extractions.
* `build-logs`, `.diagnostics`, `docs`, `tmp`: build/run logs, diagnostic reproductions, supporting notes, and retained extraction intermediates.

## Deliberate exclusions

The following workstation-only files are not versioned:

* `.tools` and `.conda-pkgs`: approximately 4.9 GB of downloaded compilers, Python/Conda environments, package caches, certificate bundles, and package-manager key material. These are replaceable dependencies and include machine-local private-key files that must not be published.
* `__pycache__`, `.pytest_cache`, `*.pyc`, `*.o`, and `*.mod`: interpreter and compiler caches that can be regenerated from the tracked source.
* `.git` and editor-specific state: repository metadata and user-specific IDE files.

The exclusions do not remove research inputs, source code, numerical outputs, figures, build logs, or manuscript evidence. Environment reconstruction is documented in `BUILD_REPLAY.md`, `LOCAL_USAGE.md`, and the requirements files under `paper/yang_2026_extension`.

## Large-file policy

The research snapshot is intentionally stored as ordinary Git objects so agents and reviewers can access files through standard Git and raw GitHub URLs without a Git LFS client. The largest included files are below GitHub's 100 MiB hard limit. GitHub may warn for files above 50 MiB; those warnings are expected for the full stochastic and reproduction JSON records.

## Verification status

The repository records both passing and failing checks. Passing unit tests, action-reaction and energy balances, fixed-point coupling checks, and document integrity checks are retained. The following limitations are not converted into passes:

* the repository certification comparison reports 157 file-level failures;
* the medium-to-fine hydrodynamic refinement change is 5.88%, above the 5% criterion;
* severe random-wave cases exceed the stated linear free-surface validity screen;
* local contact force, stroke, and touchdown timing do not pass all time-step and stiffness checks;
* the simulated interval does not satisfy the declared stable-standing condition.

See `paper/yang_2026_extension/Research_Integrity_Audit_CN_TheoryFramework.pdf` and the machine-readable JSON reports for the precise evidence and claim boundaries.

## Licensing note

The original HAMS source retains its Apache-2.0 license and attribution. Third-party papers, extracted literature, bundled JavaScript libraries, and other reference assets retain their own licenses and copyrights. Inclusion for reproducibility does not relicense those materials.
