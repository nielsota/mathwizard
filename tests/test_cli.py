from mathwizard import cli
from mathwizard.settings import DatabaseSettings, Settings


def test_db_upgrade_hides_database_password(monkeypatch, capsys) -> None:
    settings = Settings(
        db=DatabaseSettings(url="postgresql://app:test@example:5432/app")
    )
    monkeypatch.setattr(cli, "get_settings", lambda: settings)
    monkeypatch.setattr(cli, "upgrade_schema", lambda configured_settings: None)

    cli.db_upgrade()

    output = capsys.readouterr().out
    assert "postgresql://app:***@example:5432/app" in output
    assert "app:test@" not in output
