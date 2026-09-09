# Analysis notebook conventions

## What it's for

The shape of a `sot/skanb`-style exploratory notebook, and a worked before/after showing
what changes when generic Python is rewritten in team style.

## Links

- `sot/skanb` — the team's analysis notebook repo, the source for everything here.
- Conventions distilled in [../SKILL.md](../SKILL.md).

## The header cell

Every notebook opens the same way: imports grouped stdlib → third-party → Ska, then the
style, then the magic.

```python
# Standard library imports
import functools
from pathlib import Path

# Third-party imports
import astropy.table as apt
import astropy.units as u
import kadi.commands as kc
from kadi import events
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np

# Ska/Chandra imports
from cheta import fetch_eng
from cxotime import CxoTime
from ska_matplotlib import plot_cxctime

matplotlib.style.use("bmh")

%matplotlib inline
```

When working against a dev checkout rather than the installed package, that goes first:

```python
sys.path.insert(0, (Path.home() / "git" / "chandra_aca").as_posix())
```

## Notebook-only conventions

These are notebook habits, not things to carry into a package:

- **Trailing semicolon** on the last plotting call of a cell, to suppress the repr:
  `plt.hist(earth_viols4["duration"], bins=50);`
- **A bare table or `tbl.info` as the last line** of a cell is the display idiom — not
  `print(tbl)`. `tbl.pprint_all()` when the default truncation gets in the way.
- `plt.rcParams["figure.dpi"] = 72` and `["savefig.dpi"] = 72` in notebooks that produce
  many figures.
- Successive cells reassigning the same name (`att_err = att_err[...]`) is normal and fine
  here; it is not fine in a module.

## Worked example: generic Python → team style

A script plotting `AOACMAG5` for a day, shading non-tracking intervals. Both versions run
and produce the same numbers; only the second reads like team code.

**Before** — nothing here is *wrong*, and that is the point:

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from cheta import fetch
from cxotime import CxoTime

start, stop = '2026:001:00:00:00', '2026:002:00:00:00'
dat = fetch.MSIDset(['aoacmag5', 'aoacfct5', 'cobsrqid'], start, stop)
mag, fct = dat['aoacmag5'], dat['aoacfct5']

# cheta string vals carry trailing spaces
func = np.char.strip(fct.vals)
t = CxoTime(mag.times).datetime64
trak = np.interp(mag.times, fct.times, (func == 'TRAK').astype(float)) > 0.5

fig, ax = plt.subplots(figsize=(12, 5))
edges = np.flatnonzero(np.diff(trak.astype(int))) + 1
for i0, i1 in zip(np.r_[0, edges], np.r_[edges, len(trak)]):
    if not trak[i0]:
        ax.axvspan(t[i0], t[i1 - 1], color='0.85', lw=0, zorder=0)
ax.plot(t[trak], mag.vals[trak], '.', ms=2, color='C0', zorder=3)
```

Six separate tells:

| Before | After | Why |
|---|---|---|
| `CxoTime(...).datetime64` + `ax.plot` | `plot_cxctime(times, vals, ".", ax=ax)` | the big one — time axes always go through `plot_cxctime` |
| `np.char.strip(fct.vals)` | `fct.vals != "TRAK"` | string MSIDs are not space-padded; the comment was simply wrong |
| hand-rolled `np.diff` / `flatnonzero` edge finding | `logical_intervals(times, bools)` | this exists precisely for this, and returns tstart/tstop/duration |
| `np.interp` to align the flag onto mag samples | `np.searchsorted` on interval edges | interp on a boolean cast to float is fragile at the transitions |
| `fetch.MSIDset` | `fetch.Msid` per MSID | `Msid` filters bad samples; `MSID` does not |
| single quotes, `matplotlib.use('Agg')`, no style | double quotes, `matplotlib.style.use("bmh")` | ruff formatting and the house plot style |

**After** — the core of it:

```python
matplotlib.style.use("bmh")

START = "2026:001"
STOP = "2026:002"
SLOT = 5


def get_tracking_mask(times, not_trak):
    """Bool mask of ``times`` samples outside the ``not_trak`` intervals."""
    ok = np.ones(len(times), dtype=bool)
    for interval in not_trak:
        i0, i1 = np.searchsorted(times, [interval["tstart"], interval["tstop"]])
        ok[i0:i1] = False
    return ok


mag = fetch.Msid(f"aoacmag{SLOT}", START, STOP)
fct = fetch.Msid(f"aoacfct{SLOT}", START, STOP)

not_trak = logical_intervals(fct.times, fct.vals != "TRAK")
ok = get_tracking_mask(mag.times, not_trak)

_, ax = plt.subplots(figsize=(12, 5))
for interval in not_trak:
    x0, x1 = cxctime2plotdate([interval["tstart"], interval["tstop"]])
    ax.axvspan(x0, x1, color="0.85", lw=0, zorder=0)

plot_cxctime(mag.times[ok], mag.vals[ok], ".", ms=2, color="C0", ax=ax, zorder=3)
```

Note `not_trak` is computed **once** and passed in, rather than recomputed inside the
helper — the DRY check from [self-code-review.md](self-code-review.md) applied to an
expression, not a block.

## Gotchas

- **`ax.axvspan` / `ax.axvline` on a `plot_cxctime` axis need plot-date x values.**
  `plot_cxctime` puts matplotlib date numbers on the axis (days since the 1970 epoch,
  so ~19500 for a recent date), not CXC seconds (~8e8). Passing raw `times` to a span or
  line puts it millions of days off-scale — the span vanishes rather than erroring, and
  date formatting can raise `OverflowError`. Convert with
  `ska_matplotlib.cxctime2plotdate`.
- `plot_cxctime`'s third positional argument is `fmt`, so `plot_cxctime(x, y, ".", ax=ax)`
  works but `plot_cxctime(x, y, ax, ".")` does not.

## Related

- [../SKILL.md](../SKILL.md) — the conventions themselves.
- [self-code-review.md](self-code-review.md) — the pre-review checklist.
