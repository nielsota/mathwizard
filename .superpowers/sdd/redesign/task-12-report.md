# Task 12 Report — Restyle Login (and fix `--background` bug)

## Files changed
- `frontend/src/pages/Login.tsx` — rebuilt using `Card` (hard shadow), `Input`, `Button` (primary, fullWidth), and `Logo` primitives; removed the ∫ integral motif, navy proof panel, and raw `<input>/<button>` markup. Login form logic preserved verbatim: state (`username`/`password`/`loading`/`error`), `handleSubmit`, `POST /auth/login` with `credentials: 'include'`, error handling, `onLogin` callback, Dutch copy.
- `frontend/src/pages/Login.css` — full retokenise; removed all raw hex/rgba and non-token values.

## Bug fix confirmation
The invalid `var(--background)` reference (old `Login.css` line 11) is fixed. The new `.login-page` uses `background: var(--color-bg);`. No `--background` remains anywhere in `Login.css`.

## check-tokens proof
`npm run check-tokens` output — `Login.css` is NO LONGER in the offender list:
```
✗ 3 raw hex value(s) found outside index.css:
pages/ExamSearch.css:116  color: #fff;
pages/ExamSearch.css:210  border: 1px solid #fecaca;
pages/Practice.css:16  background: linear-gradient(135deg, var(--navy) 0%, #0a3a7a 100%);
```
Remaining offenders belong to later tasks (13/14), not Task 12.

## Build / Lint
- `npm run build` → PASS (`✓ built in 149ms`).
- `npm run lint` (oxlint) → PASS (no errors).
- No linter errors in `Login.tsx`.

## Design language applied
- Warm paper bg (`--color-bg`), removed the grid/radial gradient overlays.
- Two-column shell: left paper brand panel (`--color-accent-fill` fill, bold ink outline, hard shadow) with the gem `Logo` mark (wordmark hidden, size 96) inside an outlined surface tile; right form is an outlined `Card` with the signature `hard` offset shadow.
- Space Grotesk headings via `--font-display`; error uses `--danger-fill`/`--danger-ink`.
- Every color/radius/shadow/spacing references a token; no raw hex.

## Judgment calls
- Kept the Dutch "Beveiligde sessie" kicker (was previously an eyebrow on the card) as the brand-panel kicker, and moved the "Welkom terug" title into the form Card.
- Dropped the decorative axis lines and equation glyphs (part of the removed ∫/proof-panel motif) rather than retokenising them, per the neo-geometric direction.
- Simplified the submit button to `Button` text only (removed the "→" span) since the primitive owns its styling/hover.
- Added `id`s to inputs so `Input`'s `label`/`htmlFor` association works.

## Concerns
- None blocking. Visual check on `/login` deferred per instructions (dev server not run).
