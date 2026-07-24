# 3D Wizard Gem (Login) — Design

**Status:** Approved (brainstorming complete)
**Date:** 2026-07-24
**Branch / worktree:** `feat/threejs-gem` (`.worktrees/feat-threejs-gem`)

## Goal

Replace the static SVG gem in the Login page's brand panel with a low-poly,
flat-shaded, ink-outlined **3D wizard gem** rendered with three.js. The gem
tilts toward the pointer and eases back to rest — alive, but not a looping
decoration. It loads lazily and degrades gracefully to the existing SVG.

## Why this is on-brand (and the constraints it must respect)

`docs/brand-guidelines.md` is deliberately restrictive about depth and motion.
The design must honor these verbatim:

- **Motion:** "Restrained and snappy… **No decorative looping animation.**"
  → pointer-driven tilt with settle-to-rest; **no continuous spin**.
- **Anti-patterns:** no gradients, no glassmorphism, no soft blurry shadows.
  → flat per-facet solid colors (unlit material); the only shadow is the
  existing CSS hard offset on the card, not on the gem itself.
- **Signature:** flat pastel fills bounded by **bold ink outlines**.
  → inverted-hull ink silhouette + crisp facet edge lines.
- **Figure/graph palette + tokens:** everything references the semantic CSS
  tokens; **no untokenised hex** (enforced by the existing `check-tokens`).

The gem is literally the logo mark (a faceted diamond) made dimensional, so 3D
here reinforces the identity rather than fighting the flat aesthetic.

## Scope

**In scope (this iteration):**
- Login brand panel only (`frontend/src/pages/Login.tsx`), replacing
  `<Logo showWordmark={false} size={96} />`.
- Lazy-loaded three.js chunk; static SVG fallback.
- Pointer parallax + settle; reduced-motion and no-WebGL fallbacks.

**Explicitly out of scope (possible later phases, not built now):**
- Home hero / header gem.
- 3D figures in the figure system.
- Completion / celebration animations.

## Rendering approach

**Raw three.js**, added as the single new runtime dependency (`three`, with
`@types/three` dev). No `@react-three/fiber` / `drei` — they add bundle and a
paradigm the codebase (Mafs, mathjs used directly) does not otherwise use, for
one ornament.

## Geometry & material

- **Shape:** `OctahedronGeometry` (two square pyramids base-to-base), scaled
  slightly taller on Y so the head-on silhouette matches the logo diamond.
- **Facets:** `MeshBasicMaterial` with **`vertexColors`** so each face is a
  single solid pastel — unlit, therefore **no gradients**. Face colors cycle
  through the logo palette: `--sky-400`, `--sky-300`, `--sky-200`, `--peach-200`.
- **Ink silhouette:** a second mesh of the same geometry rendered with
  `side: THREE.BackSide`, scaled ~1.03, solid `--ink-950` — the inverted-hull
  outline that gives the bold continuous ink border.
- **Facet edges:** `EdgesGeometry` → `LineSegments` in `--ink-950` for crisp
  internal facet definition (kept thin so it does not read as busy).
- **Color source:** all colors are read from CSS custom properties at runtime
  via `getComputedStyle(document.documentElement)` and parsed into
  `THREE.Color`, so the gem tracks the token system. No hex literals in TS.

## Motion & interaction

- **Rest pose:** a fixed, slightly-3/4 orientation (a few degrees off head-on)
  so facets are visible at rest.
- **Parallax:** pointer position within the brand panel maps to a target tilt
  of about ±15° on X/Y. Each animation frame the current rotation eases toward
  the target (exponential smoothing / lerp).
- **Settle:** on `pointerleave`, the target returns to the rest pose; the same
  easing carries it back. No perpetual motion once at rest and untouched.
- **Loop lifecycle:** `requestAnimationFrame` loop starts on mount, is cancelled
  on unmount; renderer + geometries + materials are disposed on cleanup.
- **Resize:** a `ResizeObserver` on the mount element keeps renderer size and
  camera aspect correct.

## Accessibility & fallbacks

A single decision function chooses what to render:

- **`prefers-reduced-motion: reduce`** → render the static SVG `<Logo>`; three.js
  is never imported.
- **No WebGL support** (context creation fails) → static SVG `<Logo>`.
- **Lazy chunk still loading / errors** → Suspense/error fallback is the same
  static SVG `<Logo>`, so the panel never flashes empty.
- The 3D canvas is decorative: `aria-hidden="true"`; the accessible brand name
  is already provided by adjacent text in the panel.

## Component structure

```
frontend/src/components/gem/
  Gem.tsx          # Public wrapper. Runs capability checks; renders static <Logo>
                   #   or React.lazy(GemCanvas) inside <Suspense fallback={<Logo/>}>.
                   #   Props: { size?: number }.
  GemCanvas.tsx    # default export (lazy target). Owns the three.js lifecycle:
                   #   mount/renderer/rAF/resize/pointer handlers/dispose.
                   #   Props: { size: number }.
  gemScene.ts      # Pure, framework-free builders (unit-testable):
                   #   - buildGemGeometry(): THREE.BufferGeometry
                   #   - facetColors(tokens): THREE.Color[]  (per-face vertex colors)
                   #   - buildOutlineMesh(geometry, inkColor): THREE.Mesh
                   #   - REST_ROTATION, MAX_TILT constants
  capabilities.ts  # prefersReducedMotion(): boolean; hasWebGL(): boolean
  Gem.css          # sizing/layout for the mount element
```

- `Gem.tsx` is the only symbol Login imports. It renders the **same `<Logo>`**
  component as fallback, guaranteeing visual parity when 3D is absent.
- `Login.tsx` change is a one-line swap of `<Logo …/>` → `<Gem size={96} />`
  inside `.login-brand-mark`.

## Data flow

`Login` → `<Gem size>` → (capability check) → either `<Logo>` **or**
`<Suspense fallback={<Logo>}><GemCanvas size></Suspense>`. `GemCanvas` reads CSS
tokens once on mount, builds geometry/materials via `gemScene`, and runs the rAF
loop. No network, no app state, no props beyond `size`.

## Bundle impact

three.js (~150KB gzipped) ships as its **own lazy chunk**, imported only inside
`GemCanvas`. The Login route's initial bundle is unchanged. `vite build` output
must show a separate chunk for the gem/three code (a build-time acceptance check).

## Testing & verification

The frontend has **no JS test runner** (scripts: `tsc -b`, `oxlint`,
`check-tokens`, `build`). Rather than introduce Vitest for one visual component:

- **Automated:** a small Node assertion script `frontend/scripts/check-gem.mjs`
  (mirroring the existing `scripts/check-tokens.mjs`) imports/exercises the pure
  parts of `gemScene.ts` it can validate without a DOM — e.g. geometry face
  count > 0, `facetColors` returns one color per face, outline scale constant in
  range. Wired as an npm script `check-gem`.
  - Note: `gemScene.ts` imports `three`, which is ESM and DOM-free for geometry
    construction, so it runs under Node. Any function needing `document`
    (token reading) lives in `GemCanvas`/`capabilities`, **not** in `gemScene`.
- **Typecheck:** `tsc -b` (via `npm run build`).
- **Lint:** `oxlint`.
- **Tokens:** `npm run check-tokens` (guards against untokenised hex).
- **Build/chunk:** `npm run build`; confirm a distinct three.js chunk exists.
- **Manual visual:** `npm run dev`, verify parallax/settle on Login, verify
  reduced-motion (OS setting) shows the SVG.

## Risks

- **OneDrive-synced `node_modules`** makes installs slow; not a code risk.
- **CSS-token → THREE.Color parsing:** tokens are hex in `:root`; parse defensively
  and fall back to sane defaults if a variable is missing.
- **React 19 StrictMode double-invoke** of effects: the mount effect must be
  idempotent and fully clean up (dispose renderer, cancel rAF) so a
  mount→unmount→mount cycle leaves no leaked context.
