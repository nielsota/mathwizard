from typing import Any

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from mathwizard.db.base import Base


class FigureSchema(Base):
    __tablename__ = "figures"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    spec: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    question_id: Mapped[int | None] = mapped_column(
        ForeignKey("questions.id"), default=None, index=True
    )
    part_id: Mapped[int | None] = mapped_column(
        ForeignKey("question_parts.id"), default=None, index=True
    )
