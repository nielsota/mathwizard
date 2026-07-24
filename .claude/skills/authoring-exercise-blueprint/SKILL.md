---
name: authoring-exercise-blueprint
description: Gate 1 of exercise authoring. Produces a reviewable per-topic blueprint (competencies, exam anchors, difficulty ladder, and a planned exercise list marking existing vs new) before any YAML is generated. Use when expanding a VWO Wiskunde B topic, adding a new topic, or building a practice ladder toward a specific exam question.
disable-model-invocation: true
---

# Authoring Exercise Blueprint (Gate 1)

Produce a per-topic **blueprint** the user reviews **before** any exercise YAML is written. This is the main control point for exam-calibrated expansion.

**Prerequisite:** read `vwo-wiskundeb-exam-domain` first (competency map, difficulty rubric, schema, exam-anchor conventions).

**HARD GATE:** Do NOT write any `data/questions/practice/**` YAML in this skill. Blueprint only, then stop for approval. Generation happens in `authoring-exercises` (Gate 2).

## Workflow

Copy this checklist and track progress:

```
- [ ] Step 1: Determine target (topic to expand, new topic, or exam question to ladder toward)
- [ ] Step 2: Inventory what already exists for the topic
- [ ] Step 3: Select exam anchors
- [ ] Step 4: Design the difficulty ladder and planned exercise list
- [ ] Step 5: Write blueprint.md and stop for review
```

### Step 1: Determine target

Clarify with the user if ambiguous:
- **Expand existing topic** (vertical): add rungs/exercises to e.g. `derivatives`.
- **New topic** (horizontal): pick a slug from the domain map.
- **Toward an exam question**: build a ladder culminating in a specific `<exam_id>-q<N>`.

### Step 2: Inventory existing exercises

Read `data/questions/practice/<topic>/` (all `p*.yaml` + `_meta.yaml`) if the topic exists. Record each existing exercise's `title`, `difficulty`, and `builds_toward`. This inventory feeds the "existing vs new" column and prevents duplicates.

### Step 3: Select exam anchors

Find relevant questions in `data/questions/exams/curated/`. For each, read the `stem` and real `parts` (ignore junk parts). Record `<exam_id>-q<N>` and which competencies it exercises. Tell the user which anchors you picked and invite them to paste more if coverage feels thin.

### Step 4: Design ladder + planned list

Map competencies to rungs 1→5 (see rubric). Draft the planned exercises so that lower rungs isolate single skills and higher rungs combine them toward the anchors. Each planned exercise names the `builds_toward` anchor(s).

### Step 5: Write blueprint and stop

Write to `artifacts/exercises/<topic>/blueprint.md` using the template below, then present a summary and **stop for user approval**. Do not proceed to generation.

## Blueprint template

```markdown
# Blueprint: <topic>

**Type:** expand existing | new topic
**Date:** <YYYY-MM-DD>

## Competencies
- <competency 1>
- <competency 2>

## Exam anchors
| Exam question ID | Competencies exercised | Notes |
|---|---|---|
| VW-1025-a-18-1-o-q1 | parametric derivative, exact value, proof | figure-based |

*(User may paste additional anchors here.)*

## Difficulty ladder
| Rung | Focus | Competencies | Builds toward |
|---|---|---|---|
| 1 | single-skill drill | … | — |
| 5 | exam-style | … | VW-1025-a-18-1-o-q1 |

## Planned exercises
| Proposed id | Status | Difficulty | Competency | builds_toward | calculator | Description |
|---|---|---|---|---|---|---|
| p1 | existing | 1 | machtsregel | — | false | Machtsfuncties |
| p11 | new | 3 | product+chain | VW-1025-a-18-1-o-q1 | false | Combine product and chain rule |
```

## Handoff

End with:
> "Blueprint written to `artifacts/exercises/<topic>/blueprint.md`. Review it — edit the ladder, paste extra exam anchors, adjust the planned list — and approve. Then I'll run `authoring-exercises` to generate the YAMLs."
