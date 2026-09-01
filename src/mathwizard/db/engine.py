from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session, sessionmaker


def sqlalchemy_database_url(database_url: str) -> str:
    url = _with_psycopg_driver(make_url(database_url))
    return url.render_as_string(hide_password=False)


def create_db_engine(database_url: str, echo: bool = False) -> Engine:
    url = _with_psycopg_driver(make_url(database_url))
    if url.get_backend_name() == "sqlite":
        if url.database not in (None, ":memory:"):
            Path(url.database).parent.mkdir(parents=True, exist_ok=True)
        return create_engine(
            url,
            echo=echo,
            connect_args={"check_same_thread": False},
        )
    return create_engine(url, echo=echo, pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def _with_psycopg_driver(url: URL) -> URL:
    if url.get_backend_name() == "postgresql" and "+" not in url.drivername:
        return url.set(drivername="postgresql+psycopg")
    return url
