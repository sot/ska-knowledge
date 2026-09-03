# Aspect performance, dither, and star selection

What the aspect system actually delivers, the dither that smears the field across pixels,
and the constraints that decide which stars can be used.

**Source.** [Chandra Proposers' Observatory Guide, chapter
5](https://cxc.harvard.edu/proposer/POG/html/chap5.html), retrieved 2026-09-03. Performance
numbers are as-flown and are periodically revised — treat them as "current best" and check
the POG for anything you will publish.

## ACA magnitude

The ACA has its own instrumental magnitude, converted from Johnson V and B−V:

```
m_ACA = V + 0.426 - 1.06 (B-V) + 0.617 (B-V)^2 - 0.307 (B-V)^3
```

| | |
|---|---|
| Bright limit | `m_ACA ≈ 5.2` |
| Faint limit | `m_ACA ≈ 10.3` (extended fainter after the May 2023 dynamic background patch) |

**"Spoiler" stars** are a real selection hazard: cool N0-type stars can have visual
magnitudes far fainter than 10.5 yet produce excessive ACA counts, so mission planning
avoids them. A star's V magnitude alone does not predict its ACA behaviour.

Recent acquisition and tracking success (2024-Oct → 2025-Oct):

| `m_ACA` | Acquisition | Tracking |
|---|---|---|
| all stars | 92 % | 99 % |
| 10.0–10.3 | 61 % | 98 % |
| 10.3–10.9 | 55 % | (insufficient data) |

The steep acquisition falloff at the faint end — 92 % overall vs 61 % by 10.0–10.3 — is why
`chandra_aca.star_probs.acq_success_prob` exists rather than a simple magnitude cut.

## Accuracy — requirement vs actual

| Quantity | Requirement | Actual |
|---|---|---|
| Celestial location (absolute) | 1.0 arcsec RMS radius | **0.63 arcsec** RMS radius |
| Image reconstruction | 0.5 arcsec RMS diameter | **0.32 arcsec** RMS diameter |
| Absolute celestial pointing | 30.0 arcsec (99 %, radial) | **± 8 arcsec** (2025-Oct) |
| PCAD 10-sec stability | 0.12 arcsec (95 % RMS) | 0.09 arcsec pitch, 0.06 arcsec yaw |
| Star centroid noise | < 0.360 arcsec (1σ, 1-axis) | — |

Practical notes on absolute position:

- The 90 % source location error circle is **< 0.87 arcsec** overall, < 0.95 arcsec per
  instrument, and roughly **6 % of sources fall outside a 1 arcsec radius** — so a
  1 arcsec circle is not a 100 % containment claim.
- Off-nominal SIM-Z observations add up to **0.5 arcsec** residual offset for ACIS/HRC-S,
  and up to **3 arcsec** for HRC-I.
- Pointing error correlates with **ACA housing temperature**, with ±5 arcsec mean per-axis
  and ±3 arcsec drift within an observation. This is the physical driver behind
  `chandra_aca.drift`.
- Periscope drift contributes up to 0.5 arcsec on long (~50 ks) observations.

Relative astrometry is much better than absolute: from a 900 ks ACIS-I Orion observation,
90 % of on-axis sources land within **0.22 arcsec**, and ≈ 0.15 arcsec once 2MASS
coordinate uncertainty is removed.

## Dither

Dither moves the target across pixels to average out per-pixel response. Defaults differ by
instrument:

| Parameter | ACIS | HRC |
|---|---|---|
| Amplitude (pitch / yaw) | 16.0 / 16.0 arcsec | 20.0 / 20.0 arcsec |
| Period (pitch) | 2000.0 sec | 768.6 sec |
| Period (yaw) | 1414.0 sec | 1087.0 sec |
| Phase (pitch / yaw) | 0.0 / 0.0 rad | 0.0 / 0.0 rad |

- Rate limits: **≥ 0.02 arcsec/s** (HRC detector health) and **≤ 0.22 arcsec/s** (PCAD
  stability).
- **ACIS dither can be disabled; HRC requires a minimum dither.**
- The pitch and yaw periods are deliberately incommensurate (2000 vs 1414 s for ACIS) so the
  pattern does not repeat quickly.

Get the dither actually commanded for an observation from
`mica.starcheck.get_dither`, not from these defaults.

## Gyro-hold drift

For observations without guide-star tracking, attitude drifts as a random walk. Per-axis
variance:

```
sigma^2 = sigma_b^2 t^2 + sigma_v^2 t + sigma_u^2 t^3 / 3
```

with worst-case `sigma_u = 1.5e-5` arcsec s^-3/2, `sigma_v = 0.026` arcsec s^-1/2,
`sigma_b = 0.002` arcsec s^-1. Resulting 1σ drift:

| Elapsed | 1σ drift |
|---|---|
| 0.1 ks | 0.3 arcsec |
| 1 ks | 2.2 arcsec |
| 5 ks | 11 arcsec |
| 10 ks | 22 arcsec |

Maximum gyro-hold duration is **3.6 ks**, and on-board Kalman bias calibration needs
**~20 minutes** of guide-star tracking before the maneuver.

## Operational constraints

ACA performance is maintained when the line of sight is at least:

| From | Separation |
|---|---|
| Sun | 45° |
| Bright Earth limb | 10° |
| Dark Earth or Moon | 6° |

(The *sunshade* protection angles — 20°/6°/6° — are a different, hardware-level number;
see [aca-hardware.md](aca-hardware.md).)

Normal maneuver mode peaks at **2° per minute**.

## Monitor-star photometry

Usable over the full `m_ACA` 5.2–10.3 range, but only when a slot is dedicated to it, which
**degrades aspect accuracy by 15–25 %**. The faint limit is set by dark-current
uncertainty: at −2.1 °C the dark noise is ~1900 e⁻/s, while a 9.9 mag star gives
~7600 e⁻/s, i.e. S/N ≈ 4.

## CCD ageing

- Radiation damage raises mean dark current and the warm-pixel population over time; the
  effective warm-pixel fraction is strongly temperature dependent (expected 27–67 % across
  the −14.0 to −2.1 °C operating range). This is why `acdc` and
  `mica.archive.aca_dark` exist and why dark cals are versioned.
- **No increased CTI has been detected** in the ACA CCD, in contrast to the ACIS
  front-illuminated chips.
- Field distortion is modelled as a polynomial from CCD pixel to boresight angle with plate
  scale to third order **plus temperature-dependent terms** — which is why the transforms
  take a `t_aca` argument at all.

## Related

- [aca-hardware.md](aca-hardware.md) — optics, CCD, telemetry encoding
- [coordinates-and-frames.md](coordinates-and-frames.md) — `t_aca` and the transforms
- [chandra_aca](../../ska-packages/references/chandra_aca.md) — `star_probs`, `drift`, dark models
