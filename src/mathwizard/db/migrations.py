from alembic.config import Config

from mathwizard.settings import Settings


def alembic_config(settings: Settings) -> Config:
    config = Config(str(settings.paths.repo_root / "alembic.ini"))
    config.set_main_option(
        "script_location", str(settings.paths.repo_root / "migrations")
    )
    config.set_main_option("sqlalchemy.url", settings.db.url)
    return config
