from mathwizard.exceptions import DuplicateFigureSlugError
from mathwizard.models.domain.figure import Figure, FigureDraft
from mathwizard.ports.unit_of_work import FigureUnitOfWork


class FigureService:
    def list_figures(self, uow: FigureUnitOfWork) -> list[Figure]:
        with uow:
            return uow.figures.list()

    def get_figure(self, uow: FigureUnitOfWork, figure_id: int) -> Figure:
        with uow:
            return uow.figures.get(figure_id)

    def create_figure(self, uow: FigureUnitOfWork, draft: FigureDraft) -> Figure:
        with uow:
            if uow.figures.get_by_slug(draft.slug) is not None:
                raise DuplicateFigureSlugError(draft.slug)
            figure = uow.figures.add(draft)
            uow.commit()
        return figure
