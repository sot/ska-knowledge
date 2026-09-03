---
name: chandra-domain
description: Chandra X-ray Observatory spacecraft and ACA domain background - coordinate frames and units (CCD row/col, yag/zag arcsec, RA/Dec degrees), quaternion conventions, Chandra time systems and CXC seconds, mission and orbit, aspect camera hardware, observations and dwells, mission planning and load products. Use when the question is about how the observatory works or what a convention means, rather than which function to call.
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

## The four things most likely to be silently wrong

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

## Units cheat sheet

| Quantity | Unit |
|---|---|
| CCD row/col | ACA pixels (≈ 5 arcsec each; can be negative) |
| yag / zag | arcseconds |
| RA / Dec / roll | degrees |
| `secs` / `cxcsec` | seconds since 1998-01-01 00:00:00 **TT** |
| ACA image `IMG` | DN (data numbers) |
| CCD temperature | degC in `chandra_aca` transforms; K in some cheta paths |

## Not yet written

Mission and orbit, spacecraft subsystems, ACA hardware (optics, CCD, readout modes,
slots, dark current), star catalogs and ACA magnitudes, observations and dwells, mission
planning and load products, and a glossary.

Until those exist, the public authority for the observatory itself is the Chandra
Proposers' Observatory Guide (https://cxc.harvard.edu/proposer/POG/), and the team's own
overview is the skare3 wiki
[Ska Overview](https://github.com/sot/skare3/wiki/Ska-Overview).
