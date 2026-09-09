---
name: ska-coding-style
description: How the ACA/SOT team actually writes Ska analysis code - import aliases (apt, kc, fetch_eng), plot_cxctime instead of datetime64, CxoTime cast early, astropy Table with `ok` masks, logical_intervals instead of hand-rolled edge finding, and the skare3 self-code-review checklist. Use whenever writing or reviewing Python that touches cheta, kadi, chandra_aca, CxoTime or matplotlib for Chandra data, so the result reads like team code.
---

# Ska coding style

What makes code look like it belongs in this group. These are **conventions, not APIs** —
the public docs will not tell you any of it, and code volume on GitHub argues the other
way, so state them explicitly rather than inferring from what "works".

Derived from ~26 analysis notebooks in `sot/skanb` with commits by taldcroft since 2023,
plus the [skare3 self-code-review checklist](https://github.com/sot/skare3/wiki/Self-code-review)
(condensed in [references/self-code-review.md](references/self-code-review.md)).

## The import block

Grouped stdlib → third-party → Ska, and these aliases are not optional — they appear in
nearly every notebook:

```python
from pathlib import Path

import astropy.table as apt
import astropy.units as u
import kadi.commands as kc
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
from kadi import events

from cheta import fetch_eng
from cheta.utils import logical_intervals
from cxotime import CxoTime
from ska_matplotlib import plot_cxctime
```

| Convention | Not |
|---|---|
| `import astropy.table as apt` → `apt.Table`, `apt.vstack` | `from astropy.table import Table` (used, but `apt` dominates) |
| `import astropy.units as u` | `from astropy import units` |
| `import kadi.commands as kc` → `kc.get_observations` | `from kadi.commands import get_observations` |
| `from kadi import events` → `events.manvrs`, `events.dwells` | `import kadi.events` |
| `from cheta import fetch_eng` / `fetch_sci` / `fetch` | `import cheta.fetch as fetch` |

Legacy `Ska.engarchive` / `Chandra.Time` are a separate and worse error — see
[ska](../ska/SKILL.md) rule one.

## Plotting: `plot_cxctime`, never `datetime64`

**Time axes always go through `ska_matplotlib.plot_cxctime`.** It takes CXC seconds
directly and handles the date formatting and locators. Converting to `datetime64` or
`datetime` and calling `ax.plot` is the single most obvious tell of outside code.

```python
plot_cxctime(msid.times, msid.vals, ".", ms=2, ax=ax)          # YES
ax.plot(CxoTime(msid.times).datetime64, msid.vals, ".")        # NO
```

Signature is `plot_cxctime(times, y, fmt=None, fig=None, ax=None, ...)` — `fmt` is
positional, in the third slot, and `**kwargs` pass through to `ax.plot`.

A cheta MSID also plots itself: `msid.plot(ax=ax, lw=0.3)`.

Other plotting conventions:

- `matplotlib.style.use("bmh")` at the top of every notebook. Import it as
  `import matplotlib.style` (not `plt.style`).
- Axes are named `ax0, ax1, ax2` — `fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(12, 4))`.
  `axes` for a grid. Use `_` for a figure you will not touch: `_, ax = plt.subplots()`.
- A plotting helper takes `ax=None` and makes its own:

  ```python
  def plot_thing(start, stop, ax=None):
      if ax is None:
          _, ax = plt.subplots()
  ```

## Time: cast once, at the top

`CxoTime` for everything. Cast a `CxoTimeLike` argument on entry to the function and use
the object from then on — do not re-cast inside a loop:

```python
start = CxoTime(start)                      # at the top of the function
stop = CxoTime(stop)
q_att = fetch_eng.Msid("quat_aoattqt", start - 1 * u.day, stop + 1 * u.day)
```

`CxoTime` arithmetic with `astropy.units` quantities works and is preferred over raw
seconds: `stop - start < 60 * u.s`, `start - 5 * u.min`.

**Compare date strings directly when the API guarantees the format.** Ska `date` columns
are always the `YYYY:DDD:HH:MM:SS.sss` format, which sorts lexically, so this is correct
and much faster than casting a whole column:

```python
ok = (att_err["date"] > "2025:196") & (att_err["date"] < "2025:197")
```

Use `.secs` and `.date` to get out; `date2secs` / `secs2date` from `cxotime` for bulk
conversion of arrays.

## Tables: astropy `Table`, and the `ok` mask

Everything is an astropy `Table` (never pandas). The boolean-mask variable is named `ok`,
built in a parenthesized multi-line expression:

```python
ok = (
    (att_err["dwell_duration"] < 2000)
    & (att_err["date"] > "2025:196")
)
plot_cxctime(att_err["time"][ok], att_err["point_err"][ok], ".")
```

**Mask the column, not the table** — `dat[colname][ok]` is fast, `dat[ok][colname]` builds
a whole intermediate table first.

Set display formats on columns rather than formatting at print time:

```python
att_err["point_err"].info.format = ".2f"
```

Build tables up by column assignment, stack with `apt.vstack(list_of_tables)`, group with
`tbl.group_by("idx_manvr")` and iterate `zip(grp.groups, grp.groups.indices)`.

## cheta

**`fetch.Msid`, not `fetch.MSID`.** They are different classes: `Msid` subclasses `MSID`
with `filter_bad=True`, so bad samples are already removed and `vals`/`times` line up.
`MSID` leaves them in behind a `.bads` mask. Default to `Msid` unless you specifically
want the bad values.

Pick the unit system at import: `fetch_eng` (engineering units — the common choice),
`fetch_sci` (science, e.g. degC), or plain `fetch` (CXC units).

**String-valued MSIDs are not space-padded.** Compare directly; `np.char.strip` is
unnecessary noise:

```python
ok = pcadmd.vals == "NPNT"        # YES  (verified: dtype <U4, no padding)
ok = np.char.strip(pcadmd.vals) == "NPNT"   # NO
```

**Do not hand-roll interval finding.** `cheta.utils.logical_intervals(times, bools)`
returns a Table of `tstart` / `tstop` / `duration`; map back to sample indices with
`np.searchsorted`:

```python
intervals = logical_intervals(pcadmd.times, pcadmd.vals == "NPNT")
i0, i1 = np.searchsorted(dat["time"], [intervals["tstart"][0], intervals["tstop"][0]])
```

To restrict an MSID to kadi event intervals, use the built-in rather than masking by hand:

```python
dwells = events.dwells(pad=(-500, -100))
aoatter2_dwells = aoatter2.select_intervals(dwells, copy=True)
```

## kadi

```python
obss = apt.Table(kc.get_observations(start, stop))     # commands: what was planned
manvrs = events.manvrs.filter(start, stop).table        # events: what the spacecraft did
```

`kadi.events` queries are Django-style — `.filter(start, stop, dur__gt=1000)` — and
`.table` gets you the astropy `Table`. Relative times work: `kc.get_observations("-1 yr")`.

## Naming and constants

Module-level constants are `UPPER_SNAKE` with the unit in a trailing comment:

```python
INT_TIME = 1.696          # Integration time in seconds
BAD_PIXEL_LOW = -5        # Limit below which a pixel is considered corrupted (DN)
DN_TO_ELEC = np.float32(5.0 / 1.696)
```

Short domain names are fine and preferred over long descriptive ones: `dat`, `ok`, `evs`,
`obss`, `msid`, `i0`/`i1` for index pairs, `q_att` for an attitude quaternion.

## Before writing the code

Read [references/self-code-review.md](references/self-code-review.md) — DRY, cast early,
mask-then-column, ternary. It is short and it is the checklist reviewers actually apply.

For notebook-specific conventions (header cell, `%matplotlib inline`, trailing semicolons)
see [references/analysis-notebooks.md](references/analysis-notebooks.md).
