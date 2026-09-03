# chandra_aca

Aspect Camera Assembly (ACA) data and transforms: image telemetry, coordinate
conversions, star probabilities, alignment drift, dark current models.

- Docs: https://sot.github.io/chandra_aca
- Repo: https://github.com/sot/chandra_aca
- Source in the active env: `$CONDA_PREFIX/lib/python3.13/site-packages/chandra_aca/`

**Nothing is re-exported at package top level except `chandra_aca.transform`.** Import
from the specific module. `chandra_aca.get_aca_images` does not exist.

## Getting ACA images — read this before choosing

There are four callables with near-identical names. They are **not** competitors; there
is one front door and three backends.

```
chandra_aca.aca_image.get_aca_images(start, stop, bgsub=False, source=...)
    │
    ├── source="maude"  (default) ──> chandra_aca.maude_decom.get_aca_images
    ├── source="cxc"               ──> mica.archive.aca_l0.get_aca_images
    └── source="cheta"             ──> chandra_aca.aca_image.get_aca_images_cheta
```

**Use the front door** unless you have a specific reason not to. It normalizes column
names across backends, adds `IMGSIZE` when the backend omits it, and is the only way to
get background-subtracted images.

```python
from chandra_aca.aca_image import get_aca_images

imgs = get_aca_images("2024:001:00:00:00", "2024:001:00:10:00")   # source="maude"
```

Choosing a source:

| `source` | Backend | Use when |
|---|---|---|
| `"maude"` (default) | MAUDE server | Recent data, including data not yet in the CXC archive. Needs network. |
| `"cxc"` | mica ACA L0 archive | Bulk/historical work, offline, reproducible. Needs the L0 archive on disk. |
| `"cheta"` | cheta telemetry archive | You are already working in cheta and want consistency with other MSIDs. |

**Version gate:** `source="cheta"` and `get_aca_images_cheta` were added in
**chandra_aca 4.56.0** (2026-06-27). Older installs accept only `"maude"` and `"cxc"` and
raise `ValueError` for `"cheta"`. Notably `ska3-aca` 2026.11 ships 4.53.0, so the cheta
backend is **not** available there even though `ska3-flight` 2026.9 (4.56.0) has it —
check `chandra_aca.__version__` rather than assuming.

Call a backend directly only when you want its native behavior and columns — for example
`chandra_aca.maude_decom.get_aca_images` for MAUDE-specific frame handling.

### Background subtraction

`bgsub=True` adds `IMG_BGSUB`, `IMG_DARK`, and `T_CCD_SMOOTH`. It pulls the nearest dark
calibration via `mica.archive.aca_dark.get_dark_cal_props` and smooths CCD temperature,
so it costs extra I/O and requires mica data — do not turn it on by default.

### Gotchas

- **`IMG` is always Nx8x8 and masked.** 4x4 and 6x6 readouts are padded, with the mask
  marking absent pixels. Do not assume the array shape tells you the readout size — use
  `IMGSIZE` (or `IMGTYPE`: 0→4x4, 1→6x6, 4→8x8).
- **Three different row/col origins**, and picking the wrong one silently shifts your
  image: `IMGROW0_8X8`/`IMGCOL0_8X8` (lower-left of the 8x8 masked image — usually what
  you want), `IMGROW0`/`IMGCOL0` (lower-left of the actual 4x4/6x6/8x8 data; for 6x6 this
  is the mouse-bitten corner), and `IMGROW_A1`/`IMGCOL_A1` (the A1 pixel per the ACA
  EQ-spec).
- **Temperature units differ by path.** `get_aca_images_cheta` called directly defaults to
  `unit_system="sci"` (degC). Called *through* `get_aca_images(source="cheta")` it is
  forced to `"cxc"` (K), so the front door matches the other backends. If temperatures are
  off by ~273, this is why.
- **4x4 data masks more than the image.** For queries spanning 4x4 readouts, `BGDRMS`,
  `TEMPCCD`, `TEMPHOUS`, `TEMPPRIM`, `TEMPSEC` and `BGDSTAT` are masked too — those
  fields are not present in 4x4 telemetry.
- `TIME` is **mid-integration** (matching CXC L0), not the start or the downlink time.
- `source="maude"` is wrapped in a 3-try retry on network errors. A hang is more likely
  than an immediate failure; set a timeout if you are scripting it.

## Other modules

| Module | For |
|---|---|
| `transform` | The only module re-exported at top level. yag/zag ↔ RA/Dec ↔ CCD pixels, mag ↔ count rate, target/ACA offsets. |
| `aca_image` | `ACAImage` (ndarray subclass carrying its `row0`/`col0` origin), image fetching, `centroid_fm`, `AcaPsfLibrary`. |
| `maude_decom` | Raw MAUDE packet/blob decoding. Below the level most analysis needs. |
| `star_probs` | Acquisition and guide success probability models. |
| `drift` | ACA alignment drift and aimpoint offsets vs. time. |
| `dark_model`, `darkbins` | Dark current distribution models. |
| `dark_subtract` | Machinery behind `bgsub=True`. |
| `centroid_resid` | Centroid residuals vs. an attitude solution. |
| `planets` | Planet/solar-system body positions in ACA frames. |
| `plot` | Star field and catalog plotting. |

## Related

- [cheta](cheta.md) — the telemetry archive behind `source="cheta"`
- [mica](mica.md) — the L0 archive and dark cals behind `source="cxc"` and `bgsub=True`
- [agasc](agasc.md) — the star catalog the images are of
- [chandra-domain: coordinates and frames](../../chandra-domain/references/coordinates-and-frames.md)
