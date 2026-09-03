---
name: ska
description: Chandra X-ray Observatory and the Ska3 Python ecosystem. Use whenever working with Chandra or ACA data, engineering telemetry, MSIDs, star catalogs, aspect camera images, spacecraft commanding or states, attitude and quaternions, thermal models, or any ska/chandra_aca/cheta/kadi/agasc/mica/proseco/sparkles/xija/cxotime package. Start here to find which of the ~90 Ska packages to reach for.
---

# Ska / Chandra: where to look

Routing index for the Ska3 ecosystem. **Find the package here, then read the real API**
from the installed source or `https://sot.github.io/<pkg>` — this file deliberately does
not mirror signatures, because those change every release.

All symbols below verified against `ska3-flight` 2026.9.

## Rule zero: import paths are not guessable

Ska packages mostly do **not** re-export at top level. `chandra_aca.get_aca_images` does
not exist; it is `chandra_aca.aca_image.get_aca_images`. Always import from the module
named in the table, and check `dir()` or the source before assuming a shorter path.

## Rule one: do not use the legacy packages

**Every module in this table still imports cleanly in `ska3-flight` 2026.9** (verified).
Nothing fails loudly — legacy code just silently violates convention, so this is the single
easiest way to write wrong-looking Ska code. Dotted "namespace" package names are a Perl-era
legacy; new code is all lowercase with underscores.

| Do NOT use | Use instead |
|---|---|
| `Ska.engarchive` | `cheta` — **always**, no exceptions |
| `Chandra.Time.DateTime` | `cxotime.CxoTime` — always; substitution is usually direct |
| `Ska.Matplotlib` | `ska_matplotlib` |
| `Ska.Numpy` | `ska_numpy` |
| `Ska.DBI` | `ska_dbi` |
| `Ska.quatutil` / `ska_quatutil` | `Quaternion` or `chandra_aca` |
| `ska_parsecm` | `parse_cm` |
| `ska_shell` | `subprocess` |
| `ska_file` | `contextlib.chdir()` (Python 3.11+) |
| `ska_path` | `$SKA` + `pathlib`. **Not** `ska_helpers.paths` — that locates `chandra_models` files, it is not a general path library |
| `ska_astro`, `pyyaks` | Nothing — stdlib `logging` for `pyyaks.logger`; avoid in new code |
| `hopper` | Orphaned; still used by ACA load review, do not build on it |

**Tables are astropy `Table`, never pandas `DataFrame`.** All Ska flight packages use
astropy `Table` for consistency, and it supports things `DataFrame` cannot: multi-dimensional
column data (e.g. an 8x8 ACA image per row), column and table metadata, and `CxoTime`
columns. Convert at the edge with `tbl.to_pandas()` if you need pandas.

## I want to…

### ACA / aspect camera

| Task | Use |
|---|---|
| Get ACA image telemetry (the usual entry point) | `chandra_aca.aca_image.get_aca_images` — see [references/chandra_aca.md](../ska-packages/references/chandra_aca.md) first, it has three backends |
| ACA images, MAUDE backend directly | `chandra_aca.maude_decom.get_aca_images` |
| ACA images, CXC L0 backend directly | `mica.archive.aca_l0.get_aca_images` |
| ACA images, cheta backend directly | `chandra_aca.aca_image.get_aca_images_cheta` |
| Work with an image + its row/col origin as one object | `chandra_aca.aca_image.ACAImage` |
| Dark current calibration image | `mica.archive.aca_dark.get_dark_cal_props` |
| Acquisition / guide success probabilities | `chandra_aca.star_probs.acq_success_prob` |
| ACA alignment drift vs. time, aimpoint offsets | `chandra_aca.drift.get_aca_offsets` |

### Coordinates, time, attitude

| Task | Use |
|---|---|
| Anything with a Chandra time in any format | `cxotime.CxoTime` |
| Quaternions, attitude arithmetic | `Quaternion.Quat`, `Quaternion.normalize` |
| yag/zag ↔ RA/Dec | `chandra_aca.transform.yagzag_to_radec`, `.radec_to_yagzag` |
| CCD pixels ↔ yag/zag | `chandra_aca.transform.pixels_to_yagzag`, `.yagzag_to_pixels` |
| ACA magnitude ↔ count rate | `chandra_aca.transform.mag_to_count_rate` |
| Sun pitch **as telemetered** over a time range | `cheta.fetch` MSID `DP_PITCH` (derived parameter) |
| Sun pitch **computed** for a given RA/Dec + time | `ska_sun.pitch(ra, dec, time)` |
| Sun position, nominal roll | `ska_sun.position`, `ska_sun.nominal_roll` |
| How long a maneuver takes | `chandra_maneuver.duration` |

### Telemetry

| Task | Use |
|---|---|
| Engineering telemetry for an MSID over a time range | `cheta.fetch.MSID` / `cheta.fetch.MSIDset` |
| Same, in engineering or science units | `cheta.fetch_sci.Msid`, `cheta.fetch_eng.Msid` |
| Several MSIDs interpolated onto one time grid | `cheta.fetch.get_telem` |
| Real-time / recent telemetry not yet in the archive | `maude.get_msids` |

Choosing between cheta and maude is a latency-vs-coverage tradeoff — see
[ska-data-access](../ska-data-access/SKILL.md).

### Commanding, states, events

| Task | Use |
|---|---|
| Commands actually run (or planned) over a time range | `kadi.commands.get_cmds` |
| Spacecraft state (pitch, obsid, SIM position, …) vs. time | `kadi.commands.states.get_states` |
| State at one instant, to seed a run | `kadi.commands.states.get_continuity` |
| Collapse a state table to intervals of change | `kadi.commands.states.reduce_states` |
| Observations (obsid intervals) from commanding | `kadi.commands.observations.get_observations` |
| Star catalogs as commanded | `kadi.commands.observations.get_starcats` |
| Maneuvers, dwells, obsids as queryable events | `kadi.events.manvrs`, `.dwells`, `.obsids` |
| Parse a backstop file | `kadi.commands.read_backstop` (into a kadi cmds table) or `parse_cm.backstop.read_backstop` (raw) — both exist |
| Read OCCweb pages, directories, iFOT tables | `kadi.occweb.get_occweb_page`, `.get_occweb_dir`, `.get_ifot` |

`kadi.commands` (from the load products) and `kadi.events` (derived from telemetry) answer
different questions. Commands say what was *supposed* to happen; events say what the
spacecraft *did*.

**Freshness differs sharply between the two.** `kadi.commands` is *always fresh*: the last
30 days are generated dynamically from the Command Events sheet plus OCCweb, on top of
archive HDF5 files. `kadi.events` depends on telemetry — cron runs at 7am and the CXC L0
ingest it relies on completes ~6:30am, so events lag by up to a day. For anything more
recent than that, use `maude.get_msids`.

The same commanded-vs-actual split applies to pitch: `kadi.commands.states.get_states(
..., state_keys=['pitch'])` gives the commanded profile, while the `DP_PITCH` MSID in
cheta gives what was telemetered.

### Stars and catalogs

| Task | Use |
|---|---|
| Stars near a position from the AGASC | `agasc.get_agasc_cone` |
| One star by AGASC id | `agasc.get_star` (many: `agasc.get_stars`) |
| Which AGASC file version is in play | `agasc.get_agasc_filename` |
| The star catalog actually used for an obsid | `mica.starcheck.get_starcheck_catalog` |
| Just the catalog table / dither for an obsid | `mica.starcheck.get_starcat`, `.get_dither` |
| Generate a new star catalog | `proseco.get_aca_catalog` |
| Review / check a generated catalog | `sparkles.run_aca_review` |

### Products, statistics, thermal

| Task | Use |
|---|---|
| Aspect L1 pipeline products for an obsid | `mica.archive.asp_l1.get_files` |
| Observation parameter (obspar) file | `mica.archive.obspar.get_obspar` |
| Historical acquisition / guide star performance | `mica.stats.acq_stats.get_stats`, `mica.stats.guide_stats.get_stats` |
| Run a thermal model | `xija.ThermalModel` |
| Get the fitted model spec for a thermal model | `xija.get_model_spec.get_xija_model_spec` |
| Any file from the `chandra_models` repo, version-aware | `ska_helpers.chandra_models.get_data` |

### Monitoring and trending (`ska3-aca` only)

These are **applications, not libraries** — cron-driven monitors that write HTML reports.
Run the console script; do not import them. Full detail and gotchas in
[references/aca-monitors.md](../ska-packages/references/aca-monitors.md).

| Task | Use |
|---|---|
| Are the Ska cron jobs healthy? | `jobwatch` → `skawatch_daily` / `skawatch_hourly` (HEAD-only) |
| Fine Sun Sensor pitch/roll error trending | `fss_check` → `fss_check_daily_fss` |
| ACA high-background events | `aca_hi_bgd` → `aca_hi_bgd_update` |
| Kalman star health, perigee passages | `kalman_watch` → `kalman_watch_low_kalman_mon`, `..._kalman_perigee_mon`, `..._monitor_win_perigee` |
| One-shot / attitude error trending | `attitude_error_mon` → `attitude_error_mon` |
| Weekly ACA metrics roll-up | `aca_weekly_report` → `aca_weekly_report` |
| Month/quarter/semester boundaries for a report | `ska_report_ranges` (a real library: `in_month`, `get_update_ranges`, `timerange`) |

Requires the **`ska3-aca`** environment — none of these are in `ska3-flight`.

## Going deeper

- **[ska-packages](../ska-packages/SKILL.md)** — per-package detail: what each is for,
  canonical snippets, and the gotchas that actually bite.
- **[chandra-domain](../chandra-domain/SKILL.md)** — the spacecraft and the ACA: coordinate
  frames, time systems, star catalogs, mission planning cadence, glossary.
- **[ska-data-access](../ska-data-access/SKILL.md)** — `$SKA`, the `ska3-*` environments,
  which data source to use, and what works offsite vs. only on HEAD/GRETA.

## Upstream documentation

- **[The skare3 wiki](https://github.com/sot/skare3/wiki)** — 36 pages, mostly build,
  release, promotion and testing process. Start with
  [Ska Overview](https://github.com/sot/skare3/wiki/Ska-Overview) ("Ska 101") and
  [Ska3 runtime environment for users](https://github.com/sot/skare3/wiki/Ska3-runtime-environment-for-users).
  It is a separate git repo (`skare3.wiki.git`), so it is **not** in a normal skare3
  checkout — fetch it if you need it.
- **https://sot.github.io/** — per-package API docs. `kadi` and `cheta` docs were recently
  overhauled and are the best of them.
- **Slack `#analysis-coding`** — the team's actual support channel. Faster than guessing.
- Some packages are **private** to the ~20 `sot` org members: `parse_cm`, `maude`,
  `chandra_maneuver`, `chandra_limits`. Public doc links for these may 404.

## When this file is wrong

It will be, eventually. If routing here sent you to the wrong place, fix it — the repo is
`sot/ska-knowledge` and an edit is a small markdown PR. Getting a wrong answer is the
main way gaps get found.
