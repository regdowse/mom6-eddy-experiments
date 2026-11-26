# MOM6 eddy experiments

Idealised MOM6 experiments investigating how planetary and topographic potential vorticity gradients influence the three-dimensional structure and tilt of ocean eddies.

This repository contains a **provisional, unrun beta-zero baseline** derived from the legacy `mom6-eddy-exp1-layer-vortdiag` configuration. It uses a 1,000 km square Cartesian domain at 5 km horizontal spacing, ten isopycnal layers and the legacy flat-bottom interior with 45 km-wide sloping walls. The initial eddy is centred, cyclonic, circular and untilted. The beta-plane reference is at the domain centre, with `F_0=-7.94314e-5 s-1`, representing 33°S, and `BETA=0` for the initial control.

## Status and boundaries

The geometry and initial-condition NetCDF files have been generated and pass the offline checks described below. The analytic initialization grid template has **not** yet been compared against MOM6's runtime grid, and no model initialization or integration has been run for this configuration. It is not yet a scientifically validated control. Boundary influence, initial adjustment and the model diagnostics require a subsequent model pilot.

The existing sandbox experiments remain at `/g/data/fu5/users/rd7475/github/phd/idealised_modelling/mom6_sandbox/` as legacy references; they were not modified. The baseline points provisionally to the existing sandbox MOM6 executable in `config.yaml`, not a self-contained or retained build. Confirm the binary and source identity before an experiment. The copied `docs/MOM_parameter_doc.all` documents the legacy run's parameter defaults, not the effective output of this new configuration.

## Reproducing the current inputs on Gadi

The current scripts use the existing MOM6 Python environment and require numpy, xarray, netCDF4 and PyYAML. The reference vertical-coordinate file from the old run is copied locally for compatibility; the selected isopycnal mode uses its configured layer depths, not that file's old 100-layer coordinate. Generated NetCDF inputs and reference geometry are ignored by Git.

```bash
module load python3/3.11.7
source /g/data/fu5/users/rd7475/.venv/mom6/bin/activate
python initialisation/generate_geometry.py
python initialisation/generate_initial_state.py
```

The geometry generator refuses to replace existing generated files unless `--overwrite` is supplied. The initialization generator writes `input/initial_state.nc` and `input/layer_coord.nc` and **replaces those paths** if they already exist; preserve or rename any existing inputs first. Do not run these scripts in parallel on the same inputs. `input/geometry-provenance.json` and `input/initialization-provenance.json` record source and input hashes and validation; initial-state metadata also contains generation settings; preserve these files and checksums with a run. A generated reference grid is a template for the initializer, not runtime model output. Regenerating geometry while keeping an old initial state is invalid.

`input/sst.nc` is a constant placeholder for the legacy-named SST file; the control explicitly disables restoring and surface buoyancy forcing. Wind forcing is zero. Verify actual runtime behavior before interpreting results.

## Planned experiments

The first pilot compares beta zero with beta approximately `1.91985e-11 m-1 s-1` while holding centre f fixed. ACCESS-NRI generator and runner versions require pinning and an end-to-end compatibility check before this is used to run MOM6. The development generator passed a scratch branch and UUID test; see the local context notes for details. A provisional two-day generator plan and separate case-input preparation are in `experiments/` and `initialisation/prepare_beta_pilot.py`; they have been checked on a disposable copy, but no model jobs have been submitted.
