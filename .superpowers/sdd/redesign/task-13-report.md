# Task 13 — Restyle ExamSearch — Report

## Files changed
- `frontend/src/pages/ExamSearch.tsx`
  - Imported `Button` from `../components/ui`.
  - Replaced the three bespoke `.btn .btn--primary/--secondary/--ghost` `<button>`s with `<Button variant="primary|secondary|ghost">`, preserving each `onClick`, `disabled`, and inline SVG + Dutch label (`Beste match`, `Willekeurig`, `Opnieuw`). Added `className="search-btn"` for icon+label alignment.
  - Retokenised the decorative hero SVG strokes from dead old tokens to live ones: `--blue-light` → `--sky-300`, `--peach` → `--peach-300`, `--blue` → `--sky-500`.
  - Search logic untouched: `query`/`maxResults`/`results`/`status`/`error` state, `doFetch` POST `/api/v1/fetch` with `credentials: 'include'`, 401 → `onUnauthorized()`, loading/error/done rendering, `handleKeyDown` Enter-to-search, and `ResultCard` output all preserved.
- `frontend/src/pages/ExamSearch.css`
  - Full retokenisation. Removed the now-dead `.btn`, `.btn--primary/--secondary/--ghost` rules (and their hover/`#fff` color).
  - Error border `#fecaca` → `var(--danger-ink)`; error fill/text → `--danger-fill`/`--danger-ink`.
  - Replaced all pre-redesign dead tokens (`--navy`, `--navy-deep`, `--blue`, `--blue-light`, `--blue-wash`, `--blue-mist`, `--surface`(old), `--border`, `--bg`, `--text`, `--text-muted`, `--text-faint`, `--error`, `--error-bg`, `--radius-xl`) with the new token layer (`--color-surface`, `--color-outline`, `--color-text`, `--color-heading`, `--color-text-muted`, `--color-text-faint`, `--color-primary`, `--color-focus`, `--sky-*`, `--peach-300`, `--danger-*`, `--radius-*`, `--outline-width(-card)`, `--shadow-hard`, `--space-*`, `--radius-pill`).
  - Search card upgraded to the design signature: `--outline-width-card` bold outline + `--shadow-hard` offset shadow.

## check-tokens proof
Before: `ExamSearch.css:116 color: #fff` and `ExamSearch.css:210 border: 1px solid #fecaca` were offenders.
After: `npm run check-tokens` → ExamSearch.css NO LONGER listed. Only remaining offender is `pages/Practice.css:16` (`#0a3a7a`), which belongs to Task 14, not this task.

## Build / Lint
- `npm run build` → PASS (`tsc -b && vite build`, built in ~149ms).
- `npm run lint` → PASS (oxlint, no output).

## Judgment calls
- **Textarea kept as textarea (not forced to `Input`).** The search field is a multiline `<textarea rows={3}>` with `onKeyDown` (Enter submits, Shift+Enter newline) and `resize: vertical`. The `Input` primitive wraps a single-line `<input>`, which would drop multiline UX. Per spec guidance I retokenised `.search-input` to mirror the `Input` primitive's look (surface bg, `--outline-width` `--color-outline` border, `--radius-md`, `--color-focus` + `--sky-200` focus ring) instead. So `Button` is imported but `Input` is not.
- **Max-results number input** left as a native `<input type="number">` (not a search field / not a `.btn`) and simply retokenised to match the primitive input styling.
- **`.search-btn` helper class** added because the shared `.ui-btn` primitive does not set `inline-flex`/`gap`; this restores icon+label alignment and `nowrap`/mobile-stretch behaviour without altering the primitive.
- Search card given `--shadow-hard` (design signature for primary cards) rather than the old soft blue shadow.

## Concerns
- None blocking. `Practice.css` still fails check-tokens but that is Task 14's scope.
