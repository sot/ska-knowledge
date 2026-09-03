# Choosing a telemetry / data source

## cheta vs MAUDE

**Complementary, not competing.** Cheta is a fast on-disk archive; MAUDE is a web service
that also has real-time data.

| | cheta | MAUDE |
|---|---|---|
| Storage | On-disk, ~225 GB (circa 2025) | Web server over a ~TB archive |
| Coverage | Back-orbit only, updated daily | Real-time **+** back-orbit soon after each comm |
| Query limit | Memory only | 200,000 points **or** 3.2 MB per MSID query |
| Speed | ~20M points/sec | ~200k points/sec |
| Languages | Python only | Python, JavaScript, anything (it is a web API) |
| State codes | *Mostly* match the TDB (e.g. `3TSCMOV`) | *Strictly* match the TDB |
| String values | Trailing spaces: `"ON "`, `"OFF"` | No trailing spaces: `"ON"`, `"OFF"` |
| SI telemetry | Includes some (ACIS FP, HRC SS) | Does **not** include SI telemetry |
| Time stamp | Beginning of the sample interval | Beginning of the minor frame |

### The traps

- **Trailing spaces.** `msid.vals == "ON"` silently fails on cheta, where the value is
  `"ON "`. Use `.strip()`, or compare against the TDB state code. This is the single most
  common source of "my filter matches nothing".
- **The 200k point / 3.2 MB MAUDE cap is per MSID query**, not per request. Long spans
  need chunking; cheta has no such limit.
- **Time stamps are not the same convention** — sample interval vs minor frame. Do not
  mix sources on one time axis without checking.
- **SI telemetry is cheta-only.** If you need ACIS focal plane or HRC shield-sum, MAUDE
  cannot give it to you.

### Using both

Cheta can read MAUDE directly and will stitch the fast on-disk archive together with
recent MAUDE data to fill the tail. See
https://sot.github.io/cheta/fetch_tutorial.html#maude-telemetry-server.

## kadi: events vs commands vs states

| | Source | Answers |
|---|---|---|
| `kadi.events` | Telemetry + web resources | What the spacecraft **did** — maneuvers, NPM dwells, obsids, mech moves, momentum dumps, orbit events; plus CAPs, DSN passes, load segments from the web |
| `kadi.commands` | Load products + Command Events | What was **commanded** — every load command run on-board *or approved to run*, plus non-load commands (SCS-107, real-time ground commanding). Includes predictive commands. |
| `kadi.commands.states` | Derived from commands | **State** vs time — sun pitch, SIM position, ACIS config. Also predictive. |

### Freshness — they differ sharply

- **`kadi.commands` is always fresh.** The last 30 days are generated dynamically from the
  [Command Events sheet](https://docs.google.com/spreadsheets/d/19d6XqBhWoFjC-z1lS1nM6wLE_zjr4GYB1lOvrEGCbKQ/edit)
  (maintained by FOT MP) plus OCCweb, layered on archive HDF5 files that sync at least
  every 4 weeks. You do not need to worry about staleness here.
- **`kadi.events` lags.** Cron starts 7am and finishes in a minute or two, but it depends
  on the cheta ingest that completes ~6:30am. Effectively up to a day behind.

## Data latency, end to end

| Step | Timing |
|---|---|
| cheta CXC L0 ingest | Starts 4am local, generally done by 6:30am |
| kadi events processing | Starts 7am, finishes in a minute or two |
| HEAD → GRETA sync | 7:30am local, done within 15 minutes |
| kadi commands archive files | Updated on HEAD every 10 minutes (plus the dynamic 30-day window) |

**The clock-correlation stall.** After a safe mode or any event that significantly
disturbs clock correlation, CXCDS waits for a new correlation before processing. That can
take **several days**, during which CXC L0 processing halts and **cheta stops updating
entirely**. If cheta looks frozen after an anomaly, this is why — use MAUDE for the gap.

## Quick decision

- Need the last few hours, or real time → **MAUDE**
- Need bulk history, speed, or SI telemetry → **cheta**
- Need what was commanded, including the near future → **`kadi.commands`**
- Need what actually happened, as discrete events → **`kadi.events`**
- Need a state (pitch, SIM, ACIS config) over a span → **`kadi.commands.states`**

## Related

- [ska-environment.md](ska-environment.md) — where the data lives and how to sync it
- [ska router](../../ska/SKILL.md)
- Upstream: [Ska Overview](https://github.com/sot/skare3/wiki/Ska-Overview), which is the
  source for most of this page
