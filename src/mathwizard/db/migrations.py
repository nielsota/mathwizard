from alembic.config import Config

from mathwizard.settings import Settings


def alembic_config(settings: Settings) -> Config:
    config = Config(str(settings.repo_root / "alembic.ini"))
    config.set_main_option("script_location", str(settings.repo_root / "migrations"))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config
