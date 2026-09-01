from mathwizard.settings import Settings


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
