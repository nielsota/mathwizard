from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from mathwizard.app.auth import router as auth_router
from mathwizard.app.routes.roster import router as roster_router
from mathwizard.db.base import Base
from mathwizard.db.engine import create_db_engine, create_session_factory
from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory
from mathwizard.services.auth import AuthService, hash_password
from mathwizard.services.user import UserService
from mathwizard.settings import Settings


def make_uow_factory(tmp_path: Path) -> SqlAlchemyUnitOfWorkFactory:
    engine: Engine = create_db_engine(f"sqlite:///{tmp_path / 'api.db'}")
    Base.metadata.create_all(engine)
    return SqlAlchemyUnitOfWorkFactory(create_session_factory(engine))


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'api.db'}",
        cookie_secure=False,
        session_ttl_days=7,
    )


def make_client(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
    tmp_path: Path,
) -> TestClient:
    app = FastAPI()
    app.state.uow_factory = uow_factory
    app.state.auth_service = AuthService(make_settings(tmp_path))
    app.state.user_service = UserService()
    app.include_router(auth_router)
    app.include_router(roster_router)
    return TestClient(app)


def seed_teacher_and_students(uow_factory: SqlAlchemyUnitOfWorkFactory) -> None:
    with uow_factory() as uow:
        teacher_user = uow.users.add(
            username="teacher", password_hash=hash_password("secret")
        )
        teacher = uow.roster.add_teacher(teacher_user.id)
        for name in ("alice", "bob"):
            student_user = uow.users.add(
                username=name, password_hash=hash_password("secret")
            )
            uow.roster.add_student(student_user.id, teacher.id)
        uow.commit()


def login(client: TestClient, username: str) -> None:
    response = client.post(
        "/auth/login",
        json={"username": username, "password": "secret"},
    )
    assert response.status_code == 200


def test_students_requires_authentication(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_teacher_and_students(uow_factory)
    client = make_client(uow_factory, tmp_path)

    response = client.get("/api/v1/roster/students")

    assert response.status_code == 401


def test_teacher_can_list_students(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_teacher_and_students(uow_factory)
    client = make_client(uow_factory, tmp_path)
    login(client, "teacher")

    response = client.get("/api/v1/roster/students")

    assert response.status_code == 200
    assert [s["username"] for s in response.json()["students"]] == ["alice", "bob"]


def test_list_students_never_leaks_password_hashes(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_teacher_and_students(uow_factory)
    client = make_client(uow_factory, tmp_path)
    login(client, "teacher")

    response = client.get("/api/v1/roster/students")

    assert response.status_code == 200
    assert response.json()["students"] == [
        {"id": 2, "username": "alice"},
        {"id": 3, "username": "bob"},
    ]


def test_student_cannot_list_students(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_teacher_and_students(uow_factory)
    client = make_client(uow_factory, tmp_path)
    login(client, "alice")

    response = client.get("/api/v1/roster/students")

    assert response.status_code == 403


def test_student_can_see_teacher(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_teacher_and_students(uow_factory)
    client = make_client(uow_factory, tmp_path)
    login(client, "alice")

    response = client.get("/api/v1/roster/my-teacher")

    assert response.status_code == 200
    assert response.json()["teacher"] == {"id": 1, "username": "teacher"}


def test_teacher_cannot_see_my_teacher(tmp_path: Path) -> None:
    uow_factory = make_uow_factory(tmp_path)
    seed_teacher_and_students(uow_factory)
    client = make_client(uow_factory, tmp_path)
    login(client, "teacher")

    response = client.get("/api/v1/roster/my-teacher")

    assert response.status_code == 403
