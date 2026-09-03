# skare3 wiki: page index

36 pages at https://github.com/sot/skare3/wiki. **Not in the skare3 checkout** — it is a
separate git repo, so searching the skare3 working tree will never find any of this:

```
git clone https://github.com/sot/skare3.wiki.git
```

The wiki is overwhelmingly about **building, releasing, promoting and testing** the
environment. It contains essentially no task→function analysis guidance — that gap is what
[ska-packages](../../ska-packages/SKILL.md) and the [router](../../ska/SKILL.md) fill.

## Start here

| Page | For |
|---|---|
| [Ska Overview](https://github.com/sot/skare3/wiki/Ska-Overview) | "Ska 101" — what Ska is, package inventory, legacy packages, cheta vs MAUDE, kadi distinctions, data latency. The best single page. |
| [Ska3 runtime environment for users](https://github.com/sot/skare3/wiki/Ska3-runtime-environment-for-users) | Install, activate, `$SKA`, `ska_sync`, testing, dev environment |
| [Ska3 shiny for users](https://github.com/sot/skare3/wiki/Ska3-shiny-for-users) | The "shiny" release line for users |

## Environment / release engineering

- [Ska3 runtime environment for maintainers](https://github.com/sot/skare3/wiki/Ska3-runtime-environment-for-maintainers) (and an `(old)` variant)
- [Shiny Ska3 for maintainers](https://github.com/sot/skare3/wiki/Shiny-Ska3-for-maintainers)
- [Updating the Core Conda Packages](https://github.com/sot/skare3/wiki/Updating-the-Core-Conda-Packages)
- [Package update and metapackage update example](https://github.com/sot/skare3/wiki/Package-update-and-metapackage-update-example)
- [Out‐of‐ska3‐flight Package Maintenance](https://github.com/sot/skare3/wiki/Out%E2%80%90of%E2%80%90ska3%E2%80%90flight-Package-Maintenance)
- [Non‐FSDS Package Maintenance](https://github.com/sot/skare3/wiki/Non%E2%80%90FSDS-Package-Maintenance)
- [Ska3 RE package development flowchart](https://github.com/sot/skare3/wiki/Ska3-RE-package-development-flowchart)
- [Setting up a Ska3 on Hydra](https://github.com/sot/skare3/wiki/Setting-up-a-Ska3-on-Hydra)
- Notes: building skare3 static packages for [prime](https://github.com/sot/skare3/wiki/Notes:-building-skare3-static-packages-for-prime) / [shiny](https://github.com/sot/skare3/wiki/Notes:-building-skare3-static-packages-for-shiny)
- [Notes: Setting up a Windows ska3 environment like the FOT matlab environment](https://github.com/sot/skare3/wiki/Notes:-Setting-up-a-Windows-ska3-environment-like-the-FOT-matlab-environment)

## Promotion plans and release testing

Per-release-line promotion plans and testing pages: [Ska3 Major Update Promotion Plan](https://github.com/sot/skare3/wiki/Ska3-Major-Update-Promotion-Plan),
[Major Ska3 Update Testing Template](https://github.com/sot/skare3/wiki/Major-Ska3-Update-Testing-Template),
plus per-version pages for prime (2023.1 / py3.10), Speedy (2024.1 / py3.11),
2025.1 / py3.12, 2026.1 / py3.13, and shiny.

- [Test and review requirements for operational promotion on linux and MacOSX](https://github.com/sot/skare3/wiki/Test-and-review-requirements-for-operational-promotion-on-linux-and-MacOSX)
- [Test and review requirements for operational promotion for FOT Matlab tools](https://github.com/sot/skare3/wiki/Test-and-review-requirements-for-operational-promotion-for-FOT-Matlab-tools)
- [Functional testing of items not in ska_testr](https://github.com/sot/skare3/wiki/Functional-testing-of-items-not-in-ska_testr)

## Development practice

- [Configuration for linting and formatting with ruff](https://github.com/sot/skare3/wiki/Configuration-for-linting-and-formatting-with-ruff)
- [Documentation Guide](https://github.com/sot/skare3/wiki/Documentation-Guide)
- [Self code review](https://github.com/sot/skare3/wiki/Self-code-review)
- [Bulk Github](https://github.com/sot/skare3/wiki/Bulk-Github)
- [Thoughts on Continuous Integration](https://github.com/sot/skare3/wiki/Thoughts-on-Continuous-Integration)
- [Sybase dependencies in sot org repos](https://github.com/sot/skare3/wiki/Sybase-dependencies-in-sot-org-repos) (the longest page in the wiki)
- [Road Map](https://github.com/sot/skare3/wiki/Road-Map)
