from datetime import UTC, datetime

from sqlalchemy import JSON, Column, Enum
from sqlmodel import Field, Relationship, SQLModel

from mathwizard.enums import QuestionSource


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    sessions: list["Session"] = Relationship(back_populates="user")


class Session(SQLModel, table=True):
    # Deliberately not named "sessions": that belongs to SessionSchema, which uses a
    # different primary key. This model and its table go away with the legacy stack.
    id: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=_utcnow)
    expires_at: datetime
    revoked_at: datetime | None = None

    user: User = Relationship(back_populates="sessions")


class Teacher(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    students: list["Student"] = Relationship(back_populates="teacher")


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    teacher_id: int = Field(foreign_key="teacher.id", index=True)
    teacher: Teacher = Relationship(back_populates="students")


class Question(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    topic: str = Field(index=True)
    source: QuestionSource = Field(
        default=QuestionSource.PRACTICE,
        sa_column=Column(
            Enum(
                QuestionSource,
                values_callable=lambda enum_cls: [member.value for member in enum_cls],
                native_enum=False,
            ),
            index=True,
        ),
    )
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    exam_id: str | None = None
    title: str
    stem: str
    calculator_allowed: bool | None = None
    difficulty: int | None = None

    parts: list["QuestionPart"] = Relationship(
        back_populates="question",
        cascade_delete=True,
    )


class QuestionPart(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id")
    label: str
    text: str
    points: int

    question: Question = Relationship(back_populates="parts")


class Figure(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    title: str
    description: str | None = None
    spec: dict = Field(default_factory=dict, sa_column=Column(JSON))
    question_id: int | None = Field(default=None, foreign_key="question.id", index=True)
    part_id: int | None = Field(default=None, foreign_key="questionpart.id", index=True)