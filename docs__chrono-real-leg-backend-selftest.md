# Chrono Real-Leg Backend Synthetic Self-Test

- Status: `PASS`
- Config: `RocketRecoveryCases/Chrono_LeggedRecovery/validation/synthetic_leg_import/chrono_real_leg_mechanism_config.synthetic.json`
- Generated UTC: `2026-08-01T12:33:04+00:00`
- Synthetic only: `True`

This smoke test proves that the real-config schema can instantiate PyChrono bodies, spherical mates and absorber links. It does not solve a landing trajectory and does not validate Adams equivalence.

## Backend Result

- Pass: `True`
- Stage: `chrono_smoke_assembly`
- Created bodies: `18`
- Created links: `28`
- Unsupported items: `0`

## Manifest

- Legs: `4`
- Bodies: `16`
- Joints: `24`
- Force elements: `4`
