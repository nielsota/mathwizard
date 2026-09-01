from datetime import timedelta

import pytest

from mathwizard.clock import utcnow
from mathwizard.exceptions import (
    AuthenticationError,
    BootstrapTeacherMissingError,
    DuplicateUsernameError,
)
from mathwizard.services.auth import AuthService, BcryptPasswordHasher
from mathwizard.settings import (
    BootstrapSettings,
    DatabaseSettings,
    Settings,
    WebSettings,
)
from tests.fakes import FakePasswordHasher, FakeUnitOfWork


def _hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


def _settings() -> Settings:
    return Settings(
        db=DatabaseSettings(url="sqlite:///unused.db"),
        web=WebSettings(cookie_secure=False, session_ttl_days=7),
        bootstrap=BootstrapSettings(username="niels", password="root"),
    )


def _service() -> AuthService:
    return AuthService(_settings(), hasher=_hasher())


def _seed_root(uow: FakeUnitOfWork) -> None:
    hasher = _hasher()
    with uow:
        uow.users.add(username="root", password_hash=hasher.hash("secret"))
        uow.commit()


def _seed_teacher(uow: FakeUnitOfWork) -> None:
    hasher = _hasher()
    with uow:
        user = uow.users.add(username="niels", password_hash=hasher.hash("secret"))
        uow.roster.add_teacher(user.id)
        uow.commit()


def test_login_accepts_a_password_hashed_by_the_injected_hasher() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)

    result = _service().login(uow, "root", "secret")

    assert result.user.username == "root"


def test_login_returns_a_session_token_and_cookie_settings() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)

    result = _service().login(uow, "root", "secret")

    assert result.user.username == "root"
    assert result.session_token
    assert result.max_age_seconds == 7 * 24 * 60 * 60
    assert result.cookie_secure is False


def test_login_commits_the_new_session() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)

    _service().login(uow, "root", "secret")

    assert uow.committed is True


def test_login_rejects_a_wrong_password() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)

    with pytest.raises(AuthenticationError):
        _service().login(uow, "root", "wrong")


def test_login_rejects_an_unknown_username() -> None:
    uow = FakeUnitOfWork()

    with pytest.raises(AuthenticationError):
        _service().login(uow, "nobody", "secret")


def test_get_current_user_resolves_an_active_session() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)
    service = _service()
    token = service.login(uow, "root", "secret").session_token

    user = service.get_current_user(uow, token)

    assert user.username == "root"


def test_get_current_user_rejects_a_missing_token() -> None:
    uow = FakeUnitOfWork()

    with pytest.raises(AuthenticationError, match="Not authenticated"):
        _service().get_current_user(uow, None)


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
        _service().get_current_user(uow, "stale")


def test_logout_revokes_the_session() -> None:
    uow = FakeUnitOfWork()
    _seed_root(uow)
    service = _service()
    token = service.login(uow, "root", "secret").session_token

    service.logout(uow, token)

    with pytest.raises(AuthenticationError):
        service.get_current_user(uow, token)


def test_logout_without_a_token_is_a_no_op() -> None:
    uow = FakeUnitOfWork()

    _service().logout(uow, None)

    assert uow.committed is False


def test_bcrypt_password_hasher_round_trip() -> None:
    hasher = BcryptPasswordHasher()

    hashed = hasher.hash("s3cret")

    assert hashed != "s3cret"
    assert hasher.verify("s3cret", hashed) is True
    assert hasher.verify("wrong", hashed) is False
    assert hasher.verify("s3cret", hasher.dummy_hash) is False


def test_default_auth_service_accepts_a_bcrypt_password() -> None:
    uow = FakeUnitOfWork()
    with uow:
        uow.users.add(
            username="root",
            password_hash=BcryptPasswordHasher().hash("s3cret"),
        )
        uow.commit()

    result = AuthService(_settings()).login(uow, "root", "s3cret")

    assert result.user.username == "root"


def test_signup_creates_a_student_session() -> None:
    uow = FakeUnitOfWork()
    _seed_teacher(uow)

    result = _service().signup(uow, "ada", "password1")

    assert result.user.username == "ada"
    assert result.session_token
    assert result.max_age_seconds == 7 * 24 * 60 * 60
    assert result.cookie_secure is False
    assert result.user.password_hash == "fake:password1"


def test_signup_assigns_the_student_to_the_bootstrap_teacher() -> None:
    uow = FakeUnitOfWork()
    _seed_teacher(uow)
    result = _service().signup(uow, "ada", "password1")

    with uow:
        student = uow.roster.get_student_by_user_id(result.user.id)
        teacher_user = uow.users.get_by_username("niels")
        assert teacher_user is not None
        teacher = uow.roster.get_teacher_by_user_id(teacher_user.id)
        assert teacher is not None
        assert student is not None
        assert student.teacher_id == teacher.id


def test_signup_commits() -> None:
    uow = FakeUnitOfWork()
    _seed_teacher(uow)

    _service().signup(uow, "ada", "password1")

    assert uow.committed is True


def test_signup_strips_username() -> None:
    uow = FakeUnitOfWork()
    _seed_teacher(uow)

    result = _service().signup(uow, "  ada  ", "password1")

    assert result.user.username == "ada"


def test_signup_rejects_a_duplicate_username() -> None:
    uow = FakeUnitOfWork()
    _seed_teacher(uow)
    _service().signup(uow, "ada", "password1")

    with pytest.raises(DuplicateUsernameError):
        _service().signup(uow, "ada", "password1")


def test_signup_rejects_the_teacher_username() -> None:
    uow = FakeUnitOfWork()
    _seed_teacher(uow)

    with pytest.raises(DuplicateUsernameError):
        _service().signup(uow, "niels", "password1")


def test_signup_fails_closed_without_a_bootstrap_user() -> None:
    uow = FakeUnitOfWork()

    with pytest.raises(BootstrapTeacherMissingError):
        _service().signup(uow, "ada", "password1")

    with uow:
        assert uow.users.get_by_username("ada") is None


def test_signup_fails_closed_without_a_teacher_profile() -> None:
    uow = FakeUnitOfWork()
    hasher = _hasher()
    with uow:
        uow.users.add(username="niels", password_hash=hasher.hash("secret"))
        uow.commit()

    with pytest.raises(BootstrapTeacherMissingError):
        _service().signup(uow, "ada", "password1")

    with uow:
        assert uow.users.get_by_username("ada") is None
