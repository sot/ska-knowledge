# Load products: OCCweb working area vs released mplogs

Where the FOT mission planning products for a load live, which copy to trust, and how
to read the star catalog out of them. Matters whenever you are comparing what proseco
selected, what sparkles reviewed, and what starcheck saw for the same obsid.

Verified against the NOV1626A load with `kadi` 7.22.0, `proseco` 5.19.0, `sparkles`
4.31.3 in `ska3` (flight), 2026-11.

## Links

- `kadi.occweb` — installed source `kadi/occweb.py`
- `proseco` — https://sot.github.io/proseco
- `sparkles` — https://sot.github.io/sparkles

## Two places, two lifecycles

| Location | Owner | Lifecycle |
|---|---|---|
| OCCweb `FOT/mission_planning/Backstop/<LOAD>/` | FOT mission planning | **Working area.** Products land here for the informal preliminary review and are **overwritten in place** if that review flags something that needs correcting (e.g. a star catalog re-selected to fix a critical warning). |
| `mpcrit1/mplogs/<YYYY>/<WEEK>/ofls<v>/` | SOT mission planning | **Formally released** for full review. Products here **never change.** |

Consequence: anything found in a preliminary review exists only on OCCweb, and only
until the corrected products overwrite it. If an investigation might need the
pre-correction state, copy the whole OCCweb load directory locally **before** the fix
lands. Nothing keeps the old version.

`<LOAD>` is the load name with version letter (`NOV1626A`); in mplogs the week is
`NOV1626` and the version is the `ofls<v>` suffix (`oflsa`).

## OCCweb layout

Under `FOT/mission_planning/Backstop/<LOAD>/`:

| Path | What |
|---|---|
| `CR*.backstop` | Backstop commands |
| `starcheck.txt`, `starcheck.html`, `starcheck/` | Starcheck run on the current products |
| `matlab/starcheck/obsids.json` | Starcheck per-obsid data as JSON (see below) |
| `matlab/` | FOT MATLAB tool outputs: `<LOAD>.mat`, warnings/config logs, `cmpreview_*` logs and emails, ORviewer tarball |
| `output/<LOAD>_proseco.pkl.gz` | proseco catalogs the load was built from |
| `output/<LOAD>_dynamical_offsets.txt`, `output/TEST_*.txt` | Other FOT checks |

## Fetching from OCCweb

OCCweb uses basic auth. `kadi.occweb` reads credentials from `~/.netrc`:

```python
from kadi.occweb import get_occweb_page

base = "FOT/mission_planning/Backstop/NOV1626A/"
listing = get_occweb_page(base)  # Apache index HTML, with modification times
obsids = json.loads(get_occweb_page(base + "matlab/starcheck/obsids.json", cache=True))
pkl = get_occweb_page(base + "output/NOV1626A_proseco.pkl.gz", binary=True)
```

`path` can be relative to `https://occweb.cfa.harvard.edu/occweb/` or a full URL. Use the
directory listing's timestamps to tell which products were regenerated after a
preliminary review.

## The proseco pickle

```python
import gzip, pickle
acas = pickle.load(gzip.open("NOV1626A_proseco.pkl.gz", "rb"))
aca = acas[32816.0]  # keys are FLOAT obsids; acas[32816] raises KeyError
```

- A `dict` of `proseco.catalog.ACATable`. `aca.call_args` holds the selection inputs.
  Review-driven changes appear there as `include_ids_guide` / `exclude_ids_guide` (and
  the acq equivalents). Diffing `call_args` between two pickles is the quickest way to
  see what a review changed.
- `aca.log_info["unix_run_time"]` is when proseco ran. It identifies which run a pickle
  came from.
- **The dark map is not pickled, only `dark_date`.** The first access of `aca.dark`
  fetches the dark cal nearest `dark_date` from the *local* mica archive. That adds
  `dark` events to `log_info` with a large `dt`, timed from your access rather than the
  FOT run. proseco warns if `dark_date` disagrees with the dark cal before the obs date.
  This shows the dark cal *date* is consistent, not that the local pixels match what FOT
  had.
- `aca.agasc_file` records the AGASC path FOT used, typically a Windows path to
  `proseco_agasc_*.h5`.
- To review one catalog with sparkles, wrap it:
  `acar = ACAReviewTable(aca); acar.run_aca_review(); acar.messages`.
  `run_aca_review(acars=[aca])` rejects a plain `ACATable`.

## Starcheck `obsids.json`

A list of per-obsid dicts (not keyed). Each has `proseco_args` (the inputs starcheck
used to re-run proseco), `yellow_warn` / `orange_warn` / `warn`, `figure_of_merit`, and
`commands`. The catalog is the `MP_STARCAT` entry in `commands`, flattened as
`<FIELD><i>` for `i = 1..16`:

| Field | Meaning |
|---|---|
| `TYPE{i}` | `ACQ`, `BOT`, `GUI`, `FID`, `MON`, or `NUL` (empty) |
| `IMNUM{i}` | Slot |
| `GS_ID{i}` | AGASC id (fid number for fids) |
| `YANG{i}`, `ZANG{i}` | **Commanded** position (arcsec), from the backstop |
| `GS_YANG{i}`, `GS_ZANG{i}` | Position starcheck computes from the AGASC at the commanded attitude |
| `HALFW{i}`, `MAXMAG{i}`, `DIMDTS{i}` | Search box half-width, max mag, DIM/DTS |

```python
obs = {o["obsid"]: o for o in obsids}[32816]
cat = next(c for c in obs["commands"] if c["cmd"] == "MP_STARCAT")
```

## Gotchas

1. **The local copy of an OCCweb product may be stale.** A pickle or `obsids.json` you
   copied earlier can predate a review-driven overwrite. Compare `unix_run_time` and the
   OCCweb listing times before concluding that two tools disagree.
2. **Starcheck's proseco inputs are not the pickle's.** Starcheck re-derives `date` and
   `t_ccd` from the backstop and thermal model. In NOV1626A they differed by ~10 s and
   ~0.08 C from the pickle's `call_args`. Small, but enough to shift probabilities.
3. **Commanded positions are not proseco's positions.** In NOV1626A, backstop `YANG`/`ZANG`
   minus proseco `yang`/`zang` was +0.09 arcsec in both axes with ~0.04 arcsec scatter,
   for fids as well as stars and in every obsid. `GS_YANG`/`GS_ZANG` matched proseco to
   <0.01 arcsec. Origin unknown, and operationally irrelevant next to 25–160 arcsec search
   boxes, but don't mistake it for an attitude or AGASC discrepancy.
4. **Command quantization is 0.00625 arcsec.** `AOSTRCAT` `AO_nn_YANGLEnn` / `ZANGLEnn` are
   20-bit fields scaled at 3.03e-8 rad per count (CDB `MCMD_FLD.txt` under
   `Ska.tdb/cdb/p010/`).

## Related

- [obsids-and-undercovers.md](obsids-and-undercovers.md): which obsid a load product is
  keyed on
- [ska-data-access](../../ska-data-access/SKILL.md): `kadi.commands` for what was
  actually commanded once a load is approved
