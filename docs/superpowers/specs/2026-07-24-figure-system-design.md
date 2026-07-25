# In-house Figure System (v1) — Design

**Date:** 2026-07-24
**Status:** Approved (brainstorm)

## Goal

Replace cropped figure PNGs with a **structured, evaluable figure spec** that the
frontend redraws in house style. v1 covers **Cartesian function graphs only**, but the
schema is an **extensible element list** so points, lines, shaded regions, and parametric
curves can be added later without a schema migration. The whole slice is buildable and
testable in isolation — no exam questions or PDF parser required.

## Decisions (from brainstorm)

1. **Scope v1:** Cartesian function graphs only (`y = f(x)` over a domain), axes + grid.
2. **Rendering location:** client-side. The spec is the single source of truth; the
   frontend evaluates and draws it with **Mafs** + **mathjs**. No generated image assets.
3. **Storage:** a **separate `Figure` table**, with nullable links to a question and/or a
   question part (figures often belong to a sub-part). Standalone test figures are
   first-class.
4. **Function representation:** an **evaluable expression string** in mathjs syntax
   (e.g. `"3*x^2 - 2*x"`). LaTeX stays in the question stem for display; it is not stored
   on the figure in v1.
5. **Test data source:** **both** a version-controlled YAML corpus (seeded via CLI, like
   practice) **and** a `POST` endpoint for ad-hoc experiments.

## Data model

New table in `src/mathwizard/models/db.py`:

```python
class Figure(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)      # stable key for idempotent YAML upsert
    title: str
    description: str | None = None
    spec: dict = Field(sa_column=Column(JSON))       # the FigureSpec JSON (see below)
    question_id: int | None = Field(default=None, foreign_key="question.id", index=True)
    part_id: int | None = Field(default=None, foreign_key="questionpart.id", index=True)
```

Both foreign keys are nullable.

## Figure spec (the shared JSON contract)

Pydantic models (API schema) in `src/mathwizard/models/figure.py`. v1 only emits
`functionGraph`, but the `elements` list is the extension point. This is the same contract
the future PDF parser must emit.

```python
class FunctionGraph(BaseModel):
    type: Literal["functionGraph"] = "functionGraph"
    fn: str                                       # evaluable, mathjs syntax
    domain: tuple[float, float] | None = None     # defaults to viewport x
    color: str | None = None                      # house-style default applied by frontend

class Viewport(BaseModel):
    x: tuple[float, float]
    y: tuple[float, float] | None = None          # None -> frontend auto-fits

class FigureSpec(BaseModel):
    viewport: Viewport
    show_grid: bool = True
    x_label: str = "x"
    y_label: str = "y"
    elements: list[FunctionGraph]
```

Future element types (out of scope now, added to the `elements` union later): `point`,
`tangentLine`, `shadedRegion`, `parametricCurve`, `image` (fallback for non-mathematical
figures that can never be reconstructed).

## API

New router `src/mathwizard/app/routes/figures.py`, backed by a `FigureService`
(service-layer pattern per repo conventions). All routes require the existing cookie
session auth, like the practice routes.

- `GET /api/v1/figures` → list of `FigureSummary` (`id`, `slug`, `title`, `question_id`,
  `part_id`).
- `GET /api/v1/figures/{id}` → `FigureResponse` (summary + full `spec`). 404 if missing.
- `POST /api/v1/figures` → validate a `FigureSpec` (+ `slug`, `title`, `description?`),
  persist it, return the created `FigureResponse`. This is the quick-experiment loop.
  Structural validation is via `FigureSpec`; duplicate `slug` → 409.

Expression *evaluability* is not validated server-side (mathjs is a JS library); the
frontend guards evaluation errors (see below).

## Seeding

- YAML corpus at `data/questions/figures/*.yaml`, one figure per file:
  `slug`, `title`, `description?`, `spec`.
- `BootstrapService.seed_figures()` reads that directory and idempotently upserts on
  `slug`. Wired into `run_all()`.
- New CLI command `mathwizard.cli seed-figures`, mirroring `seed-practice`.

## Frontend

- New dependencies: `mafs`, `mathjs`.
- `frontend/src/components/FigureView.tsx`: takes a `FigureSpec`, renders `<Mafs>` with
  `<Coordinates.Cartesian>`; each `functionGraph` element → `<Plot.OfX>` whose function is
  `mathjs.compile(fn)` evaluated at `x`. Colors/stroke default to design tokens so it looks
  native. Evaluation/parse errors are caught and replaced with a graceful Dutch fallback
  message ("Kon figuur niet tekenen") instead of crashing.
- `frontend/src/pages/Figures.tsx`: a test-gallery page at route `/figures` (behind auth)
  that fetches `GET /api/v1/figures` and renders each figure via `FigureView`. This is the
  iteration surface for tuning the in-house look.
- Types added to `frontend/src/types/api.ts`: `FigureElement`, `FigureSpec`,
  `FigureSummary`, `FigureResponse`.

## Testing

- Backend (pytest): `Figure` model CRUD via the DB mixin; seed idempotency (running twice
  is a no-op); endpoint auth (401 unauthenticated); `GET` list/detail; `POST` accepts a
  valid spec and rejects a malformed one (422) and a duplicate slug (409).
- Frontend: manual visual verification on `/figures` (the repo has no frontend test
  harness today).

## Out of scope for v1 (future, additive)

Points/labels, tangent/asymptote lines, shaded regions, parametric/polar curves, geometry
primitives, the `image` fallback element, wiring figures into the exam/practice cards,
seeding exam questions into the DB, and the PDF-ingestion pipeline. Each is additive: a new
`elements` type + a new Mafs component mapping, no migration of existing figures.
