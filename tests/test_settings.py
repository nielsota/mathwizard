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
        "postgresql://app:test@example:5432/app",
    )

    settings = Settings()

    assert settings.db.url == "postgresql://app:test@example:5432/app"


def test_bootstrap_username_defaults_to_niels() -> None:
    settings = BootstrapSettings()

    assert settings.username == "niels"
    assert settings.password == "root"
