---
name: chandra-domain
description: Chandra X-ray Observatory spacecraft and ACA domain background - mission and orbit, subsystems, aspect camera hardware, coordinate frames and quaternions, time systems, star catalogs and magnitudes, observations and dwells, mission planning and load products, and a glossary of Chandra/ACA acronyms. Use when the question is about how the observatory works rather than which function to call.
---

# Chandra domain background

The context that is not in any package's docs: how the observatory and the aspect camera
actually work.

*This skill is being written. Planned reference files:*

| File | Covers |
|---|---|
| `mission-and-orbit.md` | Mission overview, the 63-hour orbit, radiation belts, perigee passage |
| `spacecraft-subsystems.md` | PCAD, OBC, EPS, SIM, the science instruments |
| `aca-hardware.md` | The aspect camera: optics, CCD, readout modes, slots, dark current |
| `coordinates-and-frames.md` | RA/Dec, yag/zag, CCD row/col, quaternions, roll conventions |
| `time-systems.md` | CXC seconds, DOY strings, and the rest of the CxoTime formats |
| `star-catalogs.md` | AGASC, ACA magnitudes, star selection |
| `observations-and-dwells.md` | Obsids, dwells, maneuvers, NPM/PPM |
| `mission-planning-and-loads.md` | The weekly load cycle, backstop, approved loads |
| `glossary.md` | Acronyms |

Until these exist, the router at [ska](../ska/SKILL.md) covers the API side, and the
Chandra Proposers' Observatory Guide (https://cxc.harvard.edu/proposer/POG/) is the best
public reference for the observatory itself.
