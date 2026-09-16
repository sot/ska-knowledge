# Self code review checklist

## What it's for

The checks a developer is expected to run over their own diff **before** requesting review.
Applying these unprompted is a large part of what makes generated code read as team code.

## Links

- Source: https://github.com/sot/skare3/wiki/Self-code-review
- The wiki is a separate git repo (`skare3.wiki.git`) and is **not** in a skare3 checkout.
- Formatting is `ruff` — let it wrap long expressions rather than hand-wrapping.

## The checks

### 1. Don't repeat yourself

Any time you copy/paste a line, ask whether it can be factored out. The subtle case is a
repeated *expression*, not a repeated block:

```python
# NO - the path is built twice, so the two branches have to be checked against each other
if dat is not None:
    dat.write(Path(data_root) / "notes.csv", format="ascii.csv", overwrite=True)
else:
    dat = Table.read(Path(data_root) / "notes.csv", format="ascii.csv")

# YES - single-sourced. A "_path" suffix is a handy reminder of the type.
notes_path = Path(data_root) / "notes.csv"
if dat is not None:
    dat.write(notes_path, format="ascii.csv", overwrite=True)
else:
    dat = Table.read(notes_path, format="ascii.csv")
```

### 2. Type-narrow early, at the top of the function

`CxoTimeLike` arguments become `CxoTime` immediately: `start = CxoTime(start)`. A directory
argument (`str` or `Path`) becomes a `Path`, after which `out_dir / "notes.csv"` is safe.

### 3. Never cast on demand inside a loop

Both a performance bug and a readability one — and worse when the cast result is
loop-invariant:

```python
# NO - CxoTime(scs107_intervals["datestart"]) is recomputed every iteration
for row in npnt:
    npnt_start = row["datestart"]
    npnt_stop = row["datestop"]
    if np.any(
        (CxoTime(npnt_start) >= CxoTime(scs107_intervals["datestart"]))
        & (CxoTime(npnt_start) <= CxoTime(scs107_intervals["datestop"]))
    ):
        continue
    if CxoTime(npnt_stop) - CxoTime(npnt_start) < 60 * u.s:
        continue

# YES - cast once per row, and exploit the API guarantee that `datestart` is a
# `date`-format string, which compares lexically without any casting at all.
for row in npnt:
    npnt_start = CxoTime(row["datestart"])
    npnt_stop = CxoTime(row["datestop"])

    # If the start of the interval is within an SCS107 interval, skip this row
    if np.any(
        (npnt_start.date >= scs107_intervals["datestart"])
        & (npnt_start.date <= scs107_intervals["datestop"])
    ):
        continue

    # If down to less than a minute, skip
    if npnt_stop - npnt_start < 60 * u.s:
        continue
```

### 4. Filter table columns in the right order

```python
dat[colname][ok]  # YES: fast
dat[ok][colname]  # NO: builds a full intermediate table first
```

### 5. Use a ternary where it fits

A variation on DRY — it avoids repeating the name of the variable being defined:

```python
value = something if bool_value else something_else
```

Applies as long as each of the three parts is shorter than a line. Ruff wraps longer ones
readably, and parentheses around the condition are encouraged where they help:

```python
value = (
    this_is_a_pretty_long_expression
    if (some_condition and some_other_condition)
    else this_is_a_different_long_expression
)
```

## Related

- [../SKILL.md](../SKILL.md) — the Ska-specific conventions these sit on top of.
- [analysis-notebooks.md](analysis-notebooks.md) — where the checklist relaxes.
- [../../ska-pull-requests/SKILL.md](../../ska-pull-requests/SKILL.md) — the next step: the
  PR description these checks are expected to have preceded.
