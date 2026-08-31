from pathlib import Path

from mathwizard.ports.unit_of_work import UnitOfWorkFactory
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import (
    BootstrapSettings,
    DatabaseSettings,
    PathSettings,
    Settings,
)
from tests.fakes import FakePasswordHasher, FakeUnitOfWorkFactory


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        db=DatabaseSettings(url="sqlite:///unused.db"),
        paths=PathSettings(repo_root=tmp_path),
        bootstrap=BootstrapSettings(
            username="root",
            password="root",
            student_usernames=["alice", "bob"],
            student_password="student",
        ),
    )


def _seed_roster(service: BootstrapService, uow_factory: UnitOfWorkFactory) -> None:
    service.seed_root_user(uow_factory())
    service.seed_root_teacher(uow_factory())
    service.seed_students(uow_factory())


def _student_usernames(uow_factory: UnitOfWorkFactory) -> list[str]:
    with uow_factory() as uow:
        root = uow.users.get_by_username("root")
        assert root is not None
        teacher = uow.roster.get_teacher_by_user_id(root.id)
        assert teacher is not None
        students = uow.roster.list_students_for_teacher(teacher.id)
        users = uow.users.get_many([student.user_id for student in students])
    return sorted(user.username for user in users)


def test_seed_root_teacher_gives_root_a_teacher_profile(tmp_path: Path) -> None:
    uow_factory = FakeUnitOfWorkFactory()
    service = BootstrapService(_settings(tmp_path), hasher=FakePasswordHasher())

    service.seed_root_user(uow_factory())
    service.seed_root_teacher(uow_factory())

    with uow_factory() as uow:
        root = uow.users.get_by_username("root")
        assert root is not None
        assert uow.roster.get_teacher_by_user_id(root.id) is not None


def test_seed_students_assigns_students_to_root(tmp_path: Path) -> None:
    uow_factory = FakeUnitOfWorkFactory()
    _seed_roster(
        BootstrapService(_settings(tmp_path), hasher=FakePasswordHasher()),
        uow_factory,
    )

    assert _student_usernames(uow_factory) == ["alice", "bob"]


def test_seed_is_idempotent(tmp_path: Path) -> None:
    uow_factory = FakeUnitOfWorkFactory()
    service = BootstrapService(_settings(tmp_path), hasher=FakePasswordHasher())

    _seed_roster(service, uow_factory)
    _seed_roster(service, uow_factory)

    assert _student_usernames(uow_factory) == ["alice", "bob"]
