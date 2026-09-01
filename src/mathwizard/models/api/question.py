from pydantic import BaseModel, Field

from mathwizard.models.domain.question import QuestionSource


class QuestionPartResponse(BaseModel):
    label: str
    text: str
    points: int


class QuestionResponse(BaseModel):
    id: int
    source: QuestionSource
    topic: str
    tags: list[str] = Field(default_factory=list)
    title: str
    # validation_alias, not alias: FastAPI serialises with by_alias=True, so an
    # alias would put the internal name `stem` on the wire.
    question_text: str = Field(validation_alias="stem")
    parts: list[QuestionPartResponse] = Field(default_factory=list)
    max_marks: int
    calculator_allowed: bool | None = None
    difficulty: int | None = None


class QuestionListResponse(BaseModel):
    source: QuestionSource
    topic: str | None = None
    questions: list[QuestionResponse]
