"""Independent-case process parallelism; each interface iteration stays sequential."""
from __future__ import annotations

import argparse
import hashlib
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from . import chrono_same_platform_multibody as model
from .common import read_json, write_json


def worker(case, end, dt, stiffness, response):
    model.CASE_ROOT = Path(case)
    model.RESUME = True
    cfg = model.landing_config(dt, end_s=end, contact_stiffness_n_m=stiffness)
    run_dir = model.CASE_ROOT / 'raw' / f"end{end:g}_dt{dt:g}_kn{cfg['contact']['normal_stiffness_n_m']:g}"
    cfg_file = run_dir / 'run-config.json'
    run_dir.mkdir(parents=True, exist_ok=True)
    if cfg_file.exists() and read_json(cfg_file) != cfg:
        raise ValueError(f'Configuration differs from checkpoint: {run_dir}')
    write_json(cfg_file, cfg)
    completed = run_dir / 'run-result.json'
    if completed.exists():
        result = read_json(completed)
        if result['run_config'] != cfg:
            raise ValueError(f'Completed configuration differs: {completed}')
        for row in result['passes']:
            raw = row['raw_history']
            if hashlib.sha256(Path(raw['path']).read_bytes()).hexdigest() != raw['sha256']:
                raise ValueError(f'Completed history hash differs: {raw["path"]}')
        result['qualification_status'] = 'computed_corrected_proxy_requires_numerical_and_physical_qualification'
        write_json(completed, result)
        return (end, dt, stiffness), str(completed)
    result = model.run_passes(8, dt, retain_response=response, end_s=end,
                              contact_stiffness_n_m=stiffness, adaptive=True)
    return (end, dt, stiffness), str(run_dir / 'run-result.json')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--case', type=Path, required=True)
    p.add_argument('--workers', type=int, default=3)
    a = p.parse_args()
    case = a.case.resolve()
    specs = [(526., .0005, None, True), (516., .0005, None, False),
             (516., .00025, None, False), (516., .000125, None, False),
             (516., .000125, 250e6, False), (516., .000125, 500e6, False)]
    paths = {}
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        pending = [pool.submit(worker, str(case), *spec) for spec in specs]
        for future in as_completed(pending):
            key, path = future.result()
            paths[key] = path
            print(f'COMPLETED CASE {key}: {path}', flush=True)
    # build_report supplies the common comparison definitions; no case is integrated twice.
    def retained(pass_count, contact_dt_s, retain_response, end_s=526., contact_stiffness_n_m=None, adaptive=False):
        return read_json(Path(paths[(end_s, contact_dt_s, contact_stiffness_n_m)]))
    model.run_passes = retained
    model.CASE_ROOT = case
    model.REPORT_PATH = case / 'chrono-same-platform-multibody-report.json'
    model.RESPONSE_PATH = case / 'Output/RocketRecovery/chrono-same-platform-multibody-response.json'
    report = model.build_report()
    print(f"All interfaces closed: {report['all_interface_runs_closed']}; step gate: {report['time_step_convergence']['pass']}", flush=True)


if __name__ == '__main__':
    main()
