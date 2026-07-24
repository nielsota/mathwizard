from pathlib import Path

import pytest

from mathwizard.db.client import DBClient
from mathwizard.exceptions import DuplicateFigureSlugError, FigureNotFoundError
from mathwizard.models.figure import FigureCreateRequest
from mathwizard.services.figure import FigureService


def make_service(tmp_path: Path) -> FigureService:
    return FigureService(DBClient(f"sqlite:///{tmp_path / 'figures.db'}"))


def make_request(slug: str = "parabool") -> FigureCreateRequest:
    return FigureCreateRequest.model_validate(
        {
            "slug": slug,
            "title": "Parabool",
            "spec": {
                "viewport": {"x": [-5, 5]},
                "elements": [{"type": "functionGraph", "fn": "x^2"}],
            },
        }
    )


def test_create_then_get_and_list(tmp_path: Path) -> None:
    service = make_service(tmp_path)

    created = service.create_figure(make_request())
    fetched = service.get_figure(created.id)
    listing = service.list_figures()

    assert fetched.slug == "parabool"
    assert fetched.spec.elements[0].fn == "x^2"
    assert [summary.slug for summary in listing.figures] == ["parabool"]


def test_create_duplicate_slug_raises(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    service.create_figure(make_request())
    with pytest.raises(DuplicateFigureSlugError):
        service.create_figure(make_request())


def test_get_missing_raises(tmp_path: Path) -> None:
    service = make_service(tmp_path)
    with pytest.raises(FigureNotFoundError):
        service.get_figure(123)
