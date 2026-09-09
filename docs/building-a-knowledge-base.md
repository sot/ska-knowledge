# Building an agent knowledge base: an annotated session

This is the complete sequence of prompts that produced
[sot/ska-knowledge](https://github.com/sot/ska-knowledge) — a Chandra/Ska knowledge base
that works both as a Claude Code plugin and as a human-readable handbook — annotated with
what each prompt accomplished and what went wrong.

It is written for someone building an equivalent knowledge base for a *different* code
infrastructure. Read part 1 for the concepts, part 2 for the prompts, part 3 for the
mistakes worth skipping.

Session date: 2026-09-02 → 2026-09-09. Claude Code 2.1.x, Opus 5.

---

## Part 1 — Concepts you need first

### Skill

A directory containing `SKILL.md`, optionally with `references/` and `scripts/`
alongside:

```
skills/
└── my-topic/
    ├── SKILL.md          # frontmatter: name + description; body under ~200 lines
    └── references/
        ├── deep-detail-a.md
        └── deep-detail-b.md
```

The critical mechanic is **progressive disclosure**: only each skill's `description` sits
in context permanently (a few hundred tokens total). When the description matches what
you're asking about, Claude invokes the skill, which pulls `SKILL.md` into context; it
then reads `references/*.md` only if needed. So depth is nearly free until it's relevant.

Write the `description` for *matching*, naming concrete packages and concepts — that string
is the entire basis on which Claude decides your skill is relevant.

### Plugin

A named bundle that can ship skills, subagents, slash commands, hooks, and MCP servers.
Declared by `.claude-plugin/plugin.json`:

```json
{
  "name": "ska",
  "description": "...",
  "author": { "name": "Chandra SOT / ACA team" }
}
```

**Omit `version` deliberately.** Then the version *is* the commit SHA, so merging to the
default branch is the entire release process — no bump ritual. (It displays as `unknown`
only while the repo has no commits at all.)

### Marketplace

Here is the part that confuses everyone: **a "marketplace" is not a store, and there is no
global registry.** It is a JSON index file inside a git repo. The conda analogy is exact:

| Conda | Claude Code |
|---|---|
| Channel (a URL you add) | Marketplace |
| `repodata.json` — the channel index | `.claude-plugin/marketplace.json` |
| Package | Plugin |
| `conda config --add channels …` | `claude plugin marketplace add owner/repo` |
| `conda install -c chan pkg` | `claude plugin install pkg@chan` |
| anaconda.org — central registry | **no equivalent for third-party plugins** |

Nothing is uploaded and nothing is registered with Anthropic. Discovery is word of mouth:
someone must be *told* to run `marketplace add`. Making the GitHub repo public does not
list it anywhere — it only means the clone works without credentials.

**One repo can be both** the marketplace and the plugin, via a marketplace entry with
`"source": "./"`. That keeps `skills/` at the repo root with no nesting:

```json
{
  "name": "sot",
  "description": "...",
  "owner": { "name": "Chandra SOT / ACA team" },
  "plugins": [
    { "name": "ska", "source": "./", "description": "..." }
  ]
}
```

Name the marketplace and the plugin *differently*. We shipped `ska@ska` first, which reads
like a typo and makes the cache path `cache/ska/ska/`; renaming the marketplace to `sot`
gave `ska@sot`. Do that on day one — it is awkward once people have installed.

### The cache — the single biggest gotcha

Installing **copies** the repo into a snapshot:

```
<config>/plugins/cache/<marketplace>/<plugin>/<commit-sha>/
```

**That snapshot, not your repo, is what Claude loads.** Editing your source files changes
nothing until you refresh it, and there are two different update commands that are easy to
confuse:

```bash
claude plugin marketplace update sot   # refreshes the INDEX only — not the content
claude plugin update ska@sot           # re-copies the content   <-- the one you need
```

Then restart. This cost us a wrong conclusion: an A/B test "showed" newly written content
didn't help, when Claude was in fact reading a pre-edit snapshot. Verify what is live:

```bash
diff -r ~/.claude/plugins/cache/sot/ska/*/skills ./skills
```

Third-party marketplaces also have **auto-update off by default**, so teammates go stale
silently unless they enable it.

### Install scope

- **user** (the default) — global, applies in every directory. **Recommend this.**
- **project** — a committed `.claude/settings.json` with `extraKnownMarketplaces` +
  `enabledPlugins`; teammates get it on clone after the folder-trust prompt.
- **local** — this repo, just you.

We started out planning per-repo project config and **dropped it**. User scope covers bare
analysis directories and notebooks, not just package repos — which is where a lot of real
work happens and where project config gives zero coverage. It is also one action instead of
a file drifting across ~90 repos, and it keeps the plugin opt-in rather than
auto-registering a marketplace for anyone who clones. Project scope stays in reserve for CI
or shared dev containers.

### Two environment facts that will bite you

1. **`/plugin` does not exist in the VS Code extension.** Plugin management needs a
   terminal. If a teammate has no `claude` on their PATH, the extension ships one at
   `~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude`.
   To check status *from inside* the extension, just ask Claude
   **"list your available skills"**.
2. **`CLAUDE_CONFIG_DIR` decides which config you write.** If you run more than one
   account, a session launched under one account will write plugin config for that account,
   including from Bash subprocesses. That is how this session contaminated the wrong config
   area. To test plugins without touching any real config, point it at a throwaway dir:
   ```bash
   CLAUDE_CONFIG_DIR=/tmp/sandbox claude plugin marketplace add ~/git/my-kb
   CLAUDE_CONFIG_DIR=/tmp/sandbox claude plugin install my-plugin@my-marketplace
   ```

---

## Part 2 — The prompts, in order

Verbatim, with annotation. Nothing here is Chandra-specific except the subject matter —
substitute your own domain.

### 1. Framing: ask for a plan, not an artifact

> Hey claude, this is the skare3 repo which serves to organize the Python and Perl packages
> that comprise the ska/ska3 runtime environment, or skare3. This serves as the basis for
> operations and analysis code that are used in the Chandra X-ray Observatory operations.
>
> I want you to learn about what we do so that you can most effectively help in our ska
> coding and chandra analysis.
>
> The first thing is to come up with a plan for organizing all the information and skills
> you will gather. This will come from web sites or documents describing chandra and
> relevant hardware on board, and then by looking into the Python (mostly) and Perl (a few)
> packages that we use. When we are developing those packages we need a way to always
> provide this broader context, for instance extracting aspect camera image data is done
> with the get_aca_images() function that is part of the chandra_aca package.
>
> So what is the best way to organize such a knowledge base for you to refer to? Ideally
> this is something that can be used by other folks doing analysis as well.

*Why this worked:* it asks for **organization**, not content, and supplies a concrete
worked example of the pain (`get_aca_images`). It also states the second audience — other
analysts — which forced a design that is readable by humans and not just machines.

*What it triggered:* repo exploration, then four clarifying questions.

### 2. Four design decisions

Claude asked; these were the answers:

| Question | Decision |
|---|---|
| Where should it live? | A new dedicated repo, shipped as a Claude Code plugin |
| Primary consumer? | Claude-first but human-readable markdown; no site build |
| First content? | Task→function map · domain primer · data & environment guide |
| Keeping it fresh? | Curated routing layer, pointing at live docs for API detail |

*The "curated + pointers" choice was the most consequential.* It means the KB never mirrors
API signatures — those drift every release. It says "for X, reach for `pkg.mod.func`" and
lets Claude read the live source for arguments.

### 3–5. Interrogate the mechanism before approving

> is the marketplace plugin required or is the .claude/settings.json sufficient?

> I don't understand the marketplace and plugin concepts. Is there some global registry
> where non-team members could discover this?

> What would the maintenance process look like? If we add a new function for instance.

*Do this.* These three questions surfaced that a marketplace is mandatory, that there is no
global registry, and — from the maintenance question — the rule that keeps the KB
maintainable: **most new functions require no edit at all**, because the KB is a routing
layer, not an API mirror. Edits are triggered by changes in *routing*, not API surface.

### 6. Approve the plan, then demand proof

> Can i see this in action?

*The highest-value prompt in the session.* It produced a controlled A/B — same questions,
plugin off vs on — and the result **contradicted the optimistic story**: baseline Claude
already knew the mainstream API well, because the repos are public and in training data.
On one question the baseline *beat* the draft routing table.

That reordered the whole project. Ask for this early.

### 7. Act on the evidence

> reorder

*Result:* content got re-prioritised by **what a model cannot already know**:

| Priority | Category |
|---|---|
| 1 | Gotchas and default-wrong traps |
| 2 | Team practice and environment (in no repo's docs) |
| 3 | Genuinely undocumented packages |
| 4 | Domain conventions |
| 5 | Mainstream API reference — *write only where a real trap exists* |

And a rule went into `CONTRIBUTING.md`: **a routing entry that only restates the docs is
not neutral, it is a liability** — it spends context and can crowd out better knowledge the
model already has.

### 8. Point at the real sources

> Before going to phase 1, you should read
> https://github.com/sot/skare3/wiki/Ska-Overview and
> https://github.com/sot/skare3/wiki/Ska3-runtime-environment-for-users

*Critical intervention.* Claude had concluded the repo was undocumented — but a GitHub
**wiki is a separate git repo** (`<repo>.wiki.git`) that a working-tree search never sees.
The wiki had 36 pages, including a "do NOT use in new code" list that became the single
highest-value section of the KB.

**Lesson for your KB:** volunteer your documentation locations. Wikis, Confluence, Google
Docs, PDFs, Slack channels — an agent cannot find what is not on disk.

### 9–10. Understand what the agent actually knows

> I'm still working to understand what is going on behind the scenes with this knowledge
> base. Assume a question Q="Write a short Ska script: fetch TEPHIN for one day, convert
> the start time to a Chandra date string, and plot it against time. Just the code." like
> in one of your A/B tests. First, when you write "claude plugin disable ska@ska", what
> resources is claude using to answer the question? Does it already have some ska context
> in memory or is it starting from scratch?

> As follow-on, when you say "claude plugin enable ska@ska", where exactly is the ska@ska
> coming from? does that refer to some files on disk? where is it defined? I assume
> eventually this points back to the KB in ~/git/ska-knowledge.

*These two forced the most important technical findings of the session.*

The first established that with the plugin off, Claude works from **model weights alone**
(no cross-session memory; each run is a fresh context) — and that **the training prior
skews legacy**, because decades of history outweigh current names in public code. Zero
tools, empty directory, it wrote `from Chandra.Time import DateTime` and
`from Ska.engarchive import fetch`, both deprecated.

That reframed the KB's job: not teaching the API, but **voting against the training prior**
where local convention diverges from code volume.

The second traced `ska@ska` through four files to the cache snapshot — and revealed that
every A/B test so far had been reading **stale content**.

### 11–14. Environment hygiene

> In the most recent session (claude configuration directory isolation) we fixed some
> cross-talk between my two account configuration areas taldcroft@cfa.harvard.edu (ska) and
> taldcroft@gmail.com (oss). you should be aware of that since previous work in this
> session was writing to the wrong config (~/.claude-oss).

> I am always running cfa/ska with code-ska that lives in ~/.claude. Nothing in my cfa/ska
> work should touch anything in the ~/.claude-oss area.

> for (2) move the hey-claude plan into ~/.claude

> About "claude on PATH is ~/.local/bin/claude → version 2.1.222, and it defaults to
> ~/.claude-oss." Why is that, and will this continue to be a problem when you run claude
> commands within my code-ska sessions?

*Skip this whole section if you have one account.* If you have two, note the outcome: the
binary defaults to `~/.claude`; the *session* decides, via `CLAUDE_CONFIG_DIR`, and Bash
subprocesses inherit it. The last prompt corrected a wrong explanation Claude had given —
worth doing, since the wrong mechanism was already written into a memory file.

### 15–17. Checkpoint and commit

> OK, hopefully the account cross talk mess is resolved. Let's get back to work. Can you
> remind me of the plan and where we are at?

> What are the 10 files to commit?

> OK, go ahead and commit.

*Note the middle one.* Asking for the file list before committing caught that the real
count was 14, not the 10 Claude had claimed — it had quoted a markdown-only subtotal.
Cheap check, worth making a habit.

### 18–21. Fix naming, then solve distribution

> Rename the marketplace to sot now

> /plugin marketplace remove ska
> /plugin marketplace add ~/git/ska-knowledge
> /plugin install ska@sot
>
> When you say "/plugin marketplace remove ska" (and the other two), is that something I'm
> supposed to type now? In the VS code claude extension prompt window that doesn't work.

> So now if I open a new VS code window from ~/git/cheta to start working on a new cheta
> feature, do I need to pull in the new ska@sot plugin? How can I check the status from
> within the VS code extension window?

> What do my teammates need to do for a one-time global install like mine? that seems a bit
> cleaner than the .claude/settings.json in every repo, but I defer to you for the best
> workflow.

*The second prompt is a genuine documentation bug report* — Claude had given slash-command
syntax to someone working in the VS Code extension, where `/plugin` does not exist. The
fourth prompt's instinct was right and became the shipped recommendation (user scope,
per-repo config dropped).

### 22–24. Execute the phases

> OK, great progress! Do the next phase now.

> You can skip all the remaining packages. Those are really applications that are not
> primarily intended as importable packages. Move on to phase 3.

> Move on to chandra-domain. From the Chandra POG, chapter 5
> (https://cxc.harvard.edu/proposer/POG/html/chap5.html#tth_chAp5) should be your focus.
> This PDF gives you important info about the ACA hardware and telemetry and commanding :
> ~/Documents/Chandra/DM11\ ACA\ user\ guide.pdf

*The middle prompt is expert pruning* — it stopped ~18 files of low-value work with one
sentence of domain judgment an agent could not have reached. The third is the same move as
prompt 8: hand over the authoritative sources, including a local PDF.

---

## Part 3 — Mistakes to skip

Every one of these actually happened.

**1. Don't trust a single A/B run, and use a pristine directory.**
Earlier test outputs sitting in the working directory were readable via `Grep`, so the
"no-KB" arm could read a correct answer off disk. Combined with single-run variance, this
produced a confident and wrong conclusion. Use an empty directory, and distinguish
*zero-tools* (measures pure model knowledge) from *tools-allowed* (measures real
behaviour) — they gave materially different answers.

**2. Refresh the plugin cache before concluding anything.**
`claude plugin update <plugin>@<marketplace>` then restart. Otherwise you are testing
content you have already replaced.

**3. Introspect the installed release, never grep the repo.**
Local checkouts run ahead of what is deployed. Two entries were written wrong this way:
classes documented in the wrong module because `master` had moved them, and a function
documented that did not exist in the installed version.

**4. Expect environments to disagree, and version-gate claims.**
Two environments here ship *different versions of the same package*, and the
higher-numbered environment had the **older** package. One function existed in one and not
the other; another function's defaults changed (`20 → 35.0`), and a flag flipped
(`False → True`) which silently changed whether it raised on bad input.

**5. Build a fact checker on day one.**
`scripts/check_symbols.py` asserts every symbol the KB names actually exists, plus concrete
numbers and defaults, and runs in **both** environments — asserting *opposite* values in
each where the API diverged. It caught four wrong claims that had already been committed.
Prose rots silently; assertions fail loudly.

**6. Document the pattern, not the instances.**
Two dozen similar tools became one file describing their shared shape plus a table of
specifics. Far more useful than two dozen thin files repeating the same scaffolding.

---

## Part 4 — Adapting this

A workable order for a different codebase:

1. **Scaffold and prove the loop before writing content.** Two manifests, one router skill
   with ~15 entries, one real reference file. Install it, then confirm in a *fresh* session
   that a cold question routes correctly. Don't write in bulk until that round-trip works.
2. **A/B immediately.** Find out what your model already knows about *your* code. If it is
   public, assume it knows the API and stop planning to re-document it.
3. **Write the conventions layer first** — deprecations, "always use X", house style,
   which of several similar functions is canonical. This is where the value concentrated in
   every measurement we made.
4. **Then environment and team practice** — how to get data, which env, what only works
   on certain hosts. Usually written down nowhere.
5. **Then the genuinely undocumented corners.** Prioritise with data, not intuition: we
   ranked by README length, presence of `docs/`, and commit count, which demoted a package
   we would otherwise have written early and promoted several we would have missed.
6. **Domain background last**, and only the conventions that make numbers wrong — units,
   epochs, sign and component orders, coordinate origins.

Two habits that paid off throughout: ask Claude to **show its verification**, not just its
conclusion; and when it states something confidently, ask **how it knows**. Several of the
findings above came from exactly that question.
