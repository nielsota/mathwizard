from datetime import timedelta

import pytest

from mathwizard.clock import utcnow
from mathwizard.exceptions import AuthenticationError
from mathwizard.services.auth import AuthService, hash_password
from mathwizard.settings import Settings
from tests.fakes import FakeUnitOfWork


def _settings() -> Settings:
    return Settings(
        database_url="sqlite:///unused.db",
        cookie_secure=False,
        session_ttl_days=7,
    )


def _seed_root(uow: FakeUnitOfWork) -> None:
    with uow:
        uow.users.add(username="root", password_hash=hash_password("secret"))
        uow.commit()


def test_login_returns_a_session_token_and_cookie_settings() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)

    result = AuthService(_settings()).login(uow, "root", "secret")

    assert result.user.username == "root"
    assert result.session_token
    assert result.max_age_seconds == 7 * 24 * 60 * 60
    assert result.cookie_secure is False


def test_login_commits_the_new_session() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)

    AuthService(_settings()).login(uow, "root", "secret")

    assert uow.committed is True


def test_login_rejects_a_wrong_password() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)

    with pytest.raises(AuthenticationError):
        AuthService(_settings()).login(uow, "root", "wrong")


def test_login_rejects_an_unknown_username() -> None:
    uow = FakeUnitOfWork()

    with pytest.raises(AuthenticationError):
        AuthService(_settings()).login(uow, "nobody", "secret")


def test_get_current_user_resolves_an_active_session() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)
    service = AuthService(_settings())
    token = service.login(uow, "root", "secret").session_token

    user = service.get_current_user(uow, token)

    assert user.username == "root"


def test_get_current_user_rejects_a_missing_token() -> None:
    uow = FakeUnitOfWork()

    with pytest.raises(AuthenticationError, match="Not authenticated"):
        AuthService(_settings()).get_current_user(uow, None)


def test_get_current_user_rejects_an_expired_session() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)
    now = utcnow()
    with uow:
        uow.sessions.add(
            token="stale",
            user_id=1,
            created_at=now - timedelta(days=8),
            expires_at=now - timedelta(days=1),
        )
        uow.commit()

    with pytest.raises(AuthenticationError, match="Invalid session"):
        AuthService(_settings()).get_current_user(uow, "stale")


def test_logout_revokes_the_session() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)
    service = AuthService(_settings())
    token = service.login(uow, "root", "secret").session_token

    service.logout(uow, token)

    with pytest.raises(AuthenticationError):
        service.get_current_user(uow, token)


def test_logout_without_a_token_is_a_no_op() -> None:
    uow = FakeUnitOfWork()

    AuthService(_settings()).logout(uow, None)

    assert uow.committed is False
