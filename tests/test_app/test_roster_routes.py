from tests.app_client import make_test_client
from tests.fakes import FakePasswordHasher, FakeUnitOfWorkFactory

from mathwizard.app.routes.roster import router as roster_router
from mathwizard.ports.unit_of_work import UnitOfWorkFactory


def seed_teacher_and_students(uow_factory: UnitOfWorkFactory) -> None:
    hasher = FakePasswordHasher()
    with uow_factory() as uow:
        teacher_user = uow.users.add(
            username="teacher", password_hash=hasher.hash("secret")
        )
        teacher = uow.roster.add_teacher(teacher_user.id)
        for name in ("alice", "bob"):
            student_user = uow.users.add(
                username=name, password_hash=hasher.hash("secret")
            )
            uow.roster.add_student(student_user.id, teacher.id)
        uow.commit()


def login(client, username: str) -> None:
    response = client.post(
        "/auth/login",
        json={"username": username, "password": "secret"},
    )
    assert response.status_code == 200


def test_students_requires_authentication() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher_and_students(uow_factory)
    client = make_test_client(uow_factory, roster_router)

    response = client.get("/api/v1/roster/students")

    assert response.status_code == 401


def test_teacher_can_list_students() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher_and_students(uow_factory)
    client = make_test_client(uow_factory, roster_router)
    login(client, "teacher")

    response = client.get("/api/v1/roster/students")

    assert response.status_code == 200
    assert [s["username"] for s in response.json()["students"]] == ["alice", "bob"]


def test_list_students_never_leaks_password_hashes() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher_and_students(uow_factory)
    client = make_test_client(uow_factory, roster_router)
    login(client, "teacher")

    response = client.get("/api/v1/roster/students")

    assert response.status_code == 200
    assert response.json()["students"] == [
        {"id": 2, "username": "alice"},
        {"id": 3, "username": "bob"},
    ]


def test_student_cannot_list_students() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher_and_students(uow_factory)
    client = make_test_client(uow_factory, roster_router)
    login(client, "alice")

    response = client.get("/api/v1/roster/students")

    assert response.status_code == 403


def test_student_can_see_teacher() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher_and_students(uow_factory)
    client = make_test_client(uow_factory, roster_router)
    login(client, "alice")

    response = client.get("/api/v1/roster/my-teacher")

    assert response.status_code == 200
    assert response.json()["teacher"] == {"id": 1, "username": "teacher"}


def test_teacher_cannot_see_my_teacher() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_teacher_and_students(uow_factory)
    client = make_test_client(uow_factory, roster_router)
    login(client, "teacher")

    response = client.get("/api/v1/roster/my-teacher")

    assert response.status_code == 403
