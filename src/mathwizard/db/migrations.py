from alembic import command
from alembic.config import Config

from mathwizard.db.engine import sqlalchemy_database_url
from mathwizard.settings import Settings


def alembic_config(settings: Settings) -> Config:
    config = Config(str(settings.paths.repo_root / "alembic.ini"))
    config.set_main_option(
        "script_location", str(settings.paths.repo_root / "migrations")
    )
    database_url = sqlalchemy_database_url(settings.db.url).replace("%", "%%")
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def upgrade_schema(settings: Settings) -> None:
    command.upgrade(alembic_config(settings), "head")
