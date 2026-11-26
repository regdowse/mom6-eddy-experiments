#!/usr/bin/env python3
"""Create the provisional Cartesian eddy-domain inputs without running MOM6.

The fixed physical-width wall profile follows the legacy ANU-tub driver.
The grid template is constructed analytically for initialization and must be
compared against the real MOM6 ocean_static.nc before scientific use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]


def make_geometry(n=200, spacing=5000.0, depth=4000.0, wall_width=45000.0):
    if n < 2 or spacing <= 0 or depth <= 0 or wall_width <= 0:
        raise ValueError('Grid size, spacing, depth and wall width must be positive.')
    edges = np.arange(n + 1, dtype=float) * spacing
    centres = (edges[:-1] + edges[1:]) / 2
    x, y = np.meshgrid(centres, centres)
    length = n * spacing
    distance = np.minimum.reduce([x, length - x, y, length - y])
    t = np.clip(distance / wall_width, 0, 1)
    topog = depth * (3 * t**2 - 2 * t**3)
    return centres, edges, topog


def write_inputs(n=200, spacing=5000.0, depth=4000.0, wall_width=45000.0, overwrite=False):
    centre, edge, topog = make_geometry(n, spacing, depth, wall_width)
    input_dir = ROOT / 'input'
    ref_dir = ROOT / 'initialisation' / 'reference'
    paths = [input_dir / 'topog.nc', input_dir / 'forcing.nc', input_dir / 'sst.nc',
             ref_dir / 'ocean_static.nc', input_dir / 'geometry-provenance.json']
    if not overwrite and any(p.exists() for p in paths):
        raise FileExistsError('A generated file exists; use --overwrite only if intentionally replacing all geometry inputs.')
    input_dir.mkdir(parents=True, exist_ok=True)
    ref_dir.mkdir(parents=True, exist_ok=True)
    xy = {'x': ('x', centre, {'units': 'm'}), 'y': ('y', centre, {'units': 'm'})}
    top = xr.Dataset({'topog': (('y', 'x'), topog, {'units': 'm'})}, coords=xy)
    zeros = np.zeros((n, n))
    names = ['tau_x', 'tau_y', 'SSS', 'LW', 'SW', 'froz_precip', 'froz_runoff',
             'latent', 'liq_precip', 'liq_runoff', 'sensible', 'evap']
    forcing = xr.Dataset({name: (('y', 'x'), zeros.copy()) for name in names}, coords=xy)
    # SST restoring is disabled in the baseline. Supply a documented placeholder
    # for the referenced file, not an assertion of active surface heat forcing.
    sst = xr.Dataset({'SST': (('y', 'x'), np.full((n, n), 24.0), {'units': 'degC'})}, coords=xy)
    wet_u = np.ones((n, n + 1)); wet_u[:, [0, -1]] = 0
    wet_v = np.ones((n + 1, n)); wet_v[[0, -1], :] = 0
    coords = {'xh': ('xh', centre, {'units': 'm'}), 'yh': ('yh', centre, {'units': 'm'}),
              'xq': ('xq', edge, {'units': 'm'}), 'yq': ('yq', edge, {'units': 'm'})}
    grid = xr.Dataset({
        'deptho': (('yh', 'xh'), topog), 'wet': (('yh', 'xh'), np.ones((n,n))),
        'wet_u': (('yh', 'xq'), wet_u), 'wet_v': (('yq', 'xh'), wet_v),
        'dxt': (('yh', 'xh'), np.full((n,n), spacing)),
        'dyt': (('yh', 'xh'), np.full((n,n), spacing)),
        # The initializer replaces this placeholder using the active MOM parameters.
        'Coriolis': (('yq', 'xq'), np.zeros((n+1,n+1))),
    }, coords=coords, attrs={'description': 'Analytic initialization template; validate against MOM6 runtime grid.'})
    for ds, path in zip((top, forcing, sst, grid), paths):
        ds.to_netcdf(path, engine='netcdf4', encoding={name: {'_FillValue': None} for name in ds.variables})
        ds.close()
    checksums = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths[:4]}
    paths[4].write_text(json.dumps({'n': n, 'spacing_m': spacing, 'depth_m': depth,
        'wall_width_m': wall_width, 'sst_restore': False, 'sha256': checksums,
        'grid_template': 'analytic; compare with MOM6 runtime grid before scientific use'}, indent=2) + '\n')
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--overwrite', action='store_true', help='replace existing generated geometry files')
    args = parser.parse_args()
    for path in write_inputs(overwrite=args.overwrite):
        print(path)


if __name__ == '__main__':
    main()
