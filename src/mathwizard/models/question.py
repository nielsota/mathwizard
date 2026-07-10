from pydantic import BaseModel, Field

from mathwizard.enums import QuestionSource


class QuestionListRequest(BaseModel):
    source: QuestionSource
    topic: str | None = None
    sort_by_difficulty: bool = True


class QuestionPartResponse(BaseModel):
    label: str
    text: str
    points: int


class QuestionResponse(BaseModel):
    id: int
    number: int
    source: QuestionSource
    topic: str
    tags: list[str] = Field(default_factory=list)
    title: str
    question_text: str
    parts: list[str] = Field(default_factory=list)
    part_details: list[QuestionPartResponse] = Field(default_factory=list)
    max_marks: int
    calculator_allowed: bool | None = None
    difficulty: int | None = None
    figure_images: list[str] = Field(default_factory=list)


class QuestionListResponse(BaseModel):
    source: QuestionSource
    topic: str | None = None
    questions: list[QuestionResponse]
