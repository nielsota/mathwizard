from pathlib import Path

import yaml

from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory
from mathwizard.models.domain.question import QuestionSource
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import DatabaseSettings, PathSettings, Settings


def _write_practice_yaml(repo_root: Path, *, title: str, difficulty: int) -> None:
    topic_dir = repo_root / "data" / "questions" / "practice" / "derivatives"
    topic_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "practice",
        "topic": "derivatives",
        "title": title,
        "stem": "Bepaal de afgeleide.",
        "difficulty": difficulty,
        "parts": [{"text": "first", "points": 2}],
    }
    with (topic_dir / "p01.yaml").open("w") as handle:
        yaml.safe_dump(payload, handle)


def test_seed_practice_questions_inserts_from_yaml(
    tmp_path: Path,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    _write_practice_yaml(tmp_path, title="Machtsfuncties", difficulty=1)
    settings = Settings(
        db=DatabaseSettings(url="sqlite:///unused.db"),
        paths=PathSettings(repo_root=tmp_path),
    )

    BootstrapService(settings).seed_practice_questions(uow_factory())

    with uow_factory() as uow:
        questions = uow.questions.list(source=QuestionSource.PRACTICE)
    assert [question.title for question in questions] == ["Machtsfuncties"]
    assert questions[0].parts[0].label == "a"


def test_seed_practice_questions_is_idempotent(
    tmp_path: Path,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    _write_practice_yaml(tmp_path, title="Machtsfuncties", difficulty=1)
    settings = Settings(
        db=DatabaseSettings(url="sqlite:///unused.db"),
        paths=PathSettings(repo_root=tmp_path),
    )
    service = BootstrapService(settings)

    service.seed_practice_questions(uow_factory())
    service.seed_practice_questions(uow_factory())

    with uow_factory() as uow:
        questions = uow.questions.list(source=QuestionSource.PRACTICE)
    assert len(questions) == 1


def test_seed_practice_questions_updates_an_existing_question(
    tmp_path: Path,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    _write_practice_yaml(tmp_path, title="Machtsfuncties", difficulty=1)
    settings = Settings(
        db=DatabaseSettings(url="sqlite:///unused.db"),
        paths=PathSettings(repo_root=tmp_path),
    )
    service = BootstrapService(settings)
    service.seed_practice_questions(uow_factory())

    _write_practice_yaml(tmp_path, title="Machtsfuncties", difficulty=4)
    service.seed_practice_questions(uow_factory())

    with uow_factory() as uow:
        questions = uow.questions.list(source=QuestionSource.PRACTICE)
    assert len(questions) == 1
    assert questions[0].difficulty == 4
