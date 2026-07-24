from sqlmodel import Session as DBSession
from sqlmodel import select

from mathwizard.db.mixins.base import NeedsEngine
from mathwizard.exceptions import FigureNotFoundError
from mathwizard.models.db import Figure


class FiguresMixin(NeedsEngine):

    def create_figure(
        self,
        slug: str,
        title: str,
        spec: dict,
        *,
        description: str | None = None,
        question_id: int | None = None,
        part_id: int | None = None,
    ) -> Figure:
        figure = Figure(
            slug=slug,
            title=title,
            spec=spec,
            description=description,
            question_id=question_id,
            part_id=part_id,
        )
        with DBSession(self.engine) as session:
            session.add(figure)
            session.commit()
            session.refresh(figure)
            return figure

    def get_figure(self, figure_id: int) -> Figure:
        with DBSession(self.engine) as session:
            figure = session.get(Figure, figure_id)
            if figure is None:
                raise FigureNotFoundError(figure_id)
            return figure

    def get_figure_by_slug(self, slug: str) -> Figure | None:
        with DBSession(self.engine) as session:
            statement = select(Figure).where(Figure.slug == slug)
            return session.exec(statement).first()

    def list_figures(self) -> list[Figure]:
        with DBSession(self.engine) as session:
            statement = select(Figure).order_by(Figure.id)
            return list(session.exec(statement).all())

    def upsert_figure(
        self,
        slug: str,
        title: str,
        spec: dict,
        *,
        description: str | None = None,
        question_id: int | None = None,
        part_id: int | None = None,
    ) -> Figure:
        with DBSession(self.engine) as session:
            statement = select(Figure).where(Figure.slug == slug)
            figure = session.exec(statement).first()
            if figure is None:
                figure = Figure(slug=slug)
                session.add(figure)
            figure.title = title
            figure.spec = spec
            figure.description = description
            figure.question_id = question_id
            figure.part_id = part_id
            session.commit()
            session.refresh(figure)
            return figure
