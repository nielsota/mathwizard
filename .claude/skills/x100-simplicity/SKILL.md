---
name: x100-simplicity
description: User-defined simplicity guidelines (X100-X109) for hunting dead code, defensive cruft, and speculative generality. Use when reviewing code for unused symbols, unreachable branches, try/except for impossible cases, re-validation of validated inputs, backwards-compat shims with no consumers, or abstractions with one implementation.
---

# Simplicity (X100-X109)

Guidelines for spotting and removing **code that exists but shouldn't**. Three families: dead code, defensive cruft, and speculative generality. Each finding here should answer "what would break if I deleted this?" with "nothing observable."

## Quick Reference

| Code | Topic | Family |
|------|-------|--------|
| X100 | Unused symbols (imports, functions, classes, constants) | Dead |
| X101 | Unreachable branches and commented-out code | Dead |
| X102 | Parameters always passed the same value | Dead |
| X103 | `try/except` that cannot fire or just re-raises | Defensive |
| X104 | Re-validation of inputs already validated upstream | Defensive |
| X105 | Fallback paths for impossible states | Defensive |
| X106 | Backwards-compat shims with no remaining callers | Defensive |
| X107 | Feature flags hardcoded the same in all envs | Defensive |
| X108 | Parameters / config knobs with one value across the codebase | Speculative |
| X109 | Abstract bases / Protocols / helpers with a single user | Speculative |

## Key Principles

1. **Falseable findings must be verified** — never flag "unused" or "single-caller" without grepping the repo first.
2. **The deletion test** — if removing the code changes nothing observable, it's a candidate.
3. **Defensive ≠ safe** — broad `except:` clauses that swallow exceptions hide bugs and are higher severity than mere clutter.
4. **Trust your boundaries** — internal code can trust framework guarantees (Pydantic validation, type system); only validate at system boundaries.

---

## X100 — Unused symbols

Functions, methods, classes, or module-level constants with no references in `src/` or `tests/` are dead.

**Verify before flagging**: `grep -r "<symbol_name>" src/ tests/`. If the only hit is the definition, it's dead.

**Common cases**:
- Imports left after a refactor
- Helper functions whose only caller was deleted
- Old "version 1" classes kept alongside their replacements
- Constants exported but never imported

**Don't flag**: dynamic dispatch (registry lookups, `getattr`, plugin systems) where the symbol is referenced by string. Search for the string form too.

## X101 — Unreachable branches and commented-out code

- Code after unconditional `return` / `raise` / `sys.exit()`
- `if False:`, `if True:` followed by `else:`, `while False:`
- Dead `elif` chains where an earlier branch matches every input
- Commented-out code blocks longer than one line — git history is the right place for old code

## X102 — Constant-valued parameters

A parameter that's passed the same literal value at every call site is not a parameter — it's a constant. Either inline the value or document why the knob exists.

**Verify**: grep call sites, list distinct values passed.

Also flag parameters that are accepted but never read inside the function body.

## X103 — Inert `try/except`

Forms to flag:

```python
try:
    x = 1 + 1          # cannot raise the caught exception
except ValueError:
    ...

try:
    do_thing()
except Exception:
    raise              # no logging, no transformation, no cleanup

try:
    do_thing()
except SomeError as e:
    raise SomeError(str(e))   # re-wrap with no added info
```

`except Exception:` followed by a bare `raise` or empty body almost always hides bugs — flag as **high** severity.

## X104 — Re-validation of pre-validated inputs

If a public function validates its arguments, private helpers it calls don't need to re-check. If a Pydantic model already enforces `field: str` is non-None, an `if x is None: raise ValueError` downstream is noise.

**Pattern**: look for `if x is None: raise` immediately after pulling `x` from a typed model or function return.

## X105 — Fallback paths for impossible states

Branches reached only when the type system or upstream validation has already failed. Often signaled by comments like:

- `# defensive`
- `# just in case`
- `# shouldn't happen`
- `# fallback for legacy data` (when there's no legacy data)

Ask: can a real input reach this branch? If no, delete it (or replace with `assert never_reached()` if the branch is genuinely unreachable but the type checker can't prove it).

## X106 — Orphaned backwards-compat shims

Old field names, deprecated aliases, or compatibility wrappers that exist for callers that no longer exist.

**Verify**: grep for usage of the old shape. If only the shim itself uses it, the shim is dead.

## X107 — Stale feature flags

Settings flags that have been hardcoded the same in every environment for a long time. The flag isn't gating anything — it's just dead config plus dead `if flag:` branches.

**Verify**: check `.env`, `.env.example`, settings classes, deployment configs. If the value is the same everywhere, propose removing the flag and inlining the active branch.

## X108 — Single-value config knobs

Settings fields, kwargs, or configuration parameters never overridden anywhere in the codebase. The "configurability" is fiction.

## X109 — Single-user abstractions

- Abstract base classes / Protocols with exactly one concrete implementation, no plausible second one in flight
- Strategy / factory patterns with one entry
- "Helper" functions called from exactly one place — inline candidates
- Generic registries with one registrant

**Don't flag**: protocols used purely for testing seams (mocking), or where a second implementation is on a known roadmap.

---

## Severity guidance

- Defensive cruft that **swallows or hides errors** → **high** (correctness risk)
- Defensive cruft that's just noise → **low** or **medium**
- Dead code → usually **low** (clutter), **medium** if it's a substantial block
- Speculative generality → **medium** (extra surface area, harder to refactor later)

## Effort guidance

- Single-symbol deletions, comment removal, single-line `try/except` collapse → **S**
- Removing a parameter or knob (touches all call sites) → **M**
- Removing an abstraction layer or feature flag (touches branches + config + tests) → **L**
