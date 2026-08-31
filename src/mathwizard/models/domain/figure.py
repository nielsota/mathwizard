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


class FigureDraft(BaseModel):
    slug: str
    title: str
    spec: FigureSpec
    description: str | None = None
    question_id: int | None = None
    part_id: int | None = None


class Figure(BaseModel):
    id: int
    slug: str
    title: str
    spec: FigureSpec
    description: str | None = None
    question_id: int | None = None
    part_id: int | None = None
