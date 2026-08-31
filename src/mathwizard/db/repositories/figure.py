from sqlalchemy import select
from sqlalchemy.orm import Session

from mathwizard.db.mapping import apply_figure_draft, figure_to_domain
from mathwizard.db.tables.figure import FigureSchema
from mathwizard.exceptions import FigureNotFoundError
from mathwizard.models.domain.figure import Figure, FigureDraft
from mathwizard.ports.figure import FigureRepository


class SqlAlchemyFigureRepository(FigureRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, draft: FigureDraft) -> Figure:
        row = FigureSchema()
        apply_figure_draft(row, draft)
        self._session.add(row)
        self._session.flush()
        return figure_to_domain(row)

    def get(self, figure_id: int) -> Figure:
        row = self._session.get(FigureSchema, figure_id)
        if row is None:
            raise FigureNotFoundError(figure_id)
        return figure_to_domain(row)

    def get_by_slug(self, slug: str) -> Figure | None:
        statement = select(FigureSchema).where(FigureSchema.slug == slug)
        row = self._session.scalars(statement).first()
        return None if row is None else figure_to_domain(row)

    def upsert(self, draft: FigureDraft) -> Figure:
        statement = select(FigureSchema).where(FigureSchema.slug == draft.slug)
        row = self._session.scalars(statement).first()
        if row is None:
            row = FigureSchema()
            self._session.add(row)
        apply_figure_draft(row, draft)
        self._session.flush()
        return figure_to_domain(row)

    def list(self) -> list[Figure]:
        statement = select(FigureSchema).order_by(FigureSchema.id)
        return [figure_to_domain(row) for row in self._session.scalars(statement).all()]
