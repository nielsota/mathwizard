from typing import Self

from pydantic import BaseModel, Field, computed_field, model_validator

from mathwizard.enums import QuestionSource


class QuestionPartDraft(BaseModel):
    text: str
    points: int
    label: str = ""


class QuestionPart(BaseModel):
    id: int
    label: str
    text: str
    points: int


class QuestionDraft(BaseModel):
    topic: str
    title: str
    stem: str
    source: QuestionSource = QuestionSource.PRACTICE
    tags: list[str] = Field(default_factory=list)
    exam_id: str | None = None
    calculator_allowed: bool | None = None
    difficulty: int | None = None
    parts: list[QuestionPartDraft] = Field(default_factory=list)

    @model_validator(mode="after")
    def _assign_default_part_labels(self) -> Self:
        for index, part in enumerate(self.parts):
            if not part.label:
                part.label = chr(ord("a") + index)
        return self


class Question(BaseModel):
    id: int
    topic: str
    title: str
    stem: str
    source: QuestionSource
    tags: list[str] = Field(default_factory=list)
    exam_id: str | None = None
    calculator_allowed: bool | None = None
    difficulty: int | None = None
    parts: list[QuestionPart] = Field(default_factory=list)

    @computed_field
    @property
    def max_marks(self) -> int:
        return sum(part.points for part in self.parts)
