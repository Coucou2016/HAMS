"""Capture source/environment identity and audit corrected solver histories."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(out):
    import pychrono
    from .chrono_same_platform_multibody import landing_config
    from .chrono_leg_model import make_system, make_contact_material, make_rocket_body, make_box_body
    config = landing_config(.0005)
    system = make_system(pychrono, config)
    material = make_contact_material(pychrono, config)
    body = make_rocket_body(pychrono, config, material)
    geom = config['solver']['deck_geometry_m']
    deck = make_box_body(pychrono, (geom['length'], geom['beam'], config['solver']['deck_thickness_m']), 1000., material, True)
    inertia = body.GetInertiaXX()
    sources = sorted((ROOT / 'analysis/rocket_recovery').glob('*.py'))
    binaries = sorted((Path(pychrono.__file__).parent).rglob('*.pyd'))
    meta = Path(sys.prefix) / 'conda-meta'
    packages = [json.loads(p.read_text()) for p in meta.glob('*.json')]
    barge = ROOT / 'RocketRecoveryCases/Barge_120x50'
    inputs = [barge / 'Input/Hydrostatic.in', barge / 'platform_config.json',
              ROOT / 'RocketRecoveryCases/Paper_WangZhi_2023/platform_config.json',
              ROOT / 'RocketRecoveryCases/Chrono_LeggedRecovery/validation/thies_absorber_curves/thies-buffer-curves.json']
    inputs.extend(sorted((barge / 'validation/hydrodynamic_runs/medium_local025_high5/Output/Hydrostar_format').glob('*.rao')))
    record = {
        'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
        'numpy': np.__version__, 'pychrono_path': pychrono.__file__,
        'actual_chrono_objects': {'material_properties_mode': system.UsingMaterialProperties(),
                                 'contact_force_model_enum': system.GetContactForceModel(),
                                 'contact_jacobian': system.IsContactStiff(),
                                 'timestepper_enum': system.GetTimestepper().GetType(),
                                 'central_mass_kg': body.GetMass(),
                                 'central_inertia_kg_m2': [inertia.x, inertia.y, inertia.z],
                                 'collision_deck_mass_kg': deck.GetMass()},
        'sources': {str(p.relative_to(ROOT)): sha(p) for p in sources},
        'input_files': {str(p.relative_to(ROOT)): sha(p) for p in inputs},
        'chrono_binaries': {str(p): sha(p) for p in binaries},
        'conda_packages': [{k: p.get(k) for k in ('name', 'version', 'build', 'channel', 'url', 'sha256')}
                           for p in packages],
        'scope': 'Actual local runtime identity; not proof of physical model accuracy',
    }
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'execution-environment.json'
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps(record, indent=2), encoding='utf-8')


def audit(out):
    from .chrono_two_way_recovery import generalized_leg_force_from_chrono_6dof
    rows = []
    auditor_hash = sha(Path(__file__))
    previous_path = out / 'corrected-run-audit.json'
    previous = json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else {}
    cache = {r['raw']: r for r in previous.get('histories', [])} if previous.get('auditor_sha256') == auditor_hash else {}
    for p in sorted((out / 'raw').glob('*/*.audit.json')):
        a = json.loads(p.read_text(encoding='utf-8'))
        raw = Path(a['raw_history']['path'])
        raw_name = str(raw.relative_to(ROOT))
        current_hash = sha(raw)
        if raw_name in cache and cache[raw_name]['sha256'] == current_hash == a['raw_history']['sha256']:
            rows.append(cache[raw_name])
            continue
        s = json.loads(raw.read_text(encoding='utf-8'))
        t = np.asarray(s['time_s'])
        dt = float(raw.parent.name.split('_dt')[1].split('_kn')[0])
        expected = round((t[-1] - t[0]) / dt) + 1
        normal = s['forces']['leg_contact_normal_force_n']
        residual = np.asarray(a['wrench_action_reaction']['impulse_residual_6dof'])
        target_time = np.linspace(t[0], t[-1], round((t[-1]-t[0])/.01)+1)
        transfer = generalized_leg_force_from_chrono_6dof(s, target_time, footpad_radius_m=.2)
        l1_impulse = np.trapezoid(np.abs(transfer['samples_6dof']), t, axis=0)
        relative_residual = np.abs(residual) / np.maximum(l1_impulse, 1.)
        row = {'raw': raw_name, 'sha256': current_hash,
               'hash_matches': current_hash == a['raw_history']['sha256'],
               'samples': len(t), 'expected_samples': expected,
               'all_grid_nodes': len(t) == expected and bool(np.allclose(np.diff(t), dt, atol=1e-10, rtol=0)),
               'normal_force_peak_n': max(max(v) for v in normal.values()),
               'positive_vertical_force_peak_n': max(max(v) for v in s['forces']['leg_contact_force_n'].values()),
               'transfer_impulse_residual_6dof': residual.tolist(),
               'transfer_max_abs_residual': float(np.max(np.abs(residual))),
               'transfer_relative_l1_residual_6dof': relative_residual.tolist(),
               'transfer_pass_1e_minus_10': bool(np.max(relative_residual) <= 1e-10),
               'finite_normal_forces': all(np.isfinite(v).all() and len(v) == len(t) for v in map(np.asarray, normal.values())),
               'power_audit_available': a['coupling_work']['available']}
        rows.append(row)
    report_path = out / 'chrono-same-platform-multibody-report.json'
    report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
    result = {'auditor_sha256': auditor_hash, 'histories': rows, 'completed_report_exists': bool(report),
              'all_histories_complete': bool(rows) and all(x['all_grid_nodes'] and x['hash_matches'] and x['finite_normal_forces'] for x in rows),
              'interface_closed': report.get('all_interface_runs_closed'),
              'contact_step_pass': report.get('time_step_convergence', {}).get('pass'),
              'impulse_transfer_pass': bool(rows) and all(r['transfer_pass_1e_minus_10'] for r in rows),
              'scope': 'Grid retention, file identity and impulse transfer; not independent contact-energy closure'}
    (out / 'corrected-run-audit.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'histories'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['capture', 'audit'])
    parser.add_argument('--case', type=Path, required=True)
    args = parser.parse_args()
    (capture if args.action == 'capture' else audit)(args.case.resolve())
