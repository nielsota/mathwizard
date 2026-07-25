# Figure Restyle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the in-house figure system (`FigureView` + `/figures` gallery) so plots and their chrome read as part of the neo-geometric MathWizard design system instead of the pre-redesign blue/grey look.

**Architecture:** Figures render client-side as SVG via the Mafs library (`Plot.OfX` + `Coordinates.Cartesian`), driven by a `FigureSpec` JSON from the API. Mafs is themed through its CSS custom properties (`--mafs-bg`, `--mafs-fg`, `--mafs-origin-color`) set on the `.figure-view` wrapper, while curve colors/line-styles are passed as props from a small house palette. The gallery page adopts the shared `Card` primitive and the design tokens so its chrome matches the rest of the app. No backend, API, or data-shape changes.

**Tech Stack:** React 19, TypeScript, Vite 8, `mafs@0.21.0`, `mathjs`, plain CSS with design tokens (`frontend/src/index.css`), `oxlint`, custom token-compliance guard (`frontend/scripts/check-tokens.mjs`).

## Global Constraints

- UI copy stays **Dutch** (existing convention).
- **No untokenised colors in component CSS.** Every color references the primitive/semantic tokens defined in `frontend/src/index.css` (`--sky-*`, `--peach-*`, `--ink-*`, `--color-*`, `--danger-*`). This includes `rgba(...)` literals, not just hex — remove them all. The guard `frontend/scripts/check-tokens.mjs` scans every `.css` under `src` except `index.css`.
- **Figure palette (from `docs/brand-guidelines.md`):** primary curve `--sky-600`, secondary curve/highlight `--peach-400`, axes/ticks/labels `--ink-950`, gridlines `--ink-200`, no gradients, flat ink-outlined, solid strokes.
- **Accessibility:** differentiate multiple curves by **line style (solid/dashed/dotted), not color alone** (ui-ux-pro-max chart + UX "Color Only" High-severity guidance). Maintain the global `prefers-reduced-motion` behavior already in `index.css` (do not add new looping/decorative motion to figures).
- **Signature shape language:** surfaces carry a `2px` ink outline (`--outline-width-card` / `--color-outline`), `--radius-lg`, flat fills; soft shadow `--shadow-soft` for passive surfaces, hard offset `--shadow-hard` reserved for emphasis.
- **Verification per task (no CSS unit tests exist):** `npm run check-tokens`, `npm run build`, and `npm run lint` must pass. Run them from `frontend/`. Visual confirmation on `/figures` is deferred to the user (agent-launched dev servers are killed by the harness).
- **Branch:** work on the current `feat/visual-redesign` branch. Stage only the files each task names — never `git add -A` (the working tree contains many unrelated untracked files).

## Starting State (verified)

Running `npm run check-tokens` from `frontend/` currently **FAILS** (this is the anchor the plan drives to green):

```
✗ 4 raw hex value(s) found outside index.css:

components/FigureView.css:12  color: #b00020;
pages/Figures.css:13  color: #55607a;
pages/Figures.css:24  background: #fff;
pages/Figures.css:37  color: #55607a;
```

Additionally (not caught by the guard, but in scope): `FigureView.tsx` hardcodes `DEFAULT_COLOR = '#2f5fed'`, and `FigureView.css` uses `rgba(47, 95, 237, …)` border/shadow literals.

## File Structure

- `frontend/src/components/FigureView.tsx` — **modify.** Replace the single hardcoded default curve color with a small house palette that cycles color **and** line-style per curve; keep spec-provided `element.color` as an override. Owns: mapping `FigureSpec.elements` → Mafs `Plot.OfX`.
- `frontend/src/components/FigureView.css` — **modify.** Theme the Mafs SVG canvas via its CSS custom properties, and retokenize the wrapper + error text. Owns: figure canvas chrome.
- `frontend/src/pages/Figures.tsx` — **modify.** Swap the ad-hoc `.figures-card` `<div>` for the shared `Card` primitive so gallery items match site cards. Owns: gallery composition.
- `frontend/src/pages/Figures.css` — **modify.** Retokenize page/header/title/subtitle/grid/loading; delete the now-unused `.figures-card` rule. Owns: gallery layout.
- `frontend/src/components/ui/Card.tsx` — **read only** (consumed, not changed). API: `<Card band?={boolean} hard?={boolean} className?={string} ...divProps>`.

No new files. No changes to `frontend/src/types/api.ts`, the API, or seed data.

## Out of Scope (do not do here)

- Wiring `FigureView` into Practice/ExamSearch cards (those still use the legacy `figure_images` `<img>` path — already tokenized).
- Adding a `/figures` nav link in the header.
- Rendering `x_label` / `y_label` axis titles or `element.domain` clipping (spec fields exist but are feature work, not styling). Note them as follow-ups; do not implement.
- Any backend, DB, or `mafs`/`mathjs` version changes.

---

### Task 1: Theme the figure canvas (FigureView)

**Files:**
- Modify: `frontend/src/components/FigureView.tsx` (whole file)
- Modify: `frontend/src/components/FigureView.css` (whole file)

**Interfaces:**
- Consumes: `FigureSpec` from `frontend/src/types/api.ts` — `{ viewport: { x: [number, number]; y?: [number, number] | null }, show_grid: boolean, x_label: string, y_label: string, elements: { type: 'functionGraph'; fn: string; domain?: [number, number] | null; color?: string | null }[] }`. Mafs `Plot.OfX` accepts `y: (x:number)=>number`, `color?: string` (accepts CSS `var(...)`; default is `var(--mafs-fg)`), `weight?: number`, `style?: 'solid' | 'dashed' | 'dotted'`.
- Produces: unchanged component contract — `FigureView` still takes exactly `{ spec: FigureSpec }` and renders a `.figure-view` wrapper containing a Mafs SVG. No prop/type changes for callers (`Figures.tsx`).

- [ ] **Step 1: Confirm the guard currently flags this file**

Run (from `frontend/`): `npm run check-tokens`
Expected: FAILS, output includes `components/FigureView.css:12  color: #b00020;`

- [ ] **Step 2: Rewrite `FigureView.tsx` to use a tokenized curve palette with per-curve line styles**

Replace the entire contents of `frontend/src/components/FigureView.tsx` with:

```tsx
import { Mafs, Coordinates, Plot } from 'mafs'
import { compile } from 'mathjs'
import 'mafs/core.css'
import type { FigureSpec } from '../types/api'
import './FigureView.css'

const DEFAULT_Y: [number, number] = [-10, 10]

// House palette. Color AND line style vary per curve so multiple plots stay
// distinguishable without relying on color alone (accessibility).
const CURVE_STYLES: { color: string; style: 'solid' | 'dashed' | 'dotted' }[] = [
  { color: 'var(--sky-600)', style: 'solid' },
  { color: 'var(--peach-400)', style: 'dashed' },
  { color: 'var(--ink-600)', style: 'dotted' },
]

interface FigureViewProps {
  spec: FigureSpec
}

export default function FigureView({ spec }: FigureViewProps) {
  const y = spec.viewport.y ?? DEFAULT_Y

  let plots: React.ReactNode
  try {
    plots = spec.elements.map((element, i) => {
      const node = compile(element.fn)
      const fn = (x: number) => node.evaluate({ x }) as number
      const preset = CURVE_STYLES[i % CURVE_STYLES.length]
      return (
        <Plot.OfX
          key={i}
          y={fn}
          color={element.color ?? preset.color}
          style={preset.style}
          weight={2.5}
        />
      )
    })
  } catch {
    return <div className="figure-error">Kon figuur niet tekenen</div>
  }

  return (
    <div className="figure-view">
      <Mafs viewBox={{ x: spec.viewport.x, y }} preserveAspectRatio={false}>
        {spec.show_grid && <Coordinates.Cartesian />}
        {plots}
      </Mafs>
    </div>
  )
}
```

- [ ] **Step 3: Rewrite `FigureView.css` to theme Mafs and retokenize the wrapper**

Replace the entire contents of `frontend/src/components/FigureView.css` with:

```css
.figure-view {
  width: 100%;
  max-width: 480px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: var(--outline-width-card) solid var(--color-outline);
  box-shadow: var(--shadow-soft);
  background: var(--color-surface);

  /* Theme the Mafs SVG canvas via its own custom properties:
     bold ink axes/labels on a clean surface, faint ink gridlines. */
  --mafs-bg: var(--color-surface);
  --mafs-fg: var(--ink-950);
  --mafs-origin-color: var(--ink-950);
}

.figure-error {
  padding: var(--space-4);
  color: var(--danger-ink);
  font-style: italic;
}
```

- [ ] **Step 4: Verify the file is hex-free and the app still builds/lints**

Run (from `frontend/`): `npm run build && npm run lint`
Expected: both PASS (tsc + vite build succeed; oxlint prints no errors).

Run (from repo root): `rg '#[0-9a-fA-F]{3,8}\b|rgba\(' frontend/src/components/FigureView.css`
Expected: no matches (no raw hex, no rgba literals in this file).

Note: the full `npm run check-tokens` will still FAIL after this task because `pages/Figures.css` offenders remain — that is expected and is cleared in Task 2.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/FigureView.tsx frontend/src/components/FigureView.css
git commit -m "style(figures): theme FigureView canvas with house tokens and per-curve line styles"
```

---

### Task 2: Restyle the figures gallery page

**Files:**
- Modify: `frontend/src/pages/Figures.tsx` (whole file)
- Modify: `frontend/src/pages/Figures.css` (whole file)

**Interfaces:**
- Consumes: `Card` from `../components/ui` — `<Card band?={boolean} hard?={boolean} className?={string}>children</Card>` (renders a `.ui-card` div: surface fill, 2px ink outline, `--radius-lg`, `--space-5` padding). `FigureView` from `../components/FigureView` (`{ spec }`). Types `FigureListResponse`, `FigureResponse` from `../types/api` (unchanged).
- Produces: unchanged route contract — `Figures` still takes `{ onUnauthorized: () => void }` and is rendered at `/figures` by `App.tsx`. No change to `App.tsx`.

- [ ] **Step 1: Confirm the guard currently flags this file**

Run (from `frontend/`): `npm run check-tokens`
Expected: FAILS, output includes `pages/Figures.css:24  background: #fff;` and two `#55607a` lines.

- [ ] **Step 2: Rewrite `Figures.tsx` to use the shared `Card` primitive**

Replace the entire contents of `frontend/src/pages/Figures.tsx` with:

```tsx
import { useEffect, useState } from 'react'
import FigureView from '../components/FigureView'
import { Card } from '../components/ui'
import type { FigureListResponse, FigureResponse } from '../types/api'
import './Figures.css'

interface FiguresProps {
  onUnauthorized: () => void
}

export default function Figures({ onUnauthorized }: FiguresProps) {
  const [figures, setFigures] = useState<FigureResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const listResp = await fetch('/api/v1/figures', { credentials: 'include' })
        if (listResp.status === 401) {
          onUnauthorized()
          return
        }
        if (!listResp.ok) throw new Error(`HTTP ${listResp.status}`)
        const list: FigureListResponse = await listResp.json()

        const details = await Promise.all(
          list.figures.map(async (summary) => {
            const resp = await fetch(`/api/v1/figures/${summary.id}`, {
              credentials: 'include',
            })
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
            return (await resp.json()) as FigureResponse
          }),
        )
        if (!active) return
        setFigures(details)
        setLoading(false)
      } catch (e) {
        if (!active) return
        setError(String(e))
        setLoading(false)
      }
    }

    load()
    return () => {
      active = false
    }
  }, [onUnauthorized])

  return (
    <div className="page-enter figures-page">
      <header className="figures-header">
        <h1 className="figures-title">Figuren</h1>
        <p className="figures-subtitle">Testgalerij voor in-house figuren</p>
      </header>

      {loading && <div className="figures-loading">Figuren laden...</div>}
      {error && <div className="search-error">{error}</div>}

      {!loading && !error && (
        <div className="figures-grid">
          {figures.map((figure) => (
            <Card key={figure.id} className="figures-card">
              <h2 className="figures-card-title">{figure.title}</h2>
              <FigureView spec={figure.spec} />
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Rewrite `Figures.css` — retokenize and drop the now-unused card rule**

Replace the entire contents of `frontend/src/pages/Figures.css` with:

```css
.figures-page {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: var(--space-6) var(--space-5);
}

.figures-header {
  margin-bottom: var(--space-6);
}

.figures-title {
  font-family: var(--font-display);
  font-size: 42px;
  font-weight: 700;
  color: var(--color-heading);
  letter-spacing: -0.02em;
  line-height: 1.15;
  margin: 0 0 var(--space-2);
}

.figures-subtitle {
  color: var(--color-text-muted);
  font-size: 16px;
  margin: 0;
}

.figures-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-5);
}

/* .figures-card chrome now comes from the shared <Card> primitive (.ui-card). */
.figures-card-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  color: var(--color-heading);
  margin: 0 0 var(--space-4);
}

.figures-loading {
  padding: var(--space-6);
  color: var(--color-text-muted);
}

@media (max-width: 640px) {
  .figures-page {
    padding: var(--space-5) var(--space-4);
  }

  .figures-title {
    font-size: 32px;
  }

  .figures-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 4: Verify the full token guard is now green, plus build + lint**

Run (from `frontend/`): `npm run check-tokens`
Expected: PASS — `✓ token compliance: no raw hex outside index.css`

Run (from `frontend/`): `npm run build && npm run lint`
Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/Figures.tsx frontend/src/pages/Figures.css
git commit -m "style(figures): adopt Card primitive and design tokens on the figures gallery"
```

---

### Task 3: Final verification sweep

**Files:**
- No code changes expected. This task is a gate: confirm the full figure restyle is coherent, on-brand, and all guards are green. If a check fails, fix the specific offending file and re-run — do not introduce new scope.

**Interfaces:**
- Consumes: the outputs of Tasks 1–2.
- Produces: a clean tree where `check-tokens`, `build`, and `lint` all pass and no untokenised colors remain anywhere in the figure code.

- [ ] **Step 1: Full guard + build + lint**

Run (from `frontend/`): `npm run check-tokens && npm run build && npm run lint`
Expected: guard prints `✓ token compliance…`; build succeeds; lint prints no errors.

- [ ] **Step 2: Grep for any remaining untokenised colors in figure files**

Run (from repo root):
`rg -n '#[0-9a-fA-F]{3,8}\b|rgba\(|#fff\b|#2f5fed' frontend/src/components/FigureView.tsx frontend/src/components/FigureView.css frontend/src/pages/Figures.tsx frontend/src/pages/Figures.css`
Expected: no matches (all figure colors flow through tokens or the `CURVE_STYLES` `var(...)` palette).

- [ ] **Step 3: Brand adherence spot-check (manual read)**

Open `docs/brand-guidelines.md` "Figure / graph palette" section and confirm the implementation matches: primary curve `--sky-600`, secondary `--peach-400`, axes `--ink-950` (via `--mafs-fg`), flat/no-gradient, 2px ink outline on the figure wrapper and gallery cards. No code change if it matches.

- [ ] **Step 4: Hand off for visual confirmation**

Tell the user: run `npm run dev` in `frontend/`, log in, visit `/figures`, and confirm the three seeded graphs (Parabool, Lijn, Derdegraads) render with ink axes, sky/peach curves, and the site's card styling. Also verify a deliberately broken `fn` still shows the tokenized "Kon figuur niet tekenen" message. (Agent cannot run a persistent dev server; this check is the user's.)

- [ ] **Step 5: Commit (only if a fix was needed in Steps 1–2)**

```bash
git add <only the file(s) you fixed>
git commit -m "style(figures): final token/brand cleanup"
```

---

## Self-Review

**1. Spec coverage (against the "doesn't look nice" goal + brand figure palette):**
- Curve colors → tokens with a11y line-styles: Task 1, Step 2. ✅
- Mafs axes/grid/bg themed to ink/surface: Task 1, Step 3. ✅
- Figure wrapper on-brand (2px ink outline, radius-lg, soft shadow): Task 1, Step 3. ✅
- Tokenized error text: Task 1, Step 3. ✅
- Gallery cards match site cards (Card primitive): Task 2, Steps 2–3. ✅
- Page/header/title/subtitle/grid/loading retokenized: Task 2, Step 3. ✅
- Token guard driven from RED → GREEN: Task 1 (partial) → Task 2, Step 4 (full green). ✅
- No new motion / reduced-motion respected: no looping animation added anywhere. ✅

**2. Placeholder scan:** No TBD/TODO/"handle edge cases"/"similar to Task N". Every code step shows complete file contents. ✅

**3. Type consistency:** `CURVE_STYLES` entries typed as `{ color: string; style: 'solid' | 'dashed' | 'dotted' }` match `Plot.OfX`'s `style` union and `color: string`. `FigureView` prop contract (`{ spec: FigureSpec }`) and `Figures` prop contract (`{ onUnauthorized }`) are unchanged, so `App.tsx` and callers need no edits. `Card` usage matches its actual signature (`band`/`hard`/`className`/children). ✅

Known cross-task note (intentional, documented in Task 1 Step 4): the *full* `check-tokens` stays red until Task 2 clears the `Figures.css` offenders; Task 1's local acceptance uses a file-scoped `rg` instead.
