# ACA hardware and telemetry encoding

The Aspect Camera Assembly: the optics, the CCD, its coordinate system, and how pixels
and status flags are actually encoded in telemetry.

**Sources.** System level from the [Chandra Proposers' Observatory Guide, chapter
5](https://cxc.harvard.edu/proposer/POG/html/chap5.html) (retrieved 2026-09-03).
Hardware and telemetry detail from the *Aspect Camera Assembly User's Manual*, Ball
Aerospace **CM0060-702**, initial release **20 May 1998** — authoritative on the encoding,
but pre-launch, so it does **not** describe later flight software changes (notably the
dynamic background patch of May 2023).

## The camera

| | |
|---|---|
| Optics | 11.2 cm aperture, F/9 Ritchey-Chrétien |
| Field of view | 1.4° × 1.4° |
| CCD | Tektronix 1024 × 1024, 24 × 24 µm pixels |
| Plate scale | **≈ 5 arcsec per pixel** |
| Spectral band | 4000–9000 Å |
| PSF | **9 arcsec FWHM — deliberately defocused**, so a star spans several pixels and can be centroided to sub-pixel precision |
| Operating temperature | −14.0 °C to −2.1 °C (the warm end reflects lost thermoelectric-cooler margin) |
| Redundancy | A spare CCD, selected by a **flip mirror** in the optical path |
| Sunshade | ~2.5 m long, ~40 cm diameter; protection angles 20° Sun, 6° Earth, 6° Moon |
| Fiducial lights | 635 nm LEDs near each science instrument, relayed via an HRMA-centre retroreflector collimator and a periscope |

The defocus is the key design choice to understand: a 9 arcsec FWHM on 5 arcsec pixels is
what makes weighted-mean centroiding to a fraction of a pixel possible.

## Coordinate system

The ACA X-Y-Z system is nominally aligned with the spacecraft system, and CCD pixels lie in
a plane parallel to Y-Z.

- **CCD rows are parallel to the Z axis; columns are parallel to the Y axis.**
- Row and column both run **−512 to 511** — the origin is the CCD *centre*, not a corner,
  which is why pixel coordinates are routinely negative.
- The centre is a 2 × 2 block of pixels `(0,0)`, `(-1,0)`, `(0,-1)`, `(-1,-1)`. There is no
  single central pixel, which is the physical reason `pix_zero_loc` (`"edge"` vs `"center"`)
  is a distinction that has to be made at all.
- `+Z` is `+columns` on both CCDs. But `+Y` is **−rows on the primary CCD and +rows on the
  redundant CCD** — the flip mirror reverses the row direction. If the redundant CCD is ever
  in use, row sense is inverted.

See [coordinates-and-frames.md](coordinates-and-frames.md) for the transforms built on this.

## Image slots and readout sizes

There are **8 image slots**, numbered 0–7 (`IMGNUM`). A typical configuration is five guide
stars plus three fiducial lights.

Pixels are labelled `A1`…`P1`, `A2`…`P2`, … in the manual's figures, and **`A1` is the
pixel with the lowest row and column number** — which is what the `IMGROW_A1`/`IMGCOL_A1`
telemetry columns report.

| Readout | Pixels telemetered | Manual's definition |
|---|---|---|
| 4×4 | **16** | `A1`–`P1` |
| "modified 6×6" | **32** | inner half `A1`–`P1` **plus** outer half `A2`–`P2` |
| 8×8 | **64** | `A1`–`P4` |

**A 6×6 readout would be 36 pixels; only 32 are telemetered.** The four corners are simply
absent — this is the origin of the "mouse-bitten corner", and the reason `chandra_aca`
returns every image as a masked 8×8 rather than trying to represent three shapes.

### Readout cadence — this bites time-resolution assumptions

Telemetry carries **16 pixel signals per update**, so:

- 4×4 → **1** telemetry update per image
- modified 6×6 → **2** updates
- 8×8 → **4** updates

And per the manual: *"after an image is completely updated, the most recent 16 pixels
supplied for that image will be repeated in telemetry until a fresh image is available
after the next CCD readout."* So consecutive telemetry samples of an 8×8 image are **not**
independent readouts, and repeated identical pixel blocks are expected behaviour, not a
glitch.

### Centroids arrive at 1.025 s but only refresh every 2.05 s

The same repeat-when-stale behaviour applies to the **centroids and magnitudes**, and this
is the version that most often gets mistaken for real data:

- On-board **integration time is 1.696 s** (`ACA<slot>_INTEG` in the ACA image telemetry,
  or `AOACINTT` in PCAD telemetry as a raw word in milliseconds, 1697.66 ms).
- Integration plus readout means fresh data are available only once every **2.05 s**.
- The ACA is nonetheless **required to supply centroid data every 1.025 s**, so when no new
  readout is ready it **repeats the previous values and sets a stale/repeat flag**.

That flag is **`AOACRPT`** ("ACA DATA: REPEAT FLAG"), sampled at 1.025 s alongside the
centroids. In normal operation it alternates 1/0/1/0 with a duty cycle of exactly 0.5.

So `AOACYAN<slot>` / `AOACZAN<slot>` / `AOACMAG<slot>` come at 1.025 s but carry only
**half that many independent measurements**. Verified over a 30-minute stretch of obsid
27589 while tracking: `AOACRPT == 1` meant the centroid was byte-identical to the previous
sample in 807 of 807 cases, and `AOACRPT == 0` meant it changed in 800 of 805 (the five
exceptions are fresh readouts that landed on the same quantised value).

Consequences worth keeping in mind:

- Any scatter, standard deviation or PSD computed over raw 1.025 s centroid samples is
  working with a series where **every other point is a duplicate**. That deflates the
  apparent sample noise and puts a spurious feature at the 2.05 s period.
- Sample counts overstate the real integration count by 2x. An N-sample dropout costs
  N/2 actual centroid updates.
- To get independent measurements, select `AOACRPT == 0` (or take every other sample from
  a known phase).

## Pixel encoding: from telemetry counts to DN to electrons

Each pixel is a **10-bit** signal (0–1023) plus a per-image **scale factor**:

- The scale factor is unsigned, **1 LSB = 0.03125 = 1/32**, never below 1.00, and is set to
  the smallest value that keeps the largest pixel from overflowing 1023.
- The manual gives the physical relation:

  ```
  no. electrons = 5 * [ (scale factor) * (pixel signal) - 50 ]
  ```

`chandra_aca` exposes the bracketed part as DN:

```python
IMG = IMGTLM * (IMGSCALE / 32.0) - 50.0    # DN
```

The `/ 32.0` *is* the scale-factor LSB. Putting the two together gives the conversion
`chandra_aca` does not state:

> **1 DN ≈ 5 electrons.**

So `IMG` in DN times 5 is electrons, and the 50-count pedestal is subtracted before
scaling to electrons.

## `BGDAVG` — how the background number is actually made

`BGDAVG` is not a mean over the whole image. Per the manual it is computed from **eight
specific pixels of the 8×8** — `A1`, `B1`, `G1`, `H1`, `I4`, `J4`, `O4`, `P4` (the corner
regions) — with iterative outlier rejection:

1. Average those eight pixel signals.
2. Discard the single pixel deviating most from the average, if any deviates by more than
   **±150 % or 10 A/D counts, whichever is larger**.
3. Repeat until nothing is discarded, then report the result.

It is a 10-bit unsigned value in A/D counts, where **1 A/D count ≈ 5 electrons** — the same
factor as above. Two consequences: `BGDAVG` is a *robust corner* estimate, so it will not
track a background gradient across the image; and it is unavailable for 4×4 readouts, which
do not telemeter those pixels (which is why `chandra_aca` masks `BGDAVG` and the
temperatures for 4×4 data).

## Where the status columns come from

The boolean columns in an ACA image table are bit fields in "image header 1" of the aspect
telemetry:

| Telemetry flag | Column |
|---|---|
| fiducial light flag | `IMGFID` |
| image number | `IMGNUM` |
| image function | `IMGFUNC` |
| saturated pixel flag | `SAT_PIXEL` |
| defective pixel flag | `DEF_PIXEL` |
| quadrant boundary flag | `QUAD_BOUND` |
| common column flag | `COMMON_COL` |
| multiple stars flag | `MULTI_STAR` |
| ionizing radiation flag | `ION_RAD` |
| pixel A1 row / column (10 bits each) | `IMGROW_A1` / `IMGCOL_A1` |

"Image header 3" words are diagnostic telemetry — the source of the `HD3TLM62`–`HD3TLM77`
columns, documented in the manual's Appendix A rather than in any package.

## Related

- [coordinates-and-frames.md](coordinates-and-frames.md) — the transform chain and units
- [aspect-performance.md](aspect-performance.md) — accuracy, dither, magnitude limits
- [chandra_aca](../../ska-packages/references/chandra_aca.md) — the code that reads all this
