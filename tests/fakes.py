from collections.abc import Sequence
from datetime import datetime
from types import TracebackType
from typing import Self

from mathwizard.exceptions import (
    FigureNotFoundError,
    QuestionNotFoundError,
    UserNotFoundError,
)
from mathwizard.models.domain.figure import Figure, FigureDraft
from mathwizard.models.domain.question import (
    Question,
    QuestionDraft,
    QuestionPart,
    QuestionSource,
)
from mathwizard.models.domain.roster import Student, Teacher
from mathwizard.models.domain.session import AuthSession
from mathwizard.models.domain.user import User
from mathwizard.ports.figure import FigureRepository
from mathwizard.ports.question import QuestionRepository
from mathwizard.ports.roster import RosterRepository
from mathwizard.ports.session import SessionRepository
from mathwizard.ports.unit_of_work import UnitOfWork, UnitOfWorkFactory
from mathwizard.ports.user import UserRepository


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id = 1

    def add(self, *, username: str, password_hash: str) -> User:
        user = User(
            id=self._next_id,
            username=username,
            password_hash=password_hash,
        )
        self._users[user.id] = user
        self._next_id += 1
        return user

    def get(self, user_id: int) -> User:
        user = self._users.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    def get_by_username(self, username: str) -> User | None:
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    def get_many(self, user_ids: Sequence[int]) -> list[User]:
        wanted = set(user_ids)
        return [
            user for user_id, user in sorted(self._users.items()) if user_id in wanted
        ]


class FakeSessionRepository(SessionRepository):
    def __init__(self) -> None:
        self._sessions: dict[str, AuthSession] = {}

    def add(
        self,
        *,
        token: str,
        user_id: int,
        created_at: datetime,
        expires_at: datetime,
    ) -> AuthSession:
        session = AuthSession(
            token=token,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
        )
        self._sessions[session.token] = session
        return session

    def get(self, token: str) -> AuthSession | None:
        return self._sessions.get(token)

    def revoke(self, token: str, revoked_at: datetime) -> None:
        session = self._sessions.get(token)
        if session is not None and session.revoked_at is None:
            self._sessions[token] = session.model_copy(
                update={"revoked_at": revoked_at}
            )


class FakeRosterRepository(RosterRepository):
    def __init__(self) -> None:
        self._teachers: dict[int, Teacher] = {}
        self._students: dict[int, Student] = {}
        self._next_teacher_id = 1
        self._next_student_id = 1

    def add_teacher(self, user_id: int) -> Teacher:
        teacher = Teacher(id=self._next_teacher_id, user_id=user_id)
        self._teachers[teacher.id] = teacher
        self._next_teacher_id += 1
        return teacher

    def add_student(self, user_id: int, teacher_id: int) -> Student:
        student = Student(
            id=self._next_student_id,
            user_id=user_id,
            teacher_id=teacher_id,
        )
        self._students[student.id] = student
        self._next_student_id += 1
        return student

    def get_teacher(self, teacher_id: int) -> Teacher | None:
        return self._teachers.get(teacher_id)

    def get_teacher_by_user_id(self, user_id: int) -> Teacher | None:
        for teacher in self._teachers.values():
            if teacher.user_id == user_id:
                return teacher
        return None

    def get_student_by_user_id(self, user_id: int) -> Student | None:
        for student in self._students.values():
            if student.user_id == user_id:
                return student
        return None

    def list_students_for_teacher(self, teacher_id: int) -> list[Student]:
        return [
            student
            for _, student in sorted(self._students.items())
            if student.teacher_id == teacher_id
        ]


class FakeQuestionRepository(QuestionRepository):
    def __init__(self) -> None:
        self._questions: dict[int, Question] = {}
        self._next_id = 1
        self._next_part_id = 1

    def add(self, draft: QuestionDraft) -> Question:
        question = self._build(self._next_id, draft)
        self._questions[question.id] = question
        self._next_id += 1
        return question

    def get(self, question_id: int) -> Question:
        question = self._questions.get(question_id)
        if question is None:
            raise QuestionNotFoundError(question_id)
        return question

    def replace(self, question_id: int, draft: QuestionDraft) -> Question:
        if question_id not in self._questions:
            raise QuestionNotFoundError(question_id)
        question = self._build(question_id, draft)
        self._questions[question_id] = question
        return question

    def list(
        self,
        *,
        topic: str | None = None,
        source: QuestionSource | None = None,
    ) -> list[Question]:
        questions = [question for _, question in sorted(self._questions.items())]
        if topic is not None:
            questions = [question for question in questions if question.topic == topic]
        if source is not None:
            questions = [
                question for question in questions if question.source == source
            ]
        return questions

    def _build(self, question_id: int, draft: QuestionDraft) -> Question:
        parts = []
        for part in draft.parts:
            parts.append(
                QuestionPart(
                    id=self._next_part_id,
                    label=part.label,
                    text=part.text,
                    points=part.points,
                )
            )
            self._next_part_id += 1
        return Question(
            id=question_id,
            topic=draft.topic,
            title=draft.title,
            stem=draft.stem,
            source=draft.source,
            tags=list(draft.tags),
            exam_id=draft.exam_id,
            calculator_allowed=draft.calculator_allowed,
            difficulty=draft.difficulty,
            parts=parts,
        )


class FakeFigureRepository(FigureRepository):
    def __init__(self) -> None:
        self._figures: dict[int, Figure] = {}
        self._next_id = 1

    def add(self, draft: FigureDraft) -> Figure:
        figure = self._build(self._next_id, draft)
        self._figures[figure.id] = figure
        self._next_id += 1
        return figure

    def get(self, figure_id: int) -> Figure:
        figure = self._figures.get(figure_id)
        if figure is None:
            raise FigureNotFoundError(figure_id)
        return figure

    def get_by_slug(self, slug: str) -> Figure | None:
        for figure in self._figures.values():
            if figure.slug == slug:
                return figure
        return None

    def upsert(self, draft: FigureDraft) -> Figure:
        existing = self.get_by_slug(draft.slug)
        if existing is None:
            return self.add(draft)
        figure = self._build(existing.id, draft)
        self._figures[existing.id] = figure
        return figure

    def list(self) -> list[Figure]:
        return [figure for _, figure in sorted(self._figures.items())]

    def _build(self, figure_id: int, draft: FigureDraft) -> Figure:
        return Figure(
            id=figure_id,
            slug=draft.slug,
            title=draft.title,
            spec=draft.spec,
            description=draft.description,
            question_id=draft.question_id,
            part_id=draft.part_id,
        )


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.users = FakeUserRepository()
        self.sessions = FakeSessionRepository()
        self.roster = FakeRosterRepository()
        self.questions = FakeQuestionRepository()
        self.figures = FakeFigureRepository()
        self.committed = False
        self.open = False

    def __enter__(self) -> Self:
        if self.open:
            raise RuntimeError("FakeUnitOfWork is already open")
        self.open = True
        self.committed = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.open = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False


class FakeUnitOfWorkFactory(UnitOfWorkFactory):
    def __init__(self, uow: FakeUnitOfWork) -> None:
        self._uow = uow

    def __call__(self) -> FakeUnitOfWork:
        return self._uow
