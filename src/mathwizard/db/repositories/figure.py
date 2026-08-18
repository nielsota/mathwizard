from sqlalchemy import select
from sqlalchemy.orm import Session

from mathwizard.db.tables.figure import FigureSchema
from mathwizard.exceptions import FigureNotFoundError
from mathwizard.models.domain.figure import Figure, FigureDraft, FigureSpec


def _to_domain(row: FigureSchema) -> Figure:
    return Figure(
        id=row.id,
        slug=row.slug,
        title=row.title,
        spec=FigureSpec.model_validate(row.spec),
        description=row.description,
        question_id=row.question_id,
        part_id=row.part_id,
    )


def _apply(row: FigureSchema, draft: FigureDraft) -> None:
    row.title = draft.title
    row.spec = draft.spec.model_dump()
    row.description = draft.description
    row.question_id = draft.question_id
    row.part_id = draft.part_id


class SqlAlchemyFigureRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, draft: FigureDraft) -> Figure:
        row = FigureSchema(slug=draft.slug)
        _apply(row, draft)
        self._session.add(row)
        self._session.flush()
        return _to_domain(row)

    def get(self, figure_id: int) -> Figure:
        row = self._session.get(FigureSchema, figure_id)
        if row is None:
            raise FigureNotFoundError(figure_id)
        return _to_domain(row)

    def get_by_slug(self, slug: str) -> Figure | None:
        statement = select(FigureSchema).where(FigureSchema.slug == slug)
        row = self._session.scalars(statement).first()
        return None if row is None else _to_domain(row)

    def upsert(self, draft: FigureDraft) -> Figure:
        statement = select(FigureSchema).where(FigureSchema.slug == draft.slug)
        row = self._session.scalars(statement).first()
        if row is None:
            row = FigureSchema(slug=draft.slug)
            self._session.add(row)
        _apply(row, draft)
        self._session.flush()
        return _to_domain(row)

    def list(self) -> list[Figure]:
        statement = select(FigureSchema).order_by(FigureSchema.id)
        return [_to_domain(row) for row in self._session.scalars(statement).all()]
