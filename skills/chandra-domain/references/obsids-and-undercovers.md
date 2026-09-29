# ObsIDs: as-run vs scheduled, and undercover observations

An observation has **two** ObsIDs, and they are not always the same. Most code that keys
report directories, database rows or filenames on "the obsid" has to decide which one it
means, and the wrong choice only shows up after a load stoppage or an undercover.

Verified against `kadi` 7.22.0 in `ska3` (flight), 2026-09.

## Links

- `kadi.commands.get_observations` — https://sot.github.io/kadi/commands_states.html
- Installed source: `kadi/commands/observations.py`, `kadi/commands/commands_v2.py`

## The two ObsIDs

| Key | Comes from | Meaning |
|---|---|---|
| `obsid` | the `COAOSQID` command actually in the load | **As-run.** What the OBC was told, what appears in telemetry (`COBSRQID`) and in the science archive |
| `obsid_sched` | the `OBSID_SCH` pseudo-command from the MP products | **Scheduled.** What the schedule said this dwell was for |

```python
>>> import kadi.commands as kc
>>> kc.get_observations(obsid_sched=31488)[0]
{'obsid': 65517, 'obsid_sched': 31488, 'obs_start': '2025:316:12:06:21.994',
 'simpos': -99616, 'source': 'NOV0825A', ...}
```

Both are filter kwargs on `get_observations()`. Over 2020:001–2026:272 about 3% of
observations (532 of 15884) have `obsid != obsid_sched`.

**Version gate.** `obsid_sched` was added in `kadi` **7.19.0**. `ska3-aca` 2026.11 ships
7.18.1, where neither the key nor the filter kwarg exists — passing `obsid_sched=` there
raises `TypeError`, so it fails loudly rather than silently returning as-run obsids. Code
that needs it must state the requirement rather than assume it.

**Pre-APR1420B.** Loads before APR1420B have no `OBSID_SCH`, so the returned observation
dict has **no `obsid_sched` key at all** — use `obs.get("obsid_sched", obs["obsid"])`. The
`obsid_sched=` filter kwarg still works there, falling back to `obsid` internally
(kadi 7.22.0), so the kwarg working is not evidence the key is present.

## OR vs ER

The split is at 38000: `obsid <= 38000` is an OR (a science observation with a proposal
behind it), above that is an ER (engineering request). `razl.observations` exposes this as
`is_OR()` / `is_ER()`. Code frequently uses "is it an ER" as a proxy for "is there a
ground aspect solution in the archive" — which is why *which* obsid you pick changes
behavior, not just a label.

## Undercover observations

An **undercover** is a cold ACIS ECS (External Calibration Source) blank-sky measurement
run in the middle of an already-scheduled science dwell. The target name is normally
**"Cold ECS Blank Sky"**; the comment in `kadi/commands/commands_v2.py` writes it as
`target="cold blank ECS"`.

The mechanism is a **mid-dwell obsid change**: the load commands the science obsid, runs
it briefly, then re-commands the obsid to a pre-assigned ER while the attitude, star
catalog and dither keep running unchanged. Both `COAOSQID` and `OBSID_SCH` are re-issued
at the switch, from the load itself:

```
2020:366:17:04:14.000 MP_OBSID    COAOSQID DEC2820A scs=132 {'id': 24882}
2020:366:17:04:14.000 LOAD_EVENT  OBSID_SCH DEC2820A scs=129 {'id': 24882}
2020:366:17:13:47.146 MP_OBSID    COAOSQID DEC2820A scs=132 {'id': 62647}   <- switch
2020:366:17:13:47.146 LOAD_EVENT  OBSID_SCH DEC2820A scs=129 {'id': 62647}
```

kadi's state machine splits the dwell into two OBS records at the `COAOSQID` change. The
second record gets the ER as `obsid` but **inherits the `obsid_sched` captured when the
OBS command was emitted** at dwell start — so it reports `obsid_sched = 24882` even though
`OBSID_SCH` says 62647 by then. That inheritance is what makes `obsid_sched` usable as
"the science observation this dwell was scheduled for"; it is not a straight reading of
`OBSID_SCH` at the switch.

Worked example, DEC2820A:

```
 obsid   sched   obs_start                obs_stop                simpos   starcat
 22949   22949   2020:366:11:09:54.252    2020:366:17:04:14.000   -99616   yes
 24882   24882   2020:366:17:11:37.397    2020:366:17:13:47.146   -99616   yes   <- 130 s stub
 62647   24882   2020:366:17:13:47.146    2020:366:22:49:17.146   -99616   yes   <- undercover
 23834   23834   2020:366:23:19:02.844    2021:001:06:45:14.163    75624   yes
```

The signature, all four together:

- `obsid` is an ER in the low 626xx range; `obsid_sched` is the displaced science obsid
- the two halves **share a `starcat_date`** — one catalog, one dwell, one attitude
- `simpos == -99616`, the parked SIM position
- `source` is an ordinary approved load, and there are **no `CMD_EVT` commands nearby** —
  this is in the schedule, not a real-time reaction

Measured over 2020:001–2026:272: 14 undercovers, from 2020:366 to 2022:274, each using a
distinct ER obsid drawn from a descending pool (62647 down to 62625). The science stub
before the switch runs 130–500 s; the undercover dwell itself is 9–39 ks.

Not every 626xx observation is an undercover. Standalone ECS measurements are scheduled
with their own obsid from the start and have `obsid == obsid_sched` (e.g. 62648, 62652,
62653).

## The other reason the two differ: loads stopped

After SCS-107 or a safe mode the observing loads stop, the SIM parks at -99616, and a
manually commanded obsid (`CMD_EVT` source) sticks for every subsequent dwell until the
loads resume. Those dwells keep their individual `obsid_sched` values but all share one
as-run `obsid`, so mismatches arrive in blocks of tens:

```
2025:315:10:58:50  SCS-107     -> SIMTRANS to -99616, ACIS shutdown
2025:315:17:12:14  MP_OBSID COAOSQID {'event': 'Obsid', 'id': 65517}
      ... every dwell through 2025:318 runs as obsid 65517 ...
```

Telling the two causes apart matters: an undercover is one or two observations inside a
healthy load, a stoppage is a multi-day block. Checking `kadi.events.scs107s` and
`kadi.events.safe_suns` over the interval separates them. Over 2020:001–2026:272 there
were 34 SCS-107 events and 4 safe suns.

kadi merges the OBS split that a *manual* (`CMD_EVT`) obsid change would otherwise cause,
controlled by `kadi.commands.conf.merge_manual_obsid_change_obs_splits` (default `True`,
added in `kadi` 7.20.0). That merging applies only to `CMD_EVT` sources — **undercover
splits are never merged**, because they come from the load itself.

## Gotchas

- **Keying on `obsid` collapses a whole stoppage into one directory.** Every dwell in a
  multi-day SCS-107 block shares the as-run obsid. Trending and per-observation report
  trees normally want `obsid_sched`.
- **Switching to `obsid_sched` can flip an ER into an OR.** An undercover keyed on
  `obsid_sched` becomes a 5-digit science obsid, so `is_ER()` goes False and code will go
  looking for a mica ASP L1 ground aspect solution that does not exist — the observation
  never ran under that obsid. Symptom: missing-data errors on exactly the handful of
  observations that had an obsid mismatch in a healthy load.
- **You cannot look up an ER's target name locally.** `mica.archive.obspar.get_obspar()`
  returns `None` for 626xx obsids (ERs are not in the science archive), and the starcheck
  database has `target_id = None` for them. Identify an undercover from the command
  pattern above, not from a target name lookup.
- **`obsid == 0` is neither.** It shows up during safe-mode recoveries; treat it as "no
  valid obsid" rather than as an OR.
- **`obsid_sched` is not simply "the latest `OBSID_SCH`".** For an undercover the load
  re-commands `OBSID_SCH` to the ER too, and the reported `obsid_sched` is the value at
  dwell start, inherited by the split record. Reading the command directly and expecting
  to reproduce `get_observations()` will disagree on exactly these cases.

## Related

- [ska router](../../ska/SKILL.md) — which kadi entry point to reach for
- [aspect-performance.md](aspect-performance.md) — what per-observation trending measures
