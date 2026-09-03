# Contributing to ska-knowledge

## What belongs here

A **routing layer**, not an API mirror. This repo says "for ACA image data, reach for
`chandra_aca.aca_image.get_aca_images`, and here is why you would pick each backend." It
does not list the arguments — `https://sot.github.io/<pkg>` and the installed source do
that, and they are always current.

**Most changes to Ska packages need no edit here.** Adding
`chandra_aca.some_new_function()` changes nothing.

| Edit needed | No edit needed |
|---|---|
| A new function is now the preferred way to do something the table covers | New kwargs on an existing function |
| A capability the table had no answer for | Internal refactors, helpers, bugfixes |
| A new naming ambiguity, or one variant becomes canonical | Version bumps |
| A package enters or leaves `ska3-flight` / `ska3-aca` | New tests, typo fixes in package docs |
| A gotcha worth recording | Anything the package's own docs already answer well |

## A weak entry is worse than no entry

Measured, not assumed — and the measurement has a subtlety worth internalizing.

Baseline Claude (no KB) knows the Ska packages well: all of `sot/` is public and in
training data. It got `chandra_aca.aca_image.get_aca_images` right unaided, and on a pitch
question it *beat* a draft routing table by knowing the `DP_PITCH` derived MSID.

**But its prior skews toward legacy code.** GitHub holds ~25 years of Ska history, and
`Ska.engarchive` / `Chandra.Time` appear in far more of it than `cheta` / `cxotime`. In a
clean-room test — empty directory, no tools, one turn — baseline wrote:

```python
from Chandra.Time import DateTime
from Ska.engarchive import fetch
```

Both legacy. With the KB loaded it wrote `cheta` + `cxotime`. So the deprecation table
earns its place on *new* code, not only on refactors.

Two rules follow, pulling in opposite directions:

**1. Do not restate what the docs already say.** A routing row that only duplicates
`sot.github.io/<pkg>` is not neutral — it spends context and can crowd out better
knowledge the model already has. A draft row said "sun pitch → `ska_sun.pitch`", which is
not wrong but is incomplete in a way that displaced a better answer:
`ska_sun.pitch(ra, dec, time)` *computes* pitch from an attitude, while `DP_PITCH` is the
*telemetered* value. Different questions.

**2. Do state anything where team convention diverges from public API.** Deprecations,
"always use X", astropy `Table` over `DataFrame`, which of four similarly-named functions
is canonical. The model cannot infer these from code volume — code volume argues the
other way.

Before adding an entry, ask what it gives that `sot.github.io/<pkg>` does not. If the
answer is "nothing", leave it out. The categories that consistently earn their place:

1. **Gotchas and default-wrong traps** — the highest-value category by a wide margin.
   The `pix_zero_loc` half-pixel shift; `IMG` always being 8x8 regardless of readout size;
   `bgsub=True` silently requiring mica data.
2. **Team practice and environment** — `$SKA`, which env for what, HEAD/GRETA vs offsite,
   occweb. In no repo's docs, so it cannot be known.
3. **Genuinely undocumented packages** — the `ska3-aca` tools with no README and no
   `docs/`. Here the model is guessing and almost anything accurate helps.
4. **Distinctions that are easy to conflate** — commanded vs actual, archive lag, unit
   systems, which of four similarly-named functions to call.

## Access control — read this before pasting

`icxc.cfa.harvard.edu`, occweb, and the aspect twiki are credential-gated. **Link to
those URLs; never copy content out of them into this repo.** This repo is public so that
`/plugin marketplace add` works without credentials for everyone on the team.

Public sources are fine to summarize with a citation: the Proposers' Observatory Guide
(https://cxc.harvard.edu/proposer/POG/), CXC/CIAO pages, published instrument papers, and
the `sot/` package docs.

## Style

Reference files follow a fixed order so both people and agents can skim them:

1. **What it's for** — two or three sentences.
2. **Links** — docs URL, repo URL, path to source in the active env.
3. **Common tasks** — task → runnable snippet.
4. **Gotchas** — the mistakes that actually get made, with the symptom that gives them
   away ("if temperatures are off by ~273, this is why").
5. **Related** — cross-links to other files here.

Other conventions:

- Keep each `SKILL.md` under ~200 lines. Depth goes in `references/`, which costs nothing
  until it is opened.
- The `description:` frontmatter is what Claude matches on. Name the concrete packages and
  concepts, not a vague category.
- Write the import path exactly. Ska packages mostly do not re-export at top level, and a
  wrong path is the single most common time-waster.
- Prefer a gotcha over a restatement of the docs. If the package docs say it clearly,
  link, do not copy.

## Verify against the installed release, not the repo

**The `~/git` checkouts are ahead of what is deployed.** Reading symbol names out of a repo
at `master` and writing them down produces confidently wrong documentation. This has already
happened twice:

- `jobwatch` master defines `SkaJobWatch`/`SkaDbWatch`/`SkaWebWatch`, so a grep of the repo
  suggested they live in `jobwatch.jobwatch`. In the installed 0.14.6 they are in
  `jobwatch.skawatch` and `jobwatch.hourly_watch` — the *application* modules, one of which
  cannot even be imported off HEAD. Only `JobWatch`/`FileWatch`/`DbWatch` are in the core.
- `fss_check` master has `get_fss_prim_data`; installed 1.0.1 does not.

**Also: environments disagree with each other.** `ska3-aca` 2026.11 ships `chandra_aca`
4.53.0 while `ska3-flight` 2026.9 ships 4.56.0 — so `get_aca_images_cheta`, added in 4.56.0,
is missing from the *higher-numbered* environment. A higher metapackage version does not mean
newer packages inside.

Consequences for writing entries here:

1. Introspect the installed package (`dir()`, `inspect.signature`, `pkg.__version__`), do
   not grep the repo.
2. If a symbol is newer than the oldest environment people use, state the version gate
   explicitly rather than presenting it as always available.
3. Add every new claim to `scripts/check_symbols.py` and run it in **both** `ska3` and
   `ska3-aca`. Version-gated claims go in `CLAIMS_VERSION_GATED`, which asserts presence
   *and* absence against the installed version.

## Verifying

Every symbol named in a routing table must exist in `ska3-flight`:

```bash
conda activate ska3
python scripts/check_symbols.py
```

Add your new claims to `CLAIMS` in that script. Code snippets should be runnable in
`ska3-flight` — not just in a personal dev env, which may be ahead of flight.

## Maintenance rhythm

- **In session** — Claude routes you wrong, you fix it. The dominant path in practice.
- **PR time** — if a package PR changes how someone should be routed, PR here too.
- **Release time** — review routing against the release's package changes.

**Editing does not take effect until you refresh the snapshot.** Installing copies this
repo into `~/.claude/plugins/cache/sot/ska/<commit-sha>/`, and that copy is what Claude
loads. After any edit:

```
claude plugin update ska@sot    # re-copy content (NOT `marketplace update`, which only
                               #  refreshes the index)
```

then restart. This bites hardest when testing your own changes: it is easy to conclude an
entry "did not help" while Claude is still reading the pre-edit snapshot.
