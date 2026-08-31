from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from mathwizard.app.auth import router
from mathwizard.db.base import Base
from mathwizard.db.engine import create_db_engine, create_session_factory
from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory
from mathwizard.services.auth import AuthService, hash_password
from mathwizard.services.user import UserService
from mathwizard.settings import Settings


def make_uow_factory(tmp_path: Path) -> SqlAlchemyUnitOfWorkFactory:
    engine: Engine = create_db_engine(f"sqlite:///{tmp_path / 'api.db'}")
    Base.metadata.create_all(engine)
    return SqlAlchemyUnitOfWorkFactory(create_session_factory(engine))


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'api.db'}",
        cookie_secure=False,
        session_ttl_days=7,
    )


def make_client(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
    settings: Settings,
) -> TestClient:
    app = FastAPI()
    app.state.uow_factory = uow_factory
    app.state.auth_service = AuthService(settings)
    app.state.user_service = UserService()
    app.include_router(router)
    return TestClient(app)


def seed_user(uow_factory: SqlAlchemyUnitOfWorkFactory) -> None:
    with uow_factory() as uow:
        user = uow.users.add(username="root", password_hash=hash_password("secret"))
        uow.roster.add_teacher(user.id)
        uow.commit()


def test_login_sets_cookie_and_me_returns_user(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_user(uow_factory)
    settings = make_settings(tmp_path)
    client = make_client(uow_factory, settings)

    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )

    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "root", "role": "teacher"}
    cookie = response.headers["set-cookie"]
    assert f"{settings.session_cookie_name}=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie

    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json() == {"id": 1, "username": "root", "role": "teacher"}


def test_login_never_returns_the_password_hash(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_user(uow_factory)
    client = make_client(uow_factory, make_settings(tmp_path))

    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )

    assert "password_hash" not in response.json()


def test_login_rejects_invalid_credentials(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_user(uow_factory)
    client = make_client(uow_factory, make_settings(tmp_path))

    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"
    assert "set-cookie" not in response.headers


def test_unknown_user_and_wrong_password_share_error(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_user(uow_factory)
    client = make_client(uow_factory, make_settings(tmp_path))

    response = client.post(
        "/auth/login",
        json={"username": "missing", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_logout_revokes_session_and_clears_cookie(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_user(uow_factory)
    settings = make_settings(tmp_path)
    client = make_client(uow_factory, settings)
    login = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )
    assert login.status_code == 200
    session_token = client.cookies.get(settings.session_cookie_name)
    assert session_token is not None

    logout = client.post("/auth/logout")

    assert logout.status_code == 204
    assert f"{settings.session_cookie_name}=" in logout.headers["set-cookie"]

    me = client.get("/auth/me")
    assert me.status_code == 401

    client.cookies.set(settings.session_cookie_name, session_token)
    stale_me = client.get("/auth/me")
    assert stale_me.status_code == 401


def test_auth_routes_use_configured_session_cookie_name(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_user(uow_factory)
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'api.db'}",
        session_cookie_name="custom_session",
        cookie_secure=False,
        session_ttl_days=7,
    )
    client = make_client(uow_factory, settings)

    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )

    assert response.status_code == 200
    assert "custom_session=" in response.headers["set-cookie"]
    assert client.cookies.get("custom_session") is not None
    assert client.cookies.get("mw_session") is None

    me = client.get("/auth/me")
    assert me.status_code == 200
