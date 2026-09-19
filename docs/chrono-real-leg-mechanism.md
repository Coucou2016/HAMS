# Chrono Real Landing-Leg Mechanism Runtime Gate

- Overall status: `blocked_missing_real_config`
- Status: `blocked`
- Ready for Chrono runtime: `False`
- Config: `RocketRecoveryCases/Chrono_LeggedRecovery/Input/chrono_real_leg_mechanism_config.json`
- Generated UTC: `2026-08-01T12:52:00+00:00`

## Policy

- Reject synthetic fixtures.
- Reject proxy fallback.
- Require Project Chrono.
- Keep HAMS as the hydrodynamic/Cummins provider only.
- Use chrono_real_leg_backend.py for config-defined body/joint/link assembly when strict real data exists.

## Blockers

| ID | Status | Evidence |
| --- | --- | --- |
| `missing_real_config` | **MISSING** | RocketRecoveryCases/Chrono_LeggedRecovery/Input/chrono_real_leg_mechanism_config.json does not exist. |

## Assembly Plan

No assembly plan is emitted until a real config exists and passes the strict source gate.
