from tests.app_client import make_settings, make_test_client
from tests.fakes import FakePasswordHasher, FakeUnitOfWorkFactory

from mathwizard.ports.unit_of_work import UnitOfWorkFactory


def seed_user(uow_factory: UnitOfWorkFactory) -> None:
    hasher = FakePasswordHasher()
    with uow_factory() as uow:
        user = uow.users.add(username="root", password_hash=hasher.hash("secret"))
        uow.roster.add_teacher(user.id)
        uow.commit()


def test_login_sets_cookie_and_me_returns_user() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_user(uow_factory)
    settings = make_settings()
    client = make_test_client(uow_factory, settings=settings)

    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )

    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "root", "role": "teacher"}
    cookie = response.headers["set-cookie"]
    assert f"{settings.web.session_cookie_name}=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie

    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json() == {"id": 1, "username": "root", "role": "teacher"}


def test_login_never_returns_the_password_hash() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_user(uow_factory)
    client = make_test_client(uow_factory)

    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )

    assert "password_hash" not in response.json()


def test_login_rejects_invalid_credentials() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_user(uow_factory)
    client = make_test_client(uow_factory)

    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"
    assert "set-cookie" not in response.headers


def test_unknown_user_and_wrong_password_share_error() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_user(uow_factory)
    client = make_test_client(uow_factory)

    response = client.post(
        "/auth/login",
        json={"username": "missing", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_logout_revokes_session_and_clears_cookie() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_user(uow_factory)
    settings = make_settings()
    client = make_test_client(uow_factory, settings=settings)
    login = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )
    assert login.status_code == 200
    session_token = client.cookies.get(settings.web.session_cookie_name)
    assert session_token is not None

    logout = client.post("/auth/logout")

    assert logout.status_code == 204
    assert f"{settings.web.session_cookie_name}=" in logout.headers["set-cookie"]

    me = client.get("/auth/me")
    assert me.status_code == 401

    client.cookies.set(settings.web.session_cookie_name, session_token)
    stale_me = client.get("/auth/me")
    assert stale_me.status_code == 401


def test_auth_routes_use_configured_session_cookie_name() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_user(uow_factory)
    settings = make_settings(session_cookie_name="custom_session")
    client = make_test_client(uow_factory, settings=settings)

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
