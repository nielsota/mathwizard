# MathWizard Visual Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace MathWizard's entire visual language with the "neo-geometric" system derived from the logo — flat pastel fills, bold ink outlines, warm paper background, Space Grotesk display type, and a hard offset-shadow signature.

**Architecture:** The app is a React 19 + Vite SPA (`frontend/`) with plain co-located CSS and a single `:root` token block in `frontend/src/index.css`. The redesign is foundation-first: we rewrite the token layer once (single source of truth), add a small set of shared UI primitives + a dev-only style-guide route as the verification surface, then cascade the new tokens through every component and page. Backend is untouched (JSON-only FastAPI; no templates).

**Tech Stack:** React 19, TypeScript, Vite 8, React Router v7, plain CSS with CSS custom properties, `better-react-mathjax`, `oxlint`. No Tailwind, no test runner.

## Global Constraints

- Source of truth for all values: `docs/brand-guidelines.md`. Copy token values verbatim.
- Every color, radius, spacing, font, and shadow in component/page CSS MUST reference a token from `:root` in `frontend/src/index.css`. No raw hex/rgb/px-radius literals in component CSS (spacing px is allowed but prefer the scale). This is enforced by `frontend/scripts/check-tokens.mjs` (Task 2).
- All UI copy stays in **Dutch**.
- Display font: `Space Grotesk` (700/500). Body font: `DM Sans` (400/500/600). No other fonts.
- Signature: primary buttons and hero/primary cards use hard offset shadow `4px 4px 0 var(--ink-950)`; nothing else gets a heavy shadow.
- Keep the SPA/JSON split — no FastAPI/Jinja templates.
- `npm run build` (in `frontend/`) and `npm run lint` MUST pass at the end of every task.
- No test runner exists; verification is: build passes, lint passes, token guard passes, and manual visual check against `docs/brand/style-tile.html` and the `/style` route.
- Commit after every task with a `feat:`/`refactor:`/`style:` prefixed message.

> **Note on code completeness:** Foundation tasks (1–4) contain the full, final code — they are the contract every later task consumes, so they are exact. Component/page restyle tasks (7–15) give the exact file, a value→token mapping, representative CSS for the key elements, and precise acceptance criteria; the implementer restyles the remaining rules to match the style tile using only tokens. This is deliberate: pixel-final CSS for 8 surfaces is discovered during implementation against the running app, not pre-written.

---

## File Structure

**Create:**
- `frontend/scripts/check-tokens.mjs` — token-compliance guard (fails on raw hex in component CSS)
- `frontend/src/components/ui/Button.tsx` + `Button.css` — button primitive
- `frontend/src/components/ui/Card.tsx` + `Card.css` — card primitive
- `frontend/src/components/ui/Input.tsx` + `Input.css` — input primitive
- `frontend/src/components/ui/Badge.tsx` + `Badge.css` — badge primitive
- `frontend/src/components/ui/index.ts` — barrel export for primitives
- `frontend/src/components/Logo.tsx` — inline SVG gem + wordmark
- `frontend/src/pages/StyleGuide.tsx` + `StyleGuide.css` — dev-only `/style` route rendering every primitive
- `frontend/public/favicon.svg` — regenerated gem favicon (overwrites the purple one)

**Modify:**
- `frontend/src/index.css` — full token-layer + base-element rewrite
- `frontend/src/App.tsx` — add `/style` route
- `frontend/src/components/Header.tsx` + `Header.css` — use `Logo`, restyle
- `frontend/src/components/UserMenu.tsx` + `UserMenu.css`
- `frontend/src/components/ExerciseCard.tsx` + `ExerciseCard.css`
- `frontend/src/components/ResultCard.tsx` + `ResultCard.css`
- `frontend/src/pages/Home.tsx` + `Home.css`
- `frontend/src/pages/Login.tsx` + `Login.css` (fixes `var(--background)` bug)
- `frontend/src/pages/ExamSearch.tsx` + `ExamSearch.css`
- `frontend/src/pages/Practice.tsx` + `Practice.css`
- `frontend/package.json` — add `check-tokens` script

**Delete (final sweep):**
- `frontend/src/assets/hero.png`, `frontend/src/assets/react.svg`, `frontend/src/assets/vite.svg` (unused boilerplate)

---

### Task 1: Token foundation + global base

Rewrite `index.css` so the entire new design language exists as tokens and the base document adopts the paper background, ink text, Space Grotesk headings, and the new focus/selection styling. Removes the graph-paper motif and old palette.

**Files:**
- Modify: `frontend/src/index.css` (full replacement of `:root` + base rules)

**Interfaces:**
- Produces: the complete semantic token set consumed by every later task:
  `--color-bg`, `--color-surface`, `--color-text`, `--color-heading`, `--color-text-muted`, `--color-text-faint`, `--color-outline`, `--color-hairline`, `--color-primary`, `--color-primary-fill`, `--color-primary-hover`, `--color-accent`, `--color-accent-fill`, `--color-focus`, `--success-fill/-ink`, `--warning-fill/-ink`, `--danger-fill/-ink`, `--font-display`, `--font-body`, `--radius-sm/-md/-lg/-pill`, `--space-1..8`, `--shadow-hard`, `--shadow-soft`, `--outline-width`, `--outline-width-card`, `--header-height`, `--container-max`, `--ease`.

- [ ] **Step 1: Replace the entire contents of `frontend/src/index.css`**

```css
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&display=swap');

:root {
  /* ── Primitives: Ink ── */
  --ink-950: #111318;
  --ink-800: #282b33;
  --ink-600: #4c515c;
  --ink-400: #878c98;
  --ink-200: #cbcfd8;

  /* ── Primitives: Sky ── */
  --sky-100: #eaf3fc;
  --sky-200: #d2e5f7;
  --sky-300: #bad6f0;
  --sky-400: #9bbee6;
  --sky-500: #6f9fd8;
  --sky-600: #3f79bf;
  --sky-700: #2a5a93;

  /* ── Primitives: Peach ── */
  --peach-100: #fdf4e8;
  --peach-200: #fbe3c6;
  --peach-300: #f6ce9e;
  --peach-400: #eab170;

  /* ── Primitives: Neutral ── */
  --paper: #fcfbf7;
  --surface: #ffffff;

  /* ── Primitives: Functional ── */
  --success-fill: #d9f0e1;
  --success-ink: #1f6b45;
  --warning-fill: #fbe8c4;
  --warning-ink: #8a5a17;
  --danger-fill: #f7d6d2;
  --danger-ink: #a62f26;

  /* ── Semantic ── */
  --color-bg: var(--paper);
  --color-surface: var(--surface);
  --color-text: var(--ink-800);
  --color-heading: var(--ink-950);
  --color-text-muted: var(--ink-600);
  --color-text-faint: var(--ink-400);
  --color-outline: var(--ink-950);
  --color-hairline: var(--ink-200);
  --color-primary: var(--sky-600);
  --color-primary-fill: var(--sky-300);
  --color-primary-hover: var(--sky-700);
  --color-accent: var(--peach-300);
  --color-accent-fill: var(--peach-200);
  --color-focus: var(--sky-600);

  /* ── Typography ── */
  --font-display: 'Space Grotesk', 'DM Sans', system-ui, sans-serif;
  --font-body: 'DM Sans', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;

  /* ── Shape ── */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-pill: 999px;
  --outline-width: 1.5px;
  --outline-width-card: 2px;

  /* ── Elevation ── */
  --shadow-hard: 4px 4px 0 var(--ink-950);
  --shadow-hard-sm: 2px 2px 0 var(--ink-950);
  --shadow-soft: 0 2px 8px rgba(17, 19, 24, 0.08);

  /* ── Spacing ── */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;

  /* ── Layout & motion ── */
  --header-height: 68px;
  --container-max: 1040px;
  --ease: cubic-bezier(0.2, 0.8, 0.2, 1);
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-body);
  color: var(--color-text);
  background: var(--color-bg);
  line-height: 1.5;
  min-height: 100vh;
}

h1, h2, h3, h4 {
  font-family: var(--font-display);
  color: var(--color-heading);
  line-height: 1.14;
  letter-spacing: -0.01em;
  font-weight: 700;
}

#root {
  position: relative;
  min-height: 100vh;
}

::selection {
  background: var(--color-accent);
  color: var(--ink-950);
}

::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: var(--sky-300);
  border-radius: var(--radius-pill);
}
::-webkit-scrollbar-thumb:hover { background: var(--sky-400); }

:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

.MathJax { font-size: 1.05em !important; }

.page-enter { animation: pageIn 0.18s var(--ease) both; }

@keyframes pageIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

- [ ] **Step 2: Verify build compiles**

Run: `cd frontend && npm run build`
Expected: build succeeds (later component CSS still references old tokens like `--navy`; those resolve to nothing but do not break the build — they are replaced in Tasks 7–15).

- [ ] **Step 3: Visual smoke check**

Run: `cd frontend && npm run dev` and open the app.
Expected: background is warm paper, base text is ink, no graph-paper grid. (Components look broken/half-styled — expected until their tasks run.)

- [ ] **Step 4: Commit**

```bash
git add frontend/src/index.css
git commit -m "feat: replace design token foundation with neo-geometric system"
```

---

### Task 2: Token-compliance guard

Add a script that scans component/page CSS for raw hex colors (which should now be tokens). It fails now (old CSS is full of hex), giving the "failing test" that Tasks 7–15 drive to green. `index.css` is exempt (it defines the primitives).

**Files:**
- Create: `frontend/scripts/check-tokens.mjs`
- Modify: `frontend/package.json` (add script)

**Interfaces:**
- Produces: `npm run check-tokens` — exits non-zero and lists `file:line` offenders when raw hex appears outside `index.css`.

- [ ] **Step 1: Write the guard script**

```js
// frontend/scripts/check-tokens.mjs
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'

const ROOT = new URL('../src', import.meta.url).pathname
const HEX = /#[0-9a-fA-F]{3,8}\b/
const EXEMPT = new Set(['index.css']) // defines primitives

function walk(dir) {
  const out = []
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) out.push(...walk(p))
    else if (name.endsWith('.css')) out.push(p)
  }
  return out
}

const offenders = []
for (const file of walk(ROOT)) {
  const base = file.split('/').pop()
  if (EXEMPT.has(base)) continue
  const lines = readFileSync(file, 'utf8').split('\n')
  lines.forEach((line, i) => {
    if (HEX.test(line)) offenders.push(`${relative(ROOT, file)}:${i + 1}  ${line.trim()}`)
  })
}

if (offenders.length) {
  console.error(`✗ ${offenders.length} raw hex value(s) found outside index.css:\n`)
  console.error(offenders.join('\n'))
  process.exit(1)
}
console.log('✓ token compliance: no raw hex outside index.css')
```

- [ ] **Step 2: Add the npm script**

In `frontend/package.json` `"scripts"`, add:

```json
"check-tokens": "node scripts/check-tokens.mjs"
```

- [ ] **Step 3: Run it and confirm it FAILS**

Run: `cd frontend && npm run check-tokens`
Expected: FAIL — lists many offenders in `components/*.css` and `pages/*.css` (e.g. `#0a3a7a`, difficulty badge hexes). This is the target the restyle tasks eliminate.

- [ ] **Step 4: Commit**

```bash
git add frontend/scripts/check-tokens.mjs frontend/package.json
git commit -m "chore: add token-compliance guard for CSS"
```

---

### Task 3: Logo component + favicon

Recreate the gem mark as crisp inline SVG (vector, token-outlined) plus an optional wordmark, and regenerate the favicon. Replaces the old inline zigzag mark and the leftover purple Vite favicon.

**Files:**
- Create: `frontend/src/components/Logo.tsx`
- Modify: `frontend/public/favicon.svg` (overwrite)

**Interfaces:**
- Produces: `Logo` React component — `interface LogoProps { showWordmark?: boolean; size?: number }`. Default `size=32`, `showWordmark=true`. Renders `<span class="mw-logo">` with SVG gem + optional "MathWizard" wordmark span (class `mw-logo-word`).

- [ ] **Step 1: Create `frontend/src/components/Logo.tsx`**

```tsx
interface LogoProps {
  showWordmark?: boolean
  size?: number
}

export default function Logo({ showWordmark = true, size = 32 }: LogoProps) {
  return (
    <span className="mw-logo">
      <svg
        className="mw-logo-mark"
        width={size}
        height={size}
        viewBox="0 0 100 100"
        role="img"
        aria-label="MathWizard"
      >
        <g stroke="var(--color-outline)" strokeWidth="5" strokeLinejoin="round" fill="none">
          <path d="M50 6 L92 50 L50 94 L8 50 Z" fill="var(--sky-400)" />
          <path d="M50 6 L92 50 L8 50 Z" fill="var(--sky-300)" />
          <path d="M20 50 L80 50 L68 62 L32 62 Z" fill="var(--peach-200)" />
        </g>
      </svg>
      {showWordmark && <span className="mw-logo-word">MathWizard</span>}
    </span>
  )
}
```

- [ ] **Step 2: Overwrite `frontend/public/favicon.svg`** (self-contained, no CSS vars — favicons can't read them)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="18" fill="#fcfbf7"/>
  <g stroke="#111318" stroke-width="5" stroke-linejoin="round" fill="none">
    <path d="M50 10 L88 50 L50 90 L12 50 Z" fill="#9bbee6"/>
    <path d="M50 10 L88 50 L12 50 Z" fill="#bad6f0"/>
    <path d="M22 50 L78 50 L67 61 L33 61 Z" fill="#fbe3c6"/>
  </g>
</svg>
```

- [ ] **Step 3: Verify build**

Run: `cd frontend && npm run build`
Expected: PASS (component is unused until Task 7, but must compile).

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/Logo.tsx frontend/public/favicon.svg
git commit -m "feat: add Logo component and regenerate favicon from mark"
```

---

### Task 4: Shared UI primitive kit + style-guide route

Create the four reusable primitives (`Button`, `Card`, `Input`, `Badge`) and a dev-only `/style` route that renders them. The style route is the manual verification surface for the whole system and doubles as living documentation.

**Files:**
- Create: `frontend/src/components/ui/Button.tsx` + `Button.css`
- Create: `frontend/src/components/ui/Card.tsx` + `Card.css`
- Create: `frontend/src/components/ui/Input.tsx` + `Input.css`
- Create: `frontend/src/components/ui/Badge.tsx` + `Badge.css`
- Create: `frontend/src/components/ui/index.ts`
- Create: `frontend/src/pages/StyleGuide.tsx` + `StyleGuide.css`
- Modify: `frontend/src/App.tsx` (add `/style` route)

**Interfaces:**
- Produces:
  - `Button` — `interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> { variant?: 'primary' | 'secondary' | 'ghost'; fullWidth?: boolean }`
  - `Card` — `interface CardProps extends React.HTMLAttributes<HTMLDivElement> { band?: boolean; hard?: boolean }` (`band` = peach top-band, `hard` = hard offset shadow)
  - `Input` — `interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> { label?: string }`
  - `Badge` — `interface BadgeProps { tone?: 'easy' | 'med' | 'hard' | 'neutral'; children: React.ReactNode }`
  - barrel: `import { Button, Card, Input, Badge } from '../components/ui'`

- [ ] **Step 1: `Button.tsx`**

```tsx
import './Button.css'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
  fullWidth?: boolean
}

export default function Button({
  variant = 'primary',
  fullWidth = false,
  className = '',
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`ui-btn ui-btn--${variant} ${fullWidth ? 'ui-btn--full' : ''} ${className}`}
      {...rest}
    />
  )
}
```

- [ ] **Step 2: `Button.css`**

```css
.ui-btn {
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 0.95rem;
  padding: 11px 20px;
  border-radius: var(--radius-md);
  border: var(--outline-width) solid var(--color-outline);
  cursor: pointer;
  transition: transform 0.12s var(--ease), box-shadow 0.12s var(--ease), background 0.12s var(--ease);
}
.ui-btn--full { width: 100%; }
.ui-btn--primary { background: var(--color-primary-fill); color: var(--ink-950); box-shadow: var(--shadow-hard); }
.ui-btn--primary:hover { background: var(--sky-400); }
.ui-btn--primary:active { transform: translate(2px, 2px); box-shadow: var(--shadow-hard-sm); }
.ui-btn--secondary { background: var(--color-surface); color: var(--ink-950); }
.ui-btn--secondary:hover { background: var(--sky-100); }
.ui-btn--ghost { background: transparent; border-color: transparent; color: var(--color-text); }
.ui-btn--ghost:hover { background: var(--sky-100); }
.ui-btn:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; }
```

- [ ] **Step 3: `Card.tsx`**

```tsx
import './Card.css'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  band?: boolean
  hard?: boolean
}

export default function Card({ band = false, hard = false, className = '', children, ...rest }: CardProps) {
  return (
    <div className={`ui-card ${hard ? 'ui-card--hard' : ''} ${className}`} {...rest}>
      {band && <div className="ui-card__band" />}
      {children}
    </div>
  )
}
```

- [ ] **Step 4: `Card.css`**

```css
.ui-card {
  background: var(--color-surface);
  border: var(--outline-width-card) solid var(--color-outline);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  transition: transform 0.12s var(--ease), box-shadow 0.12s var(--ease);
}
.ui-card--hard { box-shadow: var(--shadow-hard); }
.ui-card__band {
  height: 8px;
  margin: calc(-1 * var(--space-5)) calc(-1 * var(--space-5)) var(--space-4);
  background: var(--color-accent);
  border-bottom: var(--outline-width-card) solid var(--color-outline);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}
```

- [ ] **Step 5: `Input.tsx`**

```tsx
import './Input.css'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

export default function Input({ label, className = '', id, ...rest }: InputProps) {
  return (
    <div className="ui-field">
      {label && <label className="ui-field__label" htmlFor={id}>{label}</label>}
      <input id={id} className={`ui-input ${className}`} {...rest} />
    </div>
  )
}
```

- [ ] **Step 6: `Input.css`**

```css
.ui-field { display: flex; flex-direction: column; gap: var(--space-2); }
.ui-field__label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-faint);
}
.ui-input {
  width: 100%;
  padding: 11px 14px;
  font-family: var(--font-body);
  font-size: 0.95rem;
  background: var(--color-surface);
  color: var(--color-text);
  border: var(--outline-width) solid var(--color-outline);
  border-radius: var(--radius-md);
}
.ui-input:focus {
  outline: none;
  border-color: var(--color-focus);
  box-shadow: 0 0 0 3px var(--sky-200);
}
.ui-input::placeholder { color: var(--color-text-faint); }
```

- [ ] **Step 7: `Badge.tsx`**

```tsx
import './Badge.css'

interface BadgeProps {
  tone?: 'easy' | 'med' | 'hard' | 'neutral'
  children: React.ReactNode
}

export default function Badge({ tone = 'neutral', children }: BadgeProps) {
  return <span className={`ui-badge ui-badge--${tone}`}>{children}</span>
}
```

- [ ] **Step 8: `Badge.css`**

```css
.ui-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.72rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  border: 1px solid;
}
.ui-badge--easy { background: var(--success-fill); color: var(--success-ink); border-color: var(--success-ink); }
.ui-badge--med  { background: var(--warning-fill); color: var(--warning-ink); border-color: var(--warning-ink); }
.ui-badge--hard { background: var(--danger-fill);  color: var(--danger-ink);  border-color: var(--danger-ink); }
.ui-badge--neutral { background: var(--sky-100); color: var(--sky-700); border-color: var(--sky-300); }
```

- [ ] **Step 9: `index.ts` barrel**

```ts
export { default as Button } from './Button'
export { default as Card } from './Card'
export { default as Input } from './Input'
export { default as Badge } from './Badge'
```

- [ ] **Step 10: `StyleGuide.tsx`** (renders everything for visual verification)

```tsx
import { Button, Card, Input, Badge } from '../components/ui'
import Logo from '../components/Logo'
import './StyleGuide.css'

export default function StyleGuide() {
  return (
    <div className="styleguide page-enter">
      <header className="styleguide__hero">
        <Logo size={72} />
      </header>

      <section>
        <h2>Buttons</h2>
        <div className="styleguide__row">
          <Button variant="primary">Start oefening</Button>
          <Button variant="secondary">Bekijk uitleg</Button>
          <Button variant="ghost">Later</Button>
          <Button variant="primary" disabled>Uitgeschakeld</Button>
        </div>
      </section>

      <section>
        <h2>Badges</h2>
        <div className="styleguide__row">
          <Badge tone="easy">Makkelijk</Badge>
          <Badge tone="med">Gemiddeld</Badge>
          <Badge tone="hard">Moeilijk</Badge>
          <Badge tone="neutral">Nieuw</Badge>
        </div>
      </section>

      <section>
        <h2>Cards & inputs</h2>
        <div className="styleguide__grid">
          <Card band hard>
            <h3>Afgeleiden</h3>
            <p>Signature card: ink outline, peach band, hard shadow.</p>
            <Button variant="primary">Start</Button>
          </Card>
          <Card>
            <Input label="Onderwerp" placeholder="bv. afgeleiden…" />
            <div style={{ height: 'var(--space-4)' }} />
            <Button variant="primary" fullWidth>Zoeken</Button>
          </Card>
        </div>
      </section>
    </div>
  )
}
```

- [ ] **Step 11: `StyleGuide.css`**

```css
.styleguide { max-width: var(--container-max); margin: 0 auto; padding: var(--space-7) var(--space-5); }
.styleguide__hero { margin-bottom: var(--space-6); }
.styleguide section { margin: var(--space-6) 0; }
.styleguide h2 { font-size: 1.375rem; margin-bottom: var(--space-4); }
.styleguide__row { display: flex; flex-wrap: wrap; gap: var(--space-3); align-items: center; }
.styleguide__grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
@media (max-width: 720px) { .styleguide__grid { grid-template-columns: 1fr; } }
```

- [ ] **Step 12: Register the `/style` route in `App.tsx`**

Add the import near the other page imports:

```tsx
import StyleGuide from './pages/StyleGuide'
```

Add this route inside `<Routes>` (public, no auth gate — dev aid):

```tsx
<Route path="/style" element={<StyleGuide />} />
```

- [ ] **Step 13: Verify build + lint + visual**

Run: `cd frontend && npm run build && npm run lint`
Expected: PASS.
Then `npm run dev`, open `/style`. Expected: primitives match `docs/brand/style-tile.html` (ink outlines, hard shadow on primary button + banded card, sky focus ring on input).

- [ ] **Step 14: Verify token guard on the new files**

Run: `cd frontend && npm run check-tokens`
Expected: the new `ui/*.css` and `StyleGuide.css` add **no** new offenders (still fails only on legacy `components/*` and `pages/*`).

- [ ] **Step 15: Commit**

```bash
git add frontend/src/components/ui frontend/src/pages/StyleGuide.tsx frontend/src/pages/StyleGuide.css frontend/src/App.tsx
git commit -m "feat: add neo-geometric UI primitive kit and /style route"
```

---

### Task 7: Restyle Header + integrate Logo

> (Tasks are numbered by dependency; 5–6 intentionally folded into Task 4's kit.)

**Files:**
- Modify: `frontend/src/components/Header.tsx` (swap inline mark for `Logo`)
- Modify: `frontend/src/components/Header.css` (tokenise; remove glass/navy gradient)

**Interfaces:**
- Consumes: `Logo` from Task 3 (`<Logo size={30} />`).

- [ ] **Step 1: Swap the brand mark in `Header.tsx`**

Add import: `import Logo from './Logo'`. Replace the `<div className="mw-logo-mark">…</div>` + `<span className="mw-brand-name">MathWizard</span>` block (lines ~37–43) with:

```tsx
<Logo size={30} />
```

- [ ] **Step 2: Retokenise `Header.css`**

Value→token mapping to apply across the file:
- navy gradient / `#0a3a7a` / `--navy*` backgrounds → `var(--color-surface)` header with `border-bottom: var(--outline-width-card) solid var(--color-outline)` (flat, outlined bar — no glass/blur; remove `backdrop-filter`)
- brand text color → `var(--color-heading)`, font `var(--font-display)`, weight 700
- nav link color → `var(--color-text)`; hover/active → `var(--color-primary)` with `background: var(--sky-100)`
- dropdown menu → `var(--color-surface)`, `border: var(--outline-width) solid var(--color-outline)`, `border-radius: var(--radius-md)`, `box-shadow: var(--shadow-soft)`
- header height → `var(--header-height)`; radii → radius tokens

Representative header shell:

```css
.mw-header {
  position: sticky;
  top: 0;
  z-index: 50;
  height: var(--header-height);
  background: var(--color-surface);
  border-bottom: var(--outline-width-card) solid var(--color-outline);
}
.mw-header-inner {
  max-width: var(--container-max);
  height: 100%;
  margin: 0 auto;
  padding: 0 var(--space-5);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.mw-logo { display: inline-flex; align-items: center; gap: var(--space-2); }
.mw-logo-word { font-family: var(--font-display); font-weight: 700; font-size: 1.1rem; color: var(--color-heading); }
```

- [ ] **Step 3: Verify**

Run: `cd frontend && npm run build && npm run check-tokens`
Expected: build PASS; `check-tokens` no longer lists `Header.css`.

- [ ] **Step 4: Visual check** — `/` shows a flat white outlined header with the gem logo. Commit.

```bash
git add frontend/src/components/Header.tsx frontend/src/components/Header.css
git commit -m "style: restyle header and integrate gem logo"
```

---

### Task 8: Restyle UserMenu

**Files:**
- Modify: `frontend/src/components/UserMenu.css` (tokenise); `UserMenu.tsx` only if class hooks are needed.

**Interfaces:**
- Consumes: token layer. May use `Badge` for the role pill (`import { Badge } from './ui'`).

- [ ] **Step 1: Retokenise `UserMenu.css`**
Mapping:
- avatar / navy gradient → `var(--color-primary-fill)` fill + `var(--color-outline)` border, ink initials
- role pill → replace bespoke colors with `Badge tone="neutral"` (or `--sky-100/--sky-700/--sky-300`)
- panel → `var(--color-surface)`, `var(--outline-width) solid var(--color-outline)`, `var(--radius-md)`, `var(--shadow-soft)`
- logout hover danger (`#b4232a`, `#f0c0c2`, `#fdf3f3`) → `var(--danger-ink)` text on `var(--danger-fill)` hover
- roster card borders → `var(--color-hairline)`

- [ ] **Step 2: Verify** `npm run build && npm run check-tokens` (UserMenu.css clears). Visual: open the menu.
- [ ] **Step 3: Commit** `git commit -m "style: restyle user menu with tokens"`

---

### Task 9: Restyle ExerciseCard

**Files:**
- Modify: `frontend/src/components/ExerciseCard.tsx` (use `Card`/`Badge` where clean), `ExerciseCard.css`.

**Interfaces:**
- Consumes: `Card`, `Badge` from `./ui`. Difficulty → `Badge tone`: makkelijk=`easy`, gemiddeld=`med`, moeilijk=`hard`.

- [ ] **Step 1:** Replace difficulty badge markup with `<Badge tone={…}>`; remove the corresponding hex-defined badge classes from `ExerciseCard.css`. Map the difficulty label to tone in the component.
- [ ] **Step 2:** Retokenise remaining `ExerciseCard.css`: card surface → outline + `--radius-lg`; marks/meta text → `--color-text-muted`; expand affordance hover → `--sky-100`.
- [ ] **Step 3: Verify** `npm run build && npm run check-tokens` (ExerciseCard.css clears). Visual on `/practice/:topic`.
- [ ] **Step 4: Commit** `git commit -m "style: restyle exercise card with primitives and tokens"`

---

### Task 10: Restyle ResultCard

**Files:**
- Modify: `frontend/src/components/ResultCard.tsx`, `ResultCard.css`.

- [ ] **Step 1:** Wrap the result body in `Card` (outline + radius-lg). Retokenise: figure image frame border → `var(--color-outline)`/`var(--radius-md)`; metadata text → `--color-text-muted`; any status hex → functional tokens.
- [ ] **Step 2: Verify** `npm run build && npm run check-tokens` (ResultCard.css clears). Visual on `/search` after a query.
- [ ] **Step 3: Commit** `git commit -m "style: restyle result card with tokens"`

---

### Task 11: Restyle Home (hub)

**Files:**
- Modify: `frontend/src/pages/Home.tsx`, `Home.css`.

**Interfaces:**
- Consumes: `Card`, `Button` from `../components/ui`.

- [ ] **Step 1:** Convert hero + topic grid to the new system: topic tiles become `Card` (outline, radius-lg, hover lift); primary CTA becomes `<Button variant="primary">`. Remove the inline `animationDelay` stagger only if it references old motion; otherwise keep but retokenise duration to `--ease`.
- [ ] **Step 2:** Retokenise `Home.css`: navy hero gradient/`#0a3a7a` → paper background with an outlined hero `Card` (optionally `band`); headings → `--font-display`; text → semantic tokens; grid gaps → space scale.
- [ ] **Step 3: Verify** `npm run build && npm run check-tokens` (Home.css clears). Visual on `/`.
- [ ] **Step 4: Commit** `git commit -m "style: redesign home hub with neo-geometric cards"`

---

### Task 12: Restyle Login (and fix `--background` bug)

**Files:**
- Modify: `frontend/src/pages/Login.tsx`, `Login.css`.

**Interfaces:**
- Consumes: `Card`, `Button`, `Input` from `../components/ui`.

- [ ] **Step 1: Fix the token bug** — in `Login.css`, replace the invalid `var(--background)` reference with `var(--color-bg)`.
- [ ] **Step 2:** Rebuild the login layout: form fields → `Input`; submit → `<Button variant="primary" fullWidth>`; the form container → outlined `Card` (`hard` shadow for the signature). Replace the navy "proof panel" gradient and `∫` motif with a paper panel + the `Logo` mark. Retokenise all colors.
- [ ] **Step 3: Verify** `npm run build && npm run check-tokens` (Login.css clears). Visual on `/login` (logged out).
- [ ] **Step 4: Commit** `git commit -m "style: redesign login and fix --background token bug"`

---

### Task 13: Restyle ExamSearch

**Files:**
- Modify: `frontend/src/pages/ExamSearch.tsx`, `ExamSearch.css`.

**Interfaces:**
- Consumes: `Button`, `Input` from `../components/ui`. The existing `.btn--primary/secondary/ghost` classes are replaced by the `Button` primitive.

- [ ] **Step 1:** Replace `.btn--*` buttons with `<Button variant="…">`; replace the search field with `Input`. Remove the now-dead `.btn--*` rules and the error-border `#fecaca` (→ `var(--danger-ink)`) from `ExamSearch.css`.
- [ ] **Step 2:** Retokenise remaining layout/results CSS.
- [ ] **Step 3: Verify** `npm run build && npm run check-tokens` (ExamSearch.css clears). Visual on `/search`.
- [ ] **Step 4: Commit** `git commit -m "style: restyle exam search with primitives"`

---

### Task 14: Restyle Practice

**Files:**
- Modify: `frontend/src/pages/Practice.tsx`, `Practice.css`.

- [ ] **Step 1:** Retokenise topic header (navy/`#0a3a7a` → paper + `--font-display` heading + optional peach accent underline) and the exercise list container. `ExerciseCard` already restyled in Task 9.
- [ ] **Step 2: Verify** `npm run build && npm run check-tokens` (Practice.css clears). Visual on `/practice/:topic`.
- [ ] **Step 3: Commit** `git commit -m "style: restyle practice page with tokens"`

---

### Task 15: Align figure-system palette

Ensure planned/existing figure rendering (`docs/superpowers/plans/2026-07-24-figure-system.md`, spec `2026-07-24-figure-system-design.md`) uses the new house tokens for graph colors.

**Files:**
- Modify: figure color config/defaults where they exist; if the figure system is not yet implemented, add a short "House palette" note to the figure spec mapping graph colors to `--sky-600` (curves), `--peach-400` (secondary), `--ink-950` (axes), `--ink-200` (gridlines).

- [ ] **Step 1:** If `FigureView`/graph color defaults exist in code, point them at the token values (via CSS vars or by importing the hex constants centrally). If not implemented, update the spec's color section to the new palette so it lands correct.
- [ ] **Step 2: Verify** `npm run build` (if code changed) or doc review. Commit.

```bash
git commit -m "style: align figure-system palette with redesign tokens"
```

---

### Task 16: Final sweep — guard green, cleanup, build/lint

**Files:**
- Delete: `frontend/src/assets/hero.png`, `frontend/src/assets/react.svg`, `frontend/src/assets/vite.svg`
- Modify: any remaining CSS flagged by the guard.

- [ ] **Step 1: Run the guard — must now PASS**

Run: `cd frontend && npm run check-tokens`
Expected: `✓ token compliance: no raw hex outside index.css`. If any offenders remain, tokenise them.

- [ ] **Step 2: Remove unused boilerplate assets**

Run: `cd frontend && rm src/assets/hero.png src/assets/react.svg src/assets/vite.svg`
Then grep to confirm none are imported: `rg "hero.png|react.svg|vite.svg" frontend/src` → expect no results.

- [ ] **Step 3: Full build + lint**

Run: `cd frontend && npm run build && npm run lint`
Expected: both PASS.

- [ ] **Step 4: Full visual regression pass**

`npm run dev`, walk every route: `/login`, `/`, `/search`, `/practice/:topic`, `/style`. Confirm consistency with `docs/brand/style-tile.html`: ink outlines, hard shadow only on primary CTAs/hero cards, paper background, Space Grotesk headings, no purple, no graph paper.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: token guard green, remove unused assets, final redesign sweep"
```

---

## Self-Review

**Spec coverage (against `docs/brand-guidelines.md`):**
- Palette → Task 1 (tokens) + enforced everywhere by Task 2 guard. ✓
- Typography (Space Grotesk + DM Sans) → Task 1 `@import` + `--font-display`. ✓
- Bold ink outline + hard offset shadow signature → Tasks 1 (tokens), 4 (primitives), applied 7–14. ✓
- Logo integration + favicon → Tasks 3, 7. ✓
- Retire notebook/graph-paper/Instrument Serif → Task 1 (removed `body::before`, swapped fonts). ✓
- Retire purple favicon → Task 3. ✓
- Functional badge colors → Task 1 tokens + `Badge` primitive (Task 4), applied 9. ✓
- `--background` bug → Task 12 Step 1. ✓
- Dutch copy preserved → all restyle tasks touch CSS/markup structure, not copy. ✓
- Figure palette → Task 15. ✓

**Placeholder scan:** Foundation tasks (1–4) contain complete final code. Restyle tasks (7–15) intentionally provide value→token mappings + representative CSS + exact acceptance checks rather than full per-file CSS — documented in the "code completeness" note; each still has a concrete verification (`check-tokens` clears that file + build passes).

**Type consistency:** Primitive prop names (`variant`, `fullWidth`, `band`, `hard`, `tone`, `label`) are defined in Task 4 and referenced consistently in Tasks 7–14. Barrel import path `../components/ui` is uniform.

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-07-24-visual-redesign.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session with checkpoints for review.

**Which approach?**
