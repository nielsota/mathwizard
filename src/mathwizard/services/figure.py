from mathwizard.db.client import DBClient
from mathwizard.exceptions import DuplicateFigureSlugError
from mathwizard.models.db import Figure
from mathwizard.models.figure import (
    FigureCreateRequest,
    FigureListResponse,
    FigureResponse,
    FigureSpec,
    FigureSummary,
)


def _to_summary(figure: Figure) -> FigureSummary:
    return FigureSummary(
        id=figure.id,
        slug=figure.slug,
        title=figure.title,
        question_id=figure.question_id,
        part_id=figure.part_id,
    )


def _to_response(figure: Figure) -> FigureResponse:
    return FigureResponse(
        id=figure.id,
        slug=figure.slug,
        title=figure.title,
        description=figure.description,
        spec=FigureSpec.model_validate(figure.spec),
        question_id=figure.question_id,
        part_id=figure.part_id,
    )


class FigureService:
    def __init__(self, db: DBClient) -> None:
        self.db = db

    def list_figures(self) -> FigureListResponse:
        return FigureListResponse(
            figures=[_to_summary(figure) for figure in self.db.list_figures()],
        )

    def get_figure(self, figure_id: int) -> FigureResponse:
        return _to_response(self.db.get_figure(figure_id))

    def create_figure(self, request: FigureCreateRequest) -> FigureResponse:
        if self.db.get_figure_by_slug(request.slug) is not None:
            raise DuplicateFigureSlugError(request.slug)
        figure = self.db.create_figure(
            slug=request.slug,
            title=request.title,
            spec=request.spec.model_dump(),
            description=request.description,
        )
        return _to_response(figure)
