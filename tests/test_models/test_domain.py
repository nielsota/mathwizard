from datetime import datetime, timedelta

from mathwizard.models.domain.figure import FigureSpec, FunctionGraph, Viewport
from mathwizard.models.domain.question import (
    Question,
    QuestionDraft,
    QuestionPart,
    QuestionSource,
)
from mathwizard.models.domain.session import AuthSession


def test_auth_session_is_active_when_not_revoked_and_not_expired() -> None:
    now = datetime(2026, 8, 17, 12, 0, 0)
    session = AuthSession(
        token="tok",
        user_id=1,
        created_at=now - timedelta(days=1),
        expires_at=now + timedelta(days=1),
    )

    assert session.is_active(now) is True


def test_auth_session_is_inactive_when_expired() -> None:
    now = datetime(2026, 8, 17, 12, 0, 0)
    session = AuthSession(
        token="tok",
        user_id=1,
        created_at=now - timedelta(days=2),
        expires_at=now - timedelta(seconds=1),
    )

    assert session.is_active(now) is False


def test_auth_session_is_inactive_when_revoked() -> None:
    now = datetime(2026, 8, 17, 12, 0, 0)
    session = AuthSession(
        token="tok",
        user_id=1,
        created_at=now - timedelta(days=1),
        expires_at=now + timedelta(days=1),
        revoked_at=now - timedelta(minutes=5),
    )

    assert session.is_active(now) is False


def test_question_draft_assigns_default_part_labels_in_order() -> None:
    draft = QuestionDraft(
        topic="derivatives",
        title="Machtsfuncties",
        stem="Bepaal de afgeleide.",
        parts=[
            {"text": "first", "points": 2},
            {"text": "second", "points": 3},
        ],
    )

    assert [part.label for part in draft.parts] == ["a", "b"]


def test_question_draft_keeps_explicit_part_labels() -> None:
    draft = QuestionDraft(
        topic="derivatives",
        title="Machtsfuncties",
        stem="Bepaal de afgeleide.",
        parts=[{"text": "first", "points": 2, "label": "x"}],
    )

    assert [part.label for part in draft.parts] == ["x"]


def test_question_max_marks_sums_part_points() -> None:
    question = Question(
        id=1,
        topic="derivatives",
        title="Machtsfuncties",
        stem="Bepaal de afgeleide.",
        source=QuestionSource.PRACTICE,
        parts=[
            QuestionPart(id=1, label="a", text="first", points=2),
            QuestionPart(id=2, label="b", text="second", points=3),
        ],
    )

    assert question.max_marks == 5


def test_question_max_marks_is_zero_without_parts() -> None:
    question = Question(
        id=1,
        topic="derivatives",
        title="Machtsfuncties",
        stem="Bepaal de afgeleide.",
        source=QuestionSource.PRACTICE,
    )

    assert question.max_marks == 0


def test_question_dump_includes_max_marks_for_response_filtering() -> None:
    question = Question(
        id=1,
        topic="derivatives",
        title="Machtsfuncties",
        stem="Bepaal de afgeleide.",
        source=QuestionSource.PRACTICE,
        parts=[QuestionPart(id=1, label="a", text="first", points=2)],
    )

    assert question.model_dump()["max_marks"] == 2


def test_figure_spec_defaults() -> None:
    spec = FigureSpec(
        viewport=Viewport(x=(-5.0, 5.0)),
        elements=[FunctionGraph(fn="x^2")],
    )

    assert spec.show_grid is True
    assert spec.x_label == "x"
    assert spec.elements[0].type == "functionGraph"
