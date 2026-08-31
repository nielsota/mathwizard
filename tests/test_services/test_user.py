import pytest
from tests.fakes import FakeUnitOfWork

from mathwizard.exceptions import AuthorizationError, RoleNotAssignedError
from mathwizard.models.domain.user import UserRole
from mathwizard.services.user import UserService


def test_with_role_reports_teacher() -> None:
    uow = FakeUnitOfWork()
    with uow:
        user = uow.users.add(username="root", password_hash="h")
        uow.roster.add_teacher(user.id)
        uow.commit()

    result = UserService().with_role(uow, user)

    assert result.role is UserRole.TEACHER
    assert result.username == "root"


def test_with_role_reports_student() -> None:
    uow = FakeUnitOfWork()
    with uow:
        teacher_user = uow.users.add(username="root", password_hash="h")
        teacher = uow.roster.add_teacher(teacher_user.id)
        student_user = uow.users.add(username="student1", password_hash="h")
        uow.roster.add_student(student_user.id, teacher.id)
        uow.commit()

    result = UserService().with_role(uow, student_user)

    assert result.role is UserRole.STUDENT


def test_with_role_raises_when_no_role_is_assigned() -> None:
    uow = FakeUnitOfWork()
    with uow:
        user = uow.users.add(username="orphan", password_hash="h")
        uow.commit()

    with pytest.raises(RoleNotAssignedError):
        UserService().with_role(uow, user)


def test_list_student_users_returns_users_sorted_by_username() -> None:
    uow = FakeUnitOfWork()
    with uow:
        teacher_user = uow.users.add(username="root", password_hash="h")
        teacher = uow.roster.add_teacher(teacher_user.id)
        zoe = uow.users.add(username="zoe", password_hash="h")
        amy = uow.users.add(username="amy", password_hash="h")
        uow.roster.add_student(zoe.id, teacher.id)
        uow.roster.add_student(amy.id, teacher.id)
        uow.commit()

    students = UserService().list_student_users(uow, teacher_user)

    assert [student.username for student in students] == ["amy", "zoe"]


def test_list_student_users_requires_a_teacher() -> None:
    uow = FakeUnitOfWork()
    with uow:
        user = uow.users.add(username="orphan", password_hash="h")
        uow.commit()

    with pytest.raises(AuthorizationError, match="Teacher access required"):
        UserService().list_student_users(uow, user)


def test_get_teacher_user_returns_the_students_teacher() -> None:
    uow = FakeUnitOfWork()
    with uow:
        teacher_user = uow.users.add(username="root", password_hash="h")
        teacher = uow.roster.add_teacher(teacher_user.id)
        student_user = uow.users.add(username="student1", password_hash="h")
        uow.roster.add_student(student_user.id, teacher.id)
        uow.commit()

    found = UserService().get_teacher_user(uow, student_user)

    assert found.username == "root"


def test_get_teacher_user_requires_a_student() -> None:
    uow = FakeUnitOfWork()
    with uow:
        user = uow.users.add(username="orphan", password_hash="h")
        uow.commit()

    with pytest.raises(AuthorizationError, match="Student access required"):
        UserService().get_teacher_user(uow, user)
