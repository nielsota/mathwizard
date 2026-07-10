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
