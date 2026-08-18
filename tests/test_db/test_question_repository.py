import pytest
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from mathwizard.db.repositories.question import SqlAlchemyQuestionRepository
from mathwizard.enums import QuestionSource
from mathwizard.exceptions import QuestionNotFoundError
from mathwizard.models.domain.question import QuestionDraft


def _draft(**overrides: object) -> QuestionDraft:
    values: dict[str, object] = {
        "topic": "derivatives",
        "title": "Machtsfuncties",
        "stem": "Bepaal de afgeleide.",
        "source": QuestionSource.PRACTICE,
        "tags": ["differentieren"],
        "parts": [{"text": r"\(f(x)=x^2\)", "points": 2}],
    }
    values.update(overrides)
    return QuestionDraft(**values)


def test_add_persists_metadata_and_auto_labelled_parts(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        created = SqlAlchemyQuestionRepository(session).add(
            _draft(
                parts=[
                    {"text": "first", "points": 2},
                    {"text": "second", "points": 3},
                ],
                calculator_allowed=False,
                difficulty=1,
            )
        )
        session.commit()

    with session_factory() as session:
        stored = SqlAlchemyQuestionRepository(session).get(created.id)

    assert stored.topic == "derivatives"
    assert stored.source == QuestionSource.PRACTICE
    assert stored.tags == ["differentieren"]
    assert stored.exam_id is None
    assert stored.calculator_allowed is False
    assert stored.difficulty == 1
    assert [(part.label, part.points) for part in stored.parts] == [("a", 2), ("b", 3)]
    assert stored.max_marks == 5


def test_get_raises_when_the_question_is_missing(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        with pytest.raises(QuestionNotFoundError):
            SqlAlchemyQuestionRepository(session).get(99)


def test_list_filters_by_topic_and_source(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = SqlAlchemyQuestionRepository(session)
        repository.add(_draft(title="A", topic="derivatives"))
        repository.add(_draft(title="B", topic="goniometrie"))
        repository.add(
            _draft(title="C", topic="derivatives", source=QuestionSource.EXAM)
        )
        session.commit()

    with session_factory() as session:
        repository = SqlAlchemyQuestionRepository(session)
        by_topic = repository.list(topic="derivatives")
        by_source = repository.list(source=QuestionSource.EXAM)
        everything = repository.list()

    assert [question.title for question in by_topic] == ["A", "C"]
    assert [question.title for question in by_source] == ["C"]
    assert [question.title for question in everything] == ["A", "B", "C"]


def test_replace_overwrites_metadata_and_parts(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        created = SqlAlchemyQuestionRepository(session).add(_draft())
        session.commit()

    with session_factory() as session:
        replaced = SqlAlchemyQuestionRepository(session).replace(
            created.id,
            _draft(
                title="Goniometrie",
                topic="goniometrie",
                source=QuestionSource.EXAM,
                tags=["sinus"],
                exam_id="VWO-2024-I-01",
                parts=[{"text": "only", "points": 4}],
            ),
        )
        session.commit()

    assert replaced.id == created.id
    assert replaced.title == "Goniometrie"
    assert replaced.topic == "goniometrie"
    assert replaced.source == QuestionSource.EXAM
    assert replaced.tags == ["sinus"]
    assert replaced.exam_id == "VWO-2024-I-01"
    assert [(part.label, part.text) for part in replaced.parts] == [("a", "only")]


def test_replace_deletes_the_orphaned_parts(
    engine: Engine,
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        created = SqlAlchemyQuestionRepository(session).add(
            _draft(parts=[{"text": "one", "points": 1}, {"text": "two", "points": 1}])
        )
        session.commit()

    with session_factory() as session:
        SqlAlchemyQuestionRepository(session).replace(
            created.id, _draft(parts=[{"text": "only", "points": 1}])
        )
        session.commit()

    with engine.connect() as connection:
        count = connection.execute(text("select count(*) from question_parts")).scalar()

    assert count == 1


def test_replace_raises_when_the_question_is_missing(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        with pytest.raises(QuestionNotFoundError):
            SqlAlchemyQuestionRepository(session).replace(99, _draft())


def test_add_does_not_commit(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        SqlAlchemyQuestionRepository(session).add(_draft())
        session.rollback()

    with session_factory() as session:
        assert SqlAlchemyQuestionRepository(session).list() == []
