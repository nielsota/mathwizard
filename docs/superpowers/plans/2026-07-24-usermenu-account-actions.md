# UserMenu Account Actions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fold the logged-in user's name and the "Uitloggen" action into the existing "Menu" dropdown (`UserMenu`), removing the separate username/logout block from the header bar.

**Architecture:** `UserMenu` gains an identity header (avatar + name + role pill) at the top of its panel and a full-width "Uitloggen" action at the bottom; it receives a new `onLogout` prop forwarded from `Header`. `Header` then drops its standalone `.mw-auth` block and the now-dead CSS. No routing, API, or backend changes.

**Tech Stack:** React 19 + TypeScript, React Router DOM v7, Vite 8, plain CSS with the design tokens in `frontend/src/index.css`, oxlint. No test runner is installed.

**Branch:** `feat/students-teachers` (this is where `UserMenu` exists).

## Global Constraints

- All UI copy is in **Dutch** (e.g. "Uitloggen", "Docent", "Leerling").
- Reuse existing CSS design tokens from `frontend/src/index.css` — no new fonts or palette. Relevant tokens: `--navy #032254`, `--peach #fcdabb`, `--blue-mist #e8f1fa`, `--surface #fff`, `--border #e2e6ef`, `--text-muted #6b7280`, `--font-display` (Instrument Serif), `--font-body` (DM Sans), `--radius-sm 8px`, `--radius-md 14px`.
- **Design intent (frontend-design):** the menu becomes a proper account panel — a clear identity row (circular navy/peach avatar with initials, display-serif name, small uppercase role pill), the existing roster card, then a visually separated logout action that reveals a soft red danger tint only on hover. Refined, not flashy; match the existing math-notebook aesthetic.
- No new npm dependencies; no new files.
- **Verification (no unit-test harness exists):** each task is verified with `cd frontend && npm run build` (`tsc -b` typecheck + `vite build`) and `cd frontend && npm run lint` (oxlint). Both must exit 0. Plus the per-task manual dev-server check.
- Keep the existing `initials(name)` helper and `.mw-um-avatar` base class; the self avatar is a modifier on top of it.
- Frontend working directory is `frontend/`. All `npm` commands run there.

---

### Task 1: Add identity + logout to `UserMenu`

Add the account identity block and the "Uitloggen" action inside the `UserMenu` panel, threading a new `onLogout` prop from `Header`. To keep the build green, `Header` is updated to pass the prop in this task, but its existing `.mw-auth` block is left untouched until Task 2 (temporary, harmless duplication).

**Files:**
- Modify: `frontend/src/components/UserMenu.tsx:10-13` (add `onLogout` to props)
- Modify: `frontend/src/components/UserMenu.tsx:168` (destructure `onLogout`)
- Modify: `frontend/src/components/UserMenu.tsx:208-229` (replace eyebrow with identity block; append logout button)
- Modify: `frontend/src/components/UserMenu.css` (remove `.mw-um-eyebrow`; add identity + logout styles)
- Modify: `frontend/src/components/Header.tsx:76` (pass `onLogout` to `UserMenu`)

**Interfaces:**
- Consumes: `initials(name: string): string` (existing in `UserMenu.tsx`), `UserResponse` with `username: string` and `role: 'teacher' | 'student'` (from `../types/api`).
- Produces: `UserMenu` prop shape becomes `{ user: UserResponse; onUnauthorized: () => void; onLogout: () => void }`.

- [ ] **Step 1: Add `onLogout` to `UserMenuProps`**

In `frontend/src/components/UserMenu.tsx`, update the props interface (currently lines 10-13):

```tsx
interface UserMenuProps {
  user: UserResponse
  onUnauthorized: () => void
  onLogout: () => void
}
```

- [ ] **Step 2: Destructure `onLogout` in the component**

Change the component signature (currently line 168) from:

```tsx
export default function UserMenu({ user, onUnauthorized }: UserMenuProps) {
```

to:

```tsx
export default function UserMenu({ user, onUnauthorized, onLogout }: UserMenuProps) {
```

- [ ] **Step 3: Replace the eyebrow with an identity block and add the logout action**

In `frontend/src/components/UserMenu.tsx`, replace the panel contents. The current block is:

```tsx
        <div className="mw-dropdown-menu mw-usermenu-panel">
          <p className="mw-um-eyebrow">
            {user.role === 'teacher' ? 'Docent' : 'Leerling'}
          </p>
          {user.role === 'teacher' ? (
            <RosterCard
              title="Mijn leerlingen"
              subtitle="Bekijk je leerlingen"
              icon={studentsIcon}
            >
              <StudentsContent onUnauthorized={onUnauthorized} />
            </RosterCard>
          ) : (
            <RosterCard
              title="Mijn docent"
              subtitle="Bekijk je docent"
              icon={teacherIcon}
            >
              <MyTeacherContent onUnauthorized={onUnauthorized} />
            </RosterCard>
          )}
        </div>
```

Replace it with:

```tsx
        <div className="mw-dropdown-menu mw-usermenu-panel">
          <div className="mw-um-identity">
            <span className="mw-um-avatar mw-um-avatar--self">{initials(user.username)}</span>
            <span className="mw-um-identity-text">
              <span className="mw-um-identity-name">{user.username}</span>
              <span className="mw-um-identity-role">
                {user.role === 'teacher' ? 'Docent' : 'Leerling'}
              </span>
            </span>
          </div>

          {user.role === 'teacher' ? (
            <RosterCard
              title="Mijn leerlingen"
              subtitle="Bekijk je leerlingen"
              icon={studentsIcon}
            >
              <StudentsContent onUnauthorized={onUnauthorized} />
            </RosterCard>
          ) : (
            <RosterCard
              title="Mijn docent"
              subtitle="Bekijk je docent"
              icon={teacherIcon}
            >
              <MyTeacherContent onUnauthorized={onUnauthorized} />
            </RosterCard>
          )}

          <button type="button" className="mw-um-logout" onClick={onLogout}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path d="M6 2H3.5A1.5 1.5 0 002 3.5v9A1.5 1.5 0 003.5 14H6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
              <path d="M10 11l3-3-3-3M13 8H6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Uitloggen
          </button>
        </div>
```

- [ ] **Step 4: Update `UserMenu.css` — remove eyebrow, add identity + logout styles**

In `frontend/src/components/UserMenu.css`, delete the now-unused `.mw-um-eyebrow` rule (currently lines 10-17):

```css
.mw-um-eyebrow {
  margin: 2px 4px 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-muted);
}
```

Then add the following rules (place them after the `.mw-usermenu-panel` rule near the top of the file):

```css
.mw-um-identity {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 2px 4px 12px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--border);
}

.mw-um-avatar--self {
  width: 40px;
  height: 40px;
  font-size: 14px;
  background: linear-gradient(135deg, var(--navy) 0%, #0a3a7a 100%);
  color: var(--peach);
}

.mw-um-identity-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
  min-width: 0;
}

.mw-um-identity-name {
  max-width: 190px;
  font-family: var(--font-display);
  font-size: 18px;
  line-height: 1.1;
  color: var(--navy);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mw-um-identity-role {
  padding: 1px 8px;
  border-radius: 999px;
  background: var(--blue-mist);
  color: var(--navy);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.mw-um-logout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  margin-top: 12px;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--text-muted);
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}

.mw-um-logout:hover {
  color: #b4232a;
  border-color: #f0c0c2;
  background: #fdf3f3;
}
```

- [ ] **Step 5: Pass `onLogout` from `Header` to `UserMenu`**

In `frontend/src/components/Header.tsx`, update the `UserMenu` usage (currently line 76) from:

```tsx
          <UserMenu user={user} onUnauthorized={onUnauthorized} />
```

to:

```tsx
          <UserMenu user={user} onUnauthorized={onUnauthorized} onLogout={onLogout} />
```

Leave the existing `.mw-auth` block (lines 78-83) in place for now — it still compiles and is removed in Task 2.

- [ ] **Step 6: Verify build + lint pass**

Run: `cd frontend && npm run build`
Expected: exits 0, no TypeScript errors.

Run: `cd frontend && npm run lint`
Expected: exits 0.

- [ ] **Step 7: Manual dev-server check**

Run: `cd frontend && npm run dev` (backend running on :8001). Log in, open the "Menu" dropdown, and confirm:
- The panel now shows the identity row at the top (avatar initials + username + role pill).
- The roster card ("Mijn leerlingen" for a teacher / "Mijn docent" for a student) still expands and loads.
- A full-width "Uitloggen" button appears at the bottom; clicking it logs you out (returns to `/login`).
- (The old username + Uitloggen in the header bar still shows too — that is removed in Task 2.)

- [ ] **Step 8: Commit**

```bash
git add frontend/src/components/UserMenu.tsx frontend/src/components/UserMenu.css frontend/src/components/Header.tsx
git commit -m "feat(frontend): move user identity and logout into UserMenu panel"
```

---

### Task 2: Remove the standalone auth block from `Header`

Delete the now-redundant `.mw-auth` block from the header bar and its dead CSS, so the username and logout live only in the menu.

**Files:**
- Modify: `frontend/src/components/Header.tsx:78-83` (remove `.mw-auth` block)
- Modify: `frontend/src/components/Header.css` (remove `.mw-auth`, `.mw-user`, `.mw-logout` rules incl. mobile overrides)

**Interfaces:**
- Consumes: nothing new. `HeaderProps` keeps `onLogout: () => void` (still forwarded to `UserMenu` from Task 1).

- [ ] **Step 1: Remove the `.mw-auth` block from `Header.tsx`**

In `frontend/src/components/Header.tsx`, delete these lines (currently 78-83), including the blank line that precedes them so the `<UserMenu>` is the last child of `<nav>`:

```tsx

          <div className="mw-auth">
            <span className="mw-user">{user.username}</span>
            <button className="mw-logout" type="button" onClick={onLogout}>
              Uitloggen
            </button>
          </div>
```

After removal, the end of the `<nav>` reads:

```tsx
          <UserMenu user={user} onUnauthorized={onUnauthorized} onLogout={onLogout} />
        </nav>
      </div>
    </header>
```

Note: `onLogout` is still used (passed to `UserMenu`), so the prop stays and there is no unused-variable lint error.

- [ ] **Step 2: Remove the dead auth CSS from `Header.css`**

In `frontend/src/components/Header.css`, delete the following rules:

The main-layout auth rules (currently lines 144-179):

```css
.mw-auth {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: 10px;
  padding-left: 12px;
  border-left: 1px solid var(--border);
}

.mw-user {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--navy);
  font-size: 13px;
  font-weight: 700;
}

.mw-logout {
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 7px 10px;
  background: var(--surface);
  color: var(--text-muted);
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mw-logout:hover {
  color: var(--navy);
  background: var(--blue-wash);
}
```

The `@media (max-width: 760px)` auth override (currently lines 210-213) — remove just this rule from inside that media block:

```css
  .mw-auth {
    margin-left: 4px;
    padding-left: 10px;
  }
```

The `@media (max-width: 520px)` auth/user overrides (currently lines 226-237) — remove these two rules from inside that media block:

```css
  .mw-auth {
    width: 100%;
    justify-content: space-between;
    margin-left: 0;
    padding: 8px 0 0;
    border-top: 1px solid var(--border);
    border-left: none;
  }

  .mw-user {
    max-width: min(52vw, 220px);
  }
```

Leave all other Header CSS (brand, nav, dropdown) intact. The `@media (max-width: 520px)` block will still contain its `.mw-header-inner` and `.mw-nav` rules.

- [ ] **Step 3: Confirm no lingering references**

Run: `rg "mw-auth|mw-user\b|mw-logout" frontend/src`
Expected: no matches (all references removed).

- [ ] **Step 4: Verify build + lint pass**

Run: `cd frontend && npm run build`
Expected: exits 0, no TypeScript errors.

Run: `cd frontend && npm run lint`
Expected: exits 0.

- [ ] **Step 5: Manual dev-server check**

Run: `cd frontend && npm run dev`. Log in and confirm:
- The header bar no longer shows a separate username or "Uitloggen" button — only the brand, "Oefen onderwerpen", "Examenopgaven zoeken", and the "Menu" button.
- Username, role, and "Uitloggen" all live inside the "Menu" dropdown, and logout still works.
- Resize to <520px: the header wraps cleanly with no leftover empty auth area or border artifacts.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/Header.tsx frontend/src/components/Header.css
git commit -m "refactor(frontend): drop standalone header auth block in favor of UserMenu"
```

---

## Self-Review

**1. Spec coverage:**
- "I like the menu button" → the "Menu" trigger and dropdown are unchanged (Task 1 only adds to the panel contents).
- "uitloggen … should be there too — not separate" → Task 1 adds the "Uitloggen" action inside the panel; Task 2 removes the separate header button.
- "user name should be there too — not separate" → Task 1 adds the identity row (name + role) inside the panel; Task 2 removes the separate `.mw-user` span.
- "using frontend-design" → Task 1's Design intent + concrete CSS deliver a cohesive account panel (avatar, display-serif name, role pill, hover-danger logout) reusing existing tokens; no generic aesthetics, no new fonts.

**2. Placeholder scan:** No TBD/TODO/vague steps; every code step shows exact before/after content. Verification uses build + lint + `rg` + manual checks because there is no unit-test runner (stated in Global Constraints).

**3. Type consistency:** `UserMenuProps` is `{ user, onUnauthorized, onLogout }` in Task 1 (definition, destructure, and `Header` call site all match). `HeaderProps.onLogout` already exists and remains used after Task 2. Class names introduced in Task 1 CSS (`mw-um-identity`, `mw-um-identity-text`, `mw-um-identity-name`, `mw-um-identity-role`, `mw-um-avatar--self`, `mw-um-logout`) exactly match those used in the Task 1 JSX. Class names removed in Task 2 (`mw-auth`, `mw-user`, `mw-logout`) match those deleted from both `Header.tsx` and `Header.css`, verified by the Step 3 `rg` check.
