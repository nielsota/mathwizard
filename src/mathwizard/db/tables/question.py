from sqlalchemy import JSON, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mathwizard.db.base import Base
from mathwizard.models.domain.question import QuestionSource


class QuestionSchema(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic: Mapped[str] = mapped_column(String(255), index=True)
    source: Mapped[QuestionSource] = mapped_column(
        Enum(
            QuestionSource,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=False,
        ),
        index=True,
    )
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    exam_id: Mapped[str | None] = mapped_column(String(255), default=None)
    title: Mapped[str] = mapped_column(String(255))
    stem: Mapped[str] = mapped_column(Text)
    calculator_allowed: Mapped[bool | None] = mapped_column(default=None)
    difficulty: Mapped[int | None] = mapped_column(default=None)

    parts: Mapped[list["QuestionPartSchema"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionPartSchema.id",
        lazy="selectin",
    )


class QuestionPartSchema(Base):
    __tablename__ = "question_parts"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    label: Mapped[str] = mapped_column(String(8))
    text: Mapped[str] = mapped_column(Text)
    points: Mapped[int]

    question: Mapped[QuestionSchema] = relationship(back_populates="parts")
