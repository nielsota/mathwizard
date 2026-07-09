from pathlib import Path

from sqlalchemy import text

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


def test_create_question_returns_loaded_parts(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    question = db.create_question(
        title="Machtsfuncties",
        stem="Bepaal de afgeleide.",
        parts=[{"text": r"\(f(x)=x^2\)", "points": 2}],
        topic="derivatives",
    )

    assert len(question.parts) == 1
    assert question.parts[0].label == "a"
    assert question.parts[0].text == r"\(f(x)=x^2\)"
    assert question.parts[0].points == 2


def test_question_source_persists_enum_values_in_database(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    practice_question = db.create_question(
        title="Machtsfuncties",
        stem="Bepaal de afgeleide.",
        parts=[{"text": r"\(f(x)=x^2\)", "points": 2}],
        topic="derivatives",
        source=QuestionSource.PRACTICE,
    )
    assert practice_question.id is not None

    exam_question = db.create_question(
        title="Goniometrie",
        stem="Los op.",
        parts=[{"text": r"\(\sin(x)=0\)", "points": 3}],
        topic="goniometrie",
        source=QuestionSource.EXAM,
    )
    assert exam_question.id is not None

    with db.engine.connect() as connection:
        rows = connection.execute(
            text("select id, source from question order by id")
        ).all()

    assert rows == [
        (practice_question.id, "practice"),
        (exam_question.id, "exam"),
    ]
