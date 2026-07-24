from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.exceptions import FigureNotFoundError


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'figures.db'}")


SPEC = {
    "viewport": {"x": [-5, 5], "y": [-5, 5]},
    "show_grid": True,
    "x_label": "x",
    "y_label": "y",
    "elements": [{"type": "functionGraph", "fn": "x^2", "domain": None, "color": None}],
}


def test_create_and_get_figure(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    figure = db.create_figure("parabool", "Parabool", SPEC, description="y = x^2")

    assert figure.id is not None
    saved = db.get_figure(figure.id)
    assert saved.slug == "parabool"
    assert saved.title == "Parabool"
    assert saved.description == "y = x^2"
    assert saved.spec["elements"][0]["fn"] == "x^2"
    assert saved.question_id is None
    assert saved.part_id is None


def test_get_missing_figure_raises(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    try:
        db.get_figure(999)
    except FigureNotFoundError as exc:
        assert exc.figure_id == 999
    else:
        raise AssertionError("expected FigureNotFoundError")


def test_get_figure_by_slug(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    db.create_figure("parabool", "Parabool", SPEC)
    assert db.get_figure_by_slug("parabool") is not None
    assert db.get_figure_by_slug("bestaat-niet") is None


def test_upsert_figure_is_idempotent_on_slug(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    first = db.upsert_figure("parabool", "Parabool", SPEC)
    second = db.upsert_figure("parabool", "Parabool (herzien)", SPEC)

    assert first.id == second.id
    assert len(db.list_figures()) == 1
    assert db.get_figure(first.id).title == "Parabool (herzien)"
