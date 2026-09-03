---
name: ska-packages
description: Per-package detail for the Ska3 Python ecosystem - what each package is for, canonical code snippets, and the gotchas that bite. Covers chandra_aca, cheta, kadi, agasc, mica, proseco, sparkles, cxotime, Quaternion, xija, maude, ska_sun and friends. Use after the ska router points at a package, or when a Ska package behaves unexpectedly.
---

# Ska packages in detail

Use the [ska router](../ska/SKILL.md) to pick a package, then read its file here.

These files describe **what to reach for and what will trip you up**. They do not mirror
API signatures — read those from `https://sot.github.io/<pkg>` or the installed source at
`$CONDA_PREFIX/lib/python3.13/site-packages/<pkg>/`, which are always current.

## Packages

| File | Covers |
|---|---|
| [chandra_aca.md](references/chandra_aca.md) | ACA images, transforms, star probabilities, drift |

*Remaining reference files are being written — see the repo README for status. Until a
package has a file here, use the router table plus the package's own docs.*

## The shape of these files

Every reference file follows the same order, so you can skim to the part you need:

1. What it's for
2. Docs / repo / source location links
3. Common tasks, with runnable snippets
4. Gotchas
5. Related packages
