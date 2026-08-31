from pydantic import BaseModel

from mathwizard.models.domain.figure import FigureSpec


class FigureCreateRequest(BaseModel):
    slug: str
    title: str
    description: str | None = None
    spec: FigureSpec


class FigureSummary(BaseModel):
    id: int
    slug: str
    title: str
    question_id: int | None = None
    part_id: int | None = None


class FigureResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str | None = None
    spec: FigureSpec
    question_id: int | None = None
    part_id: int | None = None


class FigureListResponse(BaseModel):
    figures: list[FigureSummary]
