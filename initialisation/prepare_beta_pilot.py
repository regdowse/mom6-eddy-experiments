#!/usr/bin/env python3
"""Prepare separate initial inputs for the two provisional beta pilot cases.

Requires the baseline geometry first. Never overwrites an existing case.
Does not create Git branches, run MOM6 or submit jobs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import yaml
from generate_initial_state import generate

ROOT = Path(__file__).resolve().parents[1]
CASES = {'beta_0': 0.0, 'beta_33s': 1.91985e-11}


def prepare(case: str) -> Path:
    beta = CASES[case]
    case_dir = ROOT / 'input' / 'cases' / case
    provenance = ROOT / 'input' / 'case-provenance' / case
    if case_dir.exists() or provenance.exists():
        raise FileExistsError(f'{case}: case or provenance directory already exists; preserve or move it before regenerating')
    for name in ('topog.nc', 'forcing.nc', 'sst.nc'):
        if not (ROOT / 'input' / name).is_file():
            raise FileNotFoundError(f'Missing base input {name}; generate geometry first')
    case_dir.mkdir(parents=True)
    (provenance / 'docs').mkdir(parents=True)
    for name in ('topog.nc', 'forcing.nc', 'sst.nc'):
        shutil.copy2(ROOT / 'input' / name, case_dir / name)
    for name in ('MOM_override', 'build_versions.json', 'docs/MOM_parameter_doc.all'):
        shutil.copy2(ROOT / name, provenance / name)
    model_input = (ROOT / 'MOM_input').read_text()
    original = 'BETA = 0.0'
    if model_input.count(original) != 1:
        raise ValueError('Expected the baseline to contain exactly one BETA = 0.0 assignment')
    (provenance / 'MOM_input').write_text(model_input.replace(original, f'BETA = {beta:.12g}', 1))
    cfg = yaml.safe_load((ROOT / 'initialisation' / 'config.yaml').read_text())
    cfg['paths'] = {'model_directory': str(provenance),
                    'grid': str(ROOT / 'initialisation' / 'reference' / 'ocean_static.nc'),
                    'vertical_grid': str(ROOT / 'initialisation' / 'reference' / 'Vertical_coordinate.nc'),
                    'topography': str(case_dir / 'topog.nc'), 'output': str(case_dir / 'initial_state.nc')}
    config_path = provenance / 'config.yaml'
    config_path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    output, report = generate(config_path)
    # Payu stages this directory; keep the generation metadata outside it.
    shutil.move(str(case_dir / 'initialization-provenance.json'), provenance / 'initialization-provenance.json')
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in case_dir.glob('*.nc')}
    (provenance / 'case.json').write_text(json.dumps({'case':case, 'beta_m_1_s_1':beta,
        'input_directory':str(case_dir), 'input_sha256':manifest, 'validation':report}, indent=2)+'\n')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=list(CASES), help='prepare only selected case(s); default: both')
    args = parser.parse_args()
    for case in args.case or CASES:
        print(f'{case}: {prepare(case)}', flush=True)


if __name__ == '__main__':
    main()
