# ska-knowledge

Shared knowledge base for the Chandra X-ray Observatory and the **Ska3** Python
ecosystem — the ~90 packages that make up `ska3-flight` and `ska3-aca`.

It answers the question the per-package docs never do: **which of the 90 packages do I
reach for, and what will trip me up?**

Two audiences, one set of files:

- **Claude Code** loads it on demand as a plugin, in any repo or analysis directory.
- **People** can read the same markdown directly on GitHub — start at
  [skills/ska/SKILL.md](skills/ska/SKILL.md).

## Install (Claude Code)

```
/plugin marketplace add sot/ska-knowledge
/plugin install ska@sot
```

### Getting updates — read this, it is not obvious

Installing **copies** this repo into a snapshot under
`~/.claude/plugins/cache/sot/ska/<commit-sha>/`. That snapshot, not the repo, is what
Claude loads. `plugin.json` carries no `version`, so the version *is* the commit SHA —
each commit gets its own cache directory, and merging to master is the whole release
process. So a `git pull` (or, for a local checkout, editing the files) changes **nothing**
until you refresh the snapshot, and there are two different update commands:

```
/plugin marketplace update sot    # refreshes the marketplace INDEX only - not the content
/plugin update ska@sot            # re-copies the plugin content  <-- the one you need
```

Then **restart Claude Code** — the update command itself says "Restart to apply changes."

Turn on auto-update for the `sot` marketplace in `/plugin` as well; third-party
marketplaces do not auto-update by default, so without it your copy silently goes stale.

Verify which content is actually live:

```bash
diff -r ~/.claude/plugins/cache/sot/ska/*/skills ./skills
```

### For teammates

One-time, covers every repo and every directory:

```bash
claude plugin marketplace add sot/ska-knowledge
claude plugin install ska@sot
```

Equivalently, inside a terminal `claude` session: `/plugin marketplace add
sot/ska-knowledge` then `/plugin install ska@sot`. **`/plugin` does not exist in the VS
Code extension** — use a terminal. If you have no `claude` on your PATH, the extension
ships one:

```bash
$(find ~/.vscode/extensions -maxdepth 4 -path '*native-binary/claude' | sort | tail -1) plugin list
```

Then reload/restart so the skills load, and confirm by asking Claude "list your available
skills" — you should see four `ska:*` entries.

Installing at **user scope** (the default) is deliberate and is the recommended path. It
covers bare analysis directories and notebooks, not just package repos — which is where a
lot of Chandra work actually happens. A per-repo `.claude/settings.json` would cover
neither, and would need maintaining across ~90 repos.

## Reading it as a human

| Start here | For |
|---|---|
| [ska](skills/ska/SKILL.md) | The routing index — "I want to X" → package and function |
| [ska-packages](skills/ska-packages/SKILL.md) | Per-package detail, snippets, gotchas |
| [chandra-domain](skills/chandra-domain/SKILL.md) | How the observatory and the ACA work |
| [ska-data-access](skills/ska-data-access/SKILL.md) | `$SKA`, environments, which archive to use |

## Status

Content is ordered by **what a model cannot already know**, not by package popularity —
an A/B test showed baseline Claude already knows the mainstream Ska API well, so
re-documenting it adds little and can crowd out better answers. See
[CONTRIBUTING.md](CONTRIBUTING.md#a-weak-entry-is-worse-than-no-entry).

| Priority | Area | State |
|---|---|---|
| — | Plugin scaffolding, router index | Done — 51 entries, verified against `ska3-flight` 2026.9 |
| 1 | `ska-data-access` — `$SKA`, envs, data sources, offsite | **Done** |
| 2 | `ska3-aca` monitors, documented as a family | **Done** — they are applications, not importable libraries |
| 3 | `chandra-domain` — frames, time systems | **Done** (frames + time; hardware/mission still open) |
| 4 | Mainstream package gotchas (cheta, kadi, mica, proseco) — gotchas only | Planned |
| 5 | Eval harness (`claude plugin eval`) + repo rollout | Planned |

`chandra_aca` reference is written and is the model for the rest.

## How this was built

[docs/building-a-knowledge-base.md](docs/building-a-knowledge-base.md) is an annotated
export of the session that produced this repo: the concepts (skills, plugins,
marketplaces, the plugin cache), every prompt in order with what it accomplished, the
mistakes worth skipping, and a recommended order for building an equivalent knowledge base
for a different codebase.

Useful if you are standing up a knowledge base for your own code infrastructure rather
than consuming this one.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: if the routing sent you to the
wrong place, fix it — that is the main way gaps get found, and a fix is a small markdown
PR. Most new functions in Ska packages need **no** change here; this is a routing layer,
not an API mirror.

Verify routing claims still hold:

```bash
conda activate ska3
python scripts/check_symbols.py
```
