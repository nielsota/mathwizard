# Cookie Auth Login Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current Cognito/Starlette-session auth stub with first-party cookie-based authentication and a React login page.

**Architecture:** Mirror the BBVA conversational app pattern: hash passwords with `pwdlib`, store opaque session tokens in a database `Session` table, set an `HttpOnly` `SameSite=Lax` cookie on login, revoke sessions on logout, and expose `/auth/me` for frontend session restoration. FastAPI routes depend on app-state services only: `AuthServiceDep` for authentication and `QuestionServiceDep` for questions; route handlers never receive or instantiate `DBClient`. The frontend adds a `/login` page, stores the current user in React state, protects the app routes, and uses the Vite proxy for `/auth`.

**Tech Stack:** Python 3.12, FastAPI, SQLModel, Pydantic, pwdlib bcrypt hashing, pytest/TestClient, React 19, TypeScript, Vite, oxlint.

---

## File Structure

- Modify `pyproject.toml` / `uv.lock`: add `pwdlib`.
- Modify `src/mathwizard/models/db.py`: add `_utcnow()`, `User.password_hash`, user/session relationships, and `Session`.
- Modify `src/mathwizard/db/mixins/users.py`: store password hashes and keep direct `User` loading.
- Create `src/mathwizard/db/mixins/sessions.py`: create, read, and revoke DB-backed sessions.
- Modify `src/mathwizard/db/mixins/__init__.py`: export `SessionsMixin`.
- Modify `src/mathwizard/db/client.py`: include `SessionsMixin`.
- Modify `src/mathwizard/settings.py`: add `session_ttl_days`, `cookie_secure`, `bootstrap_username`, and `bootstrap_password`.
- Modify `src/mathwizard/services/bootstrap.py`: seed the configured bootstrap user with a bcrypt password hash.
- Create `src/mathwizard/services/auth.py`: hash/verify passwords, validate credentials, create/revoke sessions, and resolve users from session tokens.
- Create `src/mathwizard/models/auth.py`: define `LoginRequest` and `UserResponse`.
- Replace `src/mathwizard/app/auth.py`: implement cookie auth routes and cookie/current-user dependencies backed by `AuthService`.
- Modify `src/mathwizard/app/dependencies.py`: expose `AuthServiceDep` and `QuestionServiceDep`; do not expose `DBClientDep`.
- Modify `src/mathwizard/app/main.py`: include auth router.
- Modify `src/mathwizard/app/routes/practice.py`: require an authenticated user.
- Create `tests/test_db_auth.py`: cover password-hash user storage and session lifecycle.
- Create `tests/test_app/test_auth_routes.py`: cover login, logout, `/auth/me`, invalid credentials, and route protection.
- Modify `tests/test_app/test_practice_routes.py`: include authenticated requests.
- Modify `frontend/vite.config.ts`: proxy `/auth` to FastAPI in development.
- Modify `frontend/src/types/api.ts`: add auth request/response types.
- Create `frontend/src/pages/Login.tsx`: login form and error state.
- Create `frontend/src/pages/Login.css`: styled MathWizard login page.
- Modify `frontend/src/App.tsx`: session restoration, protected routes, login route.
- Modify `frontend/src/components/Header.tsx`: show username and logout.
- Modify `frontend/src/components/Header.css`: style auth controls.
- Modify `README.md` and `frontend/README.md`: document cookie auth and local login.

Out of scope:

- Do not keep the Cognito OAuth flow.
- Do not add signup, password reset, roles, or admin user management.
- Do not build database migrations for existing SQLite files.
- Do not protect static frontend assets.

Implementation invariants:

- Do not store plaintext passwords.
- Do not accept missing persisted IDs with fake fallbacks.
- Do not fabricate users or sessions on authentication failure.
- Use a dummy password hash for unknown usernames so invalid usernames and wrong passwords follow the same verification path.
- Logout is idempotent: clear the cookie even if no valid session exists.
- The session cookie is `HttpOnly`, `SameSite=Lax`, and `Secure` only when `settings.cookie_secure` is true.
- FastAPI route handlers depend on service dependencies (`AuthServiceDep`, `QuestionServiceDep`, and `CurrentUserDep`) only. They do not receive `DBClient`, instantiate `DBClient`, or read `app.state.db`.
- No module-level docstrings and no `from __future__ import annotations`.

Frontend design direction:

- Use the existing MathWizard graph-paper aesthetic, but make the login page feel like the locked cover of a refined mathematics notebook: asymmetric worksheet layout, navy field, peach integral mark, pale-blue construction lines, and crisp white form controls.
- Avoid generic centered SaaS login styling. No purple gradients, stock dashboard cards, or anonymous pill clutter.
- Keep motion subtle and purposeful: a short page entrance, one hover lift on the submit button, and no distracting loops.

Reference implementation:

- Use the same logic as `/Users/otaniels/Library/CloudStorage/OneDrive-TheBostonConsultingGroup,Inc/Documents/NielsOta/Code/bbva/conversational/src/conversational/api/auth.py`.
- Use the same route shape as `/Users/otaniels/Library/CloudStorage/OneDrive-TheBostonConsultingGroup,Inc/Documents/NielsOta/Code/bbva/conversational/src/conversational/api/routes/auth.py`.
- Use the same DB session pattern as `/Users/otaniels/Library/CloudStorage/OneDrive-TheBostonConsultingGroup,Inc/Documents/NielsOta/Code/bbva/conversational/src/conversational/db/mixins/sessions.py`.

---

### Task 1: Add Auth Database Models And Session Mixin

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `src/mathwizard/models/db.py`
- Modify: `src/mathwizard/db/mixins/users.py`
- Create: `src/mathwizard/db/mixins/sessions.py`
- Modify: `src/mathwizard/db/mixins/__init__.py`
- Modify: `src/mathwizard/db/client.py`
- Test: `tests/test_db_auth.py`

- [ ] **Step 1: Add password hashing dependency**

Run:

```bash
uv add pwdlib
```

Expected: `pyproject.toml` and `uv.lock` update with `pwdlib`.

- [ ] **Step 2: Write failing DB auth tests**

Create `tests/test_db_auth.py`:

```python
from datetime import timedelta
from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.models.db import _utcnow


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'auth.db'}")


def test_create_user_stores_password_hash(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    user = db.create_user("root", "hashed-password")

    assert user.id is not None
    assert user.username == "root"
    assert user.password_hash == "hashed-password"


def test_session_lifecycle(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    user = db.create_user("root", "hashed-password")
    assert user.id is not None

    session = db.create_session(user.id, timedelta(days=7))

    assert session.id
    assert session.user_id == user.id
    assert session.expires_at > _utcnow()
    assert db.get_session(session.id) is not None

    db.revoke_session(session.id)

    assert db.get_session(session.id) is None


def test_expired_session_is_not_returned(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    user = db.create_user("root", "hashed-password")
    assert user.id is not None

    session = db.create_session(user.id, timedelta(seconds=-1))

    assert db.get_session(session.id) is None
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```bash
uv run --extra dev pytest tests/test_db_auth.py -v
```

Expected: FAIL because `User.password_hash`, `_utcnow`, and session methods do not exist yet.

- [ ] **Step 4: Update DB models**

Replace the user model section in `src/mathwizard/models/db.py` with:

```python
from datetime import datetime, timezone

from sqlalchemy import Column, Enum, JSON
from sqlmodel import SQLModel, Field, Relationship

from mathwizard.enums import QuestionSource


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    sessions: list["Session"] = Relationship(back_populates="user")


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=_utcnow)
    expires_at: datetime
    revoked_at: datetime | None = None

    user: User = Relationship(back_populates="sessions")
```

Keep the existing `Question` and `QuestionPart` classes below this block unchanged.

- [ ] **Step 5: Update user mixin**

Replace `src/mathwizard/db/mixins/users.py` with:

```python
from sqlmodel import Session as DBSession
from sqlmodel import select

from mathwizard.db.mixins.base import NeedsEngine
from mathwizard.exceptions import UserNotFoundError
from mathwizard.models.db import User


class UserMixin(NeedsEngine):

    def create_user(self, username: str, password_hash: str) -> User:
        with DBSession(self.engine) as session:
            user = User(username=username, password_hash=password_hash)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_user(self, user_id: int) -> User:
        with DBSession(self.engine) as session:
            user = session.get(User, user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    def get_user_by_username(self, username: str) -> User | None:
        with DBSession(self.engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()
            return user
```

- [ ] **Step 6: Add session mixin**

Create `src/mathwizard/db/mixins/sessions.py`:

```python
import secrets
from datetime import timedelta

from sqlmodel import Session as DBSession

from mathwizard.db.mixins.base import NeedsEngine
from mathwizard.models.db import Session, _utcnow


class SessionsMixin(NeedsEngine):
    def create_session(self, user_id: int, ttl: timedelta) -> Session:
        token = secrets.token_urlsafe(32)
        now = _utcnow()
        user_session = Session(
            id=token,
            user_id=user_id,
            created_at=now,
            expires_at=now + ttl,
        )
        with DBSession(self.engine) as session:
            session.add(user_session)
            session.commit()
            session.refresh(user_session)
            return user_session

    def get_session(self, token: str) -> Session | None:
        with DBSession(self.engine) as session:
            user_session = session.get(Session, token)
            if user_session is None:
                return None
            if user_session.revoked_at is not None:
                return None
            if user_session.expires_at <= _utcnow():
                return None
            return user_session

    def revoke_session(self, token: str) -> None:
        with DBSession(self.engine) as session:
            user_session = session.get(Session, token)
            if user_session is not None and user_session.revoked_at is None:
                user_session.revoked_at = _utcnow()
                session.add(user_session)
                session.commit()
```

- [ ] **Step 7: Export and compose the session mixin**

Replace `src/mathwizard/db/mixins/__init__.py` with:

```python
from .questions import QuestionsMixin
from .sessions import SessionsMixin
from .users import UserMixin

__all__ = [
    "QuestionsMixin",
    "SessionsMixin",
    "UserMixin",
]
```

Replace `src/mathwizard/db/client.py` with:

```python
from pathlib import Path

from sqlalchemy.engine import make_url
from sqlmodel import SQLModel, create_engine

from .mixins import QuestionsMixin, SessionsMixin, UserMixin


class DBClient(UserMixin, SessionsMixin, QuestionsMixin):
    def __init__(self, database_url: str, echo: bool = False):
        Path(make_url(database_url).database).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(database_url, echo=echo)
        SQLModel.metadata.create_all(self.engine)
```

- [ ] **Step 8: Run DB auth tests**

Run:

```bash
uv run --extra dev pytest tests/test_db_auth.py -v
```

Expected: PASS.

- [ ] **Step 9: Commit Task 1**

```bash
git add pyproject.toml uv.lock src/mathwizard/models/db.py src/mathwizard/db/mixins/users.py src/mathwizard/db/mixins/sessions.py src/mathwizard/db/mixins/__init__.py src/mathwizard/db/client.py tests/test_db_auth.py
git commit -m "Add cookie session storage"
```

---

### Task 2: Add Bootstrap Password Hashing And Auth Settings

**Files:**
- Modify: `src/mathwizard/settings.py`
- Modify: `src/mathwizard/services/bootstrap.py`
- Create: `src/mathwizard/services/auth.py`
- Test: `tests/test_bootstrap_auth.py`

- [ ] **Step 1: Write failing bootstrap auth tests**

Create `tests/test_bootstrap_auth.py`:

```python
from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.services.auth import verify_password
from mathwizard.services.bootstrap import seed_root_user


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'bootstrap-auth.db'}")


def test_seed_root_user_hashes_configured_password(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    seed_root_user(db, username="teacher", password="s3cret")

    user = db.get_user_by_username("teacher")
    assert user is not None
    assert user.password_hash != "s3cret"
    assert verify_password("s3cret", user.password_hash)


def test_seed_root_user_is_idempotent(tmp_path: Path) -> None:
    db = make_db(tmp_path)

    seed_root_user(db, username="teacher", password="s3cret")
    seed_root_user(db, username="teacher", password="changed")

    user = db.get_user_by_username("teacher")
    assert user is not None
    assert verify_password("s3cret", user.password_hash)
    assert not verify_password("changed", user.password_hash)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run --extra dev pytest tests/test_bootstrap_auth.py -v
```

Expected: FAIL because `mathwizard.services.auth` does not exist yet and `seed_root_user()` does not accept explicit credentials yet.

- [ ] **Step 3: Add settings fields**

Add these fields to `Settings` in `src/mathwizard/settings.py` after `repo_root`:

```python
    session_ttl_days: int = 7
    session_cookie_name: str = "mw_session"
    cookie_secure: bool = False
    bootstrap_username: str = "root"
    bootstrap_password: str = "root"
```

- [ ] **Step 4: Update bootstrap user seeding**

Create `src/mathwizard/services/auth.py` with password hashing utilities:

```python
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

_password_hash = PasswordHash((BcryptHasher(),))
DUMMY_PASSWORD_HASH = _password_hash.hash("__not_a_real_password__")


def hash_password(plain: str) -> str:
    return _password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _password_hash.verify(plain, hashed)
```

Replace `seed_root_user()` and the `run_all()` call in `src/mathwizard/services/bootstrap.py`:

```python
def seed_root_user(db: DBClient, *, username: str, password: str) -> None:
    from mathwizard.services.auth import hash_password

    if db.get_user_by_username(username) is None:
        db.create_user(username, hash_password(password))
```

```python
def run_all(db: DBClient, practice_dir: Path) -> None:
    from mathwizard.settings import get_settings

    settings = get_settings()
    seed_root_user(
        db,
        username=settings.bootstrap_username,
        password=settings.bootstrap_password,
    )
    seed_practice_questions(db, practice_dir)
```

- [ ] **Step 5: Run bootstrap auth tests**

Run:

```bash
uv run --extra dev pytest tests/test_bootstrap_auth.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

```bash
git add src/mathwizard/settings.py src/mathwizard/services/auth.py src/mathwizard/services/bootstrap.py tests/test_bootstrap_auth.py
git commit -m "Hash bootstrapped user passwords"
```

---

### Task 3: Add Auth Service, Cookie Routes, And Dependencies

**Files:**
- Create: `src/mathwizard/models/auth.py`
- Modify: `src/mathwizard/exceptions.py`
- Modify: `src/mathwizard/services/auth.py`
- Replace: `src/mathwizard/app/auth.py`
- Modify: `src/mathwizard/app/dependencies.py`
- Modify: `src/mathwizard/app/main.py`
- Test: `tests/test_app/test_auth_routes.py`

- [ ] **Step 1: Write failing auth route tests**

Create `tests/test_app/test_auth_routes.py`:

```python
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

    logout = client.post("/auth/logout")

    assert logout.status_code == 204
    assert f"{settings.session_cookie_name}=" in logout.headers["set-cookie"]

    me = client.get("/auth/me")
    assert me.status_code == 401
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run --extra dev pytest tests/test_app/test_auth_routes.py -v
```

Expected: FAIL because `AuthService`, auth models, route dependencies, and cookie routes are not implemented yet.

- [ ] **Step 3: Add auth API models**

Create `src/mathwizard/models/auth.py`:

```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
```

- [ ] **Step 4: Add authentication exception and service**

Add to `src/mathwizard/exceptions.py`:

```python
class AuthenticationError(MathWizardError):
    pass
```

Replace `src/mathwizard/services/auth.py`:

```python
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
```

- [ ] **Step 5: Add app-state service dependencies**

Replace `src/mathwizard/app/dependencies.py` with:

```python
from typing import Annotated

from fastapi import Depends
from fastapi import Request

from mathwizard.services.auth import AuthService
from mathwizard.services.question import QuestionService


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


def get_question_service(request: Request) -> QuestionService:
    return request.app.state.question_service


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
QuestionServiceDep = Annotated[QuestionService, Depends(get_question_service)]
```

- [ ] **Step 6: Replace Cognito auth with cookie auth routes**

Replace `src/mathwizard/app/auth.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from mathwizard.app.dependencies import AuthServiceDep
from mathwizard.exceptions import AuthenticationError
from mathwizard.models.auth import LoginRequest, UserResponse
from mathwizard.models.db import User
from mathwizard.services.auth import user_response


def _set_session_cookie(
    response: Response,
    *,
    cookie_name: str,
    token: str,
    max_age_seconds: int,
    secure: bool,
) -> None:
    response.set_cookie(
        key=cookie_name,
        value=token,
        max_age=max_age_seconds,
        httponly=True,
        secure=secure,
        samesite="lax",
    )


def get_current_user(
    request: Request,
    auth_service: AuthServiceDep,
) -> User:
    session_token = request.cookies.get(auth_service.session_cookie_name)
    try:
        return auth_service.get_current_user(session_token)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


CurrentUserDep = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserResponse)
def login(
    body: LoginRequest,
    response: Response,
    auth_service: AuthServiceDep,
) -> UserResponse:
    try:
        result = auth_service.login(body)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    _set_session_cookie(
        response,
        cookie_name=auth_service.session_cookie_name,
        token=result.session_token,
        max_age_seconds=result.max_age_seconds,
        secure=result.cookie_secure,
    )
    return result.user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    auth_service: AuthServiceDep,
) -> None:
    cookie_name = auth_service.session_cookie_name
    session_token = request.cookies.get(cookie_name)
    auth_service.logout(session_token)
    response.delete_cookie(cookie_name)


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUserDep) -> UserResponse:
    return user_response(user)
```

- [ ] **Step 7: Include auth router and initialize auth service**

Modify `src/mathwizard/app/main.py`:

```python
from mathwizard.app.auth import router as auth_router
from mathwizard.app.routes.practice import router as practice_router
from mathwizard.services.auth import AuthService
```

Then update lifespan so the DB client is a local composition detail and only services are stored on app state:

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()
    db = DBClient(settings.database_url)

    app.state.settings = settings

    bootstrap.run_all(db, settings.practice_dir)
    app.state.auth_service = AuthService(db, settings)
    app.state.question_service = QuestionService(db)

    yield

    db.engine.dispose()
```

Add this after app creation:

```python
app.include_router(auth_router)
app.include_router(practice_router)
```

- [ ] **Step 8: Run auth route tests**

Run:

```bash
uv run --extra dev pytest tests/test_app/test_auth_routes.py -v
```

Expected: PASS.

- [ ] **Step 9: Commit Task 3**

```bash
git add src/mathwizard/models/auth.py src/mathwizard/exceptions.py src/mathwizard/services/auth.py src/mathwizard/app/auth.py src/mathwizard/app/dependencies.py src/mathwizard/app/main.py tests/test_app/test_auth_routes.py
git commit -m "Add cookie auth routes"
```

---

### Task 4: Protect Practice API With Cookie Auth

**Files:**
- Modify: `src/mathwizard/app/routes/practice.py`
- Modify: `tests/test_app/test_practice_routes.py`

- [ ] **Step 1: Write failing protected-route test**

Add these imports to `tests/test_app/test_practice_routes.py`:

```python
from mathwizard.services.auth import AuthService, hash_password
from mathwizard.settings import Settings
```

Add this helper:

```python
def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'api.db'}",
        cookie_secure=False,
        session_ttl_days=7,
    )
```

Update `make_client()`:

```python
def make_client(db: DBClient, tmp_path: Path) -> TestClient:
    app = FastAPI()
    app.state.auth_service = AuthService(db, make_settings(tmp_path))
    app.state.question_service = QuestionService(db)
    app.include_router(router)
    return TestClient(app)
```

Add this helper:

```python
def authenticate(client: TestClient, db: DBClient) -> None:
    db.create_user("root", hash_password("secret"))
    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )
    assert response.status_code == 200
```

Add this test:

```python
def test_get_practice_topic_requires_authentication(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, tmp_path)

    response = client.get("/api/v1/practice/derivatives")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
```

Update the existing successful practice route tests to call `authenticate(client, db)` before making the GET request.

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run --extra dev pytest tests/test_app/test_practice_routes.py -v
```

Expected: FAIL because the practice route is still public or because the auth router is not included in the test app.

- [ ] **Step 3: Protect the practice route**

Modify `src/mathwizard/app/routes/practice.py` imports:

```python
from mathwizard.app.auth import CurrentUserDep
from mathwizard.app.dependencies import QuestionServiceDep
```

Modify the route signature:

```python
def get_practice_topic(
    topic: str,
    question_service: QuestionServiceDep,
    current_user: CurrentUserDep,
    sort_by_difficulty: Annotated[bool, Query()] = True,
) -> QuestionListResponse:
```

Do not use `current_user` in the body. Its presence enforces authentication.

- [ ] **Step 4: Include auth router in practice route tests**

Add this import to `tests/test_app/test_practice_routes.py`:

```python
from mathwizard.app.auth import router as auth_router
```

Update `make_client()`:

```python
def make_client(db: DBClient, tmp_path: Path) -> TestClient:
    app = FastAPI()
    app.state.auth_service = AuthService(db, make_settings(tmp_path))
    app.state.question_service = QuestionService(db)
    app.include_router(auth_router)
    app.include_router(router)
    return TestClient(app)
```

- [ ] **Step 5: Run route tests**

Run:

```bash
uv run --extra dev pytest tests/test_app/test_auth_routes.py tests/test_app/test_practice_routes.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 4**

```bash
git add src/mathwizard/app/routes/practice.py tests/test_app/test_practice_routes.py
git commit -m "Protect practice API with cookie auth"
```

---

### Task 5: Add React Login Page And Session State

**Files:**
- Modify: `frontend/vite.config.ts`
- Modify: `frontend/src/types/api.ts`
- Create: `frontend/src/pages/Login.tsx`
- Create: `frontend/src/pages/Login.css`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Add frontend auth types**

Append to `frontend/src/types/api.ts`:

```typescript
export interface LoginRequest {
  username: string;
  password: string;
}

export interface UserResponse {
  id: number;
  username: string;
}
```

- [ ] **Step 2: Add `/auth` Vite proxy**

Update `frontend/vite.config.ts`:

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: Create login page**

Design intent from `frontend-design`: make the login page feel like a locked mathematics notebook, not a generic SaaS sign-in card. Use an asymmetric two-panel composition, pale graph-paper construction lines, a navy proof panel, and a precise white form panel.

Create `frontend/src/pages/Login.tsx`:

```tsx
import { FormEvent, useState } from 'react'
import type { LoginRequest, UserResponse } from '../types/api'
import './Login.css'

interface LoginProps {
  onLogin: (user: UserResponse) => void
}

export default function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState('root')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setLoading(true)
    setError('')

    const payload: LoginRequest = { username, password }

    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error('Ongeldige gebruikersnaam of wachtwoord')
      }

      const user: UserResponse = await response.json()
      onLogin(user)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <section className="login-shell" aria-labelledby="login-title">
        <div className="login-proof" aria-hidden="true">
          <p className="login-kicker">MathWizard</p>
          <div className="login-integral">∫</div>
          <p className="login-equation">f&apos;(x) = lim Δx→0</p>
          <p className="login-proofline">Toegang tot je oefenruimte</p>
          <div className="login-axis login-axis--x" />
          <div className="login-axis login-axis--y" />
        </div>

        <div className="login-card">
          <p className="login-eyebrow">Beveiligde sessie</p>
          <h1 id="login-title" className="login-title">Welkom terug</h1>
          <p className="login-subtitle">
            Log in om oefenopgaven, examenmateriaal en je MathWizard werkruimte te openen.
          </p>

          <form className="login-form" onSubmit={handleSubmit}>
            <label className="login-label">
              Gebruikersnaam
              <input
                className="login-input"
                value={username}
                onChange={e => setUsername(e.target.value)}
                autoComplete="username"
                required
              />
            </label>

            <label className="login-label">
              Wachtwoord
              <input
                className="login-input"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </label>

            {error && <div className="login-error">{error}</div>}

            <button className="login-button" type="submit" disabled={loading}>
              <span>{loading ? 'Sessie openen...' : 'Sessie openen'}</span>
              <span aria-hidden="true">→</span>
            </button>
          </form>
        </div>
      </section>
    </div>
  )
}
```

- [ ] **Step 4: Add login styles**

Create `frontend/src/pages/Login.css`:

```css
.login-page {
  min-height: calc(100vh - var(--header-height));
  display: grid;
  place-items: center;
  padding: 56px 20px;
  background:
    linear-gradient(rgba(198, 220, 255, 0.22) 1px, transparent 1px),
    linear-gradient(90deg, rgba(198, 220, 255, 0.22) 1px, transparent 1px),
    radial-gradient(circle at 18% 16%, rgba(255, 219, 189, 0.62), transparent 30%),
    radial-gradient(circle at 84% 18%, rgba(198, 220, 255, 0.55), transparent 28%),
    var(--background);
  background-size: 28px 28px, 28px 28px, auto, auto, auto;
}

.login-shell {
  width: min(100%, 940px);
  min-height: 560px;
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(360px, 0.92fr);
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--border);
  border-radius: 28px;
  box-shadow: 0 28px 80px rgba(3, 34, 84, 0.14);
  overflow: hidden;
  animation: loginEnter 0.42s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes loginEnter {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.99);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.login-proof {
  position: relative;
  min-height: 100%;
  padding: 42px;
  background:
    linear-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1px, transparent 1px),
    linear-gradient(135deg, var(--navy) 0%, #0a3a7a 100%);
  background-size: 34px 34px, 34px 34px, auto;
  color: var(--peach);
  overflow: hidden;
}

.login-proof::after {
  content: "";
  position: absolute;
  inset: auto -80px -120px auto;
  width: 320px;
  height: 320px;
  border: 1px solid rgba(255, 219, 189, 0.28);
  border-radius: 50%;
}

.login-kicker {
  margin: 0;
  color: rgba(255, 219, 189, 0.78);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.login-integral {
  margin-top: 92px;
  font-family: var(--font-display);
  font-size: clamp(120px, 18vw, 210px);
  line-height: 0.8;
  letter-spacing: -0.08em;
  text-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
}

.login-equation {
  position: relative;
  z-index: 1;
  margin: 38px 0 0;
  color: rgba(255, 255, 255, 0.82);
  font-family: var(--font-display);
  font-size: 30px;
}

.login-proofline {
  position: relative;
  z-index: 1;
  width: min(100%, 330px);
  margin: 14px 0 0;
  color: rgba(255, 255, 255, 0.68);
  line-height: 1.55;
}

.login-axis {
  position: absolute;
  background: rgba(255, 219, 189, 0.42);
}

.login-axis--x {
  left: 42px;
  right: 42px;
  bottom: 112px;
  height: 1px;
}

.login-axis--y {
  left: 112px;
  top: 42px;
  bottom: 42px;
  width: 1px;
}

.login-card {
  align-self: center;
  margin: 34px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 22px;
  padding: 38px;
  box-shadow: 0 18px 50px rgba(3, 34, 84, 0.10);
}

.login-eyebrow {
  margin: 0 0 6px;
  color: var(--blue);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.login-title {
  margin: 0;
  color: var(--navy);
  font-family: var(--font-display);
  font-size: clamp(40px, 6vw, 56px);
  font-weight: 400;
  letter-spacing: -0.045em;
}

.login-subtitle {
  margin: 10px 0 28px;
  color: var(--text-muted);
  line-height: 1.5;
}

.login-form {
  display: grid;
  gap: 18px;
}

.login-label {
  display: grid;
  gap: 7px;
  color: var(--navy);
  font-size: 13px;
  font-weight: 700;
}

.login-input {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 13px 14px;
  color: var(--text);
  background: #fff;
  font: inherit;
  box-shadow: inset 0 1px 0 rgba(3, 34, 84, 0.03);
}

.login-input:focus {
  outline: 2px solid var(--blue-light);
  border-color: var(--blue);
}

.login-error {
  border: 1px solid #f0b8a8;
  background: #fff4ef;
  color: #8a2f18;
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-size: 13px;
}

.login-button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: none;
  border-radius: 16px;
  padding: 14px 18px;
  background: var(--navy);
  color: var(--peach);
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(3, 34, 84, 0.18);
}

.login-button:disabled {
  cursor: progress;
  opacity: 0.65;
}

@media (max-width: 760px) {
  .login-shell {
    grid-template-columns: 1fr;
  }

  .login-proof {
    min-height: 220px;
  }

  .login-integral {
    margin-top: 34px;
    font-size: 110px;
  }

  .login-card {
    margin: 0;
    border-radius: 0;
    border-left: none;
    border-right: none;
    border-bottom: none;
  }
}
```

- [ ] **Step 5: Add app-level session restoration and protected routes**

Replace `frontend/src/App.tsx`:

```tsx
import { useEffect, useState } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import Header from './components/Header'
import ExamSearch from './pages/ExamSearch'
import Login from './pages/Login'
import Practice from './pages/Practice'
import type { UserResponse } from './types/api'
import './App.css'

function App() {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [checkingSession, setCheckingSession] = useState(true)
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    let active = true

    async function loadSession() {
      try {
        const response = await fetch('/auth/me', { credentials: 'include' })
        if (!active) return
        if (response.ok) {
          const data: UserResponse = await response.json()
          setUser(data)
        } else {
          setUser(null)
        }
      } finally {
        if (active) setCheckingSession(false)
      }
    }

    loadSession()
    return () => {
      active = false
    }
  }, [])

  async function handleLogout() {
    await fetch('/auth/logout', {
      method: 'POST',
      credentials: 'include',
    })
    setUser(null)
    navigate('/login')
  }

  function handleLogin(nextUser: UserResponse) {
    setUser(nextUser)
    const state = location.state as { from?: { pathname?: string } } | null
    const target = state?.from?.pathname ?? '/'
    navigate(target, { replace: true })
  }

  if (checkingSession) {
    return <div className="app-loading">MathWizard laden...</div>
  }

  return (
    <>
      {user && <Header user={user} onLogout={handleLogout} />}
      <main>
        <Routes>
          <Route
            path="/login"
            element={user ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />}
          />
          <Route
            path="/"
            element={user ? <ExamSearch /> : <Navigate to="/login" replace state={{ from: location }} />}
          />
          <Route
            path="/practice/:topic"
            element={user ? <Practice /> : <Navigate to="/login" replace state={{ from: location }} />}
          />
        </Routes>
      </main>
    </>
  )
}

export default App
```

Add to `frontend/src/App.css`:

```css
.app-loading {
  min-height: 100vh;
  display: grid;
  place-items: center;
  color: var(--navy);
  font-family: var(--font-display);
  font-size: 28px;
}
```

- [ ] **Step 6: Run frontend build to expose type errors**

Run:

```bash
cd frontend && npm run build
```

Expected: FAIL because `Header` does not accept auth props yet.

- [ ] **Step 7: Commit Task 5**

Do not commit yet. Task 6 updates the header and should be committed together with this frontend flow.

---

### Task 6: Add Header User Menu And Logout

**Files:**
- Modify: `frontend/src/components/Header.tsx`
- Modify: `frontend/src/components/Header.css`
- Modify: `frontend/src/pages/Practice.tsx`
- Modify: `frontend/src/pages/ExamSearch.tsx`

- [ ] **Step 1: Update authenticated fetch calls**

In `frontend/src/pages/Practice.tsx`, update the fetch call:

```typescript
fetch(`/api/v1/practice/${topic}`, {
  signal: controller.signal,
  credentials: 'include',
})
```

In `frontend/src/pages/ExamSearch.tsx`, update the fetch call:

```typescript
const resp = await fetch('/api/v1/fetch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify(payload),
})
```

- [ ] **Step 2: Update Header props and logout button**

Replace the imports and component signature in `frontend/src/components/Header.tsx`:

```tsx
import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import type { UserResponse } from '../types/api'
import './Header.css'
```

```tsx
interface HeaderProps {
  user: UserResponse
  onLogout: () => void
}

export default function Header({ user, onLogout }: HeaderProps) {
```

Add this button inside `<nav className="mw-nav">` after the exam search link:

```tsx
<div className="mw-auth">
  <span className="mw-user">{user.username}</span>
  <button className="mw-logout" type="button" onClick={onLogout}>
    Uitloggen
  </button>
</div>
```

- [ ] **Step 3: Add header auth styles**

Append to `frontend/src/components/Header.css`:

```css
.mw-auth {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: 10px;
  padding-left: 12px;
  border-left: 1px solid var(--border);
}

.mw-user {
  color: var(--navy);
  font-size: 13px;
  font-weight: 700;
}

.mw-logout {
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 7px 10px;
  background: var(--surface);
  color: var(--text-muted);
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mw-logout:hover {
  color: var(--navy);
  background: var(--blue-wash);
}
```

- [ ] **Step 4: Run frontend verification**

Run:

```bash
cd frontend && npm run build
```

Expected: PASS.

Run:

```bash
cd frontend && npm run lint
```

Expected: PASS.

- [ ] **Step 5: Commit Tasks 5 and 6 together**

```bash
git add frontend/vite.config.ts frontend/src/types/api.ts frontend/src/pages/Login.tsx frontend/src/pages/Login.css frontend/src/App.tsx frontend/src/App.css frontend/src/components/Header.tsx frontend/src/components/Header.css frontend/src/pages/Practice.tsx frontend/src/pages/ExamSearch.tsx
git commit -m "Add login page and session UI"
```

---

### Task 7: End-To-End Verification And Docs

**Files:**
- Modify: `README.md`
- Modify: `frontend/README.md`

- [ ] **Step 1: Update root README auth section**

Add this section to `README.md` after `Quick Start`:

````markdown
## Authentication

MathWizard uses first-party cookie authentication. On startup, the backend seeds a bootstrap user from `.env` settings:

```text
bootstrap_username=root
bootstrap_password=root
session_ttl_days=7
session_cookie_name=mw_session
cookie_secure=false
```

Login happens through `POST /auth/login`. Successful login sets an `HttpOnly` cookie named by `session_cookie_name`. The frontend restores sessions with `GET /auth/me` and logs out with `POST /auth/logout`.

For production, set `cookie_secure=true` so browsers only send the session cookie over HTTPS.
````

- [ ] **Step 2: Update frontend README auth notes**

Add this section to `frontend/README.md`:

```markdown
## Authentication

The Vite dev server proxies both `/api` and `/auth` to the FastAPI backend. The login page posts to `/auth/login`, and authenticated API requests use `credentials: 'include'` so the browser sends the configured session cookie.
```

- [ ] **Step 3: Run full backend tests**

Run:

```bash
uv run --extra dev pytest -v
```

Expected: PASS.

- [ ] **Step 4: Run frontend build and lint**

Run:

```bash
cd frontend && npm run build && npm run lint
```

Expected: PASS.

- [ ] **Step 5: Manual API smoke**

Start the backend with a local `.env`, then run:

```bash
curl -i -c /tmp/mathwizard-cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"username":"root","password":"root"}' \
  http://localhost:8000/auth/login
```

Expected:

```text
HTTP/1.1 200 OK
set-cookie: mw_session=...
```

Then run:

```bash
curl -b /tmp/mathwizard-cookies.txt http://localhost:8000/auth/me
```

Expected:

```json
{"id":1,"username":"root"}
```

Then run:

```bash
curl -b /tmp/mathwizard-cookies.txt http://localhost:8000/api/v1/practice/derivatives
```

Expected: `200 OK` with `source: "practice"`, `topic: "derivatives"`, and a non-empty `questions` array.

- [ ] **Step 6: Commit docs**

```bash
git add README.md frontend/README.md
git commit -m "Document cookie authentication"
```

---

## Self-Review

- Spec coverage: The plan replaces Cognito-style auth with the BBVA cookie-session pattern, adds hashed DB users, DB-backed session storage, an `AuthService`, login/logout/me routes, protected practice API, a React login page, session restoration, logout UI, and docs.
- FastAPI coverage: Routes use app-state service dependencies, response models, explicit HTTP 401 failures, and `HttpOnly` cookie handling. The protected route uses a reusable current-user dependency, and no route handler receives `DBClient`.
- Frontend coverage: Vite proxies `/auth`, the app restores sessions, unauthenticated users are routed to `/login`, authenticated fetches include credentials, and the header displays logout controls. The login page uses the `frontend-design` direction with a MathWizard-specific notebook/proof composition instead of a generic centered form.
- Placeholder scan: No TBDs or vague “add tests” steps remain; code-changing steps include exact snippets and commands.
- Type consistency: Backend `UserResponse` maps to frontend `UserResponse`; `LoginRequest` maps to frontend `LoginRequest`; `Settings.session_cookie_name` defaults to `mw_session`; DB model `password_hash` matches mixin/bootstrap/auth-service code.
