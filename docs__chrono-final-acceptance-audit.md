# Chrono/HAMS Final Acceptance Audit

- Overall status: `incomplete`
- Generated UTC: `2026-08-28T03:25:44+00:00`
- Summary: PASS `18`, PARTIAL `5`, CHECK `1`, MISSING `0`

## Requirement Results

| Group | ID | Status | Evidence | Note |
| --- | --- | --- | --- | --- |
| boundary | `hams_core_unchanged` | **PASS** | git diff -- SourceCode | Generated HAMS case outputs may be dirty; this check is limited to SourceCode. |
| boundary | `hams_official_benchmark` | **CHECK** | RocketRecoveryCases/Barge_120x50/validation/benchmark-regression.json cases=4 | The four cases were regenerated with SourceCode/hams.exe. See docs/hams-certtest-toolchain-diagnosis.md; do not relabel the recorded toolchain-sensitive failures as tolerance noise. |
| boundary | `no_commercial_required_solver` | **PASS** | Chrono reports are simulated; chrono*.py has no contact_forces() fallback. | AQWA/Adams/STAR are only mentioned as literature baselines and missing original-model data. |
| stage1 | `deck_motion_input` | **PASS** | Deck keys in Chrono report: heave_m, heave_m_s, pitch_rad, pitch_rad_s, roll_rad, roll_rad_s, surge_m, surge_m_s, sway_m, sway_m_s, yaw_rad, yaw_rad_s | DeckMotion and the leg-reaction correction are 6DOF. The Wang wave/plume baseline remains heave/roll/pitch only, so zero horizontal baseline channels are audited separately as a model limitation. |
| stage1 | `vertical_rocket_and_leg_outputs` | **PASS** | chrono-stage3-tripod-report-data.json validation.case_physical_diagnostics | This proves the Stage 3A proxy diagnostics, not a hardware-valid Adams replica. |
| stage1 | `calculated_animation` | **PASS** | visualization/chrono-stage3-lock-two-way.html + data JS + validation.animation_feedback_deck_replay + validation.chrono_time_grid | The final replay must use the plotted feedback deck and an exact endpoint-inclusive time axis; staggered decks or pre-step time labels are not accepted. |
| stage1 | `literature_scale_comparison` | **PARTIAL** | E:\Projects\20260728-HAMS\RocketRecoveryCases\Chrono_LeggedRecovery\literature-comparison-registry.json | A central registry now records pointwise Nargolkar digitized curves, Wang text indicators, Thies table/scale checks, units, extraction methods, error metrics and missing-curve gaps. Missing Wang/Thies/Yue/Li curves remain registered gaps, not reproduced claims. |
| stage2 | `generalized_force_mapping` | **PASS** | chrono-stage3-lock-two-way validation.six_dof_leg_increment | This validates six-component transfer and reciprocity; it does not imply a full 6DOF Wang wave/mooring/DP baseline. |
| stage2 | `no_force_degeneracy` | **PASS** | chrono-stage3-lock-two-way validation.rhs_composition.no_leg_degeneracy_pass |  |
| stage2 | `eccentric_response` | **PASS** | chrono-stage3-lock-two-way validation.eccentric_response |  |
| stage2 | `baseline_vs_feedback_output` | **PASS** | chrono-stage3-lock-two-way report contains baseline/with_leg_feedback/leg_induced_delta; HTML plots them. |  |
| stage2 | `loose_coupling_declared` | **PASS** | chrono-stage3-lock-two-way coupling.limitations |  |
| stage2 | `loose_coupling_fixed_point` | **PARTIAL** | chrono-stage3-lock-two-way simulations[*].validation.loose_coupling_closure_diagnostic | The published closure residual is currently pass=false; this remains honest loose coupling and is not fixed-point convergence. |
| stage2 | `time_step_convergence` | **PARTIAL** | chrono-stage3-lock-two-way validation.time_step_convergence + validation.six_dof_time_step_convergence | The current wave_port_15m half-step study fails in event-sensitive horizontal channels; this must remain visible until event localization and real horizontal restoring inputs are available. |
| stage3 | `geometric_leg_mechanism` | **PARTIAL** | Stage 3A tripod proxy passes; Stage 3B/3C diagnostics exist but fail physical checks; leg mechanism contract/import schema/import self-test/backend self-test/validation/gap tracker/request pack/request lint/builder/runtime gate define, accept, check, and block missing Adams-equivalent input fields. | This is not yet an Adams-equivalent CAD hinge/link mechanism. The request-pack lint passes and proves the .todo.csv data-acquisition package covers all strict blockers without changing model inputs. |
| stage3 | `nonlinear_buffer_interface` | **PASS** | chrono-stage3-tripod validation.nonlinear_buffer_law plus config.legs.nonlinear_buffer_law.supported_types | The table interface exists. The default active law still uses published linear k/c plus explicit hard-stop assumptions; real curve availability is audited separately. |
| stage3 | `contact_state_and_stability` | **PASS** | chrono-stage3-lock-two-way validation.contact_state_machine + lock_feedback |  |
| stage3 | `real_buffer_data` | **PARTIAL** | thies-buffer-curves.json plus chrono-stage3-thies-buffer-report-data.json | Thies 2022 Figure 4/5 curves are digitized and used in a Chrono compression_only_table buffer-law branch. The raster digitization is not original author data, and the hard stop beyond the visible curve range remains a numerical guard. |
| stage3 | `parameter_sources` | **PASS** | published=7, assumptions=11, provenance_rows=103 | Config now includes a per-parameter provenance table; rows marked as engineering assumptions or to_verify must not be treated as reproduced paper data. |
| final | `command_line_chain` | **PASS** | local-tools/Run-RocketRecoveryPipeline.ps1 plus existing generated reports and LOCAL_USAGE.md. | The audit validates the command entrypoint and artifacts; use -DryRun to inspect the full sequence without rerunning expensive simulations. |
| final | `case_artifacts` | **PASS** | chrono-stage3-lock-two-way + chrono-stage3-thies-buffer JSON/HTML, Thies curve page, literature registry and final audit page. |  |
| final | `model_realism_audit` | **PASS** | model-realism-audit.json plus model-realism-audit.html | This is an honesty gate: it can pass while still reporting PARTIAL model realism findings. |
| final | `paper_curve_metadata` | **PASS** | E:\Projects\20260728-HAMS\RocketRecoveryCases\Chrono_LeggedRecovery\literature-comparison-registry.json | Current comparison entries include source, extraction method, units and errors; missing full curves are explicit registry gaps. |
| final | `assumptions_not_claimed_as_reproduced` | **PASS** | config.parameter_audit.explicit_assumptions and report.acceptance_scope.not_claimed |  |

## Remaining Gaps

- **CHECK** `hams_official_benchmark`: The locally compiled HAMS executable reproduces the four CertTest benchmark output sets within the registered tolerances. The four cases were regenerated with SourceCode/hams.exe. See docs/hams-certtest-toolchain-diagnosis.md; do not relabel the recorded toolchain-sensitive failures as tolerance noise.
- **PARTIAL** `literature_scale_comparison`: Available Thies/Nargolkar/Wang velocity, force and displacement scales are compared. A central registry now records pointwise Nargolkar digitized curves, Wang text indicators, Thies table/scale checks, units, extraction methods, error metrics and missing-curve gaps. Missing Wang/Thies/Yue/Li curves remain registered gaps, not reproduced claims.
- **PARTIAL** `loose_coupling_fixed_point`: The partitioned Chrono/Cummins iteration publishes and satisfies an explicit reaction/deck closure residual gate. The published closure residual is currently pass=false; this remains honest loose coupling and is not fixed-point convergence.
- **PARTIAL** `time_step_convergence`: Contact, lock, and all six platform response channels satisfy the registered coarse-versus-half-step convergence gate. The current wave_port_15m half-step study fails in event-sensitive horizontal channels; this must remain visible until event localization and real horizontal restoring inputs are available.
- **PARTIAL** `geometric_leg_mechanism`: Equivalent spring-damper legs are upgraded toward geometric link mechanisms. This is not yet an Adams-equivalent CAD hinge/link mechanism. The request-pack lint passes and proves the .todo.csv data-acquisition package covers all strict blockers without changing model inputs.
- **PARTIAL** `real_buffer_data`: Real or literature-given buffer curves can be used instead of arbitrary assumptions. Thies 2022 Figure 4/5 curves are digitized and used in a Chrono compression_only_table buffer-law branch. The raster digitization is not original author data, and the hard stop beyond the visible curve range remains a numerical guard.

## Next Hardening Steps

- Replace Wang zero-filled surge/sway/yaw adapter fields with full 6DOF HAMS/Cummins platform time histories when available.
- Run local-tools/Run-RocketRecoveryPipeline.ps1 end-to-end after major model changes to refresh every artifact from source.
- Use leg_mechanism_gap_tracker.py and leg_mechanism_data_request_pack.py as the authoritative real-data punch list; fill the CSV files under RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_import_schema with CAD/Adams hinge coordinates, telescopic absorber topology, joint graph, and rod mass/inertia data, then import, validate, build, and run chrono_real_leg_mechanism_recovery.py in strict mode.
- Replace raster-digitized Thies buffer curves with original author tables or measured hydropneumatic hardware data when available.
- Use docs/literature-comparison-registry.md as the source-data punch list; digitize or obtain Wang/Thies/Yue/Li curves for point-by-point validation.
