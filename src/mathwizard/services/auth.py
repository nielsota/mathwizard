import secrets
from dataclasses import dataclass
from datetime import timedelta
from functools import cached_property

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from mathwizard.clock import utcnow
from mathwizard.exceptions import (
    AuthenticationError,
    BootstrapTeacherMissingError,
    DuplicateUsernameError,
    UserNotFoundError,
)
from mathwizard.models.domain.user import User
from mathwizard.ports.password import PasswordHasher
from mathwizard.ports.unit_of_work import AuthUnitOfWork
from mathwizard.settings import Settings

_BCRYPT = PasswordHash((BcryptHasher(),))


class BcryptPasswordHasher(PasswordHasher):
    @cached_property
    def dummy_hash(self) -> str:
        return _BCRYPT.hash("__not_a_real_password__")

    def hash(self, plain: str) -> str:
        return _BCRYPT.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return _BCRYPT.verify(plain, hashed)


@dataclass(frozen=True)
class LoginResult:
    user: User
    session_token: str
    max_age_seconds: int
    cookie_secure: bool


class AuthService:
    def __init__(
        self,
        settings: Settings,
        hasher: PasswordHasher | None = None,
    ) -> None:
        self.settings = settings
        self._hasher: PasswordHasher = hasher or BcryptPasswordHasher()

    @property
    def session_cookie_name(self) -> str:
        return self.settings.web.session_cookie_name

    def login(self, uow: AuthUnitOfWork, username: str, password: str) -> LoginResult:
        ttl = timedelta(days=self.settings.web.session_ttl_days)
        with uow:
            user = uow.users.get_by_username(username)
            # An unknown username still pays for a hash comparison, so the response
            # time does not reveal which usernames exist.
            hashed = user.password_hash if user is not None else self._hasher.dummy_hash
            password_ok = self._hasher.verify(password, hashed)
            if user is None or not password_ok:
                raise AuthenticationError("Invalid username or password")
            now = utcnow()
            session = uow.sessions.add(
                token=secrets.token_urlsafe(32),
                user_id=user.id,
                created_at=now,
                expires_at=now + ttl,
            )
            uow.commit()
        return LoginResult(
            user=user,
            session_token=session.token,
            max_age_seconds=int(ttl.total_seconds()),
            cookie_secure=self.settings.web.cookie_secure,
        )

    def signup(self, uow: AuthUnitOfWork, username: str, password: str) -> LoginResult:
        username = username.strip()
        ttl = timedelta(days=self.settings.web.session_ttl_days)
        teacher_username = self.settings.bootstrap.username
        with uow:
            if uow.users.get_by_username(username) is not None:
                raise DuplicateUsernameError(username)
            teacher_user = uow.users.get_by_username(teacher_username)
            if teacher_user is None:
                raise BootstrapTeacherMissingError(teacher_username)
            teacher = uow.roster.get_teacher_by_user_id(teacher_user.id)
            if teacher is None:
                raise BootstrapTeacherMissingError(teacher_username)
            user = uow.users.add(
                username=username,
                password_hash=self._hasher.hash(password),
            )
            uow.roster.add_student(user.id, teacher.id)
            now = utcnow()
            session = uow.sessions.add(
                token=secrets.token_urlsafe(32),
                user_id=user.id,
                created_at=now,
                expires_at=now + ttl,
            )
            uow.commit()
        return LoginResult(
            user=user,
            session_token=session.token,
            max_age_seconds=int(ttl.total_seconds()),
            cookie_secure=self.settings.web.cookie_secure,
        )

    def logout(self, uow: AuthUnitOfWork, session_token: str | None) -> None:
        if not session_token:
            return
        with uow:
            uow.sessions.revoke(session_token, utcnow())
            uow.commit()

    def get_current_user(self, uow: AuthUnitOfWork, session_token: str | None) -> User:
        if not session_token:
            raise AuthenticationError("Not authenticated")
        with uow:
            session = uow.sessions.get(session_token)
            if session is None or not session.is_active(utcnow()):
                raise AuthenticationError("Invalid session")
            try:
                return uow.users.get(session.user_id)
            except UserNotFoundError as exc:
                raise AuthenticationError("Invalid session") from exc
