# The ACA monitor / trending packages

The ~24 packages in `ska3-aca` but **not** `ska3-flight` are mostly a single family:
cron-driven monitoring and trending tools that produce HTML reports. Most have no README
and no published docs, so they are documented here as a class first — the shared shape is
the reusable knowledge, and each tool's specifics are a few lines on top of it.

Verified against `ska3-aca` (2026.11) on 2026-09-03.

## The shared shape

Nearly every one of these follows the same pattern:

1. **A console-script entry point**, declared in `setup.py` (e.g. `aca_hi_bgd_update`).
   That script — not a Python import — is the interface.
2. **A `task_schedule.cfg`** next to the source, consumed by
   [task_schedule](https://github.com/sot/task_schedule) (a Perl tool in `ska3-perl`) which
   is what actually runs it under cron on HEAD. The cfg sets the email `subject`, the
   `data_dir`, the heartbeat timeout, and alert behavior.
3. **A data directory under `$SKA/data/<name>`**, holding accumulated state (usually an
   HDF5 or ECSV table of events) plus generated plots.
4. **An HTML report** written into that tree and served on the aspect web pages.
5. **Email alerts** when the task fails or the heartbeat goes stale.

So the way to reason about one of these is: *what does it watch, where does its state
live, and what does its report look like* — not *what is its Python API*.

## The tools

| Package | Entry point | Watches / does | `$SKA/data/…` |
|---|---|---|---|
| `jobwatch` | `skawatch_daily`, `skawatch_hourly` | Meta-monitor: watches **other** Ska jobs' logs for `error/warn/fail/fatal/exception/traceback`. Base classes `JobWatch`, `FileWatch`, `DbWatch` are in `jobwatch.jobwatch`; the Ska-configured subclasses (`SkaJobWatch`, `SkaDbWatch`, `SkaWebWatch`, `SkaSqliteDbWatch`) live in `jobwatch.skawatch`, and `SkaURLWatch`/`SkaFileWatch` in `jobwatch.hourly_watch` | `skawatch3` |
| `fss_check` | `fss_check_daily_fss` | Fine Sun Sensor trending — pitch/roll error vs the OBC solution; `get_large_pitch_roll_error_intervals`, `get_spm_pitch_roll`, `plot_delta_vs_pitch_roll`. Pads around eclipses | `fss_check3` |
| `aca_hi_bgd` | `aca_hi_bgd_update` | ACA high-background events from per-slot background. Uses `BGDAVG`, `AOKALSTR`, `AOACASEQ`, `AOPCADMD`, `EPERIGEE`, `AACCCDPT`, and background-subtracted images | `aca_hi_bgd_mon` |
| `kalman_watch` | `kalman_watch_low_kalman_mon`, `kalman_watch_kalman_perigee_mon`, `kalman_watch_monitor_win_perigee` | Kalman-star health, especially perigee passages (`EventPerigee`, `KalmanDropsData`). Uses `AOKALSTR`, `EPERIGEE`, `ORBPOINT`, `XEF1000`/`EEF1000` | `kalman_watch3` |
| `attitude_error_mon` | `attitude_error_mon` | One-shot and attitude-error trending from `AOATTER1/2/3` — histograms and time plots per observation | `attitude_error_mon` |
| `aca_weekly_report` | `aca_weekly_report` | Weekly roll-up of observed/tracked metrics: acquisition anomalies, guide/fid data, Kalman, maneuvers, max CCD temp, hi-bgd events | `aca_weekly_report` |
| `ska_report_ranges` | *(library, no script)* | **Not a monitor** — the shared helper the others use for report time ranges: `in_month`, `in_quarter`, `in_semi`, `in_year`, `get_update_ranges`, `timerange` | — |

Others in this family not yet detailed here: `aimpoint_mon` (`aimpoint_mon3`),
`fid_drift_mon`, `perigee_health_plots`, `obc_rate_noise_plots`, `acq_stat_reports`,
`guide_stat_reports`, `vv_trending`, `ska_trend`.

## Gotchas

- **`ska3-aca` can be *behind* `ska3-flight` on shared packages, despite a higher version
  number.** Verified 2026-09-03: `ska3-aca` 2026.11 ships `chandra_aca` **4.53.0** while
  `ska3-flight` 2026.9 ships **4.56.0**. The metapackage version says nothing about the
  freshness of the packages inside it. Check `pkg.__version__`, not the environment label.
- **These are in `ska3-aca`, not `ska3-flight`.** A plain `ska3-flight` environment does
  not have them. If an import fails, check which environment you are in before debugging
  further.
- **`jobwatch.skawatch` cannot be imported off HEAD.** It runs
  `sorted(glob("/home/kadi/occ_ska_sync_logs/cheru/*.log"))[-1]` at **module level**
  (`skawatch.py:136`), so importing it anywhere that path is missing raises
  `IndexError: list index out of range`. Use the `skawatch_daily` / `skawatch_hourly`
  console scripts, and expect this tool to be HEAD-only. `jobwatch.jobwatch` (the core
  module with the `*Watch` classes) imports fine everywhere.
- **Most of the data directories are HEAD-only.** On a laptop only a few of these are
  synced (`kalman_watch3` and `aimpoint_mon3` typically are; `skawatch3`, `fss_check3`,
  `aca_hi_bgd_mon`, `attitude_error_mon`, `aca_weekly_report` usually are not). A tool
  failing on a missing `$SKA/data` path offsite is expected, not a bug — see
  [ska-environment.md](../../ska-data-access/references/ska-environment.md).
- **The `3` suffix means "the ska3 era" version of the data dir**, not version 3 of the
  tool: `skawatch3`, `fss_check3`, `kalman_watch3`, `aimpoint_mon3`, `arc3`. The Python 2
  era dirs without the suffix may still exist alongside.
- **Prefer the console script to importing.** These are applications, not libraries. The
  functions are written for the report pipeline and frequently assume the task_schedule
  environment (`$SKA`, a writable data dir, config files).
- **`ska_report_ranges` is the odd one out** — a genuine reusable library. If you are
  writing a new report and need "the current month/quarter/semester" boundaries, use it
  rather than rolling your own.

## Related

- [ska-data-access: ska-environment](../../ska-data-access/references/ska-environment.md) — `$SKA`, the `ska3-aca` environment
- [ska-data-access: data-sources](../../ska-data-access/references/data-sources.md) — cheta vs MAUDE, archive latency
- [chandra_aca](chandra_aca.md) — the image and transform library several of these build on
- [ska router](../../ska/SKILL.md)
