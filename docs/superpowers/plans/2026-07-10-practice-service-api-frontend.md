# Question Service API Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Serve practice questions by topic through a typed question service, FastAPI endpoint, and React practice page.

**Architecture:** Add a service module that converts DB `Question` models into `QuestionListResponse` objects from a `QuestionListRequest`. Add a small DB query method for topic/source filtering, initialize `QuestionService` in FastAPI lifespan, expose it through a service dependency, and keep route handlers dependent only on services. Update the frontend to render the new response contract with explicit topic/source/tags metadata.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, SQLModel, pytest, HTTPX/TestClient, React 19, TypeScript, Vite, oxlint.

---

## File Structure

- Modify `src/mathwizard/db/mixins/questions.py`: extend `list_questions()` with optional source/topic filtering.
- Create `src/mathwizard/models/question.py`: define `QuestionListRequest`, `QuestionPartResponse`, `QuestionResponse`, and `QuestionListResponse`.
- Create `src/mathwizard/services/question.py`: define `QuestionService` and model conversion logic.
- Create `src/mathwizard/app/dependencies.py`: define `QuestionServiceDep` using FastAPI `Annotated[..., Depends(...)]`.
- Create `src/mathwizard/app/routes/__init__.py`: mark the routes package.
- Create `src/mathwizard/app/routes/practice.py`: add `GET /api/v1/practice/{topic}`.
- Modify `src/mathwizard/app/main.py`: include the practice router.
- Create `tests/test_services/test_question.py`: test service conversion and sorting behavior.
- Create `tests/test_app/test_practice_routes.py`: test the FastAPI route contract.
- Modify `frontend/src/types/api.ts`: align frontend types to the API response.
- Modify `frontend/src/pages/Practice.tsx`: fetch and render `QuestionListResponse`.
- Modify `frontend/src/components/ExerciseCard.tsx`: render tags, numeric difficulty, source/topic metadata, and remove `exam_id`.
- Modify `frontend/src/components/ExerciseCard.css`: add refined metadata chip styling.
- Modify `frontend/src/pages/Practice.css`: add summary/filter affordance styling.

Out of scope:

- Do not build RAG/search behavior.
- Do not add write/update endpoints.
- Do not serve the built frontend from FastAPI yet.
- Do not implement database migrations for existing SQLite files.

Implementation invariants:

- Do not add fake defensive fallbacks for persisted required fields. A returned `Question` from `DBClient` must have an `id`; map it directly as `id=question.id` and let tests catch any violation.
- Keep request/response Pydantic models in `src/mathwizard/models/`, not in service modules.
- FastAPI route handlers depend on services from `app.state`, not directly on `DBClient`.

Frontend design direction:

- Preserve the current refined graph-paper MathWizard aesthetic: navy, pale blue, peach, Instrument Serif display type, and crisp white cards.
- Add metadata as small “mathematical specimen labels”: compact chips for tags, topic, and difficulty that feel like annotated workbook marginalia.
- Keep motion subtle: card expansion stays smooth; metadata chips should not introduce distracting animation.
- Avoid generic dashboard styling. No purple gradients, generic pill soup, or overbuilt filters.

---

### Task 1: Add Question Filtering Support

**Files:**
- Modify: `src/mathwizard/db/mixins/questions.py`
- Test: `tests/test_services/test_question.py`

- [ ] **Step 1: Write failing DB/service-facing query test**

Create `tests/test_services/test_question.py` with this initial content:

```python
from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'practice.db'}")


def seed_question(
    db: DBClient,
    *,
    topic: str,
    title: str,
    source: QuestionSource = QuestionSource.PRACTICE,
    difficulty: int | None = None,
    exam_id: str | None = None,
) -> None:
    db.create_question(
        title=title,
        stem=f"Stem for {title}",
        parts=[{"text": f"Part for {title}", "points": 2}],
        topic=topic,
        source=source,
        tags=[topic],
        difficulty=difficulty,
        calculator_allowed=False,
        exam_id=exam_id,
    )


def test_list_questions_filters_source_and_topic(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_question(db, topic="derivatives", title="Practice derivative")
    seed_question(db, topic="goniometry", title="Practice goniometry")
    seed_question(
        db,
        topic="derivatives",
        title="Exam derivative",
        source=QuestionSource.EXAM,
        exam_id="EXAM-1",
    )

    questions = db.list_questions(
        topic="derivatives",
        source=QuestionSource.PRACTICE,
    )

    assert [q.title for q in questions] == ["Practice derivative"]
    assert questions[0].topic == "derivatives"
    assert questions[0].source == QuestionSource.PRACTICE
    assert questions[0].parts[0].text == "Part for Practice derivative"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run --extra dev pytest tests/test_services/test_question.py::test_list_questions_filters_source_and_topic -v
```

Expected: FAIL with `TypeError` because `DBClient.list_questions()` does not accept `topic` or `source` yet.

- [ ] **Step 3: Extend `list_questions`**

Replace `list_questions()` in `src/mathwizard/db/mixins/questions.py` with:

```python
    def list_questions(
        self,
        *,
        topic: str | None = None,
        source: QuestionSource | None = None,
    ) -> list[Question]:
        statement = select(Question).order_by(Question.id)
        if topic is not None:
            statement = statement.where(Question.topic == topic)
        if source is not None:
            statement = statement.where(Question.source == source)

        with DBSession(self.engine) as session:
            questions = session.exec(statement).all()
            for question in questions:
                _ = question.parts
            return list(questions)
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run --extra dev pytest tests/test_services/test_question.py::test_list_questions_filters_source_and_topic -v
```

Expected: PASS.

- [ ] **Step 5: Commit Task 1**

```bash
git add src/mathwizard/db/mixins/questions.py tests/test_services/test_question.py
git commit -m "Add question topic query"
```

---

### Task 2: Add Question Service Request/Response Conversion

**Files:**
- Create: `src/mathwizard/models/question.py`
- Create: `src/mathwizard/services/question.py`
- Modify: `tests/test_services/test_question.py`

- [ ] **Step 1: Extend service tests before implementation**

Append these tests to `tests/test_services/test_question.py`:

```python
from mathwizard.models.question import QuestionListRequest
from mathwizard.services.question import QuestionService


def test_list_questions_returns_response_models_sorted_by_difficulty(
    tmp_path: Path,
) -> None:
    db = make_db(tmp_path)
    seed_question(db, topic="derivatives", title="Hard", difficulty=5)
    seed_question(db, topic="derivatives", title="Easy", difficulty=1)
    seed_question(db, topic="derivatives", title="Medium", difficulty=3)
    service = QuestionService(db)

    response = service.list_questions(
        QuestionListRequest(
            source=QuestionSource.PRACTICE,
            topic="derivatives",
        ),
    )

    assert response.topic == "derivatives"
    assert response.source == QuestionSource.PRACTICE
    assert [question.title for question in response.questions] == [
        "Easy",
        "Medium",
        "Hard",
    ]
    assert [question.number for question in response.questions] == [1, 2, 3]
    assert response.questions[0].source == QuestionSource.PRACTICE
    assert response.questions[0].tags == ["derivatives"]
    assert response.questions[0].question_text == "Stem for Easy"
    assert response.questions[0].parts == ["Part for Easy"]
    assert response.questions[0].max_marks == 2
    assert response.questions[0].calculator_allowed is False
    assert response.questions[0].difficulty == 1
    assert response.questions[0].figure_images == []


def test_list_questions_can_preserve_database_order(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_question(db, topic="derivatives", title="Hard", difficulty=5)
    seed_question(db, topic="derivatives", title="Easy", difficulty=1)
    service = QuestionService(db)

    response = service.list_questions(
        QuestionListRequest(
            source=QuestionSource.PRACTICE,
            topic="derivatives",
            sort_by_difficulty=False,
        ),
    )

    assert [question.title for question in response.questions] == ["Hard", "Easy"]
    assert [question.number for question in response.questions] == [1, 2]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run --extra dev pytest tests/test_services/test_question.py -v
```

Expected: FAIL because `mathwizard.services.question` and `mathwizard.models.question` do not exist yet.

- [ ] **Step 3: Implement service models and conversion**

Create `src/mathwizard/models/question.py` with this content:

```python
from pydantic import BaseModel, Field

from mathwizard.enums import QuestionSource


class QuestionListRequest(BaseModel):
    source: QuestionSource
    topic: str | None = None
    sort_by_difficulty: bool = True


class QuestionPartResponse(BaseModel):
    label: str
    text: str
    points: int


class QuestionResponse(BaseModel):
    id: int
    number: int
    source: QuestionSource
    topic: str
    tags: list[str] = Field(default_factory=list)
    title: str
    question_text: str
    parts: list[str] = Field(default_factory=list)
    part_details: list[QuestionPartResponse] = Field(default_factory=list)
    max_marks: int
    calculator_allowed: bool | None = None
    difficulty: int | None = None
    figure_images: list[str] = Field(default_factory=list)


class QuestionListResponse(BaseModel):
    source: QuestionSource
    topic: str | None = None
    questions: list[QuestionResponse]
```

Create `src/mathwizard/services/question.py` with this content:

```python
from mathwizard.db.client import DBClient
from mathwizard.models.db import Question
from mathwizard.models.question import (
    QuestionListRequest,
    QuestionListResponse,
    QuestionResponse,
    QuestionPartResponse,
)

def _sort_key(question: Question) -> tuple[bool, int, str]:
    return (
        question.difficulty is None,
        question.difficulty if question.difficulty is not None else 0,
        question.title,
    )


def _question_to_response(
    question: Question,
    *,
    number: int,
) -> QuestionResponse:
    return QuestionResponse(
        id=question.id,
        number=number,
        source=question.source,
        topic=question.topic,
        tags=question.tags,
        title=question.title,
        question_text=question.stem,
        parts=[part.text for part in question.parts],
        part_details=[
            QuestionPartResponse(
                label=part.label,
                text=part.text,
                points=part.points,
            )
            for part in question.parts
        ],
        max_marks=sum(part.points for part in question.parts),
        calculator_allowed=question.calculator_allowed,
        difficulty=question.difficulty,
        figure_images=[],
    )


class QuestionService:
    def __init__(self, db: DBClient) -> None:
        self.db = db

    def list_questions(
        self,
        request: QuestionListRequest,
    ) -> QuestionListResponse:
        questions = self.db.list_questions(
            topic=request.topic,
            source=request.source,
        )
        if request.sort_by_difficulty:
            questions = sorted(questions, key=_sort_key)

        return QuestionListResponse(
            source=request.source,
            topic=request.topic,
            questions=[
                _question_to_response(question, number=i)
                for i, question in enumerate(questions, start=1)
            ],
        )
```

- [ ] **Step 4: Run service tests to verify they pass**

Run:

```bash
uv run --extra dev pytest tests/test_services/test_question.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit Task 2**

```bash
git add src/mathwizard/models/question.py src/mathwizard/services/question.py tests/test_services/test_question.py
git commit -m "Add question service responses"
```

---

### Task 3: Add FastAPI Practice Route

**Files:**
- Create: `src/mathwizard/app/dependencies.py`
- Create: `src/mathwizard/app/routes/__init__.py`
- Create: `src/mathwizard/app/routes/practice.py`
- Modify: `src/mathwizard/app/main.py`
- Create: `tests/test_app/test_practice_routes.py`

- [ ] **Step 1: Write failing route tests**

Create `tests/test_app/test_practice_routes.py` with this content:

```python
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mathwizard.app.routes.practice import router
from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource
from mathwizard.services.question import QuestionService


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'api.db'}")


def make_client(db: DBClient) -> TestClient:
    app = FastAPI()
    app.state.question_service = QuestionService(db)
    app.include_router(router)
    return TestClient(app)


def seed_question(
    db: DBClient,
    *,
    topic: str,
    title: str,
    difficulty: int,
) -> None:
    db.create_question(
        title=title,
        stem=f"Stem for {title}",
        parts=[{"text": f"Part for {title}", "points": difficulty}],
        topic=topic,
        source=QuestionSource.PRACTICE,
        tags=["practice", topic],
        difficulty=difficulty,
        calculator_allowed=False,
    )


def test_get_practice_topic_returns_service_response(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_question(db, topic="derivatives", title="Hard", difficulty=5)
    seed_question(db, topic="derivatives", title="Easy", difficulty=1)
    client = make_client(db)

    response = client.get("/api/v1/practice/derivatives")

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "practice"
    assert data["topic"] == "derivatives"
    assert [question["title"] for question in data["questions"]] == ["Easy", "Hard"]
    assert data["questions"][0]["source"] == "practice"
    assert data["questions"][0]["tags"] == ["practice", "derivatives"]
    assert "exam_id" not in data["questions"][0]


def test_get_practice_topic_can_disable_difficulty_sort(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_question(db, topic="derivatives", title="Hard", difficulty=5)
    seed_question(db, topic="derivatives", title="Easy", difficulty=1)
    client = make_client(db)

    response = client.get("/api/v1/practice/derivatives?sort_by_difficulty=false")

    assert response.status_code == 200
    data = response.json()
    assert [question["title"] for question in data["questions"]] == ["Hard", "Easy"]
```

- [ ] **Step 2: Run route tests to verify they fail**

Run:

```bash
uv run --extra dev pytest tests/test_app/test_practice_routes.py -v
```

Expected: FAIL because `mathwizard.app.routes.practice` does not exist yet.

- [ ] **Step 3: Add FastAPI service dependency**

Create `src/mathwizard/app/dependencies.py` with this content:

```python
from typing import Annotated

from fastapi import Depends
from fastapi import Request

from mathwizard.services.question import QuestionService


def get_question_service(request: Request) -> QuestionService:
    return request.app.state.question_service


QuestionServiceDep = Annotated[QuestionService, Depends(get_question_service)]
```

- [ ] **Step 4: Add practice router**

Create `src/mathwizard/app/routes/__init__.py` as an empty file.

Create `src/mathwizard/app/routes/practice.py` with this content:

```python
from typing import Annotated

from fastapi import APIRouter, Query

from mathwizard.app.dependencies import QuestionServiceDep
from mathwizard.enums import QuestionSource
from mathwizard.models.question import (
    QuestionListRequest,
    QuestionListResponse,
)


router = APIRouter(prefix="/api/v1/practice", tags=["practice"])


@router.get("/{topic}")
def get_practice_topic(
    topic: str,
    question_service: QuestionServiceDep,
    sort_by_difficulty: Annotated[bool, Query()] = True,
) -> QuestionListResponse:
    return question_service.list_questions(
        QuestionListRequest(
            source=QuestionSource.PRACTICE,
            topic=topic,
            sort_by_difficulty=sort_by_difficulty,
        ),
    )
```

- [ ] **Step 5: Include router in the app**

Modify `src/mathwizard/app/main.py` imports and app setup:

```python
from fastapi import FastAPI

from mathwizard.app.routes.practice import router as practice_router
from mathwizard.settings import get_settings
from mathwizard.db.client import DBClient
from mathwizard.services.question import QuestionService
import mathwizard.services.bootstrap as bootstrap
```

Then add the service during lifespan after bootstrap:

```python
    app.state.question_service = QuestionService(app.state.db)
```

Then add this immediately after app creation:

```python
app = FastAPI(title="MathWizard", version="0.1.0", lifespan=lifespan)
app.include_router(practice_router)
```

- [ ] **Step 6: Run route tests**

Run:

```bash
uv run --extra dev pytest tests/test_app/test_practice_routes.py -v
```

Expected: PASS.

- [ ] **Step 7: Run backend tests together**

Run:

```bash
uv run --extra dev pytest tests/test_services/test_question.py tests/test_app/test_practice_routes.py tests/test_db_questions.py tests/test_bootstrap_questions.py -v
```

Expected: PASS.

- [ ] **Step 8: Commit Task 3**

```bash
git add src/mathwizard/app/dependencies.py src/mathwizard/app/routes/__init__.py src/mathwizard/app/routes/practice.py src/mathwizard/app/main.py tests/test_app/test_practice_routes.py
git commit -m "Add practice API route"
```

---

### Task 4: Update Frontend API Contract and Rendering

**Files:**
- Modify: `frontend/src/types/api.ts`
- Modify: `frontend/src/pages/Practice.tsx`
- Modify: `frontend/src/components/ExerciseCard.tsx`
- Modify: `frontend/src/components/ExerciseCard.css`
- Modify: `frontend/src/pages/Practice.css`

- [ ] **Step 1: Update frontend types**

Modify the practice types in `frontend/src/types/api.ts`:

```typescript
export type QuestionSource = 'practice' | 'exam' | 'generated';

export interface QuestionPart {
  label: string;
  text: string;
  points: number;
}

export interface QuestionResponse {
  id: number;
  number: number;
  source: QuestionSource;
  topic: string;
  tags: string[];
  title: string;
  question_text: string;
  parts: string[];
  part_details: QuestionPart[];
  max_marks: number;
  calculator_allowed?: boolean | null;
  difficulty?: number | null;
  figure_images: string[];
}

export interface QuestionListResponse {
  source: QuestionSource;
  topic?: string | null;
  questions: QuestionResponse[];
}
```

Keep the existing search-related interfaces above this block.

- [ ] **Step 2: Run frontend build to expose type errors**

Run:

```bash
cd frontend && npm run build
```

Expected: PASS or reveal type errors. If it passes, continue; the previous JSX is mostly compatible with the new response shape, so frontend verification may not go red until the rendering changes are applied.

- [ ] **Step 3: Update Practice page rendering**

Modify `frontend/src/pages/Practice.tsx`:

```typescript
const meta = topic ? TOPIC_META[topic] : null
const questions = practiceSet?.questions ?? []
const totalMarks = questions.reduce((sum, ex) => sum + ex.max_marks, 0)
const tagCount = new Set(questions.flatMap(ex => ex.tags)).size
```

Inside the header after the subtitle, add:

```tsx
{practiceSet && !loading && (
  <div className="practice-summary">
    <span>{questions.length} opgaven</span>
    <span>{totalMarks} punten</span>
    <span>{tagCount} labels</span>
  </div>
)}
```

Keep the existing loading, error, and empty states. Keep fetching `/api/v1/practice/${topic}`.

Replace the list rendering condition to use `questions`:

```tsx
{practiceSet && !loading && (
  <div className="practice-list">
    {questions.length > 0 ? (
      questions.map(question => (
        <ExerciseCard key={question.id} exercise={question} />
      ))
    ) : (
      <div className="practice-empty">
        <p>Geen oefenopgaven beschikbaar voor dit onderwerp.</p>
      </div>
    )}
  </div>
)}
```

- [ ] **Step 4: Update exercise card rendering**

Modify `frontend/src/components/ExerciseCard.tsx`:

```typescript
import type { QuestionResponse } from '../types/api'

interface ExerciseCardProps {
  exercise: QuestionResponse
}
```

```tsx
const difficultyLabel = exercise.difficulty ? `Niveau ${exercise.difficulty}` : 'Niveau onbekend'
```

Inside `.ex-card-meta`, render difficulty and tags:

```tsx
<span className="ex-badge ex-badge--difficulty">{difficultyLabel}</span>
{exercise.max_marks > 0 && (
  <span className="ex-badge ex-badge--marks">
    {exercise.max_marks}p
  </span>
)}
```

Inside the expanded body before the stem, add:

```tsx
<div className="ex-card-tags" aria-label="Opgave labels">
  <span className="ex-tag ex-tag--topic">{exercise.topic}</span>
  {exercise.tags.map(tag => (
    <span className="ex-tag" key={tag}>{tag}</span>
  ))}
</div>
```

Keep the existing MathJax rendering for `question_text` and `parts`.

- [ ] **Step 5: Add frontend styles**

Append to `frontend/src/components/ExerciseCard.css`:

```css
.ex-badge--difficulty {
  background: #f6f8fb;
  color: var(--navy);
  border: 1px solid var(--border);
}

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

Append to `frontend/src/pages/Practice.css`:

```css
.practice-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.practice-summary span {
  display: inline-flex;
  align-items: center;
  padding: 5px 11px;
  border-radius: 999px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--navy);
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 10px rgba(3, 34, 84, 0.04);
}
```

- [ ] **Step 6: Run frontend verification**

Run:

```bash
cd frontend && npm run build
```

Expected: PASS.

Run:

```bash
cd frontend && npm run lint
```

Expected: PASS.

- [ ] **Step 7: Commit Task 4**

```bash
git add frontend/src/types/api.ts frontend/src/pages/Practice.tsx frontend/src/components/ExerciseCard.tsx frontend/src/components/ExerciseCard.css frontend/src/pages/Practice.css
git commit -m "Render practice question metadata"
```

---

### Task 5: End-to-End Verification

**Files:**
- Verify backend and frontend changes.

- [ ] **Step 1: Run full Python tests**

Run:

```bash
uv run --extra dev pytest -v
```

Expected: PASS.

- [ ] **Step 2: Run frontend build and lint**

Run:

```bash
cd frontend && npm run build && npm run lint
```

Expected: PASS.

- [ ] **Step 3: Try the local API manually**

Start the backend:

```bash
uv run uvicorn mathwizard.app.main:app --reload --host 0.0.0.0 --port 8000
```

In another terminal, request:

```bash
curl "http://localhost:8000/api/v1/practice/derivatives"
```

Expected: JSON with `source: "practice"`, `topic: "derivatives"`, and a non-empty `questions` array when the local database has been freshly seeded from tracked `data/questions/practice`.

- [ ] **Step 4: Inspect final diff**

Run:

```bash
git diff --stat HEAD~4..HEAD
```

Expected: Diff is limited to DB query support, service/API route, frontend practice rendering, and tests.

- [ ] **Step 5: Commit verification fixes if needed**

If verification required code changes, commit them:

```bash
git add src tests frontend
git commit -m "Verify practice API rendering"
```

If no code changes were needed, do not create an empty commit.

---

## Self-Review

- Spec coverage: The plan adds request/response models under `src/mathwizard/models/`, a `QuestionService` conversion layer, returns practice questions by topic through a generic `QuestionListResponse`, makes difficulty sorting optional with default `true`, exposes the result through FastAPI, and updates the frontend to render the response.
- FastAPI coverage: The plan uses router-level prefix/tags, `Annotated` query/dependency patterns, return types for response validation, sync path operations for blocking work, and route handlers that depend on `QuestionServiceDep` instead of `DBClient`.
- Frontend coverage: The plan updates TypeScript types, page rendering, card rendering, and CSS while preserving the project’s existing refined math-notebook aesthetic.
- Placeholder scan: No placeholder steps remain; every code-changing step includes concrete file paths and code.
- Type consistency: Backend `QuestionListRequest` / `QuestionListResponse` live in `mathwizard.models.question` and map to frontend `QuestionListResponse`; `QuestionResponse` maps to frontend `QuestionResponse`; route handlers depend on `QuestionServiceDep`.
