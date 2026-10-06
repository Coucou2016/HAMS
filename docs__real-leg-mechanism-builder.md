# Chrono Real Leg Mechanism Builder Gate

- Overall status: `blocked_by_data_validation`
- Ready: `False`
- Builder mode: `strict_real_data`
- Input: `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_template.json`
- Target config: `RocketRecoveryCases/Chrono_LeggedRecovery/Input/chrono_real_leg_mechanism_config.json`
- Config written: `False`
- Generated UTC: `2026-08-01T12:51:58+00:00`

## Policy

Do not generate a runnable real-leg Chrono config unless validator.ready is true.

## Blocking Checks

| ID | Status | Evidence |
| --- | --- | --- |
| required_field_sources | **CHECK** | required=180, missing=116, blocking_source=120 |
| coordinate_system | **MISSING** | 3 coordinate-system fields are missing or blocked |
| geometry_closure | **MISSING** | 4 leg geometry checks are blocked |
| constraint_topology | **MISSING** | 24 topology fields are missing or blocked |
| body_mass_inertia | **MISSING** | 48 body-property fields are missing or blocked |
| buffer_law | **PARTIAL** | table_exists=True, blockers=2 |
| lock_hardware | **MISSING** | 3 lock fields are missing or blocked |

## Output Sections When Ready

- `coordinate_system`
- `rocket`
- `landing_conditions`
- `legs[].markers_body_frame_m`
- `legs[].joint_topology`
- `legs[].body_properties`
- `buffer_law`
- `lock_hardware`
- `source_map`
