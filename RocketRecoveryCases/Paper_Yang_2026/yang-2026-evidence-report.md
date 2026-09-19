# Yang et al. 2026 Evidence Audit

- DOI: `10.16356/j.1005-1120.2026.02.006`
- Table 2 rows: 9
- Strict rows internally consistent: 4/5
- Physics-consistent drop height at 2 m/s: 0.203943 m
- Value from printed Equation 11: 0.101972 m

## Sea-case arithmetic

- Acceleration increase from published 1-2-1 flexible baseline: 16.256%
- Main-strut load increase: 12.182%
- Buffer-stroke increase: 12.757%

## Deterministic deck realization

- Seed: 2026
- Duration: 120.000 s
- Time step: 0.010000 s
- Heave RMS: 1.71607 m
- Pitch RMS: 0.0256441 rad

The filter equations are reproduced, but the time trace is not claimed to match the paper because the white-noise normalization and random seed were not published.

## Reproduction gate

- Full ADAMS/Abaqus replica from publication alone: **False**
- Reason: The paper does not publish the mechanism geometry, inertial, buffer, contact, modal and random-realization parameters required for a unique reconstruction.
