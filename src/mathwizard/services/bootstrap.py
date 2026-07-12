from pathlib import Path
from typing import NotRequired, TypedDict

import yaml  # type: ignore[import-untyped]

from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource
from mathwizard.services.auth import hash_password
from mathwizard.settings import get_settings


class ExerciseYaml(TypedDict):
    source: str
    topic: str
    title: str
    stem: str
    parts: list[dict]
    tags: NotRequired[list[str]]
    calculator_allowed: NotRequired[bool | None]
    difficulty: NotRequired[int | None]


def seed_root_user(db: DBClient, *, username: str, password: str) -> None:
    if db.get_user_by_username(username) is None:
        db.create_user(username, hash_password(password))


def _load_practice_yaml(topic_dir: Path) -> list[ExerciseYaml]:
    exercises = []
    for f in sorted(topic_dir.glob("p*.yaml")):
        with f.open() as fh:
            exercises.append(yaml.safe_load(fh))
    return exercises


def seed_practice_questions(db: DBClient, practice_dir: Path) -> None:
    if not practice_dir.exists():
        raise FileNotFoundError(f"Practice question directory not found: {practice_dir}")

    existing_question_keys = {
        (q.source, q.topic, q.title)
        for q in db.list_questions()
    }

    for topic_dir in sorted(practice_dir.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("_"):
            continue

        for ex in _load_practice_yaml(topic_dir):
            source = QuestionSource(ex["source"])
            question_key = (source, ex["topic"], ex["title"])
            if question_key in existing_question_keys:
                continue

            db.create_question(
                title=ex["title"],
                stem=ex["stem"],
                parts=ex["parts"],
                topic=ex["topic"],
                source=source,
                tags=ex.get("tags"),
                calculator_allowed=ex.get("calculator_allowed"),
                difficulty=ex.get("difficulty"),
            )
            existing_question_keys.add(question_key)


def run_all(db: DBClient, practice_dir: Path) -> None:
    settings = get_settings()
    seed_root_user(
        db,
        username=settings.bootstrap_username,
        password=settings.bootstrap_password,
    )
    seed_practice_questions(db, practice_dir)
