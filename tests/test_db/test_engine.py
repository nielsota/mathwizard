from pathlib import Path

from sqlalchemy.engine import make_url

from mathwizard.db.engine import create_db_engine, sqlalchemy_database_url


def test_sqlalchemy_database_url_leaves_sqlite_unchanged() -> None:
    raw = "sqlite:///data/db/mathwizard.db"

    url = make_url(sqlalchemy_database_url(raw))

    assert url.drivername == "sqlite"
    assert url.database == "data/db/mathwizard.db"


def test_sqlalchemy_database_url_pins_psycopg_on_bare_postgresql() -> None:
    raw = "postgresql://mathwizard:secret@host.docker.internal:5432/mathwizard"

    url = make_url(sqlalchemy_database_url(raw))

    assert url.drivername == "postgresql+psycopg"
    assert url.host == "host.docker.internal"
    assert url.port == 5432
    assert url.database == "mathwizard"
    assert url.username == "mathwizard"
    assert url.password == "secret"


def test_sqlalchemy_database_url_pins_psycopg_on_bare_postgres() -> None:
    raw = "postgres://mathwizard:secret@host.docker.internal:5432/mathwizard"

    url = make_url(sqlalchemy_database_url(raw))

    assert url.drivername == "postgresql+psycopg"
    assert url.host == "host.docker.internal"
    assert url.port == 5432
    assert url.database == "mathwizard"
    assert url.username == "mathwizard"
    assert url.password == "secret"


def test_sqlalchemy_database_url_leaves_explicit_psycopg_driver() -> None:
    raw = "postgresql+psycopg://mathwizard:secret@host.docker.internal:5432/mathwizard"

    url = make_url(sqlalchemy_database_url(raw))

    assert url.drivername == "postgresql+psycopg"


def test_create_db_engine_creates_sqlite_parent_directory(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "mathwizard.db"

    engine = create_db_engine(f"sqlite:///{db_path}")
    engine.dispose()

    assert db_path.parent.is_dir()


def test_create_db_engine_uses_psycopg_for_prod_style_url() -> None:
    engine = create_db_engine(
        "postgresql://mathwizard:secret@host.docker.internal:5432/mathwizard"
    )
    try:
        assert engine.dialect.name == "postgresql"
        assert engine.dialect.driver == "psycopg"
        assert engine.url.host == "host.docker.internal"
        assert engine.url.database == "mathwizard"
    finally:
        engine.dispose()
