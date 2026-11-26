# Proposed repository and first beta experiments

26 November 2026. Specification for discussion and review. No configuration, repository, remote branch, input data or model run has been created under this proposal.

## Purpose and agreed direction

The paper extends the Tasman Sea tilt climatology through controlled tests of planetary and topographic PV-gradient effects. Begin with planetary beta, then investigate topography and background flow, including opposed planetary and topographic gradients. Whether their cancellation implies zero tilt is a later scientific hypothesis, not an assumed result.

Create a dedicated experiment configuration repository under `/g/data/fu5/users/rd7475/github/` (repository name and remote visibility/ownership to be agreed). Preserve `mom6_sandbox/` and its existing experiments as legacy references. Derive the new baseline from `mom6-eddy-exp1-layer-vortdiag`, documenting changes rather than changing the legacy copy.

Use the ACCESS-NRI experiment generator as the intended setup approach and the runner for orchestration, subject to version, MOM6 and environment compatibility checks. First pilot two independently identified cold-start experiments: zero beta and the 33°S beta estimate. A larger sweep and later f, topography and flow experiments can use the same organisation.

## Baseline: agreed values and proposals

| Item | Specification | Status |
|---|---|---|
| Domain | Square, at least 1000 km each side; flat interior with sloping sidewalls and closed boundaries, as in the current concept. Eddy initially centred. | Direction agreed; exact dimensions and wall design to confirm. |
| Horizontal resolution | Propose retaining current 5 km spacing: 200 x 200 cells for 1000 km square. | Proposal; check resolution and processor layout. |
| Bottom | Retain 4000 m flat interior from reference; reproduce wall shape in physical coordinates, with geometry independently validated. | Proposed; wall width, profile and corners need inspection and agreement. |
| Rotation | Beta plane, reference location at domain centre and initial eddy centre. `F_0` is centre f. For a 0–1000 km y-domain, `BETA_LAT_REF=500000 m`. | Agreed convention; confirm actual MOM6 implementation and effective settings. |
| Centre f | Approximately -7.94314e-5 s^-1, corresponding to 33°S using omega=7.292115e-5 s^-1. | Agreed reference; choose rounding at implementation. |
| Pilot beta | 0 and approximately 1.91985e-11 m^-1 s^-1 (33°S using radius 6,371,000 m). Keep centre f fixed. | Agreed pilot concept and reference; choose rounding at implementation. |
| Eddy | Current reference is cyclonic, circular, untilted, radius of maximum speed 50 km, surface speed 0.20 m/s and 500 m exponential e-folding depth. | Proposed starting point; check suitability, do not assume scientific calibration. |
| Vertical structure and physics | Current 10 isopycnal layers, fixed layer temperatures, active configured mixing and drag, and disabled surface heat/freshwater fluxes. | Proposed to carry forward initially; verify actual configuration and physical implications. |
| Diagnostics | Carry forward native-layer state/RV/PV, momentum tendencies, geometry and z-star remapped daily fields; review output needs and signs/units. | Proposed; ensure centreline measurement and budget requirements are covered. |
| Duration | Current archived run is 31 model days. | Proposal only; agree analysis window, initial adjustment and stopping criteria. |

The larger domain moves the eddy farther from walls initially, but does not prove their influence negligible throughout the run. Keep horizontal cell spacing explicit: 2x side length at unchanged resolution gives 4x horizontal cells; compute and output volume depend on decomposition, duration and diagnostics and must be measured. Existing `NIPROC=NJPROC=5` and 25 CPUs are not automatically optimal or valid for the new production layout.

The saved `initialisation/reference/ocean_static.nc`, reference interfaces and `input/topog.nc` describe the existing 100x100 geometry. The initializer verifies grid size, spacing, coordinates and bathymetry, so a larger geometry requires matching new grid, topography, forcing and any other grid-dependent inputs. Preserve agreed wall boundaries; do not replace the geometry with a uniform-bottom box unless separately agreed. Determine the existing wall-generation method before choosing how wall widths and corners translate to the new domain. Ensure the grid remains compatible with the binary and model decomposition.

## Pilot and input policy

| Case | Suggested label | Centre f (s^-1) | Beta (m^-1 s^-1) | Start |
|---|---|---:|---:|---|
| f-plane control | `beta_0` | -7.94314e-5 | 0 | Independent cold start |
| 33°S beta | `beta_33s` | -7.94314e-5 | 1.91985e-11 | Independent cold start |

Labels are proposals; exact numeric values can be rounded consistently. Use separate UUIDs and archive identities. Do not start the second case from the first case's restart. Later continuations of an individual case should retain that case's identity and document restart lineage.

**Initial-condition policy to decide before implementation:** a useful first comparison is the same physical initial eddy state for both cases, generated using the agreed centre f and geometry, with each case separately validated against its own f(y). This improves control of the initial state but does not guarantee identical balance or adjustment on the two beta planes. The existing generator reads beta and records it in NetCDF metadata and validates balance using the spatially varying Coriolis field. It must not silently label a shared file as if generated for a different beta. Compare relevant fields, metadata and balance diagnostics and choose either a clearly documented shared physical IC plus case-specific validation or case-specific files whose physical arrays are checked for equality. The generator YAML alone does not generate or validate NetCDF. Keep non-overwriting, immutable, checksummed input versions and capture the actual inputs used.

The zero-beta case is a symmetry/control test, not a promise that measured tilt will be identically zero. Define tilt and center-finding quality, acceptable adjustment and tolerances after examining numerical precision, layer collapse and boundary effects. Compare centre positions over time and depth using a defined convention; later compare with ESP/Delta consistently while accounting for their differing inputs and temporal/depth support. `wd` is diapycnal velocity, not physical vertical velocity. Momentum-curl residual is not PV-budget closure.

## Repository and storage proposal

Illustrative layout, subject to generator/Payu requirements:

```text
/g/data/fu5/users/rd7475/github/<repository-name>/
    README.md                  # purpose, quick start, provenance
    MOM_input, MOM_override    # model parameters
    config.yaml, input.nml     # Payu and run controls
    diag_table                 # requested model diagnostics
    initialisation/            # geometry/IC generation, configs and validation
    analysis/                  # versioned analysis code and tests as appropriate
    experiments/               # versioned generator/runner plans and descriptions
    docs/                      # methods, decisions, run index or links to it
```

Layout is conceptual, not a verified generator schema or an instruction to create files. Confirm what must live at repository root, how generator clones the repository and what Payu expects. Version reusable text, source, plans and a small run index. Store generated NetCDF, executable builds, restart and large model outputs outside Git in stable managed project storage; assign explicit paths and retention/backup policies before use. Scratch is suitable for temporary execution only unless its retention is explicitly acceptable. Record hashes and retained locations; Git tracking alone does not preserve external inputs or executable.

Suggested naming: `main` contains reviewed baseline and tooling; the generator creates a control and `beta_0`, `beta_33s` branches from a pinned baseline commit. These names are examples. Each branch contains a full configuration view; shared Git history avoids independently maintaining duplicate source copies. Review branch diffs and keep the plan under version control. Confirm whether generated branches must be pushed explicitly and how the remote is secured; local branch creation does not itself imply GitHub publication. Record exact generated commit, not branch name alone, because branch tips can change.

A run index should map each run to at least: readable case name; physical hypothesis; beta and centre f with units; domain and IC identity; generator plan revision and generated Git commit; input hashes and retained paths; executable hash plus build/source revisions; UUID; cold/restart starting point and lineage; actual archived controls and effective parameters; tool versions and environment; run status, dates and output path; and analysis code version. Preserve Payu manifests and validation reports along with the archived control files. Determine whether the index belongs in Git, a separate retained table, or both; update it only after comparing against actual run metadata.

## Checks and staged execution

1. **Before creating pilot cases:** review the scientific baseline and reference geometry, confirm domain size, wall geometry, numerical resolution, IC policy, run length and retained storage. Check the ACCESS generator and runner version and MOM6 support on Gadi. `/g/data/vk83/prerelease/modules` was not visible from the previous execution environment; this does not establish availability on Gadi. Check generator's handling of branches, configuration-root paths and input lists using a non-production pilot.
2. **Prepare baseline:** create grid-dependent inputs and reference geometry; verify expected dimensions, extent, depth field, wall shape, centre, f(y), wet mask and input compatibility. Record geometry-generation parameters and source checksums. Review diagnostics and verify model/executable compatibility.
3. **Generate cases:** pin baseline revision and tool version; create branches with the plan. Inspect diffs against control and verify actual effective `F_0`, `BETA`, `BETA_LAT_REF` and initial conditions. Record each branch commit and input checksums.
4. **Short pilot after explicit authorization to run:** separate cold starts and distinct UUIDs. Check each run's archived parameters, input and executable manifests, expected f(y), metadata, output location, diagnostic fields and times. Measure runtime and storage before extending.
5. **Scientific screening:** inspect stability, initial adjustment, conservation, layer thickness/collapse, eddy centreline and translation, proximity to boundaries and budget residuals at relevant depths. Compare f-plane and beta cases; establish whether observed differences are robust to initialization, output sampling, boundary distance and numerical resolution before scaling up. Quantitative tolerances must be agreed based on these diagnostics, not invented here.
6. **Review:** decide whether to proceed to more beta values and what changes are needed. Record results and preserve pilot provenance.

## Decisions still needed

- Exact repository name and GitHub visibility/owner; creation/publication is separate from this document.
- Exact domain size (minimum 1000 km), wall width/shape, and horizontal resolution (5 km proposed).
- Initial-condition sharing versus per-case generation, and acceptance of beta-dependent balance diagnostics.
- Run length, analysis period and diagnostics/output frequency needed for tilt evolution and mechanism budgets.
- Stable locations for NetCDF inputs, executable builds and archives, plus storage/retention and compute constraints.
- Version availability and implementation details of the ACCESS-NRI generator and runner on Gadi.
