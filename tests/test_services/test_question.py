from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource
from mathwizard.models.question import QuestionListRequest
from mathwizard.services.question import QuestionService


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
