from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mathwizard.app.auth import router as auth_router
from mathwizard.app.routes.roster import router as roster_router
from mathwizard.db.client import DBClient
from mathwizard.services.auth import AuthService, hash_password
from mathwizard.services.user import UserService
from mathwizard.settings import Settings


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'roster-routes.db'}")


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'roster-routes.db'}",
        cookie_secure=False,
        session_ttl_days=7,
    )


def make_client(db: DBClient, tmp_path: Path) -> TestClient:
    app = FastAPI()
    app.state.auth_service = AuthService(db, make_settings(tmp_path))
    app.state.user_service = UserService(db)
    app.include_router(auth_router)
    app.include_router(roster_router)
    return TestClient(app)


def seed_teacher_and_students(db: DBClient) -> None:
    teacher_user = db.create_user("teacher", hash_password("secret"))
    assert teacher_user.id is not None
    teacher = db.create_teacher(teacher_user.id)
    assert teacher.id is not None
    for name in ("alice", "bob"):
        student_user = db.create_user(name, hash_password("secret"))
        assert student_user.id is not None
        db.create_student(student_user.id, teacher.id)


def login(client: TestClient, username: str) -> None:
    response = client.post(
        "/auth/login",
        json={"username": username, "password": "secret"},
    )
    assert response.status_code == 200


def test_students_requires_authentication(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_teacher_and_students(db)
    client = make_client(db, tmp_path)

    response = client.get("/api/v1/roster/students")

    assert response.status_code == 401


def test_teacher_can_list_students(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_teacher_and_students(db)
    client = make_client(db, tmp_path)
    login(client, "teacher")

    response = client.get("/api/v1/roster/students")

    assert response.status_code == 200
    assert [s["username"] for s in response.json()["students"]] == ["alice", "bob"]


def test_student_cannot_list_students(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_teacher_and_students(db)
    client = make_client(db, tmp_path)
    login(client, "alice")

    response = client.get("/api/v1/roster/students")

    assert response.status_code == 403


def test_student_can_see_teacher(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_teacher_and_students(db)
    client = make_client(db, tmp_path)
    login(client, "alice")

    response = client.get("/api/v1/roster/my-teacher")

    assert response.status_code == 200
    assert response.json()["teacher"]["username"] == "teacher"


def test_teacher_cannot_see_my_teacher(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_teacher_and_students(db)
    client = make_client(db, tmp_path)
    login(client, "teacher")

    response = client.get("/api/v1/roster/my-teacher")

    assert response.status_code == 403
