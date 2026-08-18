import pytest
from sqlalchemy.orm import Session, sessionmaker

from mathwizard.db.repositories.figure import SqlAlchemyFigureRepository
from mathwizard.exceptions import FigureNotFoundError
from mathwizard.models.domain.figure import (
    FigureDraft,
    FigureSpec,
    FunctionGraph,
    Viewport,
)
from mathwizard.ports.figure import FigureRepository


def _spec(fn: str = "x^2") -> FigureSpec:
    return FigureSpec(
        viewport=Viewport(x=(-5.0, 5.0)),
        elements=[FunctionGraph(fn=fn)],
    )


def test_repository_satisfies_the_figure_repository_protocol(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository: FigureRepository = SqlAlchemyFigureRepository(session)

    assert repository is not None


def test_add_round_trips_the_typed_spec(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        created = SqlAlchemyFigureRepository(session).add(
            FigureDraft(
                slug="parabola",
                title="Parabola",
                spec=_spec(),
                description="A parabola",
            )
        )
        session.commit()

    with session_factory() as session:
        stored = SqlAlchemyFigureRepository(session).get(created.id)

    assert stored.slug == "parabola"
    assert stored.description == "A parabola"
    assert stored.spec.viewport.x == (-5.0, 5.0)
    assert stored.spec.elements[0].fn == "x^2"
    assert stored.spec.show_grid is True


def test_get_raises_when_the_figure_is_missing(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        with pytest.raises(FigureNotFoundError):
            SqlAlchemyFigureRepository(session).get(99)


def test_get_by_slug_returns_none_when_missing(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        assert SqlAlchemyFigureRepository(session).get_by_slug("nope") is None


def test_upsert_inserts_when_the_slug_is_new(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        created = SqlAlchemyFigureRepository(session).upsert(
            FigureDraft(slug="parabola", title="Parabola", spec=_spec())
        )
        session.commit()

    assert created.id == 1
    assert created.title == "Parabola"


def test_upsert_updates_in_place_when_the_slug_exists(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        created = SqlAlchemyFigureRepository(session).add(
            FigureDraft(slug="parabola", title="Old", spec=_spec("x^2"))
        )
        session.commit()

    with session_factory() as session:
        updated = SqlAlchemyFigureRepository(session).upsert(
            FigureDraft(slug="parabola", title="New", spec=_spec("x^3"))
        )
        session.commit()

    with session_factory() as session:
        figures = SqlAlchemyFigureRepository(session).list()

    assert updated.id == created.id
    assert updated.title == "New"
    assert updated.spec.elements[0].fn == "x^3"
    assert len(figures) == 1


def test_list_returns_figures_in_id_order(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = SqlAlchemyFigureRepository(session)
        repository.add(FigureDraft(slug="a", title="A", spec=_spec()))
        repository.add(FigureDraft(slug="b", title="B", spec=_spec()))
        session.commit()

    with session_factory() as session:
        figures = SqlAlchemyFigureRepository(session).list()

    assert [figure.slug for figure in figures] == ["a", "b"]
