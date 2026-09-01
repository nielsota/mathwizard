from pathlib import Path

import yaml

from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import DatabaseSettings, PathSettings, Settings
from tests.fakes import FakePasswordHasher, FakeUnitOfWorkFactory


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
        db=DatabaseSettings(url="sqlite:///unused.db"),
        paths=PathSettings(repo_root=tmp_path),
    )


def test_seed_figures_loads_yaml(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    write_figure(settings.paths.figures_dir, "parabool", "x^2")
    uow_factory = FakeUnitOfWorkFactory()

    BootstrapService(settings, hasher=FakePasswordHasher()).seed_figures(uow_factory())

    with uow_factory() as uow:
        figures = uow.figures.list()
    assert [figure.slug for figure in figures] == ["parabool"]
    assert figures[0].spec.elements[0].fn == "x^2"


def test_seed_figures_is_idempotent(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    write_figure(settings.paths.figures_dir, "parabool", "x^2")
    service = BootstrapService(settings, hasher=FakePasswordHasher())
    uow_factory = FakeUnitOfWorkFactory()

    service.seed_figures(uow_factory())
    service.seed_figures(uow_factory())

    with uow_factory() as uow:
        assert len(uow.figures.list()) == 1


def test_seed_figures_without_a_directory_is_a_noop(tmp_path: Path) -> None:
    uow_factory = FakeUnitOfWorkFactory()
    BootstrapService(make_settings(tmp_path), hasher=FakePasswordHasher()).seed_figures(
        uow_factory()
    )

    with uow_factory() as uow:
        assert uow.figures.list() == []
