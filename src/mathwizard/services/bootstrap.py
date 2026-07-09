from pathlib import Path
from typing import TypedDict

import yaml  # type: ignore[import-untyped]

from mathwizard.db.client import DBClient


class ExerciseYaml(TypedDict):
    title: str
    stem: str
    parts: list[dict]
    exam_id: str | None = None
    calculator_allowed: bool | None = None
    difficulty: int | None = None


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

    existing_exam_ids = {q.exam_id for q in db.list_questions()}

    for topic_dir in sorted(practice_dir.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("_"):
            continue

        for ex in _load_practice_yaml(topic_dir):
            if ex.get("exam_id") in existing_exam_ids:
                continue

            db.create_question(
                title=ex["title"],
                stem=ex["stem"],
                parts=ex["parts"],
                exam_id=ex.get("exam_id"),
                calculator_allowed=ex.get("calculator_allowed"),
                difficulty=ex.get("difficulty"),
            )
            existing_exam_ids.add(ex.get("exam_id"))


def run_all(db: DBClient, practice_dir: Path) -> None:
    seed_root_user(db)
    seed_practice_questions(db, practice_dir)
