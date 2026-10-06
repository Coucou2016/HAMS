# Chrono Real Leg Mechanism Data Request Pack

- Overall status: `todo_pack_written_no_model_data_changed`
- Generated UTC: `2026-08-01T13:01:34+00:00`
- Request dir: `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack`
- Strict blocking fields covered: `120`

## Files

| File | Rows | Purpose |
| --- | ---: | --- |
| `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack/field_tasks.csv` | 120 | Master task list for every strict blocking field. |
| `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack/coordinate_system.todo.csv` | 3 | Fill with rocket/deck frame metadata, then copy validated rows into coordinate_system.csv. |
| `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack/leg_azimuths.todo.csv` | 4 | Fill with real four-leg azimuths. |
| `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack/marker_coordinates.todo.csv` | 16 | Fill with B/T/K/P marker coordinates from one declared frame. |
| `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack/constraint_topology.todo.csv` | 24 | Fill with joint types, axes, limits, and slider definitions. |
| `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack/body_properties.todo.csv` | 48 | Fill with CAD mass, COM, and inertia tensors. |
| `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack/buffer_lock.todo.csv` | 5 | Fill with absorber stroke/rebound behavior and lock hardware data. |
| `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack/field_tasks.jsonl` | 120 | Line-delimited machine-readable copy of the master task list. |
| `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack/README.md` |  | Human instructions for using the request pack. |

## Field Classes

| Class | Count |
| --- | ---: |
| `azimuths` | 4 |
| `body_properties` | 48 |
| `buffer_lock` | 5 |
| `constraint_topology` | 24 |
| `coordinate_system` | 3 |
| `marker_coordinates` | 36 |

## Guardrails

- The .todo.csv files are intentionally not named like importer inputs.
- Blank or synthetic source tags must not pass strict validation.
- Current papers provide scale checks, not source-ready CAD/Adams hinge and mass-property data.

## Commands After Filling Real Data

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_importer.py import --source-dir .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_import_schema
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_validator.py report --input .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_data_imported.json
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\real_leg_mechanism_builder.py report --input .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_data_imported.json
```
