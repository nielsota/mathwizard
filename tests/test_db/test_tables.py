import pytest
from sqlalchemy import Engine, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from mathwizard.db.tables.question import QuestionPartRow, QuestionRow
from mathwizard.db.tables.user import UserRow
from mathwizard.enums import QuestionSource


def test_metadata_creates_every_expected_table(engine: Engine) -> None:
    tables = set(inspect(engine).get_table_names())

    assert tables == {
        "users",
        "sessions",
        "teachers",
        "students",
        "questions",
        "question_parts",
        "figures",
    }


def test_username_is_unique(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        session.add(UserRow(username="root", password_hash="a"))
        session.add(UserRow(username="root", password_hash="b"))

        with pytest.raises(IntegrityError):
            session.commit()


def test_question_source_is_stored_as_its_enum_value(
    engine: Engine,
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        session.add(
            QuestionRow(
                topic="derivatives",
                source=QuestionSource.PRACTICE,
                tags=[],
                title="Machtsfuncties",
                stem="Bepaal de afgeleide.",
            )
        )
        session.commit()

    with engine.connect() as connection:
        rows = connection.execute(text("select source from questions")).all()

    assert rows == [("practice",)]


def test_question_parts_are_eagerly_loaded_and_ordered(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        session.add(
            QuestionRow(
                topic="derivatives",
                source=QuestionSource.PRACTICE,
                tags=[],
                title="Machtsfuncties",
                stem="Bepaal de afgeleide.",
                parts=[
                    QuestionPartRow(label="a", text="first", points=2),
                    QuestionPartRow(label="b", text="second", points=3),
                ],
            )
        )
        session.commit()

    with session_factory() as session:
        question = session.scalars(select(QuestionRow)).one()

    assert [part.label for part in question.parts] == ["a", "b"]


def test_deleting_a_question_deletes_its_parts(
    engine: Engine,
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        question = QuestionRow(
            topic="derivatives",
            source=QuestionSource.PRACTICE,
            tags=[],
            title="Machtsfuncties",
            stem="Bepaal de afgeleide.",
            parts=[QuestionPartRow(label="a", text="first", points=2)],
        )
        session.add(question)
        session.commit()
        session.delete(question)
        session.commit()

    with engine.connect() as connection:
        remaining = connection.execute(text("select count(*) from question_parts")).scalar()

    assert remaining == 0
