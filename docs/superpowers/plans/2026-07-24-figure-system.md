# Figure System (v1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Store math figures as an evaluable, structured spec in a dedicated `Figure` table, expose them over an authenticated API (seeded from YAML + created ad hoc), and render them client-side in house style with Mafs — replacing cropped figure PNGs, starting with Cartesian function graphs.

**Architecture:** Backend follows the existing service-layer + DB-mixin pattern (`Figure` model → `FiguresMixin` → `FigureService` → `/api/v1/figures` router, wired through `app.state` dependencies). The figure spec is a Pydantic contract (`FigureSpec`) stored as JSON; v1 only emits a `functionGraph` element but the `elements` list is the extension point. Frontend adds a `FigureView` component (Mafs + mathjs) and a `/figures` gallery page that reads the API.

**Tech Stack:** Python 3.12, FastAPI, SQLModel/SQLAlchemy, Pydantic v2, Typer, pytest; React 19 + Vite 8 + TypeScript, `mafs`, `mathjs`.

## Global Constraints

- No module-level docstrings at the top of files.
- Do not use `from __future__ import annotations`.
- Business/workflow logic lives in service classes (`FigureService`), following `QuestionService`/`AuthService`. Routes depend on services via `Annotated[..., Depends(...)]`, never on the DB client directly.
- DB access lives in a mixin (`FiguresMixin`) composed into `DBClient`, following `QuestionsMixin`.
- All user-facing UI copy in **Dutch**.
- All figure API routes require the existing cookie-session auth (`CurrentUserDep`), like the practice routes.
- Spec is the single source of truth; no generated image assets. Function strings are **mathjs syntax**, evaluated in the frontend.
- Tests use the existing style: `def make_db(tmp_path)` → `DBClient(f"sqlite:///{tmp_path / 'x.db'}")`; API tests assemble a bare `FastAPI()`, set `app.state.*`, include routers, use `TestClient`.

---

## File structure

Backend:
- Modify `src/mathwizard/models/db.py` — add `Figure` table.
- Modify `src/mathwizard/exceptions.py` — add `FigureNotFoundError`, `DuplicateFigureSlugError`.
- Create `src/mathwizard/db/mixins/figures.py` — `FiguresMixin`.
- Modify `src/mathwizard/db/mixins/__init__.py` — export `FiguresMixin`.
- Modify `src/mathwizard/db/client.py` — compose `FiguresMixin`.
- Create `src/mathwizard/models/figure.py` — `FigureSpec` contract + API schemas.
- Create `src/mathwizard/services/figure.py` — `FigureService`.
- Modify `src/mathwizard/app/dependencies.py` — `get_figure_service` + `FigureServiceDep`.
- Create `src/mathwizard/app/routes/figures.py` — figures router.
- Modify `src/mathwizard/app/main.py` — wire service + include router.
- Modify `src/mathwizard/settings.py` — `figures_dir` property.
- Modify `src/mathwizard/services/bootstrap.py` — `seed_figures()` + call in `run_all()`.
- Modify `src/mathwizard/cli.py` — `seed-figures` command.
- Create `data/questions/figures/*.yaml` — sample corpus.
- Create tests under `tests/`.

Frontend:
- Modify `frontend/package.json` — add `mafs`, `mathjs` (via npm).
- Modify `frontend/src/types/api.ts` — figure types.
- Create `frontend/src/components/FigureView.tsx` (+ `.css`).
- Create `frontend/src/pages/Figures.tsx` (+ `.css`).
- Modify `frontend/src/App.tsx` — add `/figures` route.

---

### Task 1: `Figure` DB model + exceptions

**Files:**
- Modify: `src/mathwizard/models/db.py`
- Modify: `src/mathwizard/exceptions.py`
- Test: `tests/test_db_figures.py` (created in Task 2)

**Interfaces:**
- Produces: `Figure` SQLModel table with columns `id, slug, title, description, spec (JSON dict), question_id, part_id`; exceptions `FigureNotFoundError(figure_id: int)`, `DuplicateFigureSlugError(slug: str)`.

- [ ] **Step 1: Add the `Figure` table**

In `src/mathwizard/models/db.py`, append after `QuestionPart` (the file already imports `Column, JSON` from `sqlalchemy` and `Field, Relationship, SQLModel` from `sqlmodel`):

```python
class Figure(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    title: str
    description: str | None = None
    spec: dict = Field(default_factory=dict, sa_column=Column(JSON))
    question_id: int | None = Field(default=None, foreign_key="question.id", index=True)
    part_id: int | None = Field(default=None, foreign_key="questionpart.id", index=True)
```

- [ ] **Step 2: Add exceptions**

In `src/mathwizard/exceptions.py`, append:

```python
class FigureNotFoundError(MathWizardError):
    def __init__(self, figure_id: int) -> None:
        super().__init__(f"Figure {figure_id} not found")
        self.figure_id = figure_id


class DuplicateFigureSlugError(MathWizardError):
    def __init__(self, slug: str) -> None:
        super().__init__(f"Figure with slug '{slug}' already exists")
        self.slug = slug
```

- [ ] **Step 3: Verify the table is created**

Run: `uv run python -c "from mathwizard.db.client import DBClient; import tempfile, os; p=os.path.join(tempfile.mkdtemp(),'t.db'); db=DBClient(f'sqlite:///{p}'); import sqlalchemy as sa; print(sa.inspect(db.engine).get_table_names())"`
Expected: output list includes `figure`.

- [ ] **Step 4: Commit**

```bash
git add src/mathwizard/models/db.py src/mathwizard/exceptions.py
git commit -m "feat: add Figure model and figure exceptions"
```

---

### Task 2: `FiguresMixin` (DB layer)

**Files:**
- Create: `src/mathwizard/db/mixins/figures.py`
- Modify: `src/mathwizard/db/mixins/__init__.py`
- Modify: `src/mathwizard/db/client.py`
- Test: `tests/test_db_figures.py`

**Interfaces:**
- Consumes: `Figure` (Task 1), `FigureNotFoundError` (Task 1), `NeedsEngine` (existing `src/mathwizard/db/mixins/base.py`).
- Produces on `DBClient`:
  - `create_figure(slug: str, title: str, spec: dict, *, description: str | None = None, question_id: int | None = None, part_id: int | None = None) -> Figure`
  - `get_figure(figure_id: int) -> Figure` (raises `FigureNotFoundError`)
  - `get_figure_by_slug(slug: str) -> Figure | None`
  - `list_figures() -> list[Figure]`
  - `upsert_figure(slug, title, spec, *, description=None, question_id=None, part_id=None) -> Figure`

- [ ] **Step 1: Write the failing test**

Create `tests/test_db_figures.py`:

```python
from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.exceptions import FigureNotFoundError


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'figures.db'}")


SPEC = {
    "viewport": {"x": [-5, 5], "y": [-5, 5]},
    "show_grid": True,
    "x_label": "x",
    "y_label": "y",
    "elements": [{"type": "functionGraph", "fn": "x^2", "domain": None, "color": None}],
}


def test_create_and_get_figure(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    figure = db.create_figure("parabool", "Parabool", SPEC, description="y = x^2")

    assert figure.id is not None
    saved = db.get_figure(figure.id)
    assert saved.slug == "parabool"
    assert saved.title == "Parabool"
    assert saved.description == "y = x^2"
    assert saved.spec["elements"][0]["fn"] == "x^2"
    assert saved.question_id is None
    assert saved.part_id is None


def test_get_missing_figure_raises(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    try:
        db.get_figure(999)
    except FigureNotFoundError as exc:
        assert exc.figure_id == 999
    else:
        raise AssertionError("expected FigureNotFoundError")


def test_get_figure_by_slug(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    db.create_figure("parabool", "Parabool", SPEC)
    assert db.get_figure_by_slug("parabool") is not None
    assert db.get_figure_by_slug("bestaat-niet") is None


def test_upsert_figure_is_idempotent_on_slug(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    first = db.upsert_figure("parabool", "Parabool", SPEC)
    second = db.upsert_figure("parabool", "Parabool (herzien)", SPEC)

    assert first.id == second.id
    assert len(db.list_figures()) == 1
    assert db.get_figure(first.id).title == "Parabool (herzien)"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_db_figures.py -v`
Expected: FAIL (`DBClient` has no attribute `create_figure`).

- [ ] **Step 3: Write the mixin**

Create `src/mathwizard/db/mixins/figures.py`:

```python
from sqlmodel import Session as DBSession
from sqlmodel import select

from mathwizard.db.mixins.base import NeedsEngine
from mathwizard.exceptions import FigureNotFoundError
from mathwizard.models.db import Figure


class FiguresMixin(NeedsEngine):

    def create_figure(
        self,
        slug: str,
        title: str,
        spec: dict,
        *,
        description: str | None = None,
        question_id: int | None = None,
        part_id: int | None = None,
    ) -> Figure:
        figure = Figure(
            slug=slug,
            title=title,
            spec=spec,
            description=description,
            question_id=question_id,
            part_id=part_id,
        )
        with DBSession(self.engine) as session:
            session.add(figure)
            session.commit()
            session.refresh(figure)
            return figure

    def get_figure(self, figure_id: int) -> Figure:
        with DBSession(self.engine) as session:
            figure = session.get(Figure, figure_id)
            if figure is None:
                raise FigureNotFoundError(figure_id)
            return figure

    def get_figure_by_slug(self, slug: str) -> Figure | None:
        with DBSession(self.engine) as session:
            statement = select(Figure).where(Figure.slug == slug)
            return session.exec(statement).first()

    def list_figures(self) -> list[Figure]:
        with DBSession(self.engine) as session:
            statement = select(Figure).order_by(Figure.id)
            return list(session.exec(statement).all())

    def upsert_figure(
        self,
        slug: str,
        title: str,
        spec: dict,
        *,
        description: str | None = None,
        question_id: int | None = None,
        part_id: int | None = None,
    ) -> Figure:
        with DBSession(self.engine) as session:
            statement = select(Figure).where(Figure.slug == slug)
            figure = session.exec(statement).first()
            if figure is None:
                figure = Figure(slug=slug)
                session.add(figure)
            figure.title = title
            figure.spec = spec
            figure.description = description
            figure.question_id = question_id
            figure.part_id = part_id
            session.commit()
            session.refresh(figure)
            return figure
```

- [ ] **Step 4: Export the mixin**

Replace `src/mathwizard/db/mixins/__init__.py` with:

```python
from .figures import FiguresMixin
from .questions import QuestionsMixin
from .sessions import SessionsMixin
from .users import UserMixin

__all__ = [
    "FiguresMixin",
    "QuestionsMixin",
    "SessionsMixin",
    "UserMixin",
]
```

- [ ] **Step 5: Compose into `DBClient`**

In `src/mathwizard/db/client.py`, update the import and class declaration:

```python
from .mixins import FiguresMixin, QuestionsMixin, SessionsMixin, UserMixin


class DBClient(UserMixin, SessionsMixin, QuestionsMixin, FiguresMixin):
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/test_db_figures.py -v`
Expected: PASS (4 tests).

- [ ] **Step 7: Commit**

```bash
git add src/mathwizard/db/mixins/figures.py src/mathwizard/db/mixins/__init__.py src/mathwizard/db/client.py tests/test_db_figures.py
git commit -m "feat: add FiguresMixin for figure persistence"
```

---

### Task 3: Figure spec contract + API schemas

**Files:**
- Create: `src/mathwizard/models/figure.py`
- Test: `tests/test_models/test_figure.py`

**Interfaces:**
- Produces:
  - `FunctionGraph(type: Literal["functionGraph"], fn: str, domain: tuple[float, float] | None, color: str | None)`
  - `Viewport(x: tuple[float, float], y: tuple[float, float] | None)`
  - `FigureSpec(viewport: Viewport, show_grid: bool, x_label: str, y_label: str, elements: list[FunctionGraph])`
  - `FigureCreateRequest(slug: str, title: str, description: str | None, spec: FigureSpec)`
  - `FigureSummary(id: int, slug: str, title: str, question_id: int | None, part_id: int | None)`
  - `FigureResponse(id, slug, title, description, spec: FigureSpec, question_id, part_id)`
  - `FigureListResponse(figures: list[FigureSummary])`

- [ ] **Step 1: Write the failing test**

Create `tests/test_models/__init__.py` (empty) and `tests/test_models/test_figure.py`:

```python
import pytest
from pydantic import ValidationError

from mathwizard.models.figure import FigureSpec


def test_valid_function_graph_spec_parses() -> None:
    spec = FigureSpec.model_validate(
        {
            "viewport": {"x": [-5, 5]},
            "elements": [{"type": "functionGraph", "fn": "x^2"}],
        }
    )
    assert spec.show_grid is True
    assert spec.viewport.y is None
    assert spec.elements[0].fn == "x^2"
    assert spec.elements[0].type == "functionGraph"


def test_unknown_element_type_is_rejected() -> None:
    with pytest.raises(ValidationError):
        FigureSpec.model_validate(
            {
                "viewport": {"x": [-5, 5]},
                "elements": [{"type": "banana", "fn": "x^2"}],
            }
        )


def test_missing_fn_is_rejected() -> None:
    with pytest.raises(ValidationError):
        FigureSpec.model_validate(
            {"viewport": {"x": [-5, 5]}, "elements": [{"type": "functionGraph"}]}
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_models/test_figure.py -v`
Expected: FAIL (`No module named 'mathwizard.models.figure'`).

- [ ] **Step 3: Write the models**

Create `src/mathwizard/models/figure.py`:

```python
from typing import Literal

from pydantic import BaseModel, Field


class FunctionGraph(BaseModel):
    type: Literal["functionGraph"] = "functionGraph"
    fn: str
    domain: tuple[float, float] | None = None
    color: str | None = None


class Viewport(BaseModel):
    x: tuple[float, float]
    y: tuple[float, float] | None = None


class FigureSpec(BaseModel):
    viewport: Viewport
    show_grid: bool = True
    x_label: str = "x"
    y_label: str = "y"
    elements: list[FunctionGraph] = Field(default_factory=list)


class FigureCreateRequest(BaseModel):
    slug: str
    title: str
    description: str | None = None
    spec: FigureSpec


class FigureSummary(BaseModel):
    id: int
    slug: str
    title: str
    question_id: int | None = None
    part_id: int | None = None


class FigureResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str | None = None
    spec: FigureSpec
    question_id: int | None = None
    part_id: int | None = None


class FigureListResponse(BaseModel):
    figures: list[FigureSummary]
```

Note: `elements: list[FunctionGraph]` is the extension point. When more element types are added, this becomes `list[FunctionGraph | Point | ...]` with a discriminated union on `type`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_models/test_figure.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add src/mathwizard/models/figure.py tests/test_models
git commit -m "feat: add FigureSpec contract and figure API schemas"
```

---

### Task 4: `FigureService`

**Files:**
- Create: `src/mathwizard/services/figure.py`
- Test: `tests/test_services/test_figure.py`

**Interfaces:**
- Consumes: `DBClient` (Task 2 methods), models from Task 3, `DuplicateFigureSlugError`/`FigureNotFoundError` (Task 1).
- Produces `FigureService(db: DBClient)` with:
  - `list_figures() -> FigureListResponse`
  - `get_figure(figure_id: int) -> FigureResponse` (raises `FigureNotFoundError`)
  - `create_figure(request: FigureCreateRequest) -> FigureResponse` (raises `DuplicateFigureSlugError`)

- [ ] **Step 1: Write the failing test**

Create `tests/test_services/test_figure.py`:

```python
from pathlib import Path

import pytest

from mathwizard.db.client import DBClient
from mathwizard.exceptions import DuplicateFigureSlugError, FigureNotFoundError
from mathwizard.models.figure import FigureCreateRequest
from mathwizard.services.figure import FigureService


def make_service(tmp_path: Path) -> FigureService:
    return FigureService(DBClient(f"sqlite:///{tmp_path / 'figures.db'}"))


def make_request(slug: str = "parabool") -> FigureCreateRequest:
    return FigureCreateRequest.model_validate(
        {
            "slug": slug,
            "title": "Parabool",
            "spec": {
                "viewport": {"x": [-5, 5]},
                "elements": [{"type": "functionGraph", "fn": "x^2"}],
            },
        }
    )


def test_create_then_get_and_list(tmp_path: Path) -> None:
    service = make_service(tmp_path)

    created = service.create_figure(make_request())
    fetched = service.get_figure(created.id)
    listing = service.list_figures()

    assert fetched.slug == "parabool"
    assert fetched.spec.elements[0].fn == "x^2"
    assert [summary.slug for summary in listing.figures] == ["parabool"]


def test_create_duplicate_slug_raises(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    service.create_figure(make_request())
    with pytest.raises(DuplicateFigureSlugError):
        service.create_figure(make_request())


def test_get_missing_raises(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    with pytest.raises(FigureNotFoundError):
        service.get_figure(123)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_services/test_figure.py -v`
Expected: FAIL (`No module named 'mathwizard.services.figure'`).

- [ ] **Step 3: Write the service**

Create `src/mathwizard/services/figure.py`:

```python
from mathwizard.db.client import DBClient
from mathwizard.exceptions import DuplicateFigureSlugError
from mathwizard.models.db import Figure
from mathwizard.models.figure import (
    FigureCreateRequest,
    FigureListResponse,
    FigureResponse,
    FigureSpec,
    FigureSummary,
)


def _to_summary(figure: Figure) -> FigureSummary:
    return FigureSummary(
        id=figure.id,
        slug=figure.slug,
        title=figure.title,
        question_id=figure.question_id,
        part_id=figure.part_id,
    )


def _to_response(figure: Figure) -> FigureResponse:
    return FigureResponse(
        id=figure.id,
        slug=figure.slug,
        title=figure.title,
        description=figure.description,
        spec=FigureSpec.model_validate(figure.spec),
        question_id=figure.question_id,
        part_id=figure.part_id,
    )


class FigureService:
    def __init__(self, db: DBClient) -> None:
        self.db = db

    def list_figures(self) -> FigureListResponse:
        return FigureListResponse(
            figures=[_to_summary(figure) for figure in self.db.list_figures()],
        )

    def get_figure(self, figure_id: int) -> FigureResponse:
        return _to_response(self.db.get_figure(figure_id))

    def create_figure(self, request: FigureCreateRequest) -> FigureResponse:
        if self.db.get_figure_by_slug(request.slug) is not None:
            raise DuplicateFigureSlugError(request.slug)
        figure = self.db.create_figure(
            slug=request.slug,
            title=request.title,
            spec=request.spec.model_dump(),
            description=request.description,
        )
        return _to_response(figure)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_services/test_figure.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add src/mathwizard/services/figure.py tests/test_services/test_figure.py
git commit -m "feat: add FigureService"
```

---

### Task 5: Figures API router + wiring

**Files:**
- Modify: `src/mathwizard/app/dependencies.py`
- Create: `src/mathwizard/app/routes/figures.py`
- Modify: `src/mathwizard/app/main.py`
- Test: `tests/test_app/test_figure_routes.py`

**Interfaces:**
- Consumes: `FigureService` (Task 4), `CurrentUserDep` (from `mathwizard.app.auth`), models from Task 3.
- Produces: `FigureServiceDep`; routes `GET /api/v1/figures`, `GET /api/v1/figures/{figure_id}`, `POST /api/v1/figures`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_app/test_figure_routes.py`:

```python
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mathwizard.app.auth import router as auth_router
from mathwizard.app.routes.figures import router as figures_router
from mathwizard.db.client import DBClient
from mathwizard.services.auth import AuthService, hash_password
from mathwizard.services.figure import FigureService
from mathwizard.settings import Settings


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'api.db'}")


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'api.db'}",
        cookie_secure=False,
        session_ttl_days=7,
    )


def make_client(db: DBClient, tmp_path: Path) -> TestClient:
    app = FastAPI()
    app.state.auth_service = AuthService(db, make_settings(tmp_path))
    app.state.figure_service = FigureService(db)
    app.include_router(auth_router)
    app.include_router(figures_router)
    return TestClient(app)


def authenticate(client: TestClient, db: DBClient) -> None:
    db.create_user("root", hash_password("secret"))
    response = client.post("/auth/login", json={"username": "root", "password": "secret"})
    assert response.status_code == 200


VALID_BODY = {
    "slug": "parabool",
    "title": "Parabool",
    "spec": {
        "viewport": {"x": [-5, 5]},
        "elements": [{"type": "functionGraph", "fn": "x^2"}],
    },
}


def test_list_requires_authentication(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, tmp_path)
    assert client.get("/api/v1/figures").status_code == 401


def test_post_then_list_and_get(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, tmp_path)
    authenticate(client, db)

    created = client.post("/api/v1/figures", json=VALID_BODY)
    assert created.status_code == 201
    figure_id = created.json()["id"]

    listing = client.get("/api/v1/figures")
    assert listing.status_code == 200
    assert [f["slug"] for f in listing.json()["figures"]] == ["parabool"]

    detail = client.get(f"/api/v1/figures/{figure_id}")
    assert detail.status_code == 200
    assert detail.json()["spec"]["elements"][0]["fn"] == "x^2"


def test_post_duplicate_slug_conflicts(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, tmp_path)
    authenticate(client, db)
    client.post("/api/v1/figures", json=VALID_BODY)
    assert client.post("/api/v1/figures", json=VALID_BODY).status_code == 409


def test_post_malformed_spec_is_422(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, tmp_path)
    authenticate(client, db)
    bad = {"slug": "x", "title": "x", "spec": {"viewport": {"x": [-5, 5]},
           "elements": [{"type": "banana"}]}}
    assert client.post("/api/v1/figures", json=bad).status_code == 422


def test_get_missing_is_404(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, tmp_path)
    authenticate(client, db)
    assert client.get("/api/v1/figures/999").status_code == 404
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_app/test_figure_routes.py -v`
Expected: FAIL (`No module named 'mathwizard.app.routes.figures'`).

- [ ] **Step 3: Add the dependency**

In `src/mathwizard/app/dependencies.py`, add the import and provider (mirroring `get_question_service`):

```python
from mathwizard.services.figure import FigureService
```

```python
def get_figure_service(request: Request) -> FigureService:
    return request.app.state.figure_service


FigureServiceDep = Annotated[FigureService, Depends(get_figure_service)]
```

- [ ] **Step 4: Write the router**

Create `src/mathwizard/app/routes/figures.py`:

```python
from fastapi import APIRouter, HTTPException, status

from mathwizard.app.auth import CurrentUserDep
from mathwizard.app.dependencies import FigureServiceDep
from mathwizard.exceptions import DuplicateFigureSlugError, FigureNotFoundError
from mathwizard.models.figure import (
    FigureCreateRequest,
    FigureListResponse,
    FigureResponse,
)

router = APIRouter(prefix="/api/v1/figures", tags=["figures"])


@router.get("")
def list_figures(
    figure_service: FigureServiceDep,
    current_user: CurrentUserDep,
) -> FigureListResponse:
    return figure_service.list_figures()


@router.get("/{figure_id}")
def get_figure(
    figure_id: int,
    figure_service: FigureServiceDep,
    current_user: CurrentUserDep,
) -> FigureResponse:
    try:
        return figure_service.get_figure(figure_id)
    except FigureNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("", status_code=status.HTTP_201_CREATED)
def create_figure(
    body: FigureCreateRequest,
    figure_service: FigureServiceDep,
    current_user: CurrentUserDep,
) -> FigureResponse:
    try:
        return figure_service.create_figure(body)
    except DuplicateFigureSlugError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
```

- [ ] **Step 5: Wire into the app**

In `src/mathwizard/app/main.py`: add imports, register the service in `lifespan`, include the router.

```python
from mathwizard.app.routes.figures import router as figures_router
from mathwizard.services.figure import FigureService
```

Inside `lifespan`, after `app.state.question_service = QuestionService(db)`:

```python
    app.state.figure_service = FigureService(db)
```

After `app.include_router(practice_router)`:

```python
app.include_router(figures_router)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/test_app/test_figure_routes.py -v`
Expected: PASS (5 tests).

- [ ] **Step 7: Commit**

```bash
git add src/mathwizard/app/dependencies.py src/mathwizard/app/routes/figures.py src/mathwizard/app/main.py tests/test_app/test_figure_routes.py
git commit -m "feat: add figures API router and wiring"
```

---

### Task 6: Seed corpus + bootstrap + CLI

**Files:**
- Modify: `src/mathwizard/settings.py`
- Modify: `src/mathwizard/services/bootstrap.py`
- Modify: `src/mathwizard/cli.py`
- Create: `data/questions/figures/parabool.yaml`, `data/questions/figures/lijn.yaml`, `data/questions/figures/derdegraads.yaml`
- Test: `tests/test_bootstrap_figures.py`

**Interfaces:**
- Consumes: `DBClient.upsert_figure` (Task 2), `DBClient.list_figures` (Task 2), `Settings` (existing).
- Produces: `Settings.figures_dir` property; `BootstrapService.seed_figures()`; CLI `seed-figures`.

- [ ] **Step 1: Add the settings property**

In `src/mathwizard/settings.py`, add after the `practice_dir` property:

```python
    @property
    def figures_dir(self) -> Path:
        return self.data_dir / "questions" / "figures"
```

- [ ] **Step 2: Create the sample corpus**

Create `data/questions/figures/parabool.yaml`:

```yaml
slug: parabool
title: Parabool y = x^2
description: Standaardparabool
spec:
  viewport:
    x: [-5, 5]
    y: [-1, 10]
  show_grid: true
  x_label: x
  y_label: y
  elements:
  - type: functionGraph
    fn: x^2
```

Create `data/questions/figures/lijn.yaml`:

```yaml
slug: lijn
title: Rechte lijn y = 2x - 1
description: Lineaire functie
spec:
  viewport:
    x: [-5, 5]
    y: [-5, 5]
  show_grid: true
  x_label: x
  y_label: y
  elements:
  - type: functionGraph
    fn: 2*x - 1
```

Create `data/questions/figures/derdegraads.yaml`:

```yaml
slug: derdegraads
title: Derdegraadsfunctie y = x^3 - 3x
description: Kubische functie met twee toppen
spec:
  viewport:
    x: [-3, 3]
    y: [-5, 5]
  show_grid: true
  x_label: x
  y_label: y
  elements:
  - type: functionGraph
    fn: x^3 - 3*x
```

- [ ] **Step 3: Write the failing test**

Create `tests/test_bootstrap_figures.py`:

```python
from pathlib import Path

import yaml

from mathwizard.db.client import DBClient
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import Settings


def write_figure(figures_dir: Path, slug: str, fn: str) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    (figures_dir / f"{slug}.yaml").write_text(
        yaml.safe_dump(
            {
                "slug": slug,
                "title": slug.title(),
                "spec": {
                    "viewport": {"x": [-5, 5], "y": [-5, 5]},
                    "elements": [{"type": "functionGraph", "fn": fn}],
                },
            }
        )
    )


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'boot.db'}",
        repo_root=tmp_path,
    )


def test_seed_figures_loads_yaml(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    write_figure(settings.figures_dir, "parabool", "x^2")
    db = DBClient(settings.database_url)

    BootstrapService(db, settings).seed_figures()

    figures = db.list_figures()
    assert [f.slug for f in figures] == ["parabool"]
    assert figures[0].spec["elements"][0]["fn"] == "x^2"


def test_seed_figures_is_idempotent(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    write_figure(settings.figures_dir, "parabool", "x^2")
    db = DBClient(settings.database_url)
    service = BootstrapService(db, settings)

    service.seed_figures()
    service.seed_figures()

    assert len(db.list_figures()) == 1


def test_seed_figures_no_dir_is_noop(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    db = DBClient(settings.database_url)
    BootstrapService(db, settings).seed_figures()
    assert db.list_figures() == []
```

- [ ] **Step 4: Run test to verify it fails**

Run: `uv run pytest tests/test_bootstrap_figures.py -v`
Expected: FAIL (`BootstrapService` has no attribute `seed_figures`).

- [ ] **Step 5: Implement `seed_figures`**

In `src/mathwizard/services/bootstrap.py`, add a loader helper near `_load_practice_yaml`:

```python
def _load_figure_yaml(figures_dir: Path) -> list[dict]:
    figures = []
    for f in sorted(figures_dir.glob("*.yaml")):
        with f.open() as fh:
            figures.append(yaml.safe_load(fh))
    return figures
```

Add the method to `BootstrapService`:

```python
    def seed_figures(self) -> None:
        figures_dir = self.settings.figures_dir
        if not figures_dir.exists():
            return
        for fig in _load_figure_yaml(figures_dir):
            self.db.upsert_figure(
                slug=fig["slug"],
                title=fig["title"],
                spec=fig["spec"],
                description=fig.get("description"),
            )
```

Update `run_all`:

```python
    def run_all(self) -> None:
        self.seed_root_user()
        self.seed_practice_questions()
        self.seed_figures()
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/test_bootstrap_figures.py -v`
Expected: PASS (3 tests).

- [ ] **Step 7: Add the CLI command**

In `src/mathwizard/cli.py`, add after `seed_practice`:

```python
@app.command()
def seed_figures() -> None:
    """Sync figure spec YAMLs into the database (idempotent upsert)."""
    settings = get_settings()
    db = DBClient(settings.database_url)
    before = len(db.list_figures())
    BootstrapService(db, settings).seed_figures()
    after = len(db.list_figures())
    db.engine.dispose()
    rprint(
        f"[green]Figure sync complete.[/green] "
        f"{after} figures in DB (+{after - before} new)."
    )
```

- [ ] **Step 8: Verify the CLI runs**

Run: `uv run python -m mathwizard.cli seed-figures`
Expected: `Figure sync complete. 3 figures in DB (+3 new).` (first run; re-running shows `+0 new`).

- [ ] **Step 9: Commit**

```bash
git add src/mathwizard/settings.py src/mathwizard/services/bootstrap.py src/mathwizard/cli.py data/questions/figures tests/test_bootstrap_figures.py
git commit -m "feat: seed figures from YAML via bootstrap and CLI"
```

---

### Task 7: Frontend types + `FigureView` (Mafs + mathjs)

**Files:**
- Modify: `frontend/package.json` (via npm)
- Modify: `frontend/src/types/api.ts`
- Create: `frontend/src/components/FigureView.tsx`
- Create: `frontend/src/components/FigureView.css`

**Interfaces:**
- Consumes: figure JSON shape from the API (Task 5).
- Produces: TS types `FigureElement`, `FigureSpec`, `FigureSummary`, `FigureResponse`, `FigureListResponse`; component `FigureView({ spec }: { spec: FigureSpec })`.

- [ ] **Step 1: Install dependencies**

Run: `cd frontend && npm install mafs mathjs`
Expected: `package.json` `dependencies` now include `mafs` and `mathjs`; `npm install` exits 0.

- [ ] **Step 2: Add TypeScript types**

Append to `frontend/src/types/api.ts`:

```typescript
export interface FunctionGraphElement {
  type: "functionGraph";
  fn: string;
  domain?: [number, number] | null;
  color?: string | null;
}

export type FigureElement = FunctionGraphElement;

export interface FigureViewport {
  x: [number, number];
  y?: [number, number] | null;
}

export interface FigureSpec {
  viewport: FigureViewport;
  show_grid: boolean;
  x_label: string;
  y_label: string;
  elements: FigureElement[];
}

export interface FigureSummary {
  id: number;
  slug: string;
  title: string;
  question_id?: number | null;
  part_id?: number | null;
}

export interface FigureResponse extends FigureSummary {
  description?: string | null;
  spec: FigureSpec;
}

export interface FigureListResponse {
  figures: FigureSummary[];
}
```

- [ ] **Step 3: Write `FigureView`**

Create `frontend/src/components/FigureView.tsx`:

```tsx
import { Mafs, Coordinates, Plot } from 'mafs'
import { compile } from 'mathjs'
import 'mafs/core.css'
import type { FigureSpec } from '../types/api'
import './FigureView.css'

const DEFAULT_Y: [number, number] = [-10, 10]
const DEFAULT_COLOR = '#2f5fed'

interface FigureViewProps {
  spec: FigureSpec
}

export default function FigureView({ spec }: FigureViewProps) {
  const y = spec.viewport.y ?? DEFAULT_Y

  let plots: React.ReactNode
  try {
    plots = spec.elements.map((element, i) => {
      const node = compile(element.fn)
      const fn = (x: number) => node.evaluate({ x }) as number
      return (
        <Plot.OfX key={i} y={fn} color={element.color ?? DEFAULT_COLOR} />
      )
    })
  } catch {
    return <div className="figure-error">Kon figuur niet tekenen</div>
  }

  return (
    <div className="figure-view">
      <Mafs viewBox={{ x: spec.viewport.x, y }} preserveAspectRatio={false}>
        {spec.show_grid && <Coordinates.Cartesian />}
        {plots}
      </Mafs>
    </div>
  )
}
```

- [ ] **Step 4: Write the component styles**

Create `frontend/src/components/FigureView.css`:

```css
.figure-view {
  width: 100%;
  max-width: 480px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(47, 95, 237, 0.15);
  box-shadow: 0 4px 16px rgba(47, 95, 237, 0.08);
}

.figure-error {
  padding: 1rem;
  color: #b00020;
  font-style: italic;
}
```

- [ ] **Step 5: Verify the frontend builds**

Run: `cd frontend && npm run build`
Expected: `tsc -b && vite build` completes with exit 0 (no type errors from the new types/component).

- [ ] **Step 6: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/src/types/api.ts frontend/src/components/FigureView.tsx frontend/src/components/FigureView.css
git commit -m "feat: add FigureView component and figure types"
```

---

### Task 8: Figures gallery page + route

**Files:**
- Create: `frontend/src/pages/Figures.tsx`
- Create: `frontend/src/pages/Figures.css`
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Consumes: `FigureView` (Task 7); API `GET /api/v1/figures` and `GET /api/v1/figures/{id}` (Task 5); types from Task 7.
- Produces: a `/figures` route (auth-gated) rendering every figure via `FigureView`.

- [ ] **Step 1: Write the gallery page**

Create `frontend/src/pages/Figures.tsx`:

```tsx
import { useEffect, useState } from 'react'
import FigureView from '../components/FigureView'
import type { FigureListResponse, FigureResponse } from '../types/api'
import './Figures.css'

interface FiguresProps {
  onUnauthorized: () => void
}

export default function Figures({ onUnauthorized }: FiguresProps) {
  const [figures, setFigures] = useState<FigureResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const listResp = await fetch('/api/v1/figures', { credentials: 'include' })
        if (listResp.status === 401) {
          onUnauthorized()
          return
        }
        if (!listResp.ok) throw new Error(`HTTP ${listResp.status}`)
        const list: FigureListResponse = await listResp.json()

        const details = await Promise.all(
          list.figures.map(async (summary) => {
            const resp = await fetch(`/api/v1/figures/${summary.id}`, {
              credentials: 'include',
            })
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
            return (await resp.json()) as FigureResponse
          }),
        )
        if (!active) return
        setFigures(details)
        setLoading(false)
      } catch (e) {
        if (!active) return
        setError(String(e))
        setLoading(false)
      }
    }

    load()
    return () => {
      active = false
    }
  }, [onUnauthorized])

  return (
    <div className="page-enter figures-page">
      <header className="figures-header">
        <h1 className="figures-title">Figuren</h1>
        <p className="figures-subtitle">Testgalerij voor in-house figuren</p>
      </header>

      {loading && <div className="figures-loading">Figuren laden...</div>}
      {error && <div className="search-error">{error}</div>}

      {!loading && !error && (
        <div className="figures-grid">
          {figures.map((figure) => (
            <div key={figure.id} className="figures-card">
              <h2 className="figures-card-title">{figure.title}</h2>
              <FigureView spec={figure.spec} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Write the page styles**

Create `frontend/src/pages/Figures.css`:

```css
.figures-page {
  max-width: var(--container-max, 920px);
  margin: 0 auto;
  padding: 1.5rem;
}

.figures-title {
  font-family: var(--font-display, serif);
  margin: 0;
}

.figures-subtitle {
  color: #55607a;
  margin: 0.25rem 0 1.5rem;
}

.figures-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.figures-card {
  background: #fff;
  border-radius: 16px;
  padding: 1rem;
  box-shadow: 0 6px 20px rgba(47, 95, 237, 0.08);
}

.figures-card-title {
  font-size: 1rem;
  margin: 0 0 0.75rem;
}

.figures-loading {
  padding: 2rem;
  color: #55607a;
}
```

- [ ] **Step 3: Register the route**

In `frontend/src/App.tsx`, add the import:

```tsx
import Figures from './pages/Figures'
```

Add a route inside `<Routes>` after the `/practice/:topic` route:

```tsx
          <Route
            path="/figures"
            element={user ? <Figures onUnauthorized={handleUnauthorized} /> : <Navigate to="/login" replace state={{ from: location }} />}
          />
```

- [ ] **Step 4: Verify the frontend builds**

Run: `cd frontend && npm run build`
Expected: exit 0.

- [ ] **Step 5: Manual visual check**

Run backend (`uv run uvicorn mathwizard.app.main:app --port 8001`) and frontend (`cd frontend && npm run dev`), log in, visit `/figures`.
Expected: three cards (Parabool, Lijn, Derdegraads) each render a graph in house style; no console crash.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/Figures.tsx frontend/src/pages/Figures.css frontend/src/App.tsx
git commit -m "feat: add figures gallery page at /figures"
```

---

## Final verification

- [ ] Run the full backend suite: `uv run pytest -v` → all pass.
- [ ] Frontend build: `cd frontend && npm run build` → exit 0.
- [ ] Frontend lint: `cd frontend && npm run lint` → no new errors.
- [ ] `uv run python -m mathwizard.cli seed-figures` run twice → second run reports `+0 new`.

## Self-review notes (author)

- **Spec coverage:** Figure table (Task 1), spec contract (Task 3), separate-table storage with nullable question/part links (Task 1), GET list/GET detail/POST endpoints (Task 5), YAML seed + POST both supported (Tasks 5–6), client-side Mafs+mathjs render (Task 7), test gallery (Task 8), backend tests throughout. All design decisions map to a task.
- **Out of scope (intentionally no task):** annotations/points/lines/shaded regions/parametric/geometry, `image` fallback element, wiring figures into exam/practice cards, exam seeding, PDF parser.
- **Type consistency:** `create_figure`/`upsert_figure` signatures match between mixin (Task 2), service (Task 4), and bootstrap (Task 6); `FigureSpec`/`FigureResponse` field names match between Python (Task 3) and TS (Task 7); route paths match between router (Task 5) and frontend fetches (Task 8).
- **Open validation risk to confirm during build:** exact Mafs import surface (`Mafs`, `Coordinates`, `Plot`, `mafs/core.css`) and prop names (`viewBox`, `Plot.OfX` `y`) against the installed version — adjust in Task 7 Step 5 if the build flags them.
