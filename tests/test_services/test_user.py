from pathlib import Path

import pytest

from mathwizard.db.client import DBClient
from mathwizard.enums import UserRole
from mathwizard.exceptions import AuthorizationError, RoleNotAssignedError
from mathwizard.models.db import User
from mathwizard.services.user import UserService


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'user-service.db'}")


def seed_teacher_with_students(db: DBClient) -> tuple[User, list[User]]:
    teacher_user = db.create_user("teacher", "hash")
    assert teacher_user.id is not None
    teacher = db.create_teacher(teacher_user.id)
    assert teacher.id is not None

    student_users = []
    for name in ("alice", "bob"):
        student_user = db.create_user(name, "hash")
        assert student_user.id is not None
        db.create_student(student_user.id, teacher.id)
        student_users.append(student_user)
    return teacher_user, student_users


def test_get_role_returns_teacher(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    teacher_user, _ = seed_teacher_with_students(db)
    service = UserService(db)

    assert service.get_role(teacher_user) is UserRole.TEACHER


def test_get_role_returns_student(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    _, students = seed_teacher_with_students(db)
    service = UserService(db)

    assert service.get_role(students[0]) is UserRole.STUDENT


def test_get_role_raises_for_role_less_user(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    user = db.create_user("nobody", "hash")
    service = UserService(db)

    with pytest.raises(RoleNotAssignedError):
        service.get_role(user)


def test_to_response_includes_role(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    teacher_user, _ = seed_teacher_with_students(db)
    service = UserService(db)

    response = service.to_response(teacher_user)

    assert response.username == "teacher"
    assert response.role is UserRole.TEACHER


def test_list_students_returns_teacher_students(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    teacher_user, _ = seed_teacher_with_students(db)
    service = UserService(db)

    response = service.list_students(teacher_user)

    assert [s.username for s in response.students] == ["alice", "bob"]


def test_list_students_rejects_student(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    _, students = seed_teacher_with_students(db)
    service = UserService(db)

    with pytest.raises(AuthorizationError):
        service.list_students(students[0])


def test_get_my_teacher_returns_teacher(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    teacher_user, students = seed_teacher_with_students(db)
    service = UserService(db)

    response = service.get_my_teacher(students[0])

    assert response.teacher.id == teacher_user.id
    assert response.teacher.username == "teacher"


def test_get_my_teacher_rejects_teacher(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    teacher_user, _ = seed_teacher_with_students(db)
    service = UserService(db)

    with pytest.raises(AuthorizationError):
        service.get_my_teacher(teacher_user)
