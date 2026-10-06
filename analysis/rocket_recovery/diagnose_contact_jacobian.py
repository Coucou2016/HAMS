"""Compare implicit contact Jacobians on identical short prescribed-deck runs."""
from pathlib import Path
from . import chrono_same_platform_multibody as model
from .common import write_json


def main():
    root = model.ROOT / 'RocketRecoveryCases/Chrono_ContactJacobian_Diagnostic20260927'
    model.CASE_ROOT = root
    original = model.landing_config

    def config(*args, **kwargs):
        value = original(*args, **kwargs)
        value['solver']['contact_jacobian'] = True
        return value

    model.landing_config = config
    rows = {}
    for step in (.0005, .00025):
        result = model.run_passes(1, step, retain_response=False, end_s=512.)
        rows[str(step)] = result
        write_json(root / 'jacobian-diagnostic.json', {'scope': 'One-pass prescribed-deck solver sensitivity, not coupled convergence', 'runs': rows})


if __name__ == '__main__':
    main()
