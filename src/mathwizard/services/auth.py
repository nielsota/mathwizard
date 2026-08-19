import secrets
from dataclasses import dataclass
from datetime import timedelta

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from mathwizard.clock import utcnow
from mathwizard.exceptions import AuthenticationError, UserNotFoundError
from mathwizard.models.domain.user import User
from mathwizard.ports.unit_of_work import AuthUnitOfWork
from mathwizard.settings import Settings

_password_hash = PasswordHash((BcryptHasher(),))
DUMMY_PASSWORD_HASH = _password_hash.hash("__not_a_real_password__")


@dataclass(frozen=True)
class LoginResult:
    user: User
    session_token: str
    max_age_seconds: int
    cookie_secure: bool


def hash_password(plain: str) -> str:
    return _password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _password_hash.verify(plain, hashed)


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def session_cookie_name(self) -> str:
        return self.settings.session_cookie_name

    def login(self, uow: AuthUnitOfWork, username: str, password: str) -> LoginResult:
        ttl = timedelta(days=self.settings.session_ttl_days)
        with uow:
            user = uow.users.get_by_username(username)
            # An unknown username still pays for a hash comparison, so the response
            # time does not reveal which usernames exist.
            hashed = user.password_hash if user is not None else DUMMY_PASSWORD_HASH
            password_ok = verify_password(password, hashed)
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
            cookie_secure=self.settings.cookie_secure,
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
