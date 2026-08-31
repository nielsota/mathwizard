from mathwizard.settings import Settings


def test_settings_repo_root_points_to_project_root() -> None:
    settings = Settings()

    assert (settings.paths.repo_root / "pyproject.toml").exists()
    assert settings.paths.practice_dir.exists()
    assert (settings.paths.practice_dir / "derivatives" / "p1.yaml").exists()
