# Worked example: a filled-in sot PR body

## What it's for

One complete PR description, start to finish, so the shape is concrete rather than
described. Everything here is taken from real merged PRs in `sot/kadi`, `sot/agasc` and
`sot/proseco` — the wording is paraphrased, the structure is not.

## Links

- The template itself: `.github/pull_request_template.md` in the repo you are PR-ing.
- Real examples worth reading in full:
  - https://github.com/sot/kadi/pull/389 — large PR: `### Changes` + `### Test plan`
    subsections, and a genuinely filled-in Functional tests section with a linux soak test.
  - https://github.com/sot/proseco/pull/414 — `## Requires` for a cross-repo dependency,
    and an environment annotation on the platform line.
  - https://github.com/sot/agasc/pull/210 — small bugfix, `Fixes #209` filled in.
- [../SKILL.md](../SKILL.md) — the conventions this example follows.

## Common tasks

### A small, single-purpose PR

Adding one function, tests pass on the author's mac, no issue filed:

````markdown
## Description

`get_starcats()` returns a list of star catalogs, so a query spanning several years
must build and hold every catalog in memory before the caller sees the first one.
Some processing only needs one catalog at a time.

This adds `yield_starcats()`, a generator with the same signature as `get_starcats()`,
which yields each star catalog as it is built. `get_starcats()` is now a thin wrapper
that returns `list(yield_starcats(...))`, so its behavior is unchanged.

## Interface impacts

New public function `kadi.commands.observations.yield_starcats()`, added to `__all__`
and therefore available as `from kadi.commands import yield_starcats`. No changes to
existing APIs.

## Testing
<!-- If relevant describe any special setup for testing. -->

### Unit tests
- [x] Mac
```
(ska3) ➜  kadi git:(add-starcats-generator) git rev-parse --short HEAD
84792c56
(ska3) ➜  kadi git:(add-starcats-generator) pytest
============================= test session starts ==============================
platform darwin -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/aldcroft/git
configfile: pytest.ini
plugins: anyio-4.12.1, timeout-2.4.0
collected 318 items

kadi/commands/tests/test_commands.py .......................s........... [ 11%]
...................                                                      [ 16%]
kadi/commands/tests/test_commands_v2.py ssssssssssssssssssssssssssssssss [ 27%]
ssssssssssssssssssssssssssssssssssssssssssssssssssssssss                 [ 44%]
kadi/commands/tests/test_observations.py ............................... [ 55%]
............                                                             [ 58%]
kadi/tests/test_occweb.py .......................                        [100%]

============ 228 passed, 89 skipped, 1 xfailed in 151.95s (0:02:31) ============
```

Independent check of unit tests by [REVIEWER NAME]
- [ ] [PLATFORM]:

### Functional tests
<!-- Describe and document results of any functional tests, otherwise leave the text below -->
No functional testing.
````

Note what happened to each part of the template:

| Template part | Here |
|---|---|
| `Fixes #` and its comment | **Deleted** — no issue. |
| Description comment | Deleted along with the `Fixes #` line it annotates. |
| Interface impacts comment | **Replaced** by real content. |
| `## Testing` comment | **Kept** — nothing to add about setup. |
| Unit tests comment | Deleted, because the instruction it gives ("DELETE the unchecked options") was carried out. |
| `No unit tests` / `Linux` / `Windows` | **Deleted** — only Mac was run. |
| Reviewer block | **Untouched**, placeholders and all. |
| Functional tests | Comment and default sentence both **kept**. |

### A larger PR

Add subsections under Description rather than one long paragraph:

```markdown
## Description

<prose: what the current behavior is and why it is a problem>

### Changes

- <one bullet per distinct change, in the order a reader should take them>
- <name the functions and files, bold the load-bearing word: the copy is **shallow**>

### Test plan

- [x] <what you verified by hand, specifically enough to be re-run>
- [x] `ruff check` passes on `update_events.py`
- [x] <manual validation done before deploying>
```

### Filling in Functional tests

For anything cron-driven, deployed, or otherwise not covered by pytest, use `####`
sub-headings per test and paste the evidence:

```markdown
### Functional tests

#### Local mac testing by hand
<the commands, then what you checked after each one>

#### Soak test on linux (kady)
<the crontab line, how long it ran, and grep output from the log>
```

## Gotchas

- **Do not fill in the reviewer block.** It stays as `[REVIEWER NAME]` / `[PLATFORM]`
  until an actual reviewer pastes their own run into it. This is the single most tempting
  wrong move, because the placeholders look unfinished.
- **Do not delete the `<!-- -->` comments you did not act on.** They are left in place by
  convention; only the `Fixes #` comment and the Unit-tests comment get removed, and only
  because their instruction was carried out.
- **Do not paste a transcript from a dirty tree.** Commit, then `git rev-parse HEAD`, then
  `pytest`, then paste. Otherwise the SHA in the block does not describe the code that
  was tested.
- **A fenced block inside a fenced block needs four backticks** on the outer fence. Easy
  to get wrong when drafting the body in a file.
- If you draft the body into a file for `gh pr create --body-file`, that file is scratch —
  do not commit it into the repo.

## Related

- [../SKILL.md](../SKILL.md) — the template, the section-by-section conventions, and the
  transcript rules.
- [../../ska-coding-style/references/self-code-review.md](../../ska-coding-style/references/self-code-review.md)
  — run this over the diff before opening the PR.
