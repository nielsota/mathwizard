from typing import Literal

from pydantic import BaseModel, Field


class FunctionGraph(BaseModel):
    type: Literal["functionGraph"] = "functionGraph"
    fn: str
    domain: tuple[float, float] | None = None
    color: str | None = None


class Viewport(BaseModel):
    x: tuple[float, float]
    y: tuple[float, float] | None = None


class FigureSpec(BaseModel):
    viewport: Viewport
    show_grid: bool = True
    x_label: str = "x"
    y_label: str = "y"
    elements: list[FunctionGraph] = Field(default_factory=list)


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
