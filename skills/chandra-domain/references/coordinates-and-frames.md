# Coordinates and frames

The chain you almost always want, and the units at each step:

```
CCD row/col  <->  yag/zag  <->  RA/Dec
  (pixels)       (arcsec)      (degrees)
                                  ^
                        needs an attitude quaternion
```

Verified against `chandra_aca` 4.56.0 / `Quaternion` 4.3.2 in `ska3-flight` 2026.9.

## The functions

All in `chandra_aca.transform` — the one module `chandra_aca` re-exports at top level.

```python
pixels_to_yagzag(row, col, *, allow_bad=True, flight=False, t_aca=35.0, pix_zero_loc="edge")
yagzag_to_pixels(yang, zang, *, allow_bad=True, flight=False, t_aca=35.0, pix_zero_loc="edge")
yagzag_to_radec(yag, zag, q_att)
radec_to_yagzag(ra, dec, q_att)
```

Note the `*`: everything after `row, col` is **keyword-only**. Passing `pix_zero_loc`
positionally is a `TypeError`, not a silent misread.

A full round trip is good to ~1e-4 pixel:

```python
y, z = pixels_to_yagzag(123.4, -56.7)     # -> -585.784, -306.269 arcsec
yagzag_to_pixels(y, z)                    # -> 123.399887, -56.700191
```

## Units, stated plainly

- **row/col** — ACA CCD pixels. Can be negative; the CCD is indexed about its center.
- **yag/zag** — Y-angle and Z-angle, in **arcseconds**. Confirmed: with an identity
  attitude, `radec_to_yagzag(ra=1.0, dec=0.0)` returns `yag = 3600.0`.
- **ra/dec** — **degrees**.
- **1 ACA pixel ≈ 5 arcsec** (measured 4.982 in yag, 5.001 in zag near the origin, which
  is why "about 5" is the right level of precision to carry in your head).

## The two arguments people get wrong

### `pix_zero_loc` — worth 2.5 arcsec

Default is `"edge"`. The alternative `"center"` shifts results by **half a pixel ≈ 2.49
arcsec**:

```python
pixels_to_yagzag(100.0, 100.0, pix_zero_loc="edge")    # -467.734, 475.253
pixels_to_yagzag(100.0, 100.0, pix_zero_loc="center")  # -470.223, 477.750
```

Half a pixel is small enough to pass a sanity check and large enough to ruin a centroid
comparison. Decide which convention your row/col came from before calling. Centroids
generally use `"center"`; raw telemetry row/col indices generally use the default.

### `t_aca` — defaults to 35.0, not room temperature

`t_aca` is the ACA CCD temperature in **degC** feeding the plate-scale / distortion
correction, and it **defaults to 35.0**. It is a common mistake to assume ~20. If you care
about arcsec-level accuracy, pass the actual temperature (`AACCCDPT`) rather than the
default.

`flight=False` by default selects the nominal distortion model; `flight=True` selects the
flight model. Match whatever the rest of your analysis uses.

## Quaternions

`Quaternion.Quat` — the attitude object every `*_radec` call needs.

```python
q = Quat(equatorial=[ra, dec, roll])   # degrees
q.ra, q.dec, q.roll                    # back out the same three
q.equatorial                           # array([ra, dec, roll])
q.q                                    # array([x, y, z, w])  <- SCALAR IS LAST
q.transform                            # (3, 3) rotation matrix
```

**Component order is `[x, y, z, w]` with the scalar term last.** Verified:
`Quat([0, 0, 0, 1]).equatorial` is `[0, 0, 0]`, i.e. the identity. Many other libraries
(and much of the literature) put the scalar first — feeding a `[w, x, y, z]` array in
gives a wrong attitude with no error raised. This is the single most dangerous convention
mismatch in this area.

Attitude quaternions come from telemetry as `AOATTQT1-4`, or as the cheta computed MSID
`quat_aoattqt` which returns `Quat` objects directly:

```python
from cheta import fetch
qatt = fetch.Msid("quat_aoattqt", start, stop)
qatt.vals.equatorial      # ra, dec, roll per sample
```

**Computed MSIDs are lowercase-only.** Real MSIDs are conventionally uppercase and cheta
accepts either case for them, but the comps are not recognized uppercased — verified:
`fetch.msid_glob("quat_aoattqt")` resolves, while `QUAT_AOATTQT` comes back in the *bad*
list. The same applies to `quat_aoatupq`, `quat_aocmdqt`, `quat_aotarqt`. If a comp
"doesn't exist", check the case first.

## Image row/col origins — three of them

For ACA image data specifically, there are three different row/col origin conventions in
the same table, and picking the wrong one silently shifts the image. Covered in
[chandra_aca](../../ska-packages/references/chandra_aca.md): `IMGROW0_8X8`/`IMGCOL0_8X8`
(usually what you want), `IMGROW0`/`IMGCOL0`, and `IMGROW_A1`/`IMGCOL_A1`.

`chandra_aca.aca_image.ACAImage` exists precisely so an image and its `row0`/`col0` origin
travel together instead of being tracked separately.

## Related

- [time-systems.md](time-systems.md)
- [chandra_aca](../../ska-packages/references/chandra_aca.md) — images, the three origins
- [ska router](../../ska/SKILL.md)
