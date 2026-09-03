# Chandra time systems

Everything goes through **`cxotime.CxoTime`**, a subclass of `astropy.time.Time`. So all of
astropy's formats and scales work, plus five Chandra-specific formats. Never use the legacy
`Chandra.Time.DateTime` in new code.

Verified against `cxotime` 3.11.1 in `ska3-flight` 2026.9.

## The Chandra-specific formats

`cxotime` registers these into astropy at import, so they are available on any `Time`
object once `cxotime` has been imported. The same instant in each:

| Format | Value for `2026:001:12:00:00.000` | Notes |
|---|---|---|
| `date` | `'2026:001:12:00:00.000'` | The canonical Ska string: `YYYY:DOY:HH:MM:SS.sss` |
| `secs` | `883656069.184` | **CXC seconds.** Alias of astropy's `cxcsec` — identical values |
| `greta` | `'2026001.120000000'` | GRETA / FOT tooling format |
| `maude` | `2026001120000000` | MAUDE web API format, an **integer** not a string |
| `frac_year` | `2026.0013698630137` | Fractional year, for trending plots |

Standard astropy formats also work and are often what you want: `iso`, `isot`, `yday`
(same layout as `date`), `jd`, `mjd`, `unix`, `datetime`, `plot_date`.

## The one trap that actually bites

**CXC seconds count from 1998-01-01 00:00:00 *TT*, not UTC.** So:

```python
CxoTime(0).date                      # '1997:365:23:58:56.816'   <- NOT 1998:001
CxoTime('1998:001:00:00:00').secs    # 63.184
```

The 63.184 s offset is TT − UTC at that epoch (32.184 s for TT − TAI, plus 31 leap
seconds). If you assume `secs == 0` is midnight on 1998:001 UTC, everything is off by just
over a minute — small enough to look like a real effect and big enough to matter.

## Input conventions

`CxoTime` guesses the format from the input type, which is convenient and occasionally
surprising:

```python
CxoTime(0).format                    # 'secs'   <- a bare number is CXC seconds
CxoTime('2026:001').format           # 'date'   <- a YYYY:DOY string is a date
CxoTime.now().format                 # 'date'
CxoTime('2026:001').date             # '2026:001:00:00:00.000'  <- partial dates fill with zeros
```

- **Default scale is UTC** (`CxoTime(...).scale == 'utc'`). All the astropy scales are
  available: `tai`, `tt`, `tdb`, `tcb`, `tcg`, `ut1`, `local`.
- Partial `date` strings are accepted and zero-filled, so `'2026:001'` means the start of
  that day. Convenient for range arguments.
- Arithmetic follows astropy: `CxoTime(...) + 1 * u.day` gives a `CxoTime`, and the
  difference of two gives a `TimeDelta`. Use `astropy.units`, not bare numbers, when adding.

## Practical notes

- **`secs` and `cxcsec` are the same number.** Use whichever reads better; there is no
  hidden difference.
- Telemetry time columns are generally CXC seconds — see the per-source timestamp
  conventions in
  [ska-data-access: data-sources](../../ska-data-access/references/data-sources.md), since
  cheta and MAUDE stamp samples differently.
- ACA image `TIME` is **mid-integration**, not the start of the readout. See
  [chandra_aca](../../ska-packages/references/chandra_aca.md).
- For plotting against a time axis, use `ska_matplotlib.plot_cxctime` rather than
  converting by hand.

## Related

- [coordinates-and-frames.md](coordinates-and-frames.md)
- [ska router](../../ska/SKILL.md) — Rule One lists `Chandra.Time.DateTime` as legacy
