# 3D Wizard Gem (Login) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the static SVG gem in the Login brand panel with a lazy-loaded, flat-shaded, ink-outlined 3D wizard gem (three.js) that tilts toward the pointer and settles to rest, degrading gracefully to the existing SVG.

**Architecture:** One new self-contained folder `frontend/src/components/gem/`. A public `Gem` wrapper decides — via capability checks — between the static `<Logo>` SVG and a `React.lazy` `GemCanvas` (three.js) rendered inside `<Suspense fallback={<Logo/>}>`. Pure geometry/material/color builders live in `gemScene.ts` (DOM-free, Node-checkable); all imperative three.js lifecycle lives in `GemCanvas.tsx`. `Login.tsx` changes by one line.

**Tech Stack:** React 19, TypeScript (strict), Vite 8, three.js (new), oxlint, existing `check-tokens` Node script.

## Global Constraints

- Design spec: `docs/superpowers/specs/2026-07-24-threejs-gem-login-design.md` (authoritative).
- Brand (`docs/brand-guidelines.md`), copied verbatim where it binds:
  - Motion: "Restrained and snappy… **No decorative looping animation.**" → no continuous spin; pointer tilt + settle only.
  - Anti-patterns: **no gradients**, no glassmorphism, no soft blurry shadows → unlit `MeshBasicMaterial`, solid per-facet color.
  - Signature: flat pastel fills + **bold ink outline** → inverted-hull ink silhouette + facet edge lines.
  - "Untokenised hex values in component CSS" are forbidden → CSS references semantic tokens only; TS reads colors from CSS custom properties, no hex literals.
- UI copy stays **Dutch** (this feature adds no user-visible copy).
- No new test framework. Verification = `tsc` + `oxlint` + `check-tokens` + `check-gem` + `vite build` + manual visual.
- Node ≥ 22.6 is available (v25.x); the `check-gem` script runs TS via `node --experimental-strip-types`.
- Work happens in the existing worktree `.worktrees/feat-threejs-gem` on branch `feat/threejs-gem`. All commands below run from `.worktrees/feat-threejs-gem/frontend` unless stated.

## File Structure

- `frontend/package.json` — add `three` dep, `@types/three` devDep, `check-gem` script (modify).
- `frontend/src/components/gem/capabilities.ts` — `prefersReducedMotion()`, `hasWebGL()` (create).
- `frontend/src/components/gem/gemScene.ts` — pure builders + motion constants (create).
- `frontend/src/components/gem/GemCanvas.tsx` — three.js lifecycle component, lazy target (create).
- `frontend/src/components/gem/Gem.tsx` — public wrapper: capability gate + lazy + Suspense (create).
- `frontend/src/components/gem/Gem.css` — mount element sizing (create).
- `frontend/scripts/check-gem.ts` — Node assertion script for `gemScene` pure functions (create).
- `frontend/src/pages/Login.tsx` — swap `<Logo>` → `<Gem>` in `.login-brand-mark` (modify).

---

### Task 1: Add three.js dependency

**Files:**
- Modify: `frontend/package.json` (+ `package-lock.json` via npm)

**Interfaces:**
- Consumes: nothing.
- Produces: `three` importable in later tasks; `@types/three` for TS.

- [ ] **Step 1: Install three + types**

Run (from `frontend/`):

```bash
npm install three
npm install -D @types/three
```

- [ ] **Step 2: Verify the project still typechecks and builds**

Run: `npm run build`
Expected: PASS (tsc + vite build succeed; three is present but unused so far — that is fine).

- [ ] **Step 3: Commit**

```bash
git add package.json package-lock.json
git commit -m "build: add three.js dependency for 3D gem"
```

---

### Task 2: Capability detection (reduced-motion + WebGL)

**Files:**
- Create: `frontend/src/components/gem/capabilities.ts`

**Interfaces:**
- Consumes: browser `window`, `document`.
- Produces:
  - `prefersReducedMotion(): boolean`
  - `hasWebGL(): boolean`
  - `canRender3D(): boolean` (`hasWebGL() && !prefersReducedMotion()`)

- [ ] **Step 1: Write the module**

Create `frontend/src/components/gem/capabilities.ts`:

```ts
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return false
  }
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export function hasWebGL(): boolean {
  if (typeof document === 'undefined') return false
  try {
    const canvas = document.createElement('canvas')
    const gl = canvas.getContext('webgl2') ?? canvas.getContext('webgl')
    return gl !== null
  } catch {
    return false
  }
}

export function canRender3D(): boolean {
  return hasWebGL() && !prefersReducedMotion()
}
```

- [ ] **Step 2: Verify typecheck + lint**

Run: `npm run build && npm run lint`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add src/components/gem/capabilities.ts
git commit -m "feat(gem): add WebGL and reduced-motion capability checks"
```

---

### Task 3: Pure gem scene builders + Node assertion script

**Files:**
- Create: `frontend/src/components/gem/gemScene.ts`
- Create: `frontend/scripts/check-gem.ts`
- Modify: `frontend/package.json` (add `check-gem` script)

**Interfaces:**
- Consumes: `three`.
- Produces (all DOM-free, safe to import under Node):
  - `REST_ROTATION: { x: number; y: number }`
  - `MAX_TILT: number` (radians)
  - `OUTLINE_SCALE: number`
  - `GemPalette` = `{ facets: THREE.Color[]; ink: THREE.Color }`
  - `DEFAULT_PALETTE: GemPalette` (hardcoded fallback colors; the only place raw color values live, used when CSS vars are unavailable e.g. under Node)
  - `buildGemGeometry(): THREE.BufferGeometry`
  - `applyFacetColors(geometry: THREE.BufferGeometry, facets: THREE.Color[]): void`
  - `buildGemMesh(palette: GemPalette): THREE.Mesh`
  - `buildOutlineMesh(geometry: THREE.BufferGeometry, ink: THREE.Color): THREE.Mesh`
  - `buildEdgeLines(geometry: THREE.BufferGeometry, ink: THREE.Color): THREE.LineSegments`

- [ ] **Step 1: Write the failing check script**

Create `frontend/scripts/check-gem.ts`:

```ts
import {
  DEFAULT_PALETTE,
  OUTLINE_SCALE,
  applyFacetColors,
  buildEdgeLines,
  buildGemGeometry,
  buildGemMesh,
  buildOutlineMesh,
} from '../src/components/gem/gemScene.ts'

let failures = 0
function check(label: string, cond: boolean): void {
  if (!cond) {
    failures += 1
    console.error(`FAIL: ${label}`)
  } else {
    console.log(`ok: ${label}`)
  }
}

const geometry = buildGemGeometry()
const position = geometry.getAttribute('position')
check('geometry has vertices', position.count > 0)
check('geometry vertices form whole triangles', position.count % 3 === 0)

applyFacetColors(geometry, DEFAULT_PALETTE.facets)
const color = geometry.getAttribute('color')
check('facet colors applied per vertex', color !== undefined && color.count === position.count)

const mesh = buildGemMesh(DEFAULT_PALETTE)
check('gem mesh built', mesh.geometry !== undefined && mesh.material !== undefined)

const outline = buildOutlineMesh(geometry, DEFAULT_PALETTE.ink)
check('outline scaled outward', outline.scale.x === OUTLINE_SCALE && OUTLINE_SCALE > 1)

const edges = buildEdgeLines(geometry, DEFAULT_PALETTE.ink)
check('edge lines built', edges.geometry !== undefined)

if (failures > 0) {
  console.error(`\ncheck-gem: ${failures} failure(s)`)
  process.exit(1)
}
console.log('\ncheck-gem: all checks passed')
```

- [ ] **Step 2: Add the npm script**

In `frontend/package.json` `"scripts"`, add:

```json
"check-gem": "node --experimental-strip-types scripts/check-gem.ts"
```

- [ ] **Step 3: Run it to confirm it fails**

Run: `npm run check-gem`
Expected: FAIL — cannot resolve `../src/components/gem/gemScene.ts` (module does not exist yet).

- [ ] **Step 4: Implement `gemScene.ts`**

Create `frontend/src/components/gem/gemScene.ts`:

```ts
import {
  BackSide,
  BufferGeometry,
  Color,
  EdgesGeometry,
  Float32BufferAttribute,
  LineBasicMaterial,
  LineSegments,
  Mesh,
  MeshBasicMaterial,
  OctahedronGeometry,
} from 'three'

export const REST_ROTATION = { x: -0.18, y: 0.5 }
export const MAX_TILT = 0.26
export const OUTLINE_SCALE = 1.03

export interface GemPalette {
  facets: Color[]
  ink: Color
}

// Fallback values (used under Node / when CSS vars are missing). These mirror
// the logo palette tokens; the running app overrides them from CSS custom
// properties, so these are the ONLY raw color values in TS.
export const DEFAULT_PALETTE: GemPalette = {
  facets: [
    new Color('#9bbee6'), // --sky-400
    new Color('#bad6f0'), // --sky-300
    new Color('#d2e5f7'), // --sky-200
    new Color('#fbe3c6'), // --peach-200
  ],
  ink: new Color('#111318'), // --ink-950
}

export function buildGemGeometry(): BufferGeometry {
  const geometry = new OctahedronGeometry(1, 0)
  geometry.scale(1, 1.35, 1)
  return geometry
}

export function applyFacetColors(geometry: BufferGeometry, facets: Color[]): void {
  const position = geometry.getAttribute('position')
  const vertexCount = position.count
  const colors = new Float32Array(vertexCount * 3)
  const triangleCount = vertexCount / 3
  for (let t = 0; t < triangleCount; t += 1) {
    const facet = facets[t % facets.length]
    for (let v = 0; v < 3; v += 1) {
      const offset = (t * 3 + v) * 3
      colors[offset] = facet.r
      colors[offset + 1] = facet.g
      colors[offset + 2] = facet.b
    }
  }
  geometry.setAttribute('color', new Float32BufferAttribute(colors, 3))
}

export function buildGemMesh(palette: GemPalette): Mesh {
  const geometry = buildGemGeometry()
  applyFacetColors(geometry, palette.facets)
  const material = new MeshBasicMaterial({ vertexColors: true })
  return new Mesh(geometry, material)
}

export function buildOutlineMesh(geometry: BufferGeometry, ink: Color): Mesh {
  const material = new MeshBasicMaterial({ color: ink, side: BackSide })
  const mesh = new Mesh(geometry, material)
  mesh.scale.setScalar(OUTLINE_SCALE)
  return mesh
}

export function buildEdgeLines(geometry: BufferGeometry, ink: Color): LineSegments {
  const edges = new EdgesGeometry(geometry, 1)
  return new LineSegments(edges, new LineBasicMaterial({ color: ink }))
}
```

- [ ] **Step 5: Run the check script to confirm it passes**

Run: `npm run check-gem`
Expected: PASS — "check-gem: all checks passed".

- [ ] **Step 6: Verify typecheck + lint + tokens**

Run: `npm run build && npm run lint && npm run check-tokens`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/components/gem/gemScene.ts scripts/check-gem.ts package.json
git commit -m "feat(gem): add pure gem scene builders with node assertion check"
```

---

### Task 4: GemCanvas — three.js lifecycle component

**Files:**
- Create: `frontend/src/components/gem/GemCanvas.tsx`

**Interfaces:**
- Consumes: `three`; `gemScene.ts` (Task 3).
- Produces: `default export function GemCanvas(props: { size: number }): JSX.Element` — the lazy-loaded three.js renderer. Reads CSS tokens for colors; runs pointer-parallax rAF loop; disposes on unmount.

- [ ] **Step 1: Implement the component**

Create `frontend/src/components/gem/GemCanvas.tsx`:

```tsx
import { useEffect, useRef } from 'react'
import {
  Color,
  Group,
  OrthographicCamera,
  Scene,
  WebGLRenderer,
} from 'three'
import {
  DEFAULT_PALETTE,
  MAX_TILT,
  REST_ROTATION,
  buildEdgeLines,
  buildGemMesh,
  buildOutlineMesh,
  type GemPalette,
} from './gemScene'

function readColor(styles: CSSStyleDeclaration, varName: string, fallback: Color): Color {
  const raw = styles.getPropertyValue(varName).trim()
  if (raw === '') return fallback
  try {
    return new Color(raw)
  } catch {
    return fallback
  }
}

function readPalette(): GemPalette {
  if (typeof document === 'undefined') return DEFAULT_PALETTE
  const styles = getComputedStyle(document.documentElement)
  return {
    facets: [
      readColor(styles, '--sky-400', DEFAULT_PALETTE.facets[0]),
      readColor(styles, '--sky-300', DEFAULT_PALETTE.facets[1]),
      readColor(styles, '--sky-200', DEFAULT_PALETTE.facets[2]),
      readColor(styles, '--peach-200', DEFAULT_PALETTE.facets[3]),
    ],
    ink: readColor(styles, '--ink-950', DEFAULT_PALETTE.ink),
  }
}

interface GemCanvasProps {
  size: number
}

export default function GemCanvas({ size }: GemCanvasProps) {
  const mountRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const mount = mountRef.current
    if (mount === null) return

    const palette = readPalette()
    const scene = new Scene()

    const frustum = 1.6
    const camera = new OrthographicCamera(-frustum, frustum, frustum, -frustum, 0.1, 10)
    camera.position.z = 4

    const renderer = new WebGLRenderer({ antialias: true, alpha: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setSize(size, size)
    mount.appendChild(renderer.domElement)

    const gem = buildGemMesh(palette)
    const outline = buildOutlineMesh(gem.geometry, palette.ink)
    const edges = buildEdgeLines(gem.geometry, palette.ink)

    const group = new Group()
    group.add(outline)
    group.add(gem)
    group.add(edges)
    group.rotation.x = REST_ROTATION.x
    group.rotation.y = REST_ROTATION.y
    scene.add(group)

    const target = { x: REST_ROTATION.x, y: REST_ROTATION.y }

    function handlePointerMove(event: PointerEvent) {
      const rect = renderer.domElement.getBoundingClientRect()
      const nx = ((event.clientX - rect.left) / rect.width) * 2 - 1
      const ny = ((event.clientY - rect.top) / rect.height) * 2 - 1
      target.y = REST_ROTATION.y + nx * MAX_TILT
      target.x = REST_ROTATION.x + ny * MAX_TILT
    }

    function handlePointerLeave() {
      target.x = REST_ROTATION.x
      target.y = REST_ROTATION.y
    }

    const interactionSurface = mount.closest<HTMLElement>('.login-brand') ?? mount
    interactionSurface.addEventListener('pointermove', handlePointerMove)
    interactionSurface.addEventListener('pointerleave', handlePointerLeave)

    let frameId = 0
    function animate() {
      group.rotation.x += (target.x - group.rotation.x) * 0.1
      group.rotation.y += (target.y - group.rotation.y) * 0.1
      renderer.render(scene, camera)
      frameId = requestAnimationFrame(animate)
    }
    animate()

    const resizeObserver = new ResizeObserver(() => {
      renderer.setSize(size, size)
    })
    resizeObserver.observe(mount)

    return () => {
      cancelAnimationFrame(frameId)
      resizeObserver.disconnect()
      interactionSurface.removeEventListener('pointermove', handlePointerMove)
      interactionSurface.removeEventListener('pointerleave', handlePointerLeave)
      renderer.domElement.remove()
      renderer.dispose()
      gem.geometry.dispose()
      ;(gem.material as { dispose(): void }).dispose()
      ;(outline.material as { dispose(): void }).dispose()
      edges.geometry.dispose()
      ;(edges.material as { dispose(): void }).dispose()
    }
  }, [size])

  return <div ref={mountRef} className="gem-canvas" style={{ width: size, height: size }} aria-hidden="true" />
}
```

- [ ] **Step 2: Verify typecheck + lint**

Run: `npm run build && npm run lint`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add src/components/gem/GemCanvas.tsx
git commit -m "feat(gem): add three.js gem canvas with pointer parallax"
```

---

### Task 5: Gem wrapper + styles (capability gate, lazy, fallback)

**Files:**
- Create: `frontend/src/components/gem/Gem.tsx`
- Create: `frontend/src/components/gem/Gem.css`

**Interfaces:**
- Consumes: `capabilities.ts` (Task 2); `GemCanvas.tsx` (Task 4); existing `Logo` (`frontend/src/components/Logo.tsx`).
- Produces: `export default function Gem(props: { size?: number }): JSX.Element`. Renders static `<Logo showWordmark={false} size>` unless `canRender3D()`, in which case a `React.lazy(GemCanvas)` inside `<Suspense fallback={<Logo …/>}>`.

- [ ] **Step 1: Write the wrapper**

Create `frontend/src/components/gem/Gem.tsx`:

```tsx
import { Suspense, lazy, useMemo } from 'react'
import Logo from '../Logo'
import { canRender3D } from './capabilities'
import './Gem.css'

const GemCanvas = lazy(() => import('./GemCanvas'))

interface GemProps {
  size?: number
}

export default function Gem({ size = 96 }: GemProps) {
  const enable3D = useMemo(() => canRender3D(), [])
  const fallback = <Logo showWordmark={false} size={size} />

  if (!enable3D) return fallback

  return (
    <div className="gem" style={{ width: size, height: size }}>
      <Suspense fallback={fallback}>
        <GemCanvas size={size} />
      </Suspense>
    </div>
  )
}
```

- [ ] **Step 2: Write the styles**

Create `frontend/src/components/gem/Gem.css`:

```css
.gem {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.gem-canvas {
  display: block;
}

.gem-canvas canvas {
  display: block;
}
```

- [ ] **Step 3: Verify typecheck + lint + tokens + build (confirm three chunk splits)**

Run: `npm run build && npm run lint && npm run check-tokens`
Expected: PASS. In the `vite build` output, confirm a **separate chunk** whose size reflects three.js (a few hundred KB) distinct from the main/login chunk — this proves lazy code-splitting works.

- [ ] **Step 4: Commit**

```bash
git add src/components/gem/Gem.tsx src/components/gem/Gem.css
git commit -m "feat(gem): add Gem wrapper with lazy load and SVG fallback"
```

---

### Task 6: Integrate into the Login brand panel

**Files:**
- Modify: `frontend/src/pages/Login.tsx`

**Interfaces:**
- Consumes: `Gem` (Task 5).
- Produces: Login brand panel renders `<Gem size={96} />` instead of `<Logo …/>`.

- [ ] **Step 1: Swap the mark**

In `frontend/src/pages/Login.tsx`:

Replace the import:

```tsx
import Logo from '../components/Logo'
```

with:

```tsx
import Gem from '../components/gem/Gem'
```

And replace the brand-mark element:

```tsx
          <div className="login-brand-mark">
            <Logo showWordmark={false} size={96} />
          </div>
```

with:

```tsx
          <div className="login-brand-mark">
            <Gem size={96} />
          </div>
```

- [ ] **Step 2: Verify typecheck + lint + tokens + build**

Run: `npm run build && npm run lint && npm run check-tokens && npm run check-gem`
Expected: PASS.

- [ ] **Step 3: Manual visual check**

Run: `npm run dev`, open the Login page.
Expected:
- Gem renders in the brand panel; tilts toward the cursor and eases back to rest when the pointer leaves; **no continuous spin**.
- Facets are solid pastels with a bold ink outline (no gradient, no gloss).
- With OS "Reduce motion" enabled (or a browser without WebGL), the static SVG logo shows instead.

- [ ] **Step 4: Commit**

```bash
git add src/pages/Login.tsx
git commit -m "feat(gem): use 3D gem in login brand panel"
```

---

## Self-Review

- **Spec coverage:** rendering approach (Task 1, 4), geometry/material/outline (Task 3), motion + settle (Task 4), reduced-motion/WebGL/lazy fallbacks (Task 2, 5), token-sourced colors (Task 3 default + Task 4 CSS read), lazy chunk split (Task 5 build check), Login integration (Task 6), verification strategy (every task) — all covered.
- **Placeholder scan:** none; every code/command step is concrete.
- **Type consistency:** `GemPalette`, `DEFAULT_PALETTE`, and builder signatures defined in Task 3 are used unchanged in Tasks 4 and the check script; `Gem`/`GemCanvas` prop shapes match between Tasks 4–6.
- **Scope:** single subsystem (login gem), single worktree; no unrelated refactoring.
