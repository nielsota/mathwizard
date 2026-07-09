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
    assert questions[0].tags == []


def test_seed_practice_questions_ignores_matching_exam_question(tmp_path: Path) -> None:
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
    db.create_question(
        title="Machtsfuncties",
        stem="Bepaal de afgeleide.",
        parts=[{"text": r"\(f(x)=x^2\)", "points": 2}],
        topic="derivatives",
        source=QuestionSource.EXAM,
        exam_id="VWO-2024-I-01",
    )

    seed_practice_questions(db, practice_dir)

    questions = db.list_questions()
    practice_questions = [
        question for question in questions if question.source == QuestionSource.PRACTICE
    ]
    assert len(questions) == 2
    assert len(practice_questions) == 1
    assert practice_questions[0].exam_id is None
