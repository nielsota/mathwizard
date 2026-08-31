from pathlib import Path

from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import Settings


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url="sqlite:///unused.db",
        repo_root=tmp_path,
        bootstrap_username="root",
        bootstrap_password="root",
        bootstrap_student_usernames=["alice", "bob"],
        bootstrap_student_password="student",
    )


def _seed_roster(
    service: BootstrapService,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    service.seed_root_user(uow_factory())
    service.seed_root_teacher(uow_factory())
    service.seed_students(uow_factory())


def _student_usernames(uow_factory: SqlAlchemyUnitOfWorkFactory) -> list[str]:
    with uow_factory() as uow:
        root = uow.users.get_by_username("root")
        assert root is not None
        teacher = uow.roster.get_teacher_by_user_id(root.id)
        assert teacher is not None
        students = uow.roster.list_students_for_teacher(teacher.id)
        users = uow.users.get_many([student.user_id for student in students])
    return sorted(user.username for user in users)


def test_seed_root_teacher_gives_root_a_teacher_profile(
    tmp_path: Path,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    service = BootstrapService(_settings(tmp_path))

    service.seed_root_user(uow_factory())
    service.seed_root_teacher(uow_factory())

    with uow_factory() as uow:
        root = uow.users.get_by_username("root")
        assert root is not None
        assert uow.roster.get_teacher_by_user_id(root.id) is not None


def test_seed_students_assigns_students_to_root(
    tmp_path: Path,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    _seed_roster(BootstrapService(_settings(tmp_path)), uow_factory)

    assert _student_usernames(uow_factory) == ["alice", "bob"]


def test_seed_is_idempotent(
    tmp_path: Path,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    service = BootstrapService(_settings(tmp_path))

    _seed_roster(service, uow_factory)
    _seed_roster(service, uow_factory)

    assert _student_usernames(uow_factory) == ["alice", "bob"]
