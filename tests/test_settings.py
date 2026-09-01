import pytest

from mathwizard.settings import BootstrapSettings, Settings


def test_settings_repo_root_points_to_project_root() -> None:
    settings = Settings()

    assert (settings.paths.repo_root / "pyproject.toml").exists()
    assert settings.paths.practice_dir.exists()
    assert (settings.paths.practice_dir / "derivatives" / "p1.yaml").exists()
    assert (
        settings.paths.frontend_dist_dir
        == settings.paths.repo_root / "frontend" / "dist"
    )


def test_default_database_url_uses_data_db_directory() -> None:
    settings = Settings()

    assert settings.db.url == "sqlite:///data/db/mathwizard.db"


def test_database_url_reads_db_url_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DB__URL",
        "postgresql://mathwizard:secret@host.docker.internal:5432/mathwizard",
    )

    settings = Settings()

    assert (
        settings.db.url
        == "postgresql://mathwizard:secret@host.docker.internal:5432/mathwizard"
    )


def test_bootstrap_username_defaults_to_niels() -> None:
    settings = BootstrapSettings()

    assert settings.username == "niels"
    assert settings.password == "root"
