from mathwizard.settings import Settings


def test_settings_repo_root_points_to_project_root() -> None:
    settings = Settings(
        openai_api_key="dummy",
        session_secret_key="dummy",
        cognito_domain="dummy",
        cognito_client_id="dummy",
        cognito_client_secret="dummy",
        cognito_user_pool_id="dummy",
    )

    assert settings.repo_root.name == "question-model-metadata"
    assert settings.practice_dir.exists()
    assert (settings.practice_dir / "derivatives" / "p1.yaml").exists()
