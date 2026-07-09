# Question Model Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add first-class question metadata for `topic`, enum-backed `source`, and `tags` at the database/model layer, while keeping practice questions separate from exam identity.

**Architecture:** Store `topic` as an indexed slug, `source` as a `StrEnum`-backed field, and `tags` as a JSON list on `Question`. Thread these fields through the existing `QuestionsMixin` create/update API and the practice bootstrap seed path only; public API routes, service response schemas, and frontend contracts are intentionally left for a follow-up plan.

**Tech Stack:** Python 3.12, SQLModel, SQLAlchemy, SQLite, pytest, PyYAML.

---

## File Structure

- Create `src/mathwizard/enums.py`: define `QuestionSource` as a `StrEnum`.
- Modify `src/mathwizard/models/db.py`: add `topic`, `source`, and `tags` fields to `Question`.
- Modify `src/mathwizard/db/mixins/questions.py`: accept, persist, and update `topic`, `source`, and `tags`.
- Modify `src/mathwizard/services/bootstrap.py`: derive `topic` from `data/questions/practice/<topic>/`, seed `source=QuestionSource.PRACTICE`, seed optional YAML `tags`, and do not assign `exam_id` for practice questions.
- Create `tests/test_db_questions.py`: verify DB create/update behavior for the new fields.
- Create `tests/test_bootstrap_questions.py`: verify practice seeding derives `topic`, keeps `exam_id` empty, and persists tags.

Out of scope for this plan:

- Do not update FastAPI routes or response models.
- Do not update frontend TypeScript types or UI rendering.
- Do not build RAG or filtering behavior yet; this plan only stores metadata needed later.
- Do not add migrations; this repo currently uses `SQLModel.metadata.create_all`. Existing local SQLite files may need to be recreated after implementation.

---

### Task 1: Persist Question Metadata

**Files:**
- Create: `src/mathwizard/enums.py`
- Create: `tests/test_db_questions.py`
- Modify: `src/mathwizard/models/db.py`
- Modify: `src/mathwizard/db/mixins/questions.py`

- [ ] **Step 1: Write failing tests for create/update metadata**

Create `tests/test_db_questions.py` with this content:

```python
from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'test.db'}")


def test_create_question_persists_topic_source_and_tags(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    question = db.create_question(
        title="Machtsfuncties",
        stem="Bepaal de afgeleide.",
        parts=[{"text": r"\(f(x)=x^2\)", "points": 2}],
        topic="derivatives",
        source=QuestionSource.PRACTICE,
        tags=["differentieren", "machtsregel"],
        calculator_allowed=False,
        difficulty=1,
    )

    assert question.id is not None
    saved = db.get_question(question.id)

    assert saved.topic == "derivatives"
    assert saved.source == QuestionSource.PRACTICE
    assert saved.tags == ["differentieren", "machtsregel"]
    assert saved.exam_id is None
    assert saved.calculator_allowed is False
    assert saved.difficulty == 1
    assert len(saved.parts) == 1
    assert saved.parts[0].label == "a"
    assert saved.parts[0].text == r"\(f(x)=x^2\)"
    assert saved.parts[0].points == 2


def test_update_question_can_change_topic_source_tags_and_exam_id(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    question = db.create_question(
        title="Machtsfuncties",
        stem="Bepaal de afgeleide.",
        parts=[{"text": r"\(f(x)=x^2\)", "points": 2}],
        topic="derivatives",
        source=QuestionSource.PRACTICE,
        tags=["differentieren"],
    )
    assert question.id is not None

    updated = db.update_question(
        question.id,
        topic="goniometrie",
        source=QuestionSource.EXAM,
        tags=["sinus", "vergelijkingen"],
        exam_id="VWO-2024-I-01",
    )

    assert updated.topic == "goniometrie"
    assert updated.source == QuestionSource.EXAM
    assert updated.tags == ["sinus", "vergelijkingen"]
    assert updated.exam_id == "VWO-2024-I-01"
    assert updated.title == "Machtsfuncties"
    assert updated.parts[0].text == r"\(f(x)=x^2\)"
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/test_db_questions.py -v
```

Expected: FAIL because `mathwizard.enums.QuestionSource` and the new `QuestionsMixin.create_question()` metadata arguments do not exist yet.

- [ ] **Step 3: Create the source enum**

Create `src/mathwizard/enums.py` with this content:

```python
from enum import StrEnum


class QuestionSource(StrEnum):
    PRACTICE = "practice"
    EXAM = "exam"
    GENERATED = "generated"
```

- [ ] **Step 4: Add metadata fields to `Question`**

Modify `src/mathwizard/models/db.py` so its imports and `Question` class match this shape:

```python
from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field, Relationship

from mathwizard.enums import QuestionSource


class Question(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    topic: str = Field(index=True)
    source: QuestionSource = Field(default=QuestionSource.PRACTICE, index=True)
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    exam_id: str | None = None
    title: str
    stem: str
    calculator_allowed: bool | None = None
    difficulty: int | None = None

    parts: list["QuestionPart"] = Relationship(
        back_populates="question",
        cascade_delete=True,
    )
```

Keep `User` and `QuestionPart` in the same file unchanged.

- [ ] **Step 5: Thread metadata through `QuestionsMixin.create_question`**

Modify `src/mathwizard/db/mixins/questions.py` to import `QuestionSource`:

```python
from mathwizard.enums import QuestionSource
```

Then update the start of `create_question`:

```python
    def create_question(
        self,
        title: str,
        stem: str,
        parts: list[dict],
        *,
        topic: str,
        source: QuestionSource = QuestionSource.PRACTICE,
        tags: list[str] | None = None,
        exam_id: str | None = None,
        calculator_allowed: bool | None = None,
        difficulty: int | None = None,
    ) -> Question:
        question = Question(
            title=title,
            stem=stem,
            topic=topic,
            source=source,
            tags=tags or [],
            exam_id=exam_id,
            calculator_allowed=calculator_allowed,
            difficulty=difficulty,
        )
```

Keep the existing session, part creation, commit, and refresh logic unchanged.

- [ ] **Step 6: Thread metadata through `QuestionsMixin.update_question`**

Modify the `update_question` signature in `src/mathwizard/db/mixins/questions.py`:

```python
    def update_question(
        self,
        question_id: int,
        *,
        title: str | None = None,
        stem: str | None = None,
        topic: str | None = None,
        source: QuestionSource | None = None,
        tags: list[str] | None = None,
        exam_id: str | None = None,
        calculator_allowed: bool | None = None,
        difficulty: int | None = None,
        parts: list[dict] | None = None,
    ) -> Question:
```

Then add these assignments after the existing `stem` update:

```python
            if topic is not None:
                question.topic = topic
            if source is not None:
                question.source = source
            if tags is not None:
                question.tags = tags
```

Keep all existing update behavior for `exam_id`, `calculator_allowed`, `difficulty`, and `parts`.

- [ ] **Step 7: Run tests to verify Task 1 passes**

Run:

```bash
uv run pytest tests/test_db_questions.py -v
```

Expected: PASS with both tests passing.

- [ ] **Step 8: Commit Task 1**

```bash
git add src/mathwizard/enums.py tests/test_db_questions.py src/mathwizard/models/db.py src/mathwizard/db/mixins/questions.py
git commit -m "Add question metadata fields"
```

---

### Task 2: Seed Practice Metadata

**Files:**
- Create: `tests/test_bootstrap_questions.py`
- Modify: `src/mathwizard/services/bootstrap.py`

- [ ] **Step 1: Write failing bootstrap test**

Create `tests/test_bootstrap_questions.py` with this content:

```python
from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource
from mathwizard.services.bootstrap import seed_practice_questions


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'bootstrap.db'}")


def test_seed_practice_questions_uses_folder_name_as_topic(tmp_path: Path) -> None:
    practice_dir = tmp_path / "questions" / "practice"
    topic_dir = practice_dir / "derivatives"
    topic_dir.mkdir(parents=True)
    (topic_dir / "p1.yaml").write_text(
        "\n".join([
            "title: Machtsfuncties",
            "stem: Bepaal de afgeleide van de volgende functies.",
            "calculator_allowed: false",
            "difficulty: 1",
            "tags:",
            "- differentieren",
            "- machtsregel",
            "parts:",
            "- text: \\\\(f(x)=x^2\\\\)",
            "  points: 2",
            "",
        ])
    )
    db = make_db(tmp_path)

    seed_practice_questions(db, practice_dir)

    questions = db.list_questions()
    assert len(questions) == 1
    assert questions[0].topic == "derivatives"
    assert questions[0].source == QuestionSource.PRACTICE
    assert questions[0].tags == ["differentieren", "machtsregel"]
    assert questions[0].exam_id is None
    assert questions[0].title == "Machtsfuncties"
    assert questions[0].parts[0].points == 2


def test_seed_practice_questions_is_idempotent_without_exam_id(tmp_path: Path) -> None:
    practice_dir = tmp_path / "questions" / "practice"
    topic_dir = practice_dir / "derivatives"
    topic_dir.mkdir(parents=True)
    (topic_dir / "p1.yaml").write_text(
        "\n".join([
            "title: Machtsfuncties",
            "stem: Bepaal de afgeleide.",
            "parts:",
            "- text: \\\\(f(x)=x^2\\\\)",
            "  points: 2",
            "",
        ])
    )
    db = make_db(tmp_path)

    seed_practice_questions(db, practice_dir)
    seed_practice_questions(db, practice_dir)

    questions = db.list_questions()
    assert len(questions) == 1
    assert questions[0].topic == "derivatives"
    assert questions[0].title == "Machtsfuncties"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_bootstrap_questions.py -v
```

Expected: FAIL because `seed_practice_questions()` still deduplicates with `exam_id` and does not pass `topic`, `source`, or `tags` to `db.create_question()` yet.

- [ ] **Step 3: Tighten the YAML type definition**

Modify the imports and `ExerciseYaml` definition in `src/mathwizard/services/bootstrap.py`:

```python
from pathlib import Path
from typing import NotRequired, TypedDict

import yaml  # type: ignore[import-untyped]

from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource


class ExerciseYaml(TypedDict):
    title: str
    stem: str
    parts: list[dict]
    tags: NotRequired[list[str]]
    calculator_allowed: NotRequired[bool | None]
    difficulty: NotRequired[int | None]
```

- [ ] **Step 4: Replace `exam_id` practice deduplication**

Inside `seed_practice_questions`, replace:

```python
    existing_exam_ids = {q.exam_id for q in db.list_questions()}
```

with:

```python
    existing_practice_keys = {
        (q.topic, q.title)
        for q in db.list_questions()
        if q.source == QuestionSource.PRACTICE
    }
```

Then replace the old per-exercise duplicate guard:

```python
            if ex.get("exam_id") in existing_exam_ids:
                continue
```

with:

```python
            practice_key = (topic_dir.name, ex["title"])
            if practice_key in existing_practice_keys:
                continue
```

- [ ] **Step 5: Pass folder topic, practice source, and tags during seeding**

Modify the `db.create_question(...)` call inside `seed_practice_questions`:

```python
            db.create_question(
                title=ex["title"],
                stem=ex["stem"],
                parts=ex["parts"],
                topic=topic_dir.name,
                source=QuestionSource.PRACTICE,
                tags=ex.get("tags", []),
                calculator_allowed=ex.get("calculator_allowed"),
                difficulty=ex.get("difficulty"),
            )
            existing_practice_keys.add(practice_key)
```

Do not pass `exam_id` for practice questions.

- [ ] **Step 6: Run bootstrap test to verify it passes**

Run:

```bash
uv run pytest tests/test_bootstrap_questions.py -v
```

Expected: PASS with both bootstrap tests passing.

- [ ] **Step 7: Run DB and bootstrap tests together**

Run:

```bash
uv run pytest tests/test_db_questions.py tests/test_bootstrap_questions.py -v
```

Expected: PASS with all four tests passing.

- [ ] **Step 8: Commit Task 2**

```bash
git add tests/test_bootstrap_questions.py src/mathwizard/services/bootstrap.py
git commit -m "Seed practice questions with metadata"
```

---

### Task 3: Run Focused Project Checks

**Files:**
- Verify: `src/mathwizard/enums.py`
- Verify: `src/mathwizard/models/db.py`
- Verify: `src/mathwizard/db/mixins/questions.py`
- Verify: `src/mathwizard/services/bootstrap.py`
- Verify: `tests/test_db_questions.py`
- Verify: `tests/test_bootstrap_questions.py`

- [ ] **Step 1: Run focused tests**

Run:

```bash
uv run pytest tests/test_db_questions.py tests/test_bootstrap_questions.py -v
```

Expected: PASS with all four tests passing.

- [ ] **Step 2: Run broader Python test suite**

Run:

```bash
uv run pytest -v
```

Expected: PASS, or only unrelated pre-existing failures. If unrelated failures appear, capture the failing test names and error messages before proceeding.

- [ ] **Step 3: Run Python lint/type-adjacent check if available**

Run:

```bash
uv run ruff check src/mathwizard tests
```

Expected: PASS if Ruff is configured in this environment. If `ruff` is not installed or not configured, record the exact command output and do not treat that as an implementation failure.

- [ ] **Step 4: Inspect git diff**

Run:

```bash
git diff -- src/mathwizard/enums.py src/mathwizard/models/db.py src/mathwizard/db/mixins/questions.py src/mathwizard/services/bootstrap.py tests/test_db_questions.py tests/test_bootstrap_questions.py
```

Expected: Diff only includes the enum, model, DB mixin, bootstrap seeding path, and focused tests described in this plan.

- [ ] **Step 5: Commit verification note if changes were needed**

If Task 3 required code changes, commit them:

```bash
git add src/mathwizard/enums.py src/mathwizard/models/db.py src/mathwizard/db/mixins/questions.py src/mathwizard/services/bootstrap.py tests/test_db_questions.py tests/test_bootstrap_questions.py
git commit -m "Verify question metadata update"
```

If Task 3 required no code changes, do not create an empty commit.

---

## Follow-Up Plan Boundary

The next plan should update consumers of `Question.topic`, `Question.source`, and `Question.tags`, including:

- FastAPI practice/search routes and response schemas.
- Frontend `PracticeExercise` and related TypeScript types.
- UI filters or labels that display topic/source/tags.
- Service-layer search/query methods that filter by topic/source/tags.
- RAG indexing decisions for tags and topic weighting.

This plan intentionally stops before those changes so the database contract can land independently.

---

## Self-Review

- Spec coverage: The plan adds `topic`, enum-backed `source`, and `tags`; persists them through DB create/update; derives practice `topic` from the folder slug; keeps practice `exam_id` empty; and makes practice seeding idempotent without `exam_id`. API, service response, frontend, filtering, and RAG work are explicitly deferred.
- Placeholder scan: No placeholder steps remain; every code-changing step includes concrete code and every verification step includes an exact command and expected result.
- Type consistency: The model fields are `topic: str`, `source: QuestionSource`, and `tags: list[str]`; `create_question`, `update_question`, tests, and bootstrap all use those same names.
