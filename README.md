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
/plugin install ska@ska
```

### Getting updates — read this, it is not obvious

Installing **copies** this repo into a snapshot under
`~/.claude/plugins/cache/ska/ska/<version>/`. That snapshot, not the repo, is what Claude
loads. So a `git pull` (or, for a local checkout, editing the files) changes **nothing**
until you refresh the snapshot, and there are two different update commands:

```
/plugin marketplace update ska    # refreshes the marketplace INDEX only - not the content
/plugin update ska@ska            # re-copies the plugin content  <-- the one you need
```

Then **restart Claude Code** — the update command itself says "Restart to apply changes."

Turn on auto-update for the `ska` marketplace in `/plugin` as well; third-party
marketplaces do not auto-update by default, so without it your copy silently goes stale.

Verify which content is actually live:

```bash
diff -r ~/.claude/plugins/cache/ska/ska/*/skills ./skills
```

### For a whole repo

Commit this to the repo's `.claude/settings.json` and everyone who clones gets it after
the standard one-time folder-trust prompt, with no manual install:

```json
{
  "extraKnownMarketplaces": {
    "ska": { "source": { "source": "github", "repo": "sot/ska-knowledge" } }
  },
  "enabledPlugins": { "ska@ska": true }
}
```

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
| 1 | `ska-data-access` — `$SKA`, envs, data sources, offsite | Next |
| 2 | Undocumented `ska3-aca` packages (jobwatch, fss_check, aca_hi_bgd, kalman_watch, …) | Planned |
| 3 | `chandra-domain` — frames, time systems, hardware | Planned |
| 4 | Mainstream package gotchas (cheta, kadi, mica, proseco) — gotchas only | Planned |
| 5 | Eval harness (`claude plugin eval`) + repo rollout | Planned |

`chandra_aca` reference is written and is the model for the rest.

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
