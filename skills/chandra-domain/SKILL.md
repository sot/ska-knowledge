---
name: chandra-domain
description: Chandra X-ray Observatory spacecraft and ACA domain background - coordinate frames and units (CCD row/col, yag/zag arcsec, RA/Dec degrees), quaternion conventions, Chandra time systems and CXC seconds, mission and orbit, aspect camera hardware, observations and dwells, as-run vs scheduled ObsID and undercover (cold ECS blank sky) observations, mission planning and load products. Use when the question is about how the observatory works or what a convention means, rather than which function to call.
---

# Chandra domain background

The conventions and context that are not in any package's API docs. Read these when a
number looks wrong rather than when you need a function name — for function routing use
the [ska router](../ska/SKILL.md).

## Written

| File | Covers |
|---|---|
| [coordinates-and-frames.md](references/coordinates-and-frames.md) | The `row/col ↔ yag/zag ↔ RA/Dec` chain, units at each step, `pix_zero_loc` and `t_aca`, quaternion component order, the three image row/col origins |
| [time-systems.md](references/time-systems.md) | `CxoTime`, the five Chandra-specific formats, CXC seconds and the TT epoch offset, input-guessing rules |
| [aca-hardware.md](references/aca-hardware.md) | Optics and CCD, the ACA coordinate system, image slots and 4×4 / modified 6×6 / 8×8 readouts, readout and centroid cadence (`AOACRPT`), pixel encoding (DN ↔ electrons), how `BGDAVG` is computed, where the status columns come from |
| [obsids-and-undercovers.md](references/obsids-and-undercovers.md) | As-run `obsid` vs scheduled `obsid_sched`, the OR/ER split at 38000, undercover (cold ECS blank sky) observations and how to spot one, obsid behavior after SCS-107 and safe mode |
| [aspect-performance.md](references/aspect-performance.md) | ACA magnitude and its limits, acquisition/tracking success, the track/search dropout cycle on a marginal star, accuracy requirements vs actuals, dither defaults, gyro-hold drift, operational constraints, CCD ageing |

## Most likely to be silently wrong

1. **Quaternion component order is `[x, y, z, w]` — scalar last.** Much of the literature
   and many libraries put the scalar first. Feeding `[w, x, y, z]` gives a wrong attitude
   with no error raised.
2. **CXC seconds count from 1998-01-01 00:00:00 TT, not UTC.** `CxoTime(0)` is
   `1997:365:23:58:56.816`; `1998:001:00:00:00` UTC is `63.184` seconds.
3. **`pix_zero_loc` defaults to `"edge"`** and switching to `"center"` moves you half a
   pixel, ≈ 2.49 arcsec.
4. **`t_aca`'s default changed** (20 → 35.0 degC in `chandra_aca` 4.55.0), as did
   `allow_bad` (False → True) and whether the args are keyword-only. Pass `t_aca`
   explicitly; never inherit it.
5. **A "modified 6×6" readout telemeters 32 pixels, not 36.** The four corners are
   absent — that is the mouse-bitten corner, and the reason every image comes back as a
   masked 8×8.
6. **An 8×8 image takes 4 telemetry updates**, and the last 16 pixels *repeat* until the
   next CCD readout. Consecutive samples are not independent readouts.
7. **Centroids are telemetered every 1.025 s but only refresh every 2.05 s.** Integration
   time is 1.696 s, so the ACA repeats the previous `AOACYAN`/`AOACZAN`/`AOACMAG` values
   and flags it with `AOACRPT` to meet its 1.025 s delivery requirement. Half of every
   raw centroid series is duplicated samples; select `AOACRPT == 0` for independent ones.
8. **`BGDAVG` is a robust average of 8 corner pixels**, not a whole-image mean, so it
   cannot track a gradient across the image.
9. **An observation has two ObsIDs.** `obsid` is as-run, `obsid_sched` is what the
   schedule said; they differ for ~3% of observations, in blocks after SCS-107 and
   singly for undercovers. `obsid_sched` needs `kadi` >= 7.19.0 and is absent from
   the returned dict for pre-APR1420B loads.

## Units cheat sheet

| Quantity | Unit |
|---|---|
| CCD row/col | ACA pixels (≈ 5 arcsec each; can be negative) |
| yag / zag | arcseconds |
| RA / Dec / roll | degrees |
| `secs` / `cxcsec` | seconds since 1998-01-01 00:00:00 **TT** |
| ACA image `IMG` | DN (data numbers); **1 DN ≈ 5 electrons** |
| CCD temperature | degC in `chandra_aca` transforms; K in some cheta paths |

## Not yet written

Mission and orbit, spacecraft subsystems beyond the ACA, dwells and maneuvers,
mission planning and load products beyond the ObsID story, and a glossary.

Until those exist, the public authority for the observatory itself is the Chandra
Proposers' Observatory Guide (https://cxc.harvard.edu/proposer/POG/), and the team's own
overview is the skare3 wiki
[Ska Overview](https://github.com/sot/skare3/wiki/Ska-Overview).
