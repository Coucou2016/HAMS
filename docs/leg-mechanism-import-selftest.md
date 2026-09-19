# Chrono Leg Mechanism Import Self-Test

- Status: `PASS`
- Generated UTC: `2026-08-01T12:10:25+00:00`
- Source category: `synthetic_test_fixture`
- Synthetic config: `RocketRecoveryCases/Chrono_LeggedRecovery/validation/synthetic_leg_import/chrono_real_leg_mechanism_config.synthetic.json`
- Production config: `RocketRecoveryCases/Chrono_LeggedRecovery/Input/chrono_real_leg_mechanism_config.json`
- Production config written by self-test: `False`

This fixture proves the importer, validator and builder code path only. It must not be used as CAD/Adams-quality leg data.

## Checks

| ID | Pass | Evidence |
| --- | --- | --- |
| `csv_import` | `True` | changes=101, output=RocketRecoveryCases/Chrono_LeggedRecovery/validation/synthetic_leg_import/leg_mechanism_data_synthetic.json |
| `synthetic_validation` | `True` | ready=True, mode=synthetic_selftest |
| `builder_nonproduction_output` | `True` | config=RocketRecoveryCases/Chrono_LeggedRecovery/validation/synthetic_leg_import/chrono_real_leg_mechanism_config.synthetic.json, production=RocketRecoveryCases/Chrono_LeggedRecovery/Input/chrono_real_leg_mechanism_config.json |

## CSV Files

- `RocketRecoveryCases/Chrono_LeggedRecovery/validation/synthetic_leg_import/csv/coordinate_system.csv`: 3 rows
- `RocketRecoveryCases/Chrono_LeggedRecovery/validation/synthetic_leg_import/csv/leg_azimuths.csv`: 4 rows
- `RocketRecoveryCases/Chrono_LeggedRecovery/validation/synthetic_leg_import/csv/marker_coordinates.csv`: 16 rows
- `RocketRecoveryCases/Chrono_LeggedRecovery/validation/synthetic_leg_import/csv/constraint_topology.csv`: 24 rows
- `RocketRecoveryCases/Chrono_LeggedRecovery/validation/synthetic_leg_import/csv/body_properties.csv`: 48 rows
- `RocketRecoveryCases/Chrono_LeggedRecovery/validation/synthetic_leg_import/csv/buffer_lock.csv`: 6 rows
