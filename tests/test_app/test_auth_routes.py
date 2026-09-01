from tests.app_client import make_settings, make_test_client
from tests.fakes import FakePasswordHasher, FakeUnitOfWorkFactory

from mathwizard.app.routes.roster import router as roster_router
from mathwizard.ports.unit_of_work import UnitOfWorkFactory
from mathwizard.settings import Settings


def seed_user(uow_factory: UnitOfWorkFactory) -> None:
    hasher = FakePasswordHasher()
    with uow_factory() as uow:
        user = uow.users.add(username="root", password_hash=hasher.hash("secret"))
        uow.roster.add_teacher(user.id)
        uow.commit()


def seed_teacher(
    uow_factory: UnitOfWorkFactory, settings: Settings | None = None
) -> None:
    settings = settings or make_settings()
    hasher = FakePasswordHasher()
    with uow_factory() as uow:
        user = uow.users.add(
            username=settings.bootstrap.username,
            password_hash=hasher.hash("secret"),
        )
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


def test_login_rejects_overlong_password() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_user(uow_factory)
    client = make_test_client(uow_factory)

    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "x" * 200},
    )

    assert response.status_code == 422
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


def test_signup_sets_cookie_and_returns_student() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher(uow_factory)
    settings = make_settings()
    client = make_test_client(uow_factory, settings=settings)

    response = client.post(
        "/auth/signup",
        json={
            "username": "ada",
            "password": "password1",
            "password_confirm": "password1",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"id": 2, "username": "ada", "role": "student"}
    cookie = response.headers["set-cookie"]
    assert f"{settings.web.session_cookie_name}=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie

    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json() == {"id": 2, "username": "ada", "role": "student"}


def test_signup_student_appears_on_teacher_roster() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher(uow_factory)
    client = make_test_client(uow_factory, roster_router)

    client.post(
        "/auth/signup",
        json={
            "username": "ada",
            "password": "password1",
            "password_confirm": "password1",
        },
    )
    login = client.post(
        "/auth/login",
        json={"username": "niels", "password": "secret"},
    )
    assert login.status_code == 200

    roster = client.get("/api/v1/roster/students")
    assert roster.status_code == 200
    assert any(row["username"] == "ada" for row in roster.json()["students"])


def test_signup_rejects_duplicate_username() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher(uow_factory)
    client = make_test_client(uow_factory)
    payload = {
        "username": "ada",
        "password": "password1",
        "password_confirm": "password1",
    }
    assert client.post("/auth/signup", json=payload).status_code == 200

    response = client.post("/auth/signup", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Username 'ada' is already taken"
    assert "set-cookie" not in response.headers


def test_signup_rejects_password_mismatch() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher(uow_factory)
    client = make_test_client(uow_factory)

    response = client.post(
        "/auth/signup",
        json={
            "username": "ada",
            "password": "password1",
            "password_confirm": "password2",
        },
    )

    assert response.status_code == 422
    assert "set-cookie" not in response.headers


def test_signup_rejects_short_password() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher(uow_factory)
    client = make_test_client(uow_factory)

    response = client.post(
        "/auth/signup",
        json={
            "username": "ada",
            "password": "short",
            "password_confirm": "short",
        },
    )

    assert response.status_code == 422


def test_signup_rejects_overlong_password() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher(uow_factory)
    client = make_test_client(uow_factory)
    password = "x" * 200

    response = client.post(
        "/auth/signup",
        json={
            "username": "ada",
            "password": password,
            "password_confirm": password,
        },
    )

    assert response.status_code == 422
    assert "set-cookie" not in response.headers


def test_signup_rejects_blank_username() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher(uow_factory)
    client = make_test_client(uow_factory)

    response = client.post(
        "/auth/signup",
        json={
            "username": "   ",
            "password": "password1",
            "password_confirm": "password1",
        },
    )

    assert response.status_code == 422


def test_signup_fails_closed_without_teacher() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    client = make_test_client(uow_factory)

    response = client.post(
        "/auth/signup",
        json={
            "username": "ada",
            "password": "password1",
            "password_confirm": "password1",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Bootstrap teacher 'niels' is not configured"
    with uow_factory() as uow:
        assert uow.users.get_by_username("ada") is None
