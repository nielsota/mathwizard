import pytest
from tests.fakes import FakeUnitOfWork

from mathwizard.exceptions import DuplicateFigureSlugError, FigureNotFoundError
from mathwizard.models.domain.figure import (
    FigureDraft,
    FigureSpec,
    FunctionGraph,
    Viewport,
)
from mathwizard.services.figure import FigureService


def _spec(fn: str = "x^2") -> FigureSpec:
    return FigureSpec(viewport=Viewport(x=(-5.0, 5.0)), elements=[FunctionGraph(fn=fn)])


def test_create_figure_returns_the_persisted_entity() -> None:
    uow = FakeUnitOfWork()

    figure = FigureService().create_figure(
        uow,
        FigureDraft(slug="parabola", title="Parabola", spec=_spec(), description="d"),
    )

    assert figure.id == 1
    assert figure.slug == "parabola"
    assert figure.description == "d"


def test_create_figure_commits() -> None:
    uow = FakeUnitOfWork()

    FigureService().create_figure(
        uow, FigureDraft(slug="parabola", title="Parabola", spec=_spec())
    )

    assert uow.committed is True


def test_create_figure_rejects_a_duplicate_slug() -> None:
    uow = FakeUnitOfWork()
    service = FigureService()
    service.create_figure(
        uow, FigureDraft(slug="parabola", title="Parabola", spec=_spec())
    )

    with pytest.raises(DuplicateFigureSlugError):
        service.create_figure(
            uow, FigureDraft(slug="parabola", title="Other", spec=_spec())
        )


def test_list_figures_returns_domain_entities() -> None:
    uow = FakeUnitOfWork()
    service = FigureService()
    service.create_figure(uow, FigureDraft(slug="a", title="A", spec=_spec()))
    service.create_figure(uow, FigureDraft(slug="b", title="B", spec=_spec()))

    figures = service.list_figures(uow)

    assert [figure.slug for figure in figures] == ["a", "b"]


def test_get_figure_raises_when_missing() -> None:
    uow = FakeUnitOfWork()

    with pytest.raises(FigureNotFoundError):
        FigureService().get_figure(uow, 99)
