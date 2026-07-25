# Home Hub Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the post-login landing page (currently the exam search) with a sleek home "hub" where students pick between practicing per topic (subboxes per onderwerp) or searching exam questions.

**Architecture:** Add a new `Home` page mounted at `/`, move the existing `ExamSearch` page to `/search`, and extract the duplicated topic metadata (currently copied in `Header.tsx` and `Practice.tsx`) into one shared `constants/topics.ts` module that `Home`, `Header`, and `Practice` all consume. Routing and the header nav are updated so `/` renders the hub and "Examenopgaven zoeken" points at `/search`.

**Tech Stack:** React 19 + TypeScript, React Router DOM v7, Vite 8, plain CSS with design tokens in `frontend/src/index.css`, oxlint. No test runner is installed.

## Global Constraints

- All UI copy is in **Dutch** (match existing tone, e.g. "Oefen onderwerpen", "Examenopgaven zoeken", "Uitloggen").
- Reuse existing CSS design tokens from `frontend/src/index.css` — do NOT introduce new fonts or a color palette. Tokens: `--navy #032254`, `--navy-deep #021a3f`, `--blue #85b5e2`, `--blue-light #bddef4`, `--blue-mist #e8f1fa`, `--blue-wash #f2f7fc`, `--peach #fcdabb`, `--peach-light #fef0e0`, `--peach-dark #f5c9a3`, `--surface #fff`, `--border #e2e6ef`, fonts `--font-display` (Instrument Serif) / `--font-body` (DM Sans), radii `--radius-sm/md/lg/xl` = 8/14/20/28px, `--container-max 920px`.
- Every authenticated `fetch` keeps `credentials: 'include'` (unchanged behavior; Home makes no fetch).
- No new npm dependencies.
- **Verification (no unit-test harness exists):** each task is verified with `cd frontend && npm run build` (runs `tsc -b` typecheck + `vite build`) and `cd frontend && npm run lint` (oxlint), plus the manual dev-server checklist in the task. Both commands must exit 0.
- Follow existing file conventions: one `.css` file per page/component, imported at the top of the `.tsx`; default-export React function components.
- Frontend working directory is `frontend/` relative to repo root. All `npm` commands run there.

---

### Task 1: Shared topic metadata module

Extract the topic list/metadata that is currently duplicated (as `practiceTopics` in `Header.tsx` and `TOPIC_META` in `Practice.tsx`) into a single source of truth. No visual or behavioral change — this is a pure refactor that must still build.

**Files:**
- Create: `frontend/src/constants/topics.ts`
- Modify: `frontend/src/components/Header.tsx:6-12` (remove local `practiceTopics`, import shared list)
- Modify: `frontend/src/components/Header.tsx:63-71` (render from shared list)
- Modify: `frontend/src/pages/Practice.tsx:7-33` (remove local `TOPIC_META`, import shared map)
- Modify: `frontend/src/pages/Practice.tsx:45` (use shared map)

**Interfaces:**
- Produces:
  - `interface TopicMeta { slug: string; label: string; subtitle: string; icon: string }`
  - `const TOPICS: TopicMeta[]` — ordered list of the 5 topics
  - `const TOPIC_MAP: Record<string, TopicMeta>` — slug → meta lookup

- [ ] **Step 1: Create the shared constants module**

Create `frontend/src/constants/topics.ts`:

```ts
export interface TopicMeta {
  slug: string
  label: string
  subtitle: string
  icon: string
}

export const TOPICS: TopicMeta[] = [
  {
    slug: 'unitcircle',
    label: 'Eenheidscirkel',
    subtitle: 'Sinus, cosinus en tangens op de eenheidscirkel',
    icon: '⊙',
  },
  {
    slug: 'derivatives',
    label: 'Afgeleiden',
    subtitle: 'Differentiëren en afgeleide functies',
    icon: "f'",
  },
  {
    slug: 'rootfinding',
    label: 'Wortels vinden',
    subtitle: 'Snijpunten, nulpunten en vergelijkingen oplossen',
    icon: '√',
  },
  {
    slug: 'parametric',
    label: 'Parametrische vergelijkingen',
    subtitle: 'Parametrische krommen en vergelijkingen',
    icon: 't→',
  },
  {
    slug: 'goniometrie',
    label: 'Goniometrie',
    subtitle: 'Goniometrische functies, identiteiten en vergelijkingen',
    icon: 'θ',
  },
]

export const TOPIC_MAP: Record<string, TopicMeta> = Object.fromEntries(
  TOPICS.map(topic => [topic.slug, topic]),
)
```

- [ ] **Step 2: Refactor `Header.tsx` to use the shared list**

In `frontend/src/components/Header.tsx`, delete the local `practiceTopics` array (lines 6-12) and add the import after the existing imports (keep line 3 `import type { UserResponse }` etc.):

```tsx
import { useState, useRef, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import type { UserResponse } from '../types/api'
import { TOPICS } from '../constants/topics'
import './Header.css'
```

Then update the dropdown menu render (currently lines 63-71) to map over `TOPICS`:

```tsx
            {dropdownOpen && (
              <div className="mw-dropdown-menu">
                {TOPICS.map(topic => (
                  <Link key={topic.slug} to={`/practice/${topic.slug}`} className="mw-dropdown-item">
                    {topic.label}
                  </Link>
                ))}
              </div>
            )}
```

- [ ] **Step 3: Refactor `Practice.tsx` to use the shared map**

In `frontend/src/pages/Practice.tsx`, delete the local `TOPIC_META` object (lines 7-33) and add the import after line 4:

```tsx
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import ExerciseCard from '../components/ExerciseCard'
import type { QuestionListResponse } from '../types/api'
import { TOPIC_MAP } from '../constants/topics'
import './Practice.css'
```

Then change the `meta` lookup (currently line 45) from `TOPIC_META[topic]` to `TOPIC_MAP[topic]`:

```tsx
  const meta = topic ? TOPIC_MAP[topic] : null
```

Leave everything else in `Practice.tsx` unchanged (`meta.icon`, `meta?.title`, `meta?.subtitle` all still resolve against `TopicMeta`).

- [ ] **Step 4: Verify build + lint pass**

Run: `cd frontend && npm run build`
Expected: exits 0, no TypeScript errors (a `dist/` is produced).

Run: `cd frontend && npm run lint`
Expected: exits 0, no lint errors.

- [ ] **Step 5: Manual dev-server smoke check**

Run: `cd frontend && npm run dev` (leave backend running separately on :8001 as usual).
Open `http://localhost:3001`, log in, and confirm:
- The header "Oefen onderwerpen" dropdown still lists all 5 topics and each link opens the correct `/practice/:topic` page.
- A practice page (e.g. `/practice/derivatives`) still shows the correct title/subtitle/icon.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/constants/topics.ts frontend/src/components/Header.tsx frontend/src/pages/Practice.tsx
git commit -m "refactor(frontend): extract shared topic metadata module"
```

---

### Task 2: Home hub page component + styles

Build the new landing page as a self-contained component and stylesheet. It is not wired into routing yet (that happens in Task 3), so the app is unchanged for now but must still build.

**Files:**
- Create: `frontend/src/pages/Home.tsx`
- Create: `frontend/src/pages/Home.css`

**Interfaces:**
- Consumes: `TOPICS` from `../constants/topics` (Task 1), `UserResponse` from `../types/api`.
- Produces: `export default function Home(props: { user: UserResponse })` — the page rendered at `/` in Task 3.

- [ ] **Step 1: Create `Home.tsx`**

Create `frontend/src/pages/Home.tsx`:

```tsx
import { useNavigate } from 'react-router-dom'
import { TOPICS } from '../constants/topics'
import type { UserResponse } from '../types/api'
import './Home.css'

interface HomeProps {
  user: UserResponse
}

export default function Home({ user }: HomeProps) {
  const navigate = useNavigate()

  return (
    <div className="page-enter home">
      <header className="home-hero">
        <p className="home-eyebrow">Welkom terug, {user.username}</p>
        <h1 className="home-title">Waar wil je mee aan de slag?</h1>
        <p className="home-lede">
          Oefen gericht per onderwerp of doorzoek de examenbank met AI-zoeken.
        </p>
      </header>

      <section className="home-section">
        <div className="home-section-head">
          <h2 className="home-section-title">Oefen onderwerpen</h2>
          <p className="home-section-sub">Kies een onderwerp om gericht te oefenen</p>
        </div>

        <div className="home-topic-grid">
          {TOPICS.map((topic, index) => (
            <button
              key={topic.slug}
              type="button"
              className="home-topic-card"
              style={{ animationDelay: `${0.06 * index}s` }}
              onClick={() => navigate(`/practice/${topic.slug}`)}
            >
              <span className="home-topic-icon" aria-hidden="true">{topic.icon}</span>
              <span className="home-topic-label">{topic.label}</span>
              <span className="home-topic-sub">{topic.subtitle}</span>
              <span className="home-topic-arrow" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path d="M4 9h10M10 5l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
            </button>
          ))}
        </div>
      </section>

      <section className="home-section">
        <button
          type="button"
          className="home-search-lane"
          onClick={() => navigate('/search')}
        >
          <div className="home-search-accent" aria-hidden="true">
            <svg viewBox="0 0 200 200" fill="none" width="200" height="200">
              <circle cx="100" cy="100" r="80" stroke="var(--blue-light)" strokeWidth="1" opacity="0.5" />
              <circle cx="100" cy="100" r="50" stroke="var(--blue-light)" strokeWidth="1" opacity="0.35" />
              <line x1="20" y1="100" x2="180" y2="100" stroke="var(--peach)" strokeWidth="1" opacity="0.4" />
              <line x1="100" y1="20" x2="100" y2="180" stroke="var(--peach)" strokeWidth="1" opacity="0.4" />
              <path d="M30 170 Q100 40 170 170" stroke="var(--blue)" strokeWidth="1.5" opacity="0.25" fill="none" />
            </svg>
          </div>

          <div className="home-search-body">
            <span className="home-search-kicker">Examenbank</span>
            <span className="home-search-title">Examenopgaven zoeken</span>
            <span className="home-search-desc">
              Beschrijf een opgave en vind met AI de meest relevante examenopgaven.
            </span>
          </div>

          <span className="home-search-cta">
            Zoeken
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M4 9h10M10 5l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
        </button>
      </section>
    </div>
  )
}
```

- [ ] **Step 2: Create `Home.css`**

Create `frontend/src/pages/Home.css`:

```css
.home {
  display: flex;
  flex-direction: column;
  gap: 44px;
}

/* Hero */
.home-hero {
  position: relative;
}

.home-eyebrow {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--blue);
  margin: 0 0 8px;
}

.home-title {
  font-family: var(--font-display);
  font-size: 46px;
  font-weight: 400;
  line-height: 1.1;
  letter-spacing: -0.5px;
  color: var(--navy);
  margin: 0 0 10px;
}

.home-lede {
  font-size: 17px;
  color: var(--text-muted);
  max-width: 520px;
  margin: 0;
}

/* Sections */
.home-section-head {
  margin-bottom: 18px;
}

.home-section-title {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 400;
  color: var(--navy);
  margin: 0 0 2px;
}

.home-section-sub {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

/* Topic subboxes */
.home-topic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.home-topic-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  padding: 20px 20px 22px;
  text-align: left;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-family: var(--font-body);
  box-shadow: 0 2px 14px rgba(133, 181, 226, 0.08);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  animation: homeCardIn 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes homeCardIn {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

.home-topic-card:hover {
  transform: translateY(-3px);
  border-color: var(--blue-light);
  box-shadow: 0 10px 28px rgba(3, 34, 84, 0.1);
}

.home-topic-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  margin-bottom: 8px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--navy) 0%, #0a3a7a 100%);
  color: var(--peach);
  font-family: var(--font-display);
  font-size: 20px;
  font-style: italic;
  box-shadow: 0 4px 14px rgba(3, 34, 84, 0.2);
}

.home-topic-label {
  font-size: 17px;
  font-weight: 700;
  color: var(--navy);
}

.home-topic-sub {
  font-size: 13px;
  line-height: 1.45;
  color: var(--text-muted);
}

.home-topic-arrow {
  position: absolute;
  top: 20px;
  right: 18px;
  color: var(--blue);
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.home-topic-card:hover .home-topic-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* Exam search lane */
.home-search-lane {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 20px;
  width: 100%;
  padding: 28px 30px;
  text-align: left;
  cursor: pointer;
  font-family: var(--font-body);
  border: 1px solid var(--navy);
  border-radius: var(--radius-xl);
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%);
  color: #fff;
  box-shadow: 0 8px 30px rgba(3, 34, 84, 0.22);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.home-search-lane:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 40px rgba(3, 34, 84, 0.3);
}

.home-search-accent {
  position: absolute;
  top: 50%;
  right: -30px;
  transform: translateY(-50%);
  opacity: 0.5;
  pointer-events: none;
}

.home-search-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  position: relative;
  z-index: 1;
  flex: 1;
}

.home-search-kicker {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--peach);
}

.home-search-title {
  font-family: var(--font-display);
  font-size: 30px;
  line-height: 1.1;
  color: #fff;
}

.home-search-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.78);
  max-width: 460px;
}

.home-search-cta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1;
  flex-shrink: 0;
  padding: 11px 20px;
  border-radius: var(--radius-sm);
  background: var(--peach);
  color: var(--navy);
  font-size: 14px;
  font-weight: 700;
  transition: transform 0.18s ease, background 0.18s ease;
}

.home-search-lane:hover .home-search-cta {
  background: var(--peach-dark);
  transform: translateX(2px);
}

/* Mobile */
@media (max-width: 640px) {
  .home {
    gap: 34px;
  }

  .home-title {
    font-size: 34px;
  }

  .home-lede {
    font-size: 15px;
  }

  .home-topic-grid {
    grid-template-columns: 1fr;
  }

  .home-search-lane {
    flex-direction: column;
    align-items: flex-start;
    padding: 22px;
  }

  .home-search-accent {
    display: none;
  }

  .home-search-cta {
    align-self: stretch;
    justify-content: center;
  }
}
```

- [ ] **Step 3: Verify build + lint pass**

Run: `cd frontend && npm run build`
Expected: exits 0. `Home.tsx` compiles (it is an unused module for now, which is fine — it is an exported module, not an unused local).

Run: `cd frontend && npm run lint`
Expected: exits 0.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Home.tsx frontend/src/pages/Home.css
git commit -m "feat(frontend): add home hub page component and styles"
```

---

### Task 3: Wire routing so `/` is the hub and `/search` is exam search

Mount `Home` at `/`, move `ExamSearch` to `/search`, and repoint the header's "Examenopgaven zoeken" link. This is the task that changes what the user sees after login.

**Files:**
- Modify: `frontend/src/App.tsx:1-8` (import `Home`)
- Modify: `frontend/src/App.tsx:74-87` (route table)
- Modify: `frontend/src/components/Header.tsx:74-79` (nav link target + active state)

**Interfaces:**
- Consumes: `Home` from `./pages/Home` with prop `{ user: UserResponse }` (Task 2); `ExamSearch` with prop `{ onUnauthorized: () => void }` (existing, unchanged).

- [ ] **Step 1: Import `Home` in `App.tsx`**

In `frontend/src/App.tsx`, add the import (keep the existing `ExamSearch`, `Login`, `Practice` imports):

```tsx
import { useCallback, useEffect, useState } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import Header from './components/Header'
import ExamSearch from './pages/ExamSearch'
import Home from './pages/Home'
import Login from './pages/Login'
import Practice from './pages/Practice'
import type { UserResponse } from './types/api'
import './App.css'
```

- [ ] **Step 2: Update the route table in `App.tsx`**

Replace the `<Routes>` block (currently lines 74-87) with:

```tsx
        <Routes>
          <Route
            path="/login"
            element={user ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />}
          />
          <Route
            path="/"
            element={user ? <Home user={user} /> : <Navigate to="/login" replace state={{ from: location }} />}
          />
          <Route
            path="/search"
            element={user ? <ExamSearch onUnauthorized={handleUnauthorized} /> : <Navigate to="/login" replace state={{ from: location }} />}
          />
          <Route
            path="/practice/:topic"
            element={user ? <Practice onUnauthorized={handleUnauthorized} /> : <Navigate to="/login" replace state={{ from: location }} />}
          />
        </Routes>
```

Note: `handleLogin` already defaults its redirect target to `/` (line 62), which now correctly lands on the hub. No change needed there.

- [ ] **Step 3: Repoint the header "Examenopgaven zoeken" link**

In `frontend/src/components/Header.tsx`, update the nav link (currently lines 74-79) to target `/search` and mark it active on that path:

```tsx
          <Link
            to="/search"
            className={`mw-nav-link ${location.pathname === '/search' ? 'active' : ''}`}
          >
            Examenopgaven zoeken
          </Link>
```

The brand link (`<Link to="/">`) already returns users to the hub, so no separate "Home" nav item is required.

- [ ] **Step 4: Verify build + lint pass**

Run: `cd frontend && npm run build`
Expected: exits 0, no TypeScript errors.

Run: `cd frontend && npm run lint`
Expected: exits 0.

- [ ] **Step 5: Manual dev-server verification checklist**

Run: `cd frontend && npm run dev` (backend running on :8001).
Log in, then confirm each:
- After login you land on `/` showing the **hub** (hero "Waar wil je mee aan de slag?", the "Oefen onderwerpen" subbox grid, and the "Examenopgaven zoeken" lane) — NOT the old search page.
- Clicking a topic subbox navigates to `/practice/:topic` and loads that topic's questions.
- Clicking the "Examenopgaven zoeken" lane navigates to `/search` and the search UI works exactly as before.
- The header "Examenopgaven zoeken" link goes to `/search` and shows the active style there.
- Clicking the MathWizard brand logo returns to `/` (the hub).
- The "Oefen onderwerpen" header dropdown still routes to each topic.
- Reloading while on `/search` or `/practice/derivatives` keeps you on that page (session restore works); reloading while logged out redirects to `/login`.
- Resize to mobile width (<640px): hero, single-column topic grid, and stacked search lane all render cleanly.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/App.tsx frontend/src/components/Header.tsx
git commit -m "feat(frontend): make home hub the landing page, move exam search to /search"
```

---

## Self-Review

**1. Spec coverage:**
- "new home page (not examenopgaven zoeken) after login" → Task 3 mounts `Home` at `/`; `ExamSearch` moved to `/search`.
- "click either oefen onderwerpen … or examenopgaven zoeken" → Home has the "Oefen onderwerpen" section and the "Examenopgaven zoeken" lane (Task 2).
- "subboxes with onderwerp" → `home-topic-grid` renders one subbox per topic (Task 2), sourced from shared `TOPICS` (Task 1).
- "sleek / frontend-design" → Task 2 CSS uses the existing math/notebook design language (Instrument Serif display, navy/peach/blue tokens, staggered card entrance, gradient search lane, hover lifts) rather than generic AI aesthetics; no new fonts/palette per Global Constraints.
- "writing-plans first" → this document.

**2. Placeholder scan:** No TBD/TODO/"handle edge cases" placeholders; every code step contains complete content. Verification steps use build + lint + explicit manual checklist because no unit-test runner is installed (stated in Global Constraints).

**3. Type consistency:** `TopicMeta` fields (`slug`, `label`, `subtitle`, `icon`) are used identically in `topics.ts`, `Home.tsx`, `Header.tsx` (`topic.slug`/`topic.label`), and `Practice.tsx` (`meta.icon`/`meta.title`/`meta.subtitle`). `Home` prop is `{ user: UserResponse }` in both Task 2 (definition) and Task 3 (usage). `ExamSearch` keeps its existing `{ onUnauthorized }` prop.
