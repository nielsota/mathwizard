# Task 9 Report: Restyle ExerciseCard

## Files changed
- `frontend/src/components/ExerciseCard.tsx` — imported `Badge` from `./ui`; replaced the three bespoke `<span className="ex-badge …">` chips (difficulty, marks, calculator) with `<Badge tone={…}>`. `difficultyMeta()` now returns `{ label, tone }` instead of `{ label, className }`.
- `frontend/src/components/ExerciseCard.css` — removed all dead `.ex-badge*` classes (base + `--marks`, `--calc`, `--no-calc`, `--difficulty`, `--difficulty-easy/medium/hard/unknown`) which held all 14 raw-hex offenders; retokenised every remaining rule (old undefined tokens like `--surface`, `--border`, `--blue-*`, `--peach-light`, `--text*`, `--border-light` were replaced with the new token layer).

## Difficulty → tone mapping (in component)
| difficulty value | Dutch label | Badge tone |
|---|---|---|
| `null` | Onbekend | `neutral` |
| `<= 1` | Makkelijk | `easy` |
| `=== 2` | Gemiddeld | `med` |
| `>= 3` | Moeilijk | `hard` |

Marks chip (`{max_marks}p`) and calculator chip (`Rekenmachine` / `Zonder rekenmachine`) → `Badge tone="neutral"`.

## Retokenisation summary
- Card surface: `--color-surface` + `var(--outline-width-card) solid var(--color-outline)` + `--radius-lg` (matches `Card` primitive styling; applied directly rather than wrapping in `<Card>` to preserve the expand/collapse `<article>` interaction).
- Hover / expanded elevation: raw `rgba(...)` shadows → `--shadow-soft`.
- Number/title meta text → `--color-text-muted`.
- Toggle chevron affordance: transparent default, hover + expanded background → `--sky-100`, icon color `--color-primary`.
- Divider → `--color-hairline`; stem/parts text → `--color-text`; list marker → `--color-primary`.
- Figure frame → `var(--outline-width) solid var(--color-hairline)` + `--radius-md`.
- Paddings/gaps/margins mapped to the `--space-*` scale.

## check-tokens proof (ExerciseCard.css cleared)
Before: 14 hex offenders in `components/ExerciseCard.css` (lines 75–113).
After: `npm run check-tokens | grep -c ExerciseCard.css` → `0`. ExerciseCard.css no longer in the offender list. (Guard still exits 1 due to unrelated files: ResultCard, Home, Login, Practice, ExamSearch — out of scope for Task 9.)

## Build / lint
- `npm run build` → PASS (built in ~150ms).
- `npm run lint` (oxlint) → PASS, no findings.

## Judgment calls
- Did NOT wrap the body in `<Card>` — the card owns an expand/collapse `<article>` with header click + toggle; applying surface/outline/radius tokens directly to `.ex-card` is cleaner and keeps behavior intact (spec explicitly allows this).
- Switched the visible difficulty labels from English (`Easy/Medium/Hard/Unknown`) to Dutch (`Makkelijk/Gemiddeld/Moeilijk/Onbekend`) to honor the "all UI copy stays in Dutch" global constraint and the spec's Dutch tone mapping. This is a copy change but aligns the previously-inconsistent English badge with the rest of the Dutch UI.
- Marks + calculator chips use `tone="neutral"` (the interface note permits neutral for meta chips). This drops the previous peach/red color coding for calculator state; acceptable under the flat/neutral design language.
- Preserved: expand/collapse behavior, MathJax rendering, all ARIA attributes, chevron rotation animation, and Dutch copy (`Opgave`, `Rekenmachine`, `Uitklappen`/`Inklappen`).

## Concerns
- None blocking. Minor: the calculator-allowed vs not distinction is now purely textual (both neutral badges); if visual differentiation is desired later, a dedicated tone could be added to the `Badge` primitive.
