from pathlib import Path

import pytest

from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource
from mathwizard.services.bootstrap import seed_practice_questions


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'bootstrap.db'}")


def write_practice_question(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join([*lines, ""]))


def test_seed_practice_questions_fails_when_directory_is_missing(tmp_path: Path) -> None:
    practice_dir = tmp_path / "questions" / "practice"
    db = make_db(tmp_path)

    with pytest.raises(FileNotFoundError, match=str(practice_dir)):
        seed_practice_questions(db, practice_dir)


def test_seed_practice_questions_uses_yaml_topic_not_folder_name(tmp_path: Path) -> None:
    practice_dir = tmp_path / "questions" / "practice"
    topic_dir = practice_dir / "folder-is-not-metadata"
    topic_dir.mkdir(parents=True)
    (topic_dir / "p1.yaml").write_text(
        "\n".join([
            "source: practice",
            "topic: derivatives",
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
            "source: practice",
            "topic: derivatives",
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


def test_seed_practice_questions_updates_matching_practice_question_from_yaml(
    tmp_path: Path,
) -> None:
    practice_dir = tmp_path / "questions" / "practice"
    topic_dir = practice_dir / "derivatives"
    topic_dir.mkdir(parents=True)
    question_path = topic_dir / "p1.yaml"
    write_practice_question(
        question_path,
        [
            "source: practice",
            "topic: derivatives",
            "title: Machtsfuncties",
            "stem: Bepaal de afgeleide.",
            "calculator_allowed: false",
            "difficulty: 1",
            "tags:",
            "- differentieren",
            "parts:",
            r"- text: \(f(x)=x^2\)",
            "  points: 2",
        ],
    )
    db = make_db(tmp_path)

    seed_practice_questions(db, practice_dir)
    write_practice_question(
        question_path,
        [
            "source: practice",
            "topic: derivatives",
            "title: Machtsfuncties",
            "stem: Bepaal opnieuw de afgeleide.",
            "calculator_allowed: true",
            "difficulty: 3",
            "tags:",
            "- kettingregel",
            "- differentieren",
            "parts:",
            r"- text: \(f(x)=x^3\)",
            "  points: 4",
            "- label: b",
            r"  text: \(g(x)=2x^2\)",
            "  points: 3",
        ],
    )

    seed_practice_questions(db, practice_dir)

    questions = db.list_questions(source=QuestionSource.PRACTICE)
    assert len(questions) == 1
    question = questions[0]
    assert question.stem == "Bepaal opnieuw de afgeleide."
    assert question.tags == ["kettingregel", "differentieren"]
    assert question.calculator_allowed is True
    assert question.difficulty == 3
    assert [(part.label, part.text, part.points) for part in question.parts] == [
        ("a", r"\(f(x)=x^3\)", 4),
        ("b", r"\(g(x)=2x^2\)", 3),
    ]


def test_seed_practice_questions_updates_unique_source_title_topic_rename(
    tmp_path: Path,
) -> None:
    practice_dir = tmp_path / "questions" / "practice"
    topic_dir = practice_dir / "goniometrie"
    topic_dir.mkdir(parents=True)
    question_path = topic_dir / "p1.yaml"
    write_practice_question(
        question_path,
        [
            "source: practice",
            "topic: goniometry",
            "title: Van cosinus naar sinus",
            "stem: Bepaal exact de sinus.",
            "parts:",
            r"- text: \(\cos(\alpha)=\frac{3}{5}\)",
            "  points: 3",
        ],
    )
    db = make_db(tmp_path)

    seed_practice_questions(db, practice_dir)
    write_practice_question(
        question_path,
        [
            "source: practice",
            "topic: goniometrie",
            "title: Van cosinus naar sinus",
            "stem: Bepaal exact de sinus na de topic-rename.",
            "parts:",
            r"- text: \(\cos(\alpha)=\frac{5}{13}\)",
            "  points: 4",
            r"- text: \(\cos(\alpha)=\frac{8}{17}\)",
            "  points: 5",
        ],
    )

    seed_practice_questions(db, practice_dir)

    questions = db.list_questions(source=QuestionSource.PRACTICE)
    assert len(questions) == 1
    question = questions[0]
    assert question.topic == "goniometrie"
    assert question.title == "Van cosinus naar sinus"
    assert question.stem == "Bepaal exact de sinus na de topic-rename."
    assert [(part.text, part.points) for part in question.parts] == [
        (r"\(\cos(\alpha)=\frac{5}{13}\)", 4),
        (r"\(\cos(\alpha)=\frac{8}{17}\)", 5),
    ]


def test_seed_practice_questions_does_not_fallback_update_ambiguous_title(
    tmp_path: Path,
) -> None:
    practice_dir = tmp_path / "questions" / "practice"
    topic_dir = practice_dir / "vectors"
    topic_dir.mkdir(parents=True)
    write_practice_question(
        topic_dir / "p1.yaml",
        [
            "source: practice",
            "topic: vectors",
            "title: Hoek tussen twee lijnen",
            "stem: Nieuwe vectorvraag.",
            "parts:",
            r"- text: '\(\ell: \vec{x}=\vec{0}+t\vec{a}\)'",
            "  points: 2",
        ],
    )
    db = make_db(tmp_path)
    db.create_question(
        title="Hoek tussen twee lijnen",
        stem="Bestaande parametric-vraag.",
        parts=[{"text": r"\(l: y=2x+1\)", "points": 3}],
        topic="parametric",
        source=QuestionSource.PRACTICE,
    )
    db.create_question(
        title="Hoek tussen twee lijnen",
        stem="Bestaande analytic-vraag.",
        parts=[{"text": r"\(m: y=-x+4\)", "points": 3}],
        topic="analytic_geometry",
        source=QuestionSource.PRACTICE,
    )

    seed_practice_questions(db, practice_dir)

    questions = db.list_questions(source=QuestionSource.PRACTICE)
    assert len(questions) == 3
    stems_by_topic = {question.topic: question.stem for question in questions}
    assert stems_by_topic == {
        "parametric": "Bestaande parametric-vraag.",
        "analytic_geometry": "Bestaande analytic-vraag.",
        "vectors": "Nieuwe vectorvraag.",
    }


def test_seed_practice_questions_clears_optional_fields_missing_from_yaml(
    tmp_path: Path,
) -> None:
    practice_dir = tmp_path / "questions" / "practice"
    topic_dir = practice_dir / "derivatives"
    topic_dir.mkdir(parents=True)
    question_path = topic_dir / "p1.yaml"
    write_practice_question(
        question_path,
        [
            "source: practice",
            "topic: derivatives",
            "title: Machtsfuncties",
            "stem: Bepaal de afgeleide.",
            "calculator_allowed: false",
            "difficulty: 1",
            "tags:",
            "- differentieren",
            "parts:",
            r"- text: \(f(x)=x^2\)",
            "  points: 2",
        ],
    )
    db = make_db(tmp_path)

    seed_practice_questions(db, practice_dir)
    write_practice_question(
        question_path,
        [
            "source: practice",
            "topic: derivatives",
            "title: Machtsfuncties",
            "stem: Bepaal de afgeleide zonder metadata.",
            "parts:",
            r"- text: \(f(x)=x^4\)",
            "  points: 5",
        ],
    )

    seed_practice_questions(db, practice_dir)

    questions = db.list_questions(source=QuestionSource.PRACTICE)
    assert len(questions) == 1
    question = questions[0]
    assert question.tags == []
    assert question.calculator_allowed is None
    assert question.difficulty is None
    assert question.parts[0].text == r"\(f(x)=x^4\)"


def test_seed_practice_questions_ignores_matching_exam_question(tmp_path: Path) -> None:
    practice_dir = tmp_path / "questions" / "practice"
    topic_dir = practice_dir / "derivatives"
    topic_dir.mkdir(parents=True)
    (topic_dir / "p1.yaml").write_text(
        "\n".join([
            "source: practice",
            "topic: derivatives",
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
