# Exercise Authoring Skills — Design Spec

**Date:** 2026-07-19
**Status:** Draft for review
**Owner:** Niels Ota

## Goal

Give the agent a reliable, review-gated system for authoring VWO Wiskunde B **practice exercise YAMLs** — expanding both **horizontally** (more topics) and **vertically** (more exercises per topic) — such that the practice content forms a deliberate **difficulty ladder toward exam readiness**, anchored to real past-exam questions.

## Approach

Three skills plus a thin sync CLI, following the existing `creating-*` skill style and the ticket→design→plan→implement review culture:

1. A shared reference skill encoding exam-competency know-how and the YAML schema.
2. A **Gate 1** skill that produces a per-topic *blueprint* (reviewed before any generation).
3. A **Gate 2** skill that generates the YAMLs from the approved blueprint and syncs them to the DB.

## Scope

- Authoring practice exercise YAMLs in the **existing schema** (`stem`, `parts[]` with `text`+`points`, `difficulty`, `tags`, `calculator_allowed`, `title`; topic `_meta.yaml`).
- Problem **statements only** — no worked solutions or answer keys.
- A per-exercise `builds_toward` reference field linking practice → exam question(s).
- A CLI to sync authored YAMLs into the SQLite DB, reusing existing seeding.

## Non-Goals

- No worked solutions / answer keys.
- No frontend changes.
- The `Question` model change for `builds_toward` and the "recover the ladder" endpoint are **out of scope here** — deferred to a separate ticket→design→plan→implement (see Deferred Back-End Work).
- No changes to the exam ingestion pipeline (`processed/` → `curated/`).

## Locked Decisions

| Decision | Choice |
|---|---|
| Primary goal | Deliberate difficulty ladder per topic → exam readiness |
| Output | Practice YAMLs only (statements, no solutions) |
| Review flow | Two gates: blueprint approved → generate → review |
| Exam linkage | Per-exercise `builds_toward: [<exam-question-id>, …]` (list) |
| Ladder cardinality | Typically many practice → one exam; list allows many-to-many |
| Domain knowledge | Its own reusable reference skill |
| DB sync | Thin Typer CLI reusing `BootstrapService.seed_practice_questions()` |

## Domain reasoning — what "exam-level" requires

From `data/questions/exams/curated/…`, exam items characteristically:
- **Combine multiple competencies** in one question (e.g. parametric differentiation + exact value + algebraic proof + reading a figure).
- Demand **exact** answers and **justification/proof**, not just a computed number.
- Are frequently **calculator-restricted**.
- Are embedded in **dense Dutch context** and often reference a **figure**.

Implication: a good ladder is not "more sums." Each topic needs rungs from **single-skill drills** (difficulty 1) up to **multi-competency, proof-carrying, figure/context, exam-style** items (difficulty 5), with each rung's competencies mapped to the exam question it builds toward.

### Difficulty rubric (1–5)

- **1** — single skill, mechanical (e.g. differentiate a power function).
- **2** — single skill with a twist (roots/fractions, simplify first).
- **3** — two skills combined, light context.
- **4** — multi-step, exact answers or short justification, some context/figure.
- **5** — exam-style: multiple competencies, exact + proof, calculator-restricted, figure/context.

## Skills

### 1. `vwo-wiskundeb-exam-domain` (reference, shared)

Encodes the reusable know-how so quality doesn't depend on re-derivation:
- VWO Wiskunde B **competency framework** (per topic/domain).
- What exam-level items demand (exact answers, proof, multi-step, figures, calculator rules).
- The **difficulty rubric** above.
- The **practice YAML schema** + valid-LaTeX and Dutch-style conventions.
- How to locate and cite exam anchors under `data/questions/exams/curated/`.

`disable-model-invocation: true`; read by the two gate skills.

### 2. `authoring-exercise-blueprint` (Gate 1)

Input: a topic (existing or new), or a target exam question.
Output: `artifacts/exercises/<topic>/blueprint.md`, containing:
- **Competencies** the topic requires.
- **Reference exam anchors** — relevant `curated` question IDs + why (user can paste more if some are missing).
- **Difficulty ladder** — rungs 1→5 mapping competencies to anchors.
- **Planned exercise list** (the "list of exercises per topic"): a table of
  `id · difficulty · competency · builds_toward · calculator · one-line description`,
  marking **existing vs. new** so gaps are visible (drives horizontal + vertical growth).

Ends by asking the user to review/edit/approve the blueprint. No YAML is written in this gate.

### 3. `authoring-exercises` (Gate 2)

Input: an approved `blueprint.md`.
Actions:
- Write `data/questions/practice/<topic>/pN.yaml` (and `_meta.yaml` for new topics) in the exact schema, one per planned new exercise.
- Set `builds_toward`, `difficulty`, `tags`, `calculator_allowed`, valid LaTeX, well-posed Dutch statements.
- **Self-check** before handoff: schema valid, no duplicate of an existing item, calibrated to its rung, LaTeX well-formed.
- On user OK, run the sync CLI and report created/updated counts.

## Sync CLI

- New thin CLI (Typer, already a dependency): `uv run python -m mathwizard.cli seed-practice`.
- Builds `DBClient(settings.database_url)` and calls `BootstrapService(db, settings).seed_practice_questions()` (existing idempotent upsert keyed on source/topic/title).
- Prints created/updated summary. Business logic stays in the service; the CLI is only an entry point.
- Unknown YAML keys (e.g. `builds_toward`) are ignored by the current upsert, so statements sync immediately; the link persists once the deferred change lands.

## Artifacts & locations

| Artifact | Location |
|---|---|
| Reference skill | `.claude/skills/vwo-wiskundeb-exam-domain/SKILL.md` |
| Blueprint skill | `.claude/skills/authoring-exercise-blueprint/SKILL.md` |
| Generation skill | `.claude/skills/authoring-exercises/SKILL.md` |
| Per-topic blueprint | `artifacts/exercises/<topic>/blueprint.md` |
| Practice YAMLs | `data/questions/practice/<topic>/pN.yaml` (+ `_meta.yaml`) |
| Sync CLI | `src/mathwizard/cli.py` |

## Data field: `builds_toward`

Added to practice YAML:

```yaml
builds_toward:
  - VW-1025-a-18-1-o-q1
```

Written by Gate 2 now; ignored by current seeding; becomes DB-persisted after the deferred change.

## Deferred Back-End Work (separate ticket → design → plan → implement)

1. Add `builds_toward` to the `Question` model and persist it (extend `create_question`/`replace_question` + seeding to pass it through).
2. Add an endpoint to **recover the competency ladder** (given an exam question, return the practice items that build toward it, ordered by difficulty).

## Workflow (how the user uses the agent)

1. "Expand `<topic>`" / "New topic `<x>`" / "Build a ladder toward `<exam-question-id>`".
2. Agent runs Gate 1 → blueprint. **User reviews** (main control point): edits ladder, pastes extra exam anchors, approves.
3. Agent runs Gate 2 → writes YAMLs, self-checks, then syncs to DB on approval.
4. User spot-checks in the app. Repeat to deepen (vertical) or add topics (horizontal).

## Open questions

- Exact set of new topics for the first horizontal expansion (decided per-blueprint, not here).
- Whether to also maintain a top-level cross-topic coverage index later (deferred; per-topic blueprint suffices for now).
