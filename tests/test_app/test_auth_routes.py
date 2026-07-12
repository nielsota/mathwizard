from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mathwizard.app.auth import router
from mathwizard.db.client import DBClient
from mathwizard.services.auth import AuthService, hash_password
from mathwizard.settings import Settings


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'auth-routes.db'}")


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'auth-routes.db'}",
        cookie_secure=False,
        session_ttl_days=7,
    )


def make_client(db: DBClient, settings: Settings) -> TestClient:
    app = FastAPI()
    app.state.auth_service = AuthService(db, settings)
    app.include_router(router)
    return TestClient(app)


def seed_user(db: DBClient) -> None:
    db.create_user("root", hash_password("secret"))


def test_login_sets_cookie_and_me_returns_user(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_user(db)
    settings = make_settings(tmp_path)
    client = make_client(db, settings)

    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )

    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "root"}
    cookie = response.headers["set-cookie"]
    assert f"{settings.session_cookie_name}=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie

    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json() == {"id": 1, "username": "root"}


def test_login_rejects_invalid_credentials(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_user(db)
    client = make_client(db, make_settings(tmp_path))

    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"
    assert "set-cookie" not in response.headers


def test_unknown_user_and_wrong_password_share_error(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_user(db)
    client = make_client(db, make_settings(tmp_path))

    response = client.post(
        "/auth/login",
        json={"username": "missing", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_logout_revokes_session_and_clears_cookie(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_user(db)
    settings = make_settings(tmp_path)
    client = make_client(db, settings)
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
    db = make_db(tmp_path)
    seed_user(db)
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'auth-routes.db'}",
        session_cookie_name="custom_session",
        cookie_secure=False,
        session_ttl_days=7,
    )
    client = make_client(db, settings)

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
