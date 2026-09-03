---
name: ska-data-access
description: How to get at Chandra and Ska data - the ska3-flight/aca/core/matlab conda environments and how to activate them, the $SKA data root and ska_sync, choosing between cheta, MAUDE, kadi commands, kadi events and kadi states as a data source, data latency and the clock-correlation stall, and working offsite versus on HEAD or GRETA. Use when setting up an environment, when data looks stale or missing, or when deciding which archive to pull from.
---

# Ska data and environments

## Which source do I pull from?

| Need | Use |
|---|---|
| Last few hours, or real time | **MAUDE** (`maude.get_msids`, or cheta's MAUDE data source) |
| Bulk history, speed, or SI telemetry (ACIS FP, HRC SS) | **cheta** (`cheta.fetch`) |
| What was commanded, including the near future | **`kadi.commands`** |
| What actually happened, as discrete events | **`kadi.events`** |
| A state (pitch, SIM position, ACIS config) over a span | **`kadi.commands.states`** |

Full comparison, including the traps → [references/data-sources.md](references/data-sources.md).

**Three traps worth knowing before you start:**

- **Trailing spaces.** cheta string values carry them (`"ON "`), MAUDE does not (`"ON"`).
  `vals == "ON"` silently matches nothing on cheta. This is the most common "my filter
  returned zero rows".
- **`kadi.commands` is always fresh; `kadi.events` lags up to a day.** Different
  mechanisms — commands are regenerated dynamically for the last 30 days, events wait on
  the overnight telemetry ingest.
- **After a safe mode, cheta can stop updating for days** while CXCDS waits on a new clock
  correlation. Not a bug. Use MAUDE for the gap.

## Environments

| Metapackage | What |
|---|---|
| `ska3-flight` | ~50 Chandra-ops packages, released ~10x/year — the operational env |
| `ska3-core` | ~500 open-source deps, updated ~yearly with the Python bump |
| `ska3-aca` | `ska3-flight` + ~24 ACA-team tools |
| `ska3-matlab` | Flight packages at older pins, bundled in the FOT MATLAB tools |
| `ska3-perl` | Perl interpreter and packages (optional) |

On HEAD or GRETA everything is preinstalled:

```
source /proj/sot/ska3/flight/bin/ska_envs.sh     # or .csh
```

Standalone install, `$SKA` setup, `ska_sync`, the masters/dev environment, and the
channel promotion ladder → [references/ska-environment.md](references/ska-environment.md).

## Upstream

The [skare3 wiki](https://github.com/sot/skare3/wiki) is the authority on all of this —
in particular [Ska Overview](https://github.com/sot/skare3/wiki/Ska-Overview) and
[Ska3 runtime environment for users](https://github.com/sot/skare3/wiki/Ska3-runtime-environment-for-users).
It is a **separate git repo** (`skare3.wiki.git`) and is *not* present in a normal skare3
checkout, so grep will never find it:

```
git clone https://github.com/sot/skare3.wiki.git
```

Page index → [references/skare3-wiki-index.md](references/skare3-wiki-index.md).
