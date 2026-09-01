from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from mathwizard.db.base import Base
from mathwizard.db.engine import create_db_engine, create_session_factory
from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory

# Nested conftest pytestmark is not inherited on pytest 9, so the hook marks items.
DB_MARKER = pytest.mark.db
TEST_DB_DIR = Path(__file__).parent


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        item_path = getattr(item, "path", None)
        if item_path is not None and item_path.is_relative_to(TEST_DB_DIR):
            item.add_marker(DB_MARKER)


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(engine: Engine) -> sessionmaker[Session]:
    return create_session_factory(engine)


@pytest.fixture
def uow_factory(session_factory: sessionmaker[Session]) -> SqlAlchemyUnitOfWorkFactory:
    return SqlAlchemyUnitOfWorkFactory(session_factory)
