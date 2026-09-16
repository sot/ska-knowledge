---
name: ska-pull-requests
description: How the ACA/SOT team writes a pull request description for a sot repo - the shared .github/pull_request_template.md, which sections to fill, keep or delete, and the pasted `git rev-parse HEAD` + `pytest` shell transcript that the Unit tests section expects as evidence. Use when opening a PR or drafting a PR body for kadi, cheta, chandra_aca, agasc, proseco, mica or any other sot repo.
---

# Pull request descriptions in sot repos

A sot PR body is a **filled-in template, not free-form prose**, and its Unit tests section
wants a *pasted shell transcript* rather than a claim that tests pass. Neither is
guessable: the generic "## Summary / ## Test plan" shape is wrong here, and a PR that
asserts "all tests pass" without the output will be sent back.

Verified against the templates in ~87 local `sot` checkouts and against merged PRs in
`kadi`, `chandra_aca`, `agasc` and `proseco` by three different authors.

## Rule zero: read the repo's own template

```bash
cat .github/pull_request_template.md
```

**Do not write the sections from memory.** 61 of the sot repos with a template share one
byte-identical copy (the one below), but the rest diverge in ways that matter:

| Repo | Difference |
|---|---|
| `razl` | Same as canonical, plus an explicit `Test output:` hint naming the two commands |
| `arc`, `acis_taco`, `acisfp_check` | **No Unit tests section at all** — Description / Interface impacts / Functional testing only |
| `ska_testr`, `task_schedule`, `watch_cron_logs` | Much older short form: Description, one Testing checkbox, `Fixes #` |
| `astropy`, `pandas`, `stingray` | Not sot repos — these follow upstream conventions, not this skill |

GitHub pre-fills the web PR form from that file. If you are writing to a file or using
`gh pr create --body-file`, you have to reproduce the structure yourself.

## The canonical template

```markdown
## Description

<!--If this fixes an issue then fill this, otherwise DELETE the line below -->
Fixes #

## Interface impacts
<!-- API changes, file format updates, coordination of changes with the community. -->

## Testing
<!-- If relevant describe any special setup for testing. -->

### Unit tests
<!-- At least one of these must be checked if unit tests exist. DELETE the unchecked/untested options. -->
- [ ] No unit tests
- [ ] Mac
- [ ] Linux
- [ ] Windows

Independent check of unit tests by [REVIEWER NAME]
- [ ] [PLATFORM]:

### Functional tests
<!-- Describe and document results of any functional tests, otherwise leave the text below -->
No functional testing.
```

## Section by section

| Section | What the team actually does |
|---|---|
| **Description** | Prose, and **why before what** — the problem or current behavior first, then the change. For a substantial PR, add `### Changes` (one bullet per change) and `### Test plan` subsections under it. |
| `Fixes #` | Fill in the issue number, or **delete the line** — its own comment says so. Deleting is correct when there is no issue. |
| **Interface impacts** | Name new or changed public API, file formats, anything needing coordination. `None` is a fine answer; so is leaving it empty. |
| **Unit tests** | Tick **only** platforms you actually ran, and **delete the other option lines** — including `No unit tests`. Then the transcript (below). |
| Reviewer block | **Leave the `[REVIEWER NAME]` / `[PLATFORM]` placeholders alone.** The reviewer fills these in with their own name, platform and transcript. Filling it in yourself is a real error, not a tidy-up. |
| **Functional tests** | Leave the literal `No functional testing.` if there was none. Otherwise document it properly: the commands run, the environment, and the relevant output. |

**Leave the `<!-- ... -->` hint comments in place.** This looks like leftover scaffolding
but it is the convention — across `kadi` #389, `agasc` #210 and `proseco` #414, three
authors all left the comments in the sections they had nothing to add to. Do not strip
them.

## The Unit tests transcript is the point

This is the convention most easily missed. The `razl` template spells out what the others
leave implicit:

```
Test output:
<!-- Enter output from the following:
git rev-parse HEAD
pytest
-->
```

So: a fenced code block under the ticked platform, holding a **verbatim shell transcript**
of exactly those two commands, in that order:

````markdown
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
...
============ 228 passed, 89 skipped, 1 xfailed in 151.95s (0:02:31) ============
```
````

What makes it evidence rather than decoration:

- **Paste it unedited** — prompt lines, conda env in the prompt, pytest header
  (platform, Python, pytest and plugin versions, `rootdir`) and the final count line. The
  header is how a reviewer knows *which* environment produced this.
- **Commit first, then run, then paste.** The SHA has to be the commit the run was done
  at, which means a dirty tree invalidates the transcript.
- **Run the whole suite** from the repo root, not a `-k` subset. (`pytest --lf` shows up
  occasionally for a re-run, but a full run is the norm.)
- **Skips and xfails stay in.** They are expected — `kadi`'s `test_commands_v2.py` skips
  wholesale off HEAD, `agasc` skips without its data files. Do not trim them or explain
  them away.
- **Annotate the platform line when the environment is load-bearing**, e.g.
  `- [x] Mac (ska3 flight 2026.1 with chandra_aca @ 06d34eb)`.
- Short or long SHA are both used; `--short` is the more common.

## Cross-repo PRs

When a PR needs an unmerged PR in another repo, add a `## Requires` section with the
links — not part of the template, but established practice:

```markdown
## Requires
- https://github.com/sot/chandra_aca/pull/202
```

Reviewers then run with a `PYTHONPATH` pointing at the sibling checkout, and their
transcript shows it (`env PYTHONPATH=/Users/jean/git/cheta pytest`). Say in the PR which
sibling branch is needed.

## Gotchas

- **The generic PR shape is wrong here.** No `## Summary`, no emoji headers, no invented
  section names. The template's headings are the contract.
- **Never tick a platform box you did not run on**, and never replace the transcript with
  "all tests pass" — the output *is* the deliverable of that section.
- **`rootdir: /Users/<you>/git`** in the pytest header is the parent of the repo, because
  there is a `pytest.ini` there. That is normal in this group; it is not a misconfiguration
  to fix before pasting.
- Tests that need `$SKA` data or HEAD access will skip offsite. Paste the skips; do not
  claim coverage you did not get. See
  [ska-data-access](../ska-data-access/SKILL.md) for what is available where.
- A PR body is not a commit message. It can be long, it can have headings, and it should
  explain the motivation that the diff cannot.

## Before you open it

Run the [self-code-review checklist](../ska-coding-style/references/self-code-review.md)
over your own diff first — it is the step the team expects to have happened already, and
it is what the reviewer will apply.

## Related

- [references/worked-example.md](references/worked-example.md) — a complete filled-in PR
  body, annotated.
- [ska-coding-style](../ska-coding-style/SKILL.md) — conventions for the code in the diff.
- [ska-data-access](../ska-data-access/SKILL.md) — which environment and which platform you
  can honestly claim.
