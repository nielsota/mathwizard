from dataclasses import dataclass
from datetime import timedelta

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from mathwizard.db.client import DBClient
from mathwizard.exceptions import AuthenticationError, UserNotFoundError
from mathwizard.models.auth import LoginRequest, UserResponse
from mathwizard.models.db import User
from mathwizard.settings import Settings


_password_hash = PasswordHash((BcryptHasher(),))
DUMMY_PASSWORD_HASH = _password_hash.hash("__not_a_real_password__")


@dataclass(frozen=True)
class LoginResult:
    user: UserResponse
    session_token: str
    max_age_seconds: int
    cookie_secure: bool


def hash_password(plain: str) -> str:
    return _password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _password_hash.verify(plain, hashed)


def user_response(user: User) -> UserResponse:
    assert user.id is not None
    return UserResponse(id=user.id, username=user.username)


class AuthService:
    def __init__(self, db: DBClient, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    @property
    def session_cookie_name(self) -> str:
        return self.settings.session_cookie_name

    def login(self, body: LoginRequest) -> LoginResult:
        user = self.db.get_user_by_username(body.username)
        hashed = user.password_hash if user is not None else DUMMY_PASSWORD_HASH
        password_ok = verify_password(body.password, hashed)
        if user is None or not password_ok:
            raise AuthenticationError("Invalid username or password")

        ttl = timedelta(days=self.settings.session_ttl_days)
        user_session = self.db.create_session(user.id, ttl)
        return LoginResult(
            user=user_response(user),
            session_token=user_session.id,
            max_age_seconds=int(ttl.total_seconds()),
            cookie_secure=self.settings.cookie_secure,
        )

    def logout(self, session_token: str | None) -> None:
        if session_token:
            self.db.revoke_session(session_token)

    def get_current_user(self, session_token: str | None) -> User:
        if not session_token:
            raise AuthenticationError("Not authenticated")
        user_session = self.db.get_session(session_token)
        if user_session is None:
            raise AuthenticationError("Invalid session")
        try:
            return self.db.get_user(user_session.user_id)
        except UserNotFoundError as exc:
            raise AuthenticationError("Invalid session") from exc
