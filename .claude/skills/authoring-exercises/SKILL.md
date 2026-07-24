---
name: authoring-exercises
description: Gate 2 of exercise authoring. Generates VWO Wiskunde B practice exercise YAMLs from an approved blueprint (correct schema, difficulty, tags, calculator flag, builds_toward, valid LaTeX), self-checks them, and syncs them into the database. Use after a blueprint from authoring-exercise-blueprint has been approved.
disable-model-invocation: true
---

# Authoring Exercises (Gate 2)

Generate practice exercise YAMLs from an **approved** blueprint, then sync them into the DB.

**Prerequisites:**
- Read `vwo-wiskundeb-exam-domain` (schema, rubric, conventions).
- An approved `artifacts/exercises/<topic>/blueprint.md` exists. If not, run `authoring-exercise-blueprint` first — do not invent a plan here.

## Workflow

```
- [ ] Step 1: Load the approved blueprint
- [ ] Step 2: Determine next p<N> index
- [ ] Step 3: Write one YAML per NEW planned exercise
- [ ] Step 4: Self-check every file
- [ ] Step 5: Sync to the database
- [ ] Step 6: Report and hand off for review
```

### Step 1: Load the approved blueprint

Read `artifacts/exercises/<topic>/blueprint.md`. Only generate exercises marked **new** in the planned list. For a **new topic**, also create `data/questions/practice/<topic>/_meta.yaml` (title + subtitle).

### Step 2: Determine next `p<N>` index

List existing `data/questions/practice/<topic>/p*.yaml` and continue numbering from the highest (e.g. if `p10.yaml` exists, start at `p11`). Never overwrite an existing file.

### Step 3: Write one YAML per new exercise

Use the schema from the reference skill. For each new exercise set: `source: practice`, `topic`, `tags`, `calculator_allowed`, `difficulty`, `builds_toward` (from the blueprint), `parts` (`points` + `text`), `stem`, `title`.

- All prose in **Dutch**; math in `\( … \)` / `\[ … \]`.
- Calibrate to the rung's `difficulty`; combine competencies as the rung dictates.
- `title` must be **unique within the topic** (the DB upsert keys on `(source, topic, title)`).

### Step 4: Self-check every file

Confirm for each generated file:

```
- [ ] Valid YAML, parses cleanly
- [ ] source=practice; topic matches folder; difficulty 1-5
- [ ] title unique within the topic (not a duplicate of an existing one)
- [ ] LaTeX well-formed and balanced
- [ ] Statement is well-posed and solvable at its level (no missing data)
- [ ] calculator_allowed set intentionally
- [ ] builds_toward IDs exist under data/questions/exams/curated/
```

### Step 5: Sync to the database

After the user OKs the files, run the sync CLI (idempotent upsert, reuses bootstrap seeding):

```bash
uv run python -m mathwizard.cli seed-practice
```

### Step 6: Report and hand off

List the files created and the sync summary (how many practice questions now in the DB), then:
> "Generated <N> exercises for `<topic>` and synced to the DB. Spot-check them in the app; tell me which to revise."

## Notes

- `builds_toward` persists to the DB only after the deferred back-end change; statements sync immediately.
- If a generated statement cannot be made well-posed without a figure, prefer a text-only reformulation (practice YAMLs have no figure support).
