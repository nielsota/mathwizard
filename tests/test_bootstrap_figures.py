from pathlib import Path

import yaml

from mathwizard.db.client import DBClient
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import Settings


def write_figure(figures_dir: Path, slug: str, fn: str) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    (figures_dir / f"{slug}.yaml").write_text(
        yaml.safe_dump(
            {
                "slug": slug,
                "title": slug.title(),
                "spec": {
                    "viewport": {"x": [-5, 5], "y": [-5, 5]},
                    "elements": [{"type": "functionGraph", "fn": fn}],
                },
            }
        )
    )


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'boot.db'}",
        repo_root=tmp_path,
    )


def test_seed_figures_loads_yaml(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    write_figure(settings.figures_dir, "parabool", "x^2")
    db = DBClient(settings.database_url)

    BootstrapService(db, settings).seed_figures()

    figures = db.list_figures()
    assert [f.slug for f in figures] == ["parabool"]
    assert figures[0].spec["elements"][0]["fn"] == "x^2"


def test_seed_figures_is_idempotent(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    write_figure(settings.figures_dir, "parabool", "x^2")
    db = DBClient(settings.database_url)
    service = BootstrapService(db, settings)

    service.seed_figures()
    service.seed_figures()

    assert len(db.list_figures()) == 1


def test_seed_figures_no_dir_is_noop(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    db = DBClient(settings.database_url)
    BootstrapService(db, settings).seed_figures()
    assert db.list_figures() == []
