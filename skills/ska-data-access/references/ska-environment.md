# The Ska3 runtime environment

Source of truth: the skare3 wiki
[Ska3 runtime environment for users](https://github.com/sot/skare3/wiki/Ska3-runtime-environment-for-users)
and [Ska Overview](https://github.com/sot/skare3/wiki/Ska-Overview). This page is the
short form plus the things that bite.

Supported platforms: **linux-64, Windows-64, macOS ARM-64**.

## What the environments are

| Metapackage | What it is |
|---|---|
| `ska3-flight` | The ~50 Chandra-operations packages. Released ~10x/year. The operational environment. |
| `ska3-core` | The ~500 open-source dependencies (numpy, astropy, matplotlib, scipy…). Updated ~once/year, usually with a Python version bump. |
| `ska3-aca` | `ska3-flight` **plus** ~24 ACA-team tools (jobwatch, fss_check, kalman_watch, aca_hi_bgd, …) |
| `ska3-matlab` | Flight packages at slightly older pins, bundled into the FOT MATLAB tools on Windows |
| `ska3-perl` | Perl interpreter and Perl packages. Optional. |
| `*-latest` variants | Unpinned versions, used to resolve a fresh environment rather than reproduce a release |

"Ska3" vs "Ska": Ska3 is the Python 3 environment. Legacy Ska2 (Python 2) still exists on
HEAD and chimchim for old production scripts. For ordinary use they mean the same thing.

## Activating

**On HEAD or GRETA** — everything is pre-installed:

```
source /proj/sot/ska3/flight/bin/ska_envs.csh    # csh/tcsh
source /proj/sot/ska3/flight/bin/ska_envs.sh     # bash
```

Recommended alias, so your prompt shows Ska3 is active:

```bash
alias ska3='source /proj/sot/ska3/flight/bin/ska_envs.sh; export PS1="ska3-$PS1"'
```
```csh
alias ska3 'source /proj/sot/ska3/flight/bin/ska_envs.csh; set prompt="ska3-$prompt:q"'
```

**Standalone** (laptop, Mac/Linux/Windows):

```
conda create -n ska3 ska3-flight --override-channels \
  -c https://icxc.cfa.harvard.edu/aspect/ska3-conda/flight
conda activate ska3
```

Update in place:

```
conda update ska3-flight --override-channels \
  -c https://icxc.cfa.harvard.edu/aspect/ska3-conda/flight
```

**Development / masters** environment, tracking package master branches:

```
conda create -n ska3-dev --override-channels \
  -c https://icxc.cfa.harvard.edu/aspect/ska3-conda/masters \
  -c https://icxc.cfa.harvard.edu/aspect/ska3-conda/flight \
  ska3-core-latest ska3-flight-latest ska3-perl-latest
```

The channel promotion ladder is **`masters` → `test` → `flight`**, served from
`https://icxc.cfa.harvard.edu/aspect/ska3-conda/<channel>`.

## `$SKA` — the data root

```bash
mkdir ~/ska
export SKA=${HOME}/ska        # bash
setenv SKA ${HOME}/ska        # csh
```

On production systems `$SKA` is `/proj/sot/ska`. Under it: `data/` (the bulk of it),
`analysis/`, `ops/`, `www/`.

Syncing data to a laptop:

```
ska_sync --install          # writes $SKA/ska_sync_config
# edit that file: remote host (e.g. kadi.cfa.harvard.edu) and your username
ska_sync                    # prints an rsync command to run
```

Smoke test that data is wired up:

```python
from Ska.tdb import msids; msids.find('tephin')
from kadi import events; events.normal_suns.filter('2014:001')
```

## Remote access without installing

SSH to `chimchim` or a HEAD linux machine from VS Code (Remote-SSH). You get a terminal
and Jupyter notebooks with full Ska access, editing as if local. FOT MP use this
successfully — often easier than maintaining a standalone install.

## Gotchas

- **Conda < 4.8 does not work.** Delete and reinstall rather than trying to upgrade.
- **Import performance on HEAD/GRETA**: installing Ska3 on *local* disk is noticeably
  faster than the shared `/proj/sot` path.
- Windows users need WSL for `rsync`-based data sync.
- If `conda create` hits dependency conflicts, create the env first and then
  `conda install` the metapackage into it as a second step.
- The wiki's Miniconda download links pin an older Python (3.10-era installer); the
  environments themselves are now Python 3.13. The installer Python does not have to match.

## Related

- [data-sources.md](data-sources.md) — which archive to pull from, and its latency
- [ska router](../../ska/SKILL.md)
