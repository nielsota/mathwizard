---
name: vwo-wiskundeb-exam-domain
description: Reference knowledge for authoring VWO Wiskunde B practice exercises — the competency framework, what exam-level questions demand, the difficulty rubric, the practice YAML schema, and LaTeX/Dutch conventions. Read this before authoring or planning exercises with authoring-exercise-blueprint or authoring-exercises.
disable-model-invocation: true
---

# VWO Wiskunde B — Exam Domain Reference

Shared know-how for authoring exam-calibrated practice exercises. Read this before running `authoring-exercise-blueprint` (Gate 1) or `authoring-exercises` (Gate 2).

## What exam-level questions demand

From `data/questions/exams/curated/`, real exam items typically:

- **Combine multiple competencies** in one question (e.g. parametric differentiation + exact value + algebraic proof + reading a figure).
- Require **exact** answers (`\frac{1}{2}\sqrt{2}`, not `0.71`) and **justification / proof** (`Bewijs dat…`, `Toon aan…`), not just a number.
- Are frequently **calculator-restricted** (`calculator_allowed: false`).
- Sit in **dense Dutch context** and often reference a **figure**.

A good practice ladder is therefore not "more sums." Each rung adds competency load until it resembles an exam item.

## Difficulty rubric (`difficulty: 1`–`5`)

| Level | Meaning |
|-------|---------|
| 1 | Single skill, mechanical (e.g. differentiate a power function). |
| 2 | Single skill with a twist (roots/fractions, simplify first). |
| 3 | Two skills combined, light context. |
| 4 | Multi-step; exact answers or short justification; some context/figure. |
| 5 | Exam-style: multiple competencies, exact + proof, calculator-restricted, context. |

## Topic / competency map

Existing practice topics: `derivatives`, `goniometrie`, `parametric`, `rootfinding`, `unitcircle`.

VWO Wiskunde B domains for horizontal expansion (topic slug → core competencies):

- **derivatives** — power/product/quotient/chain rule; tangent lines; rate of change.
- **extrema-optimization** — stationary points, min/max, sign charts, applied optimisation.
- **integration** — antiderivatives, definite integrals, area between curves.
- **volume-of-revolution** — rotation about axes, integral setup.
- **rootfinding** — algebraic & exact solving, substitution, domain restrictions.
- **inequalities** — sign analysis, quadratic/rational inequalities.
- **exponential-logarithmic** — laws, equations, growth/decay, `e` and `ln`.
- **goniometrie** — sin/cos/tan, radians, equations, identities, transformations.
- **unitcircle** — exact values, symmetry, reference angles.
- **families-of-functions** — parameters, shared properties, proofs across a family.
- **asymptotes** — vertical/horizontal/oblique, limit reasoning, proofs of position.
- **analytic-geometry** — lines, circles, distance, intersections.
- **parametric** — parametric curves, vectors, angle between lines, motion.
- **algebraic-proof** — `Bewijs dat…` reasoning as a standalone skill.

When adding a **new topic**, pick a clear slug from this list (or a well-justified new one) and create `_meta.yaml` (see schema).

## Exam anchors

Real exam questions are the top of every ladder.

- Location: `data/questions/exams/curated/<exam_id>/q<N>.yaml`.
- Question ID scheme: `<exam_id>-q<N>` (e.g. `VW-1025-a-18-1-o-q1`). This is the value used in `builds_toward`.
- Cite anchors **by ID** and reference only their **meaningful parts**: curated extraction is noisy (some files contain junk `parts` with empty text and non-alphanumeric labels — ignore those).
- Read the anchor's `stem` and real `parts` to identify which competencies it exercises.

## Practice YAML schema

One file per exercise: `data/questions/practice/<topic>/p<N>.yaml`.

```yaml
source: practice          # always "practice"
topic: derivatives        # matches the folder slug
tags:                     # short Dutch keyword tags
- differentieren
- machtsregel
calculator_allowed: false # true/false
difficulty: 1             # 1-5 per rubric
builds_toward:            # exam question IDs this item ladders toward (optional list)
- VW-1025-a-18-1-o-q1
parts:                    # one or more parts
- points: 3
  text: \(f(x) = 3x^7 - 2x^5 + x^3\)
- points: 3
  text: \(g(x) = \frac{2}{x^3} + \frac{5}{x^2}\)
stem: Bepaal de afgeleide van de volgende functies.
title: Machtsfuncties
```

Per-topic metadata: `data/questions/practice/<topic>/_meta.yaml`

```yaml
title: Oefenopgaven Afgeleiden
subtitle: Leer differentiëren met machtsregel, productregel, quotiëntregel en kettingregel
```

Notes:
- `builds_toward` is written now; it is ignored by the current DB seeding until the deferred back-end change lands. Statements sync regardless.
- The upsert keys on `(source, topic, title)`, so **`title` must be unique within a topic**.

## LaTeX & Dutch conventions

- Inline math: `\( … \)`; display math: `\[ … \]`. (Both are supported by the frontend MathJax config.)
- All prose in **Dutch**, matching the existing exercises' tone.
- Prefer **exact** forms in expected answers; phrase proofs as `Bewijs dat…` / `Toon aan…`.
- Fractions `\frac{a}{b}`, roots `\sqrt{}` / `\sqrt[3]{}`, powers `x^{n}`.
- Keep each part focused; assign `points` proportional to work (mirror exam weighting: 2–5 typical).
