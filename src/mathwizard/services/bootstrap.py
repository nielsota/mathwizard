from pathlib import Path
from typing import NotRequired, TypedDict

import yaml  # type: ignore[import-untyped]

from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource
from mathwizard.services.auth import hash_password
from mathwizard.settings import Settings


class ExerciseYaml(TypedDict):
    source: str
    topic: str
    title: str
    stem: str
    parts: list[dict]
    tags: NotRequired[list[str]]
    calculator_allowed: NotRequired[bool | None]
    difficulty: NotRequired[int | None]


def _load_practice_yaml(topic_dir: Path) -> list[ExerciseYaml]:
    exercises = []
    for f in sorted(topic_dir.glob("p*.yaml")):
        with f.open() as fh:
            exercises.append(yaml.safe_load(fh))
    return exercises


class BootstrapService:
    def __init__(self, db: DBClient, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def seed_root_user(self) -> None:
        username = self.settings.bootstrap_username
        if self.db.get_user_by_username(username) is None:
            self.db.create_user(username, hash_password(self.settings.bootstrap_password))

    def seed_practice_questions(self) -> None:
        practice_dir = self.settings.practice_dir
        if not practice_dir.exists():
            raise FileNotFoundError(
                f"Practice question directory not found: {practice_dir}"
            )

        existing_practice_question_ids = {}
        existing_practice_question_ids_by_source_title = {}
        for question in self.db.list_questions(source=QuestionSource.PRACTICE):
            if question.id is None:
                raise RuntimeError(
                    f"Persisted practice question has no id: {question.topic}/{question.title}"
                )
            existing_practice_question_ids[
                (question.source, question.topic, question.title)
            ] = question.id
            source_title_key = (question.source, question.title)
            existing_practice_question_ids_by_source_title.setdefault(
                source_title_key,
                [],
            ).append(question.id)

        for topic_dir in sorted(practice_dir.iterdir()):
            if not topic_dir.is_dir() or topic_dir.name.startswith("_"):
                continue

            for ex in _load_practice_yaml(topic_dir):
                source = QuestionSource(ex["source"])
                question_key = (source, ex["topic"], ex["title"])
                existing_question_id = existing_practice_question_ids.get(question_key)
                if existing_question_id is None:
                    source_title_key = (source, ex["title"])
                    matching_question_ids = (
                        existing_practice_question_ids_by_source_title.get(
                            source_title_key,
                            [],
                        )
                    )
                    if len(matching_question_ids) == 1:
                        existing_question_id = matching_question_ids[0]
                if existing_question_id is not None:
                    self.db.replace_question(
                        existing_question_id,
                        title=ex["title"],
                        stem=ex["stem"],
                        parts=ex["parts"],
                        topic=ex["topic"],
                        source=source,
                        tags=ex.get("tags", []),
                        calculator_allowed=ex.get("calculator_allowed"),
                        difficulty=ex.get("difficulty"),
                    )
                    existing_practice_question_ids[question_key] = existing_question_id
                    continue

                question = self.db.create_question(
                    title=ex["title"],
                    stem=ex["stem"],
                    parts=ex["parts"],
                    topic=ex["topic"],
                    source=source,
                    tags=ex.get("tags"),
                    calculator_allowed=ex.get("calculator_allowed"),
                    difficulty=ex.get("difficulty"),
                )
                if question.id is None:
                    raise RuntimeError(
                        f"Created practice question has no id: {ex['topic']}/{ex['title']}"
                    )
                existing_practice_question_ids[question_key] = question.id
                source_title_key = (source, ex["title"])
                existing_practice_question_ids_by_source_title.setdefault(
                    source_title_key,
                    [],
                ).append(question.id)

    def run_all(self) -> None:
        self.seed_root_user()
        self.seed_practice_questions()
