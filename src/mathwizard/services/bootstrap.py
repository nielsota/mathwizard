from pathlib import Path
from typing import NotRequired, TypedDict

import yaml

from mathwizard.models.domain.figure import FigureDraft, FigureSpec
from mathwizard.models.domain.question import QuestionDraft, QuestionSource
from mathwizard.ports.password import PasswordHasher
from mathwizard.ports.unit_of_work import BootstrapUnitOfWork
from mathwizard.services.auth import BcryptPasswordHasher
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
    for path in sorted(topic_dir.glob("p*.yaml")):
        with path.open() as handle:
            exercises.append(yaml.safe_load(handle))
    return exercises


def _load_figure_yaml(figures_dir: Path) -> list[dict]:
    figures = []
    for path in sorted(figures_dir.glob("*.yaml")):
        with path.open() as handle:
            figures.append(yaml.safe_load(handle))
    return figures


def _to_draft(exercise: ExerciseYaml) -> QuestionDraft:
    return QuestionDraft(
        topic=exercise["topic"],
        title=exercise["title"],
        stem=exercise["stem"],
        source=QuestionSource(exercise["source"]),
        tags=exercise.get("tags", []),
        calculator_allowed=exercise.get("calculator_allowed"),
        difficulty=exercise.get("difficulty"),
        parts=exercise["parts"],
    )


class BootstrapService:
    def __init__(
        self,
        settings: Settings,
        hasher: PasswordHasher | None = None,
    ) -> None:
        self.settings = settings
        self._hasher = hasher or BcryptPasswordHasher()

    def seed_root_user(self, uow: BootstrapUnitOfWork) -> None:
        username = self.settings.bootstrap.username
        with uow:
            if uow.users.get_by_username(username) is None:
                uow.users.add(
                    username=username,
                    password_hash=self._hasher.hash(self.settings.bootstrap.password),
                )
                uow.commit()

    def seed_root_teacher(self, uow: BootstrapUnitOfWork) -> None:
        with uow:
            user = uow.users.get_by_username(self.settings.bootstrap.username)
            if user is None:
                raise RuntimeError(
                    f"Bootstrap user {self.settings.bootstrap.username} does not exist"
                )
            if uow.roster.get_teacher_by_user_id(user.id) is None:
                uow.roster.add_teacher(user.id)
                uow.commit()

    def seed_students(self, uow: BootstrapUnitOfWork) -> None:
        with uow:
            root = uow.users.get_by_username(self.settings.bootstrap.username)
            if root is None:
                raise RuntimeError(
                    f"Bootstrap user {self.settings.bootstrap.username} does not exist"
                )
            teacher = uow.roster.get_teacher_by_user_id(root.id)
            if teacher is None:
                raise RuntimeError("Bootstrap teacher does not exist")
            for username in self.settings.bootstrap.student_usernames:
                if uow.users.get_by_username(username) is not None:
                    continue
                student_user = uow.users.add(
                    username=username,
                    password_hash=self._hasher.hash(
                        self.settings.bootstrap.student_password
                    ),
                )
                uow.roster.add_student(student_user.id, teacher.id)
            uow.commit()

    def seed_practice_questions(self, uow: BootstrapUnitOfWork) -> None:
        practice_dir = self.settings.paths.practice_dir
        if not practice_dir.exists():
            raise FileNotFoundError(
                f"Practice question directory not found: {practice_dir}"
            )

        with uow:
            existing_ids: dict[tuple[QuestionSource, str, str], int] = {}
            ids_by_title: dict[tuple[QuestionSource, str], list[int]] = {}
            for question in uow.questions.list(source=QuestionSource.PRACTICE):
                existing_ids[(question.source, question.topic, question.title)] = (
                    question.id
                )
                ids_by_title.setdefault((question.source, question.title), []).append(
                    question.id
                )

            for topic_dir in sorted(practice_dir.iterdir()):
                if not topic_dir.is_dir() or topic_dir.name.startswith("_"):
                    continue
                for exercise in _load_practice_yaml(topic_dir):
                    draft = _to_draft(exercise)
                    key = (draft.source, draft.topic, draft.title)
                    question_id = existing_ids.get(key)
                    # A question whose topic moved is still the same question as long
                    # as its title is unambiguous, so it is updated rather than doubled.
                    if question_id is None:
                        candidates = ids_by_title.get((draft.source, draft.title), [])
                        if len(candidates) == 1:
                            question_id = candidates[0]
                    if question_id is not None:
                        uow.questions.replace(question_id, draft)
                        existing_ids[key] = question_id
                        continue
                    created = uow.questions.add(draft)
                    existing_ids[key] = created.id
                    ids_by_title.setdefault((draft.source, draft.title), []).append(
                        created.id
                    )
            uow.commit()

    def seed_figures(self, uow: BootstrapUnitOfWork) -> None:
        figures_dir = self.settings.paths.figures_dir
        if not figures_dir.exists():
            return
        with uow:
            for figure in _load_figure_yaml(figures_dir):
                uow.figures.upsert(
                    FigureDraft(
                        slug=figure["slug"],
                        title=figure["title"],
                        spec=FigureSpec.model_validate(figure["spec"]),
                        description=figure.get("description"),
                    )
                )
            uow.commit()

    def run_all(self, uow: BootstrapUnitOfWork) -> None:
        self.seed_root_user(uow)
        self.seed_root_teacher(uow)
        self.seed_students(uow)
        self.seed_practice_questions(uow)
        self.seed_figures(uow)
