from pathlib import Path

from mathwizard.db.client import DBClient
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.settings import Settings


def make_service(tmp_path: Path) -> BootstrapService:
    db = DBClient(f"sqlite:///{tmp_path / 'bootstrap.db'}")
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'bootstrap.db'}",
        repo_root=tmp_path,
        bootstrap_username="root",
        bootstrap_password="root",
        bootstrap_student_usernames=["alice", "bob"],
        bootstrap_student_password="student",
    )
    return BootstrapService(db, settings)


def seed_roster(svc: BootstrapService) -> None:
    svc.seed_root_user()
    svc.seed_root_teacher()
    svc.seed_students()


def test_seed_root_teacher_gives_root_a_teacher_profile(tmp_path: Path) -> None:
    svc = make_service(tmp_path)

    svc.seed_root_user()
    svc.seed_root_teacher()

    root = svc.db.get_user_by_username("root")
    assert root is not None
    assert root.id is not None
    assert svc.db.get_teacher_by_user_id(root.id) is not None


def test_seed_students_assigns_students_to_root(tmp_path: Path) -> None:
    svc = make_service(tmp_path)

    seed_roster(svc)

    root = svc.db.get_user_by_username("root")
    assert root is not None
    assert root.id is not None
    teacher = svc.db.get_teacher_by_user_id(root.id)
    assert teacher is not None
    assert teacher.id is not None
    students = svc.db.list_student_users_for_teacher(teacher.id)
    assert [s.username for s in students] == ["alice", "bob"]


def test_seed_is_idempotent(tmp_path: Path) -> None:
    svc = make_service(tmp_path)

    seed_roster(svc)
    seed_roster(svc)

    root = svc.db.get_user_by_username("root")
    assert root is not None
    assert root.id is not None
    teacher = svc.db.get_teacher_by_user_id(root.id)
    assert teacher is not None
    assert teacher.id is not None
    students = svc.db.list_student_users_for_teacher(teacher.id)
    assert [s.username for s in students] == ["alice", "bob"]
