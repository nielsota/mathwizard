# Task 11 Report — Restyle Home (hub)

## Files changed
- `frontend/src/pages/Home.tsx` — hero, topic tiles, and search lane rebuilt on the shared `Card`/`Button` primitives.
- `frontend/src/pages/Home.css` — fully retokenised; no raw hex remains.

## What changed

### Home.tsx
- Hero converted to `<Card band hard>` (peach top-band + hard offset shadow signature) instead of a bare `<header>`.
- Topic tiles converted from raw `<button>` to `<Card role="button" tabIndex={0}>` with `onClick` + `onKeyDown` (Enter/Space) so keyboard activation is preserved after moving from a native button to a div-based Card. Topic navigation (`/practice/:slug`) unchanged.
- Inline `animationDelay` stagger kept (`0.06 * index`); the CSS keyframe it drives now uses `--ease` timing.
- Search lane converted to `<Card hard>` containing the copy + a real `<Button variant="primary">` primary CTA that navigates to `/search`. Removed the decorative navy/graph-paper SVG accent (old visual language).

### Home.css
- Removed navy hero gradient, `#0a3a7a` icon gradient, navy search-lane gradient, `#fff` text, and all `rgba(...)` shadows.
- Surface/outline/radius/padding now inherited from the `Card` primitive; Home.css only adds layout, typography, hover lift, and the topic grid.
- Hover lift on topic cards now uses `--shadow-hard` (signature) instead of a soft navy blur.
- Topic icon: flat `--color-primary-fill` fill with `--outline-width` ink outline instead of the navy gradient chip.
- All colors → semantic tokens (`--color-heading`, `--color-text-muted`, `--color-primary`, `--color-primary-fill`), all gaps/margins → `--space-*`, radii → `--radius-*`, motion → `--ease`.

## check-tokens proof
`npm run check-tokens` output (offenders):
```
pages/ExamSearch.css:116
pages/ExamSearch.css:210
pages/Login.css:46, 169, 180, 181, 182
pages/Practice.css:16
```
`Home.css` is **no longer** in the offender list. (The script still exits 1 because other, out-of-scope pages — ExamSearch/Login/Practice — remain to be done in later tasks.)

## Build / Lint
- `npm run build` → PASS (built in ~176ms, 59 modules).
- `npm run lint` (oxlint) → PASS (no warnings/errors).

## Judgment calls
- Topic tiles use `Card` as `role="button"` + `tabIndex` + `onKeyDown` rather than nesting a `<button>`, keeping single-element semantics and full keyboard support.
- Gave both the hero and the search CTA card `hard` (offset shadow) as the two "primary" surfaces on the page, per the signature guidance; topic tiles only get the hard shadow on hover as their lift.
- Dropped the decorative circle/grid SVG in the search lane — it belonged to the retired graph-paper/navy language and has no token-safe equivalent.
- Kept pixel font-sizes (46/30/26/17px etc.) since there is no type-scale token; only color/radius/shadow/space are token-enforced.

## Concerns
- None blocking. Kept raw px font sizes (no type token exists); consistent with other restyled components (e.g. ExerciseCard).
