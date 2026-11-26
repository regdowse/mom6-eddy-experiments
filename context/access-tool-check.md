# ACCESS experiment tools: read-only environment check

26 November 2026, `gadi-login-04.gadi.nci.org.au`. No package installation, experiment creation, Payu checkout or job submission performed.

## Results

- The existing MOM6 environment `/g/data/fu5/users/rd7475/.venv/mom6/` contains Payu **1.3.6**. Its model registry explicitly includes `mom6`; the local `payu clone --help` and `payu checkout --help` describe clone/start-point, branch, UUID and restart options. This confirms available interface support, not end-to-end compatibility with the future configuration or current generator.
- `experiment-generator` and `experiment-runner` were not found by `pip show` in that environment, and no executables were found on the initial PATH.
- The documented prerelease path `/g/data/vk83/prerelease/modules` was not visible in this execution session on the login host. Consequently `payu/dev` and its included generator/runner could not be inspected, and their installed versions and command behaviour are unverified. Visibility here does not prove the path is inaccessible from the user's normal shell or that a particular project membership is needed.
- The [generator source](https://github.com/ACCESS-NRI/access-experiment-generator/blob/main/src/experiment_generator/experiment_generator.py) obtains accepted model names from the active Payu model registry and passes the selected model to Payu clone. The installed Payu registry includes `mom6`. This is supportive evidence, but the installed generator and its compatibility with Payu 1.3.6 have not been tested. Its [README](https://github.com/ACCESS-NRI/access-experiment-generator) documents the prerelease module; its generic YAML guide currently lists other model types rather than `mom6`, whereas Chris Bull supplied a mom6 example.
- Generator and runner describe branch-based configuration and orchestration, but no proof yet exists for this repository, external NetCDF staging, cold-start behavior, UUID handling or branch publication. The current repository contains planning files only and is not yet Payu-ready.

## Next checks on the user's normal Gadi login shell

Read-only commands:

```bash
ls -ld /g/data/vk83 /g/data/vk83/prerelease/modules
module use /g/data/vk83/prerelease/modules
module show payu/dev
module load payu/dev
which payu experiment-generator experiment-runner
payu --version
experiment-generator --help
experiment-runner --help
python -m pip show payu experiment-generator experiment-runner
```

Module commands change the current shell environment only. If the path is unavailable there too, determine access/module location with ACCESS-NRI documentation or support before changing packages or project memberships. If available, capture module and package versions, compare the generator's accepted model registry, then use an isolated disposable configuration for a later non-submitting compatibility test. No installation, new environment or permissions change is authorised by this note.

## Follow-up: independent scratch environment and development source

Reg confirmed the documented `/g/data/vk83` path was also unavailable from his normal Gadi shell. To test the published packages without modifying the existing MOM6 environment, a separate Python 3.11.7 virtual environment was created at `/scratch/fu5/rd7475/tmp/access-tools-probe/`. On 26 November 2026, pip installed experiment-generator 1.0.0, experiment-runner 0.3.2 and Payu 1.4.0. All three command-line help/version checks succeeded. This is a temporary probe, not a production environment or a pinned project dependency lock; scratch retention is not guaranteed.

The PyPI generator 1.0.0 has a hard-coded model list (`access-esm1.5`, `access-esm1.6`, `access-om2`, `access-om3`) and rejects `mom6`, even though its Payu 1.4.0 supports mom6. Do not use this release for the planned mom6-solo generator workflow without further action.

A separate read-only development-source probe was cloned in scratch at `/scratch/fu5/rd7475/tmp/access-generator-source-probe/`, Git commit `8cbec23b62adb71c15f19e268d90f0542acad280`. Loading its source with the scratch Payu environment showed `mom6` in the generator's accepted model list. Its MOM6 input updater was exercised on a disposable synthetic MOM_input: changing BETA to 1.91985e-11 preserved F_0 and BETA_LAT_REF and round-tripped successfully. No actual branch, Payu setup, initial-condition generation or model integration was tested; this does not establish end-to-end compatibility. The development source was inspected via PYTHONPATH, not installed as a production package.

Recommended next compatibility step: in a disposable scratch workspace, check the pinned development generator plus the intended Payu/runner versions with a minimal mom6 configuration, including branch creation, unique identities and MOM_input changes, without submitting jobs. Establish a reproducible, version-pinned environment outside scratch if the pilot succeeds. Confirm exact supported source/release and module access with ACCESS-NRI as appropriate. Existing environment `/g/data/fu5/users/rd7475/.venv/mom6/` was not changed.

## Scratch-only branch-generation pilot — 26 November 2026

The development generator at commit `8cbec23b62adb71c15f19e268d90f0542acad280` was exercised with Payu 1.4.0 and a minimal synthetic MOM6 Git repository under `/scratch/fu5/rd7475/tmp/mom6-generator-test-JWV8VB/`. The fixture uses `/bin/true` as an executable, an empty input directory and a minimal namelist: it is not a runnable scientific model. No model or runner job was submitted.

A two-case YAML plan using `model_type: mom6` created `ctrl`, `beta_0` and `beta_33s` branches. Automated inspection of the second scratch test verified beta 0 and 1.91985e-11, unchanged F_0 = -7.94314e-5 and BETA_LAT_REF = 500000, three distinct UUIDs, and no restart entry in their synthetic configs. The MOM_input diff between ctrl and beta_33s contains the beta edit only. Payu created distinct named archive directories in scratch. Absence of a configured restart is not evidence that an actual model cold start was executed.

The first plan used `keep_uuid: false`, `new_uuid: true`. The generator first created a control identity during clone, then rechecked out ctrl with new_uuid and generated a second identity/archive, leaving the initial one behind. A fresh clone test with `new_uuid: false` retained the initial ctrl identity on that checkout and still created distinct new identities for the two newly created perturbation branches. This is observed behaviour for this fixture and version combination, not a blanket UUID policy for existing runs. Existing branch/archives, reruns and intentional resets require separate checks; do not delete archives to resolve naming.

Generator leaves `.expt_remove_states/` untracked in the generated scratch control directory; determine how to preserve or ignore this state before relying on a clean Git working tree or repeat generation. The zero-beta branch had only a metadata commit because beta was already zero in control, while the nonzero beta branch had an additional parameter-change commit. Archive symlink points to the last checked-out branch, not all experiments simultaneously.

Still untested: real configuration and binary; initial NetCDF generation and staging; repeated invocation and UUID preservation; runner job orchestration; actual cold starts, diagnostics and outputs; pushing branches; full model execution and reproducibility. The scratch virtual environment/source are transient and not a pinned production setup. Keep versions/commit and hashes for a future stable environment after validating the intended workflow.

## Rerun UUID check

On 26 November 2026, the same scratch plan was run again with `new_uuid: false`, with the control and two beta archives present. The existing branch UUIDs and archive associations were preserved in this fixture. For a fresh pilot the working proposal is therefore `keep_uuid: false`, `new_uuid: false`, checking the resulting UUIDs before any run; do not apply this as a blind rule if an existing archive is missing or a deliberate new identity is required. Payu's `keep_uuid` precedence and the runner's own settings must also be verified for actual jobs. The test did not cover missing archives, changed plans, restart chains or job submission.
