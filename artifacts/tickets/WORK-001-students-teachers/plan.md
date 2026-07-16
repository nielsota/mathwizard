# Implementation Plan: WORK-001

**Design**: Context-based plan
**Design ID**: N/A
**Related Ticket**: None
**Created**: 2026-07-16

## Overview

Introduce two user types — **teacher** and **student** — on top of the existing minimal `User`/session auth. Each teacher has many students; each student is assigned to exactly one teacher. The relationship is modeled by **composition**: `User` remains the auth identity, and separate `Teacher` and `Student` profile tables each hold a one-to-one `user_id` FK back to `User`, with `Student.teacher_id` pointing at `Teacher`. The frontend gains a single **toggle menu** in the header holding role-specific cards that expand **inline**: teachers get a "See students" card, students get a "My teacher" card.

## Design Decisions (locked)

- **Data model**: Composition. `Teacher` and `Student` profile tables reference `User.id`. No polymorphic inheritance, no `role` column on `User`. Role is *derived* at read time by looking up which profile table owns the user.
- **User/assignment creation**: Bootstrap/seed only. No runtime signup or teacher-facing creation API in this scope.
- **`root` user**: Becomes a teacher (owns the seeded students).
- **Toggle menu**: One card per role, content expands **inline** in the menu. **No new routes.**

## Success Criteria

- [ ] `Teacher` and `Student` tables exist and are created via `SQLModel.metadata.create_all` at startup (no migrations).
- [ ] A teacher user has many students; a student user is linked to exactly one teacher (mutual `teacher.students` / `student.teacher` relationships).
- [ ] `GET /auth/me` and `POST /auth/login` responses include the user's `role` (`teacher` | `student`).
- [ ] `GET /api/v1/roster/students` returns the calling teacher's students; returns 403 for students.
- [ ] `GET /api/v1/roster/my-teacher` returns the calling student's teacher; returns 403 for teachers.
- [ ] Bootstrap seeds `root` as a teacher plus a small set of students assigned to `root`.
- [ ] Header shows a toggle menu; teachers see a "See students" card, students see a "My teacher" card; clicking a card expands its content inline (fetched from the roster API).
- [ ] All new backend logic lives in service classes (per `CLAUDE.md`); routes depend on services, not on `DBClient` or `app.state`.
- [ ] Unit + route + bootstrap tests pass; existing auth-route tests updated for the new `role` field.

## Out of Scope

- Runtime signup, teacher UI to add/assign/remove students, editing profiles.
- Reassigning a student to a different teacher.
- Multiple teachers per student.
- Role-based restriction of existing practice/exam routes (only the new roster routes are role-gated).
- Serving the built frontend from FastAPI (dev proxy setup is unchanged).
- Database migrations (repo uses `create_all`; local SQLite is recreated after schema change).

## Task Breakdown

### Task 1: Data model — `Teacher`/`Student` tables + roster DB mixin

**ID**: WORK-001-T01
**Dependencies**: None
**Status**: ⬜ Not Started

**What to do**:
1. Add a `UserRole` enum in `enums.py`.
2. Add `Teacher` and `Student` SQLModel table models in `models/db.py` with mutual relationships.
3. Create a `RosterMixin` in `db/mixins/roster.py` with creation and lookup methods.
4. Register `RosterMixin` in `db/mixins/__init__.py` and on `DBClient`.
5. Write DB-layer unit tests.

**Implementation Details**:

```python
# enums.py
from enum import Enum


class UserRole(str, Enum):
    TEACHER = "teacher"
    STUDENT = "student"
```

```python
# models/db.py  (new tables; keep existing User/Session/Question as-is)
class Teacher(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    students: list["Student"] = Relationship(back_populates="teacher")


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    teacher_id: int = Field(foreign_key="teacher.id", index=True)
    teacher: Teacher = Relationship(back_populates="students")
```

```python
# db/mixins/roster.py
from sqlmodel import Session as DBSession, select

from mathwizard.db.mixins.base import NeedsEngine
from mathwizard.models.db import Student, Teacher, User


class RosterMixin(NeedsEngine):
    def create_teacher(self, user_id: int) -> Teacher:
        with DBSession(self.engine) as session:
            teacher = Teacher(user_id=user_id)
            session.add(teacher)
            session.commit()
            session.refresh(teacher)
            return teacher

    def create_student(self, user_id: int, teacher_id: int) -> Student:
        with DBSession(self.engine) as session:
            student = Student(user_id=user_id, teacher_id=teacher_id)
            session.add(student)
            session.commit()
            session.refresh(student)
            return student

    def get_teacher_by_user_id(self, user_id: int) -> Teacher | None:
        with DBSession(self.engine) as session:
            return session.exec(
                select(Teacher).where(Teacher.user_id == user_id)
            ).first()

    def get_student_by_user_id(self, user_id: int) -> Student | None:
        with DBSession(self.engine) as session:
            return session.exec(
                select(Student).where(Student.user_id == user_id)
            ).first()

    def list_student_users_for_teacher(self, teacher_id: int) -> list[User]:
        with DBSession(self.engine) as session:
            return list(
                session.exec(
                    select(User)
                    .join(Student, Student.user_id == User.id)
                    .where(Student.teacher_id == teacher_id)
                    .order_by(User.username)
                ).all()
            )

    def get_teacher_user(self, teacher_id: int) -> User | None:
        with DBSession(self.engine) as session:
            teacher = session.get(Teacher, teacher_id)
            if teacher is None:
                return None
            return session.get(User, teacher.user_id)
```

```python
# db/client.py
class DBClient(UserMixin, SessionsMixin, QuestionsMixin, RosterMixin):
    ...
```

**Files to create/modify**:
- `src/mathwizard/enums.py`: add `UserRole`.
- `src/mathwizard/models/db.py`: add `Teacher`, `Student` tables + relationships.
- `src/mathwizard/db/mixins/roster.py`: new `RosterMixin`.
- `src/mathwizard/db/mixins/__init__.py`: export `RosterMixin`.
- `src/mathwizard/db/client.py`: mix in `RosterMixin`.
- `tests/test_db_roster.py`: DB-layer tests.

**Acceptance Criteria**:
- [ ] Creating a teacher then a student linked to it persists both, with `student.teacher_id == teacher.id`.
  - **Validation Method**: `pytest tests/test_db_roster.py`
  - **Expected Result**: Row created; `list_student_users_for_teacher` returns the student's `User`.
- [ ] `get_teacher_by_user_id` / `get_student_by_user_id` return `None` for users without that profile.
  - **Validation Method**: Unit test with a plain user.
  - **Expected Result**: `None` returned, no exception.

**Validation Checklist**:
- [ ] Tables created by `create_all` (fresh SQLite file works end to end).
- [ ] `unique=True` on `user_id` prevents duplicate profiles.

**Testing Requirements**:
- [ ] Unit tests written and passing
- [ ] All acceptance criteria validated

**Notes**:
- Follow the existing mixin idiom: each method opens its own `DBSession(self.engine)`.
- `Student.teacher_id` is **required** (student must have exactly one teacher). Seed teachers before students.

---

### Task 2: API schemas + authorization exception

**ID**: WORK-001-T02
**Dependencies**: WORK-001-T01
**Status**: ⬜ Not Started

**What to do**:
1. Add `role: UserRole` to `UserResponse`.
2. Add roster response schemas in a new `models/user.py`.
3. Add `AuthorizationError` (and a `RoleNotAssignedError`) to `exceptions.py`.

**Implementation Details**:

```python
# models/auth.py
from mathwizard.enums import UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
```

```python
# models/user.py  (new)
from pydantic import BaseModel


class StudentSummary(BaseModel):
    id: int
    username: str


class TeacherSummary(BaseModel):
    id: int
    username: str


class StudentsResponse(BaseModel):
    students: list[StudentSummary]


class MyTeacherResponse(BaseModel):
    teacher: TeacherSummary
```

```python
# exceptions.py
class AuthorizationError(MathWizardError):
    pass


class RoleNotAssignedError(MathWizardError):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"User {user_id} has no teacher or student role")
        self.user_id = user_id
```

**Files to create/modify**:
- `src/mathwizard/models/auth.py`: add `role` to `UserResponse`.
- `src/mathwizard/models/user.py`: new roster schemas.
- `src/mathwizard/exceptions.py`: `AuthorizationError`, `RoleNotAssignedError`.

**Acceptance Criteria**:
- [ ] `UserResponse` serializes `role` as `"teacher"`/`"student"`.
  - **Validation Method**: Instantiate and `.model_dump()`.
  - **Expected Result**: `role` present as the string value.

**Validation Checklist**:
- [ ] No `RootModel`, no `...` defaults (per FastAPI skill).

**Testing Requirements**:
- [ ] Covered indirectly by service/route tests in later tasks.

**Notes**:
- Keep `StudentSummary`/`TeacherSummary` minimal (id + username) to avoid leaking `password_hash`.

---

### Task 3: `UserService` — role resolution + roster queries

**ID**: WORK-001-T03
**Dependencies**: WORK-001-T01, WORK-001-T02
**Status**: ⬜ Not Started

**What to do**:
1. Create `UserService` in `services/user.py` following the `QuestionService`/`AuthService` pattern.
2. Implement `get_role`, `to_response`, `list_students`, `get_my_teacher`.
3. Add a `get_user_service` dependency + `UserServiceDep` alias.
4. Construct `UserService` in `main.py` lifespan and attach to `app.state`.
5. Write service-layer unit tests.

**Implementation Details**:

```python
# services/user.py
from mathwizard.db.client import DBClient
from mathwizard.enums import UserRole
from mathwizard.exceptions import AuthorizationError, RoleNotAssignedError
from mathwizard.models.auth import UserResponse
from mathwizard.models.db import User
from mathwizard.models.user import (
    MyTeacherResponse,
    StudentSummary,
    StudentsResponse,
    TeacherSummary,
)


class UserService:
    def __init__(self, db: DBClient) -> None:
        self.db = db

    def get_role(self, user: User) -> UserRole:
        assert user.id is not None
        if self.db.get_teacher_by_user_id(user.id) is not None:
            return UserRole.TEACHER
        if self.db.get_student_by_user_id(user.id) is not None:
            return UserRole.STUDENT
        raise RoleNotAssignedError(user.id)

    def to_response(self, user: User) -> UserResponse:
        assert user.id is not None
        return UserResponse(id=user.id, username=user.username, role=self.get_role(user))

    def list_students(self, user: User) -> StudentsResponse:
        assert user.id is not None
        teacher = self.db.get_teacher_by_user_id(user.id)
        if teacher is None:
            raise AuthorizationError("Teacher access required")
        assert teacher.id is not None
        students = self.db.list_student_users_for_teacher(teacher.id)
        return StudentsResponse(
            students=[
                StudentSummary(id=s.id, username=s.username)
                for s in students
                if s.id is not None
            ]
        )

    def get_my_teacher(self, user: User) -> MyTeacherResponse:
        assert user.id is not None
        student = self.db.get_student_by_user_id(user.id)
        if student is None:
            raise AuthorizationError("Student access required")
        teacher_user = self.db.get_teacher_user(student.teacher_id)
        if teacher_user is None or teacher_user.id is None:
            raise RoleNotAssignedError(user.id)
        return MyTeacherResponse(
            teacher=TeacherSummary(id=teacher_user.id, username=teacher_user.username)
        )
```

```python
# app/dependencies.py
def get_user_service(request: Request) -> UserService:
    return request.app.state.user_service


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
```

```python
# app/main.py (lifespan)
app.state.user_service = UserService(db)
```

**Files to create/modify**:
- `src/mathwizard/services/user.py`: new `UserService`.
- `src/mathwizard/app/dependencies.py`: `get_user_service` + `UserServiceDep`.
- `src/mathwizard/app/main.py`: construct + attach `UserService`.
- `tests/test_services/test_user.py`: service unit tests.

**Acceptance Criteria**:
- [ ] `get_role` returns `TEACHER`/`STUDENT` correctly and raises `RoleNotAssignedError` for a role-less user.
  - **Validation Method**: `pytest tests/test_services/test_user.py`
  - **Expected Result**: Correct role; exception for plain user.
- [ ] `list_students` raises `AuthorizationError` when called by a student; `get_my_teacher` raises for a teacher.
  - **Validation Method**: Unit tests seeding both roles.
  - **Expected Result**: `AuthorizationError` raised.

**Validation Checklist**:
- [ ] Service takes only `DBClient` (matches `QuestionService`).
- [ ] No DB access outside `DBClient` mixin methods.

**Testing Requirements**:
- [ ] Unit tests written and passing
- [ ] All acceptance criteria validated

**Notes**:
- Role resolution is centralized here so both auth responses and roster routes share one source of truth (avoids coupling `AuthService` to `UserService`).

---

### Task 4: Auth responses include `role` + roster routes

**ID**: WORK-001-T04
**Dependencies**: WORK-001-T03
**Status**: ⬜ Not Started

**What to do**:
1. Refactor `AuthService.login` so `LoginResult` carries the `User` model (not a pre-built `UserResponse`).
2. Update `/auth/login` and `/auth/me` to build the response via `UserService.to_response` (so `role` is included). Remove/retire the module-level `user_response` helper in favor of `UserService.to_response`.
3. Add a roster router `app/routes/roster.py` with two role-gated endpoints.
4. Register the roster router in `main.py`.
5. Map `AuthorizationError` → HTTP 403 in the routes.
6. Update existing auth-route tests to expect the new `role` field.

**Implementation Details**:

```python
# services/auth.py  (LoginResult now carries the User model)
@dataclass(frozen=True)
class LoginResult:
    user: User
    session_token: str
    max_age_seconds: int
    cookie_secure: bool
```

```python
# app/auth.py
@router.post("/login", response_model=UserResponse)
def login(
    body: LoginRequest,
    response: Response,
    auth_service: AuthServiceDep,
    user_service: UserServiceDep,
) -> UserResponse:
    try:
        result = auth_service.login(body)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    _set_session_cookie(response, cookie_name=auth_service.session_cookie_name,
                        token=result.session_token, max_age_seconds=result.max_age_seconds,
                        secure=result.cookie_secure)
    return user_service.to_response(result.user)


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUserDep, user_service: UserServiceDep) -> UserResponse:
    return user_service.to_response(user)
```

```python
# app/routes/roster.py
from fastapi import APIRouter, HTTPException, status

from mathwizard.app.auth import CurrentUserDep
from mathwizard.app.dependencies import UserServiceDep
from mathwizard.exceptions import AuthorizationError
from mathwizard.models.user import MyTeacherResponse, StudentsResponse

router = APIRouter(prefix="/api/v1/roster", tags=["roster"])


@router.get("/students")
def list_students(user: CurrentUserDep, user_service: UserServiceDep) -> StudentsResponse:
    try:
        return user_service.list_students(user)
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/my-teacher")
def my_teacher(user: CurrentUserDep, user_service: UserServiceDep) -> MyTeacherResponse:
    try:
        return user_service.get_my_teacher(user)
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
```

```python
# app/main.py
app.include_router(roster_router)
```

**Files to create/modify**:
- `src/mathwizard/services/auth.py`: `LoginResult.user: User`; drop `user_response` usage in `login`.
- `src/mathwizard/app/auth.py`: inject `UserServiceDep` into `login`/`me`; build responses via `UserService`.
- `src/mathwizard/app/routes/roster.py`: new roster router.
- `src/mathwizard/app/routes/__init__.py`: export roster router if the package re-exports routers.
- `src/mathwizard/app/main.py`: include roster router.
- `tests/test_app/test_auth_routes.py`: update assertions to include `role`; `make_client` must also set `app.state.user_service`.
- `tests/test_app/test_roster_routes.py`: new route tests (teacher sees students, student sees teacher, cross-role → 403, unauthenticated → 401).

**Acceptance Criteria**:
- [ ] `POST /auth/login` and `GET /auth/me` include `role` in the JSON body.
  - **Validation Method**: `pytest tests/test_app/test_auth_routes.py`
  - **Expected Result**: `{"id":..., "username":..., "role":"teacher"}`.
- [ ] `GET /api/v1/roster/students` returns the teacher's students; a student caller gets 403.
  - **Validation Method**: `pytest tests/test_app/test_roster_routes.py`
  - **Expected Result**: 200 with student list for teacher; 403 for student.
- [ ] `GET /api/v1/roster/my-teacher` returns the teacher for a student; a teacher caller gets 403; unauthenticated gets 401.
  - **Validation Method**: Route tests.
  - **Expected Result**: Correct status codes.

**Validation Checklist**:
- [ ] Routes depend only on services + `CurrentUserDep` (no direct `DBClient`/`app.state` access).
- [ ] One HTTP operation per function (per FastAPI skill).

**Testing Requirements**:
- [ ] Unit/route tests written and passing
- [ ] Existing auth-route tests updated and green

**Notes**:
- Test harnesses that mount routers manually must now also set `app.state.user_service = UserService(db)` alongside `app.state.auth_service`.

---

### Task 5: Bootstrap seeding — root teacher + students

**ID**: WORK-001-T05
**Dependencies**: WORK-001-T01
**Status**: ⬜ Not Started

**What to do**:
1. Add seed settings for students (usernames + shared default password) in `settings.py`.
2. Extend `BootstrapService` to (a) ensure `root` has a `Teacher` profile, and (b) seed student users assigned to `root`.
3. Keep seeding idempotent (only create profiles/users that don't already exist).
4. Write bootstrap tests.

**Implementation Details**:

```python
# settings.py (additions)
bootstrap_student_usernames: list[str] = ["student1", "student2"]
bootstrap_student_password: str = "student"
```

```python
# services/bootstrap.py (additions)
def seed_root_teacher(self) -> None:
    user = self.db.get_user_by_username(self.settings.bootstrap_username)
    if user is None or user.id is None:
        return
    if self.db.get_teacher_by_user_id(user.id) is None:
        self.db.create_teacher(user.id)

def seed_students(self) -> None:
    root = self.db.get_user_by_username(self.settings.bootstrap_username)
    if root is None or root.id is None:
        return
    teacher = self.db.get_teacher_by_user_id(root.id)
    if teacher is None or teacher.id is None:
        return
    for username in self.settings.bootstrap_student_usernames:
        if self.db.get_user_by_username(username) is not None:
            continue
        user = self.db.create_user(
            username, hash_password(self.settings.bootstrap_student_password)
        )
        assert user.id is not None
        self.db.create_student(user.id, teacher.id)

def run_all(self) -> None:
    self.seed_root_user()
    self.seed_root_teacher()
    self.seed_students()
    self.seed_practice_questions()
```

**Files to create/modify**:
- `src/mathwizard/settings.py`: `bootstrap_student_usernames`, `bootstrap_student_password`.
- `src/mathwizard/services/bootstrap.py`: `seed_root_teacher`, `seed_students`, updated `run_all`.
- `tests/test_bootstrap_roster.py`: bootstrap tests.

**Acceptance Criteria**:
- [ ] After `run_all`, `root` has a `Teacher` profile and the seeded students exist as `Student`s assigned to `root`.
  - **Validation Method**: `pytest tests/test_bootstrap_roster.py`
  - **Expected Result**: `list_student_users_for_teacher(root_teacher.id)` returns the seeded students.
- [ ] Running `run_all` twice does not create duplicates.
  - **Validation Method**: Call twice, assert counts unchanged.
  - **Expected Result**: Idempotent.

**Validation Checklist**:
- [ ] Ordering: root user → root teacher → students → questions.
- [ ] Existing `seed_root_user` behavior unchanged.

**Testing Requirements**:
- [ ] Unit tests written and passing
- [ ] All acceptance criteria validated

**Notes**:
- Because the repo uses `create_all` only, an existing local `data/mathwizard.db` must be deleted once so the new tables are created. Note this in the PR description.

---

### Task 6: Frontend — toggle menu with inline role cards

**ID**: WORK-001-T06
**Dependencies**: WORK-001-T04
**Status**: ⬜ Not Started

**What to do**:
1. Add `role` to the `UserResponse` type and add roster response types in `frontend/src/types/api.ts`.
2. Build a new `UserMenu` component (`frontend/src/components/UserMenu.tsx` + `.css`) — a header toggle menu that renders role-specific cards which expand **inline** and fetch their content on open.
3. Integrate `UserMenu` into `Header.tsx` (reusing the existing dropdown open/close + click-outside pattern).
4. Ensure `App.tsx` passes the `user` (now with `role`) to `Header`/`UserMenu` (already flows via props; verify type).

**Implementation Details**:

Types:

```ts
// frontend/src/types/api.ts
export type UserRole = 'teacher' | 'student';

export interface UserResponse {
  id: number;
  username: string;
  role: UserRole;
}

export interface StudentSummary { id: number; username: string; }
export interface TeacherSummary { id: number; username: string; }
export interface StudentsResponse { students: StudentSummary[]; }
export interface MyTeacherResponse { teacher: TeacherSummary; }
```

Component behavior (`UserMenu.tsx`):
- Trigger: an icon button in the header nav (grid/cards glyph) using the existing `mw-nav-dropdown` structure (`useRef` + click-outside, auto-close on route change).
- Panel: a column of **cards**. For `role === 'teacher'` render a single "See students" card; for `role === 'student'` a single "My teacher" card.
- Each card is expandable inline: clicking the card header toggles a body; on first expand, fetch the relevant endpoint (`/api/v1/roster/students` or `/api/v1/roster/my-teacher`) with `credentials: 'include'`, show a loading state, then render the list/teacher inline. Handle 401 via the existing `onUnauthorized` prop passed down from `App`, and 403/empty gracefully.

Fetch example:

```ts
const resp = await fetch('/api/v1/roster/students', { credentials: 'include' });
if (resp.status === 401) { onUnauthorized(); return; }
const data: StudentsResponse = await resp.json();
```

**Design direction** (apply `frontend-design` skill; stay cohesive with existing tokens in `index.css`):
- Reuse the app's palette (`--navy`, `--peach`, `--surface`, `--border`) and radii (`--radius-md/lg`). Panel uses the header's glassmorphism language (`backdrop-filter: blur`).
- Cards: `--surface` background, `1px solid var(--border)`, `--radius-lg`, subtle shadow; a small peach/navy accent icon per card; chevron that rotates on expand.
- Inline expansion: height/opacity transition (reuse the `dropIn`/`page-enter` easing vocabulary) so content reveals smoothly rather than popping.
- Students list: compact rows (avatar initial in a navy circle + username). "My teacher": a single highlighted row/badge.
- Keep it restrained and editorial to match the existing serif-title + DM Sans aesthetic; do not introduce new fonts.

**Files to create/modify**:
- `frontend/src/types/api.ts`: add `role` + roster types.
- `frontend/src/components/UserMenu.tsx`: new component.
- `frontend/src/components/UserMenu.css`: new styles.
- `frontend/src/components/Header.tsx`: mount `UserMenu` in the nav; thread `user` + `onUnauthorized`.
- `frontend/src/App.tsx`: pass `onUnauthorized` into `Header` if not already; verify `user.role` type flows.

**Acceptance Criteria**:
- [ ] A logged-in teacher sees a toggle menu with a "See students" card; expanding it lists their students inline.
  - **Validation Method**: Manual — log in as `root`, open menu, expand card.
  - **Expected Result**: Seeded students appear inline; no navigation occurs.
- [ ] A logged-in student sees a "My teacher" card; expanding it shows their teacher inline.
  - **Validation Method**: Manual — log in as a seeded student.
  - **Expected Result**: `root` shown as teacher inline.
- [ ] Menu closes on click-outside and on route change; a 401 during fetch redirects to login.
  - **Validation Method**: Manual.
  - **Expected Result**: Consistent with existing dropdown behavior.

**Validation Checklist**:
- [ ] `npm run build` (tsc + vite) succeeds with no type errors.
- [ ] `npm run lint` (oxlint) passes.
- [ ] No new routes added (inline only).

**Testing Requirements**:
- [ ] Manual verification of both roles
- [ ] Build + lint green

**Notes**:
- Reuse the click-outside + route-change-close logic already present in `Header.tsx` rather than reinventing it.
- Dev is proxied (`/api`, `/auth` → :8001); no CORS changes needed.

---

## Execution Order

1. **WORK-001-T01**: Data model — `Teacher`/`Student` tables + `RosterMixin`.
2. **WORK-001-T02**: API schemas (`role`, roster) + `AuthorizationError`.
3. **WORK-001-T03**: `UserService` (role resolution + roster queries) + DI wiring.
4. **WORK-001-T04**: Auth responses include `role` + roster routes.
5. **WORK-001-T05**: Bootstrap seeding — root teacher + students.
6. **WORK-001-T06**: Frontend toggle menu with inline role cards.

(T05 depends only on T01 and may be done in parallel with T03/T04; T06 requires T04.)

## Testing Strategy

**Test-Driven Development Approach:**
- Write DB/service/route tests alongside each backend task; each task must be green before moving on.
- Update existing tests impacted by the new `role` field in the same task that introduces the change (T04).

**Test Types:**
- Unit Tests: `RosterMixin` (T01), `UserService` (T03), bootstrap seeding (T05).
- Integration Tests: auth routes with `role` (T04), roster routes incl. 401/403 (T04).
- Manual Verification: frontend toggle menu for both roles (T06).

**Commands:**
- Backend: `uv run pytest`
- Frontend: `cd frontend && npm run build && npm run lint`

## Open Questions / Risks

- **Schema recreation**: No migrations — an existing `data/mathwizard.db` must be deleted once so the new tables are created. Low risk locally; call it out in the PR.
- **Role-less users**: Any user without a teacher/student profile triggers `RoleNotAssignedError` on `/auth/me`. Bootstrap guarantees `root` is a teacher, so this only affects manually created users. Acceptable given bootstrap-only creation.
- **Seed student password**: Seeded students share a default password (`bootstrap_student_password`). Fine for dev; document that it should be overridden via env for any non-local use.

## Related Documentation

- **Design**: N/A (context-based)
- **Backend exploration**: [Backend architecture report](867adce6-775e-46fc-97fa-87044ae11176)
- **Frontend exploration**: [Frontend architecture report](74168812-57ff-4a33-9d53-bdfbcd7ec7ac)

---

## Gap Analysis

*To be populated after implementation*

---

## Lessons Learned

*To be populated during implementation*

---

## Key Decisions and Deviations from Plan

*To be populated during implementation*

---

## Validation Results

*To be populated during implementation*
