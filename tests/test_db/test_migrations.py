from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import inspect

from mathwizard.db.base import Base
from mathwizard.db.engine import create_db_engine
from mathwizard.db.migrations import upgrade_schema
from mathwizard.settings import DatabaseSettings, Settings


def _upgrade_to_head(tmp_path: Path) -> str:
    database_url = f"sqlite:///{tmp_path / 'migrated.db'}"
    upgrade_schema(Settings(db=DatabaseSettings(url=database_url)))
    return database_url


def test_upgrade_schema_creates_every_table(tmp_path: Path) -> None:
    engine = create_db_engine(_upgrade_to_head(tmp_path))

    tables = set(inspect(engine).get_table_names())
    engine.dispose()

    assert {
        "users",
        "sessions",
        "teachers",
        "students",
        "questions",
        "question_parts",
        "figures",
    } <= tables


def test_migrations_have_no_drift_against_table_metadata(tmp_path: Path) -> None:
    engine = create_db_engine(_upgrade_to_head(tmp_path))

    with engine.connect() as connection:
        context = MigrationContext.configure(
            connection,
            opts={"compare_type": True, "target_metadata": Base.metadata},
        )
        diff = compare_metadata(context, Base.metadata)
    engine.dispose()

    assert diff == []
