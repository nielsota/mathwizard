# Practice Card Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Polish practice exercise cards by showing difficulty as easy/medium/hard color-coded badges, removing per-question topic/tag clutter, and toning down the `Opgave N` typography.

**Architecture:** Keep this frontend-only. The API can continue returning numeric `difficulty`, `topic`, and `tags`; the practice UI decides how much metadata to render. `ExerciseCard` maps numeric difficulty into a visual label/class, renders marks/calculator metadata, and leaves topic context to the `Practice` page header.

**Tech Stack:** React 19, TypeScript, Vite, oxlint, CSS modules-by-file pattern.

---

## File Structure

- Modify `frontend/src/components/ExerciseCard.tsx`: add a local difficulty mapping helper, remove per-card topic/tag rendering, and keep the card header metadata focused on difficulty/marks/calculator.
- Modify `frontend/src/components/ExerciseCard.css`: add color-coded difficulty badge classes, remove unused tag styles, and make `.ex-card-number` visually quieter.
- Modify `frontend/src/pages/Practice.tsx`: remove the per-topic tag-count summary so keywords are not emphasized on the practice page.
- No backend changes: `QuestionResponse.difficulty`, `topic`, and `tags` remain part of the API contract for future filtering/RAG.

Out of scope:

- Do not change the database model or YAML question format.
- Do not change sorting behavior.
- Do not add a frontend test framework for this small visual polish task.
- Do not remove `topic` or `tags` from TypeScript API types.

Implementation invariants:

- Numeric difficulty maps as: `difficulty <= 1` -> `Easy`, `difficulty === 2` -> `Medium`, `difficulty >= 3` -> `Hard`.
- Missing/null difficulty renders `Unknown` with a neutral style.
- Topic and keyword tags are not rendered on every question card.
- The topic still appears once in the practice page header via `TOPIC_META`.
- `Opgave N` remains visible and readable, but no longer uses the display font or oversized navy treatment.

---

### Task 1: Add Color-Coded Difficulty Labels

**Files:**
- Modify: `frontend/src/components/ExerciseCard.tsx`
- Modify: `frontend/src/components/ExerciseCard.css`

- [ ] **Step 1: Add the difficulty mapping helper**

In `frontend/src/components/ExerciseCard.tsx`, add this helper above `ExerciseCard`:

```tsx
function difficultyMeta(difficulty?: number | null) {
  if (difficulty == null) {
    return { label: 'Unknown', className: 'ex-badge--difficulty-unknown' }
  }

  if (difficulty <= 1) {
    return { label: 'Easy', className: 'ex-badge--difficulty-easy' }
  }

  if (difficulty === 2) {
    return { label: 'Medium', className: 'ex-badge--difficulty-medium' }
  }

  return { label: 'Hard', className: 'ex-badge--difficulty-hard' }
}
```

- [ ] **Step 2: Use the helper in the card header**

In `frontend/src/components/ExerciseCard.tsx`, replace:

```tsx
const difficultyLabel = exercise.difficulty ? `Niveau ${exercise.difficulty}` : 'Niveau onbekend'
const bodyId = `exercise-${exercise.id}-body`
const visibleTags = exercise.tags.filter(tag => tag !== exercise.topic)
```

with:

```tsx
const difficulty = difficultyMeta(exercise.difficulty)
const bodyId = `exercise-${exercise.id}-body`
```

Then replace:

```tsx
<span className="ex-badge ex-badge--difficulty">{difficultyLabel}</span>
```

with:

```tsx
<span className={`ex-badge ex-badge--difficulty ${difficulty.className}`}>
  {difficulty.label}
</span>
```

- [ ] **Step 3: Add color-coded difficulty styles**

In `frontend/src/components/ExerciseCard.css`, replace the existing `.ex-badge--difficulty` block:

```css
.ex-badge--difficulty {
  background: #f6f8fb;
  color: var(--navy);
  border: 1px solid var(--border);
}
```

with:

```css
.ex-badge--difficulty {
  border: 1px solid transparent;
}

.ex-badge--difficulty-easy {
  background: #ecfdf3;
  color: #027a48;
  border-color: #abefc6;
}

.ex-badge--difficulty-medium {
  background: #fffaeb;
  color: #b54708;
  border-color: #fedf89;
}

.ex-badge--difficulty-hard {
  background: #fef3f2;
  color: #b42318;
  border-color: #fecdca;
}

.ex-badge--difficulty-unknown {
  background: #f6f8fb;
  color: var(--text-muted);
  border-color: var(--border);
}
```

- [ ] **Step 4: Verify TypeScript and lint**

Run:

```bash
cd frontend && npm run build && npm run lint
```

Expected: PASS.

- [ ] **Step 5: Commit Task 1**

```bash
git add frontend/src/components/ExerciseCard.tsx frontend/src/components/ExerciseCard.css
git commit -m "Polish practice difficulty badges"
```

---

### Task 2: Remove Per-Question Topic And Keyword Chips

**Files:**
- Modify: `frontend/src/components/ExerciseCard.tsx`
- Modify: `frontend/src/components/ExerciseCard.css`
- Modify: `frontend/src/pages/Practice.tsx`

- [ ] **Step 1: Remove topic/tag rendering from each card**

In `frontend/src/components/ExerciseCard.tsx`, delete this block from the expanded card body:

```tsx
<div className="ex-card-tags" aria-label="Opgave labels">
  <span className="ex-tag ex-tag--topic">{exercise.topic}</span>
  {visibleTags.map(tag => (
    <span className="ex-tag" key={tag}>{tag}</span>
  ))}
</div>
```

After deletion, the expanded body should start with:

```tsx
{expanded && (
  <div className="ex-card-body" id={bodyId}>
    <div className="ex-card-divider" />
    <MathJax dynamic>
      <div
        className="ex-card-stem"
        dangerouslySetInnerHTML={{ __html: exercise.question_text }}
      />
```

- [ ] **Step 2: Remove unused tag styles**

In `frontend/src/components/ExerciseCard.css`, delete these blocks:

```css
.ex-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.ex-tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 9px;
  border-radius: 999px;
  background: var(--blue-wash);
  color: var(--navy);
  border: 1px solid var(--blue-light);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.ex-tag--topic {
  background: var(--navy);
  border-color: var(--navy);
  color: var(--peach);
}
```

- [ ] **Step 3: Remove keyword count from practice summary**

In `frontend/src/pages/Practice.tsx`, delete:

```tsx
const tagCount = new Set(questions.flatMap(ex => ex.tags)).size
```

Then replace:

```tsx
<div className="practice-summary">
  <span>{questions.length} opgaven</span>
  <span>{totalMarks} punten</span>
  <span>{tagCount} labels</span>
</div>
```

with:

```tsx
<div className="practice-summary">
  <span>{questions.length} opgaven</span>
  <span>{totalMarks} punten</span>
</div>
```

- [ ] **Step 4: Verify no tag UI references remain**

Run:

```bash
rg "ex-card-tags|ex-tag|tagCount|labels" frontend/src
```

Expected: no matches for removed UI classes/count. If `labels` appears in unrelated text, inspect it before changing anything.

- [ ] **Step 5: Verify frontend**

Run:

```bash
cd frontend && npm run build && npm run lint
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

```bash
git add frontend/src/components/ExerciseCard.tsx frontend/src/components/ExerciseCard.css frontend/src/pages/Practice.tsx
git commit -m "Remove per-question metadata chips"
```

---

### Task 3: Tone Down The Exercise Number Typography

**Files:**
- Modify: `frontend/src/components/ExerciseCard.css`

- [ ] **Step 1: Replace the exercise number style**

In `frontend/src/components/ExerciseCard.css`, replace:

```css
.ex-card-number {
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--navy);
  flex-shrink: 0;
}
```

with:

```css
.ex-card-number {
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
```

- [ ] **Step 2: Update the mobile override**

In the mobile media query in `frontend/src/components/ExerciseCard.css`, replace:

```css
.ex-card-number {
  font-size: 18px;
}
```

with:

```css
.ex-card-number {
  font-size: 12px;
}
```

- [ ] **Step 3: Manual visual check**

Start the dev servers:

```bash
./scripts/dev_deploy.sh
```

Open:

```text
http://localhost:3001/practice/unitcircle
```

Expected after login:

- Exercise numbers are still readable.
- `Opgave 1`, `Opgave 2`, etc. no longer dominate the card header.
- Difficulty badges are visibly color-coded as Easy, Medium, or Hard.
- Topic and keyword chips do not appear inside each expanded question card.

- [ ] **Step 4: Verify frontend**

Run:

```bash
cd frontend && npm run build && npm run lint
```

Expected: PASS.

- [ ] **Step 5: Commit Task 3**

```bash
git add frontend/src/components/ExerciseCard.css
git commit -m "Tone down practice card numbering"
```

---

### Task 4: Final Verification

**Files:**
- No source changes expected.

- [ ] **Step 1: Run frontend verification**

```bash
cd frontend && npm run build && npm run lint
```

Expected: PASS.

- [ ] **Step 2: Run backend tests to confirm no contract drift**

```bash
uv run --extra dev pytest -v
```

Expected: PASS.

- [ ] **Step 3: Check diff scope**

```bash
git diff --stat main...HEAD
```

Expected: changes are limited to:

```text
frontend/src/components/ExerciseCard.tsx
frontend/src/components/ExerciseCard.css
frontend/src/pages/Practice.tsx
```

If port-change files or unrelated local files appear, do not include them in this polish branch unless the user explicitly asks.

---

## Self-Review

- Spec coverage: The plan covers all three requested remarks: color-coded `Easy`/`Medium`/`Hard` difficulty labels, removal of per-question topic/keyword chips, and toned-down `Opgave N` typography.
- Placeholder scan: No `TBD`, vague test instructions, or “similar to” steps remain. Each code-changing step includes exact snippets.
- Type consistency: `QuestionResponse.difficulty` remains `number | null | undefined`; helper input matches that type. No API model or backend schema changes are introduced.
- Scope check: This is a small frontend polish plan. It intentionally avoids backend/data changes and new test infrastructure.
