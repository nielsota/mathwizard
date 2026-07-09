from pathlib import Path
from typing import NotRequired, TypedDict

import yaml  # type: ignore[import-untyped]

from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource


class ExerciseYaml(TypedDict):
    title: str
    stem: str
    parts: list[dict]
    tags: NotRequired[list[str]]
    calculator_allowed: NotRequired[bool | None]
    difficulty: NotRequired[int | None]


def seed_root_user(db: DBClient) -> None:
    if db.get_user_by_username("root") is None:
        db.create_user("root", "root")


def _load_practice_yaml(topic_dir: Path) -> list[ExerciseYaml]:
    exercises = []
    for f in sorted(topic_dir.glob("p*.yaml")):
        with f.open() as fh:
            exercises.append(yaml.safe_load(fh))
    return exercises


def seed_practice_questions(db: DBClient, practice_dir: Path) -> None:
    if not practice_dir.exists():
        return

    existing_practice_keys = {
        (q.topic, q.title)
        for q in db.list_questions()
        if q.source == QuestionSource.PRACTICE
    }

    for topic_dir in sorted(practice_dir.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("_"):
            continue

        for ex in _load_practice_yaml(topic_dir):
            practice_key = (topic_dir.name, ex["title"])
            if practice_key in existing_practice_keys:
                continue

            db.create_question(
                title=ex["title"],
                stem=ex["stem"],
                parts=ex["parts"],
                topic=topic_dir.name,
                source=QuestionSource.PRACTICE,
                tags=ex.get("tags", []),
                calculator_allowed=ex.get("calculator_allowed"),
                difficulty=ex.get("difficulty"),
            )
            existing_practice_keys.add(practice_key)


def run_all(db: DBClient, practice_dir: Path) -> None:
    seed_root_user(db)
    seed_practice_questions(db, practice_dir)
