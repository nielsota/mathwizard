from pathlib import Path

from mathwizard.db.client import DBClient


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'roster.db'}")


def test_create_teacher_and_student(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    teacher_user = db.create_user("teacher", "hash")
    student_user = db.create_user("student", "hash")
    assert teacher_user.id is not None
    assert student_user.id is not None

    teacher = db.create_teacher(teacher_user.id)
    assert teacher.id is not None
    assert teacher.user_id == teacher_user.id

    student = db.create_student(student_user.id, teacher.id)
    assert student.id is not None
    assert student.user_id == student_user.id
    assert student.teacher_id == teacher.id


def test_list_student_users_for_teacher(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    teacher_user = db.create_user("teacher", "hash")
    assert teacher_user.id is not None
    teacher = db.create_teacher(teacher_user.id)
    assert teacher.id is not None

    alice = db.create_user("alice", "hash")
    bob = db.create_user("bob", "hash")
    assert alice.id is not None
    assert bob.id is not None
    db.create_student(alice.id, teacher.id)
    db.create_student(bob.id, teacher.id)

    students = db.list_student_users_for_teacher(teacher.id)

    assert [s.username for s in students] == ["alice", "bob"]


def test_get_teacher_user(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    teacher_user = db.create_user("teacher", "hash")
    assert teacher_user.id is not None
    teacher = db.create_teacher(teacher_user.id)
    assert teacher.id is not None

    resolved = db.get_teacher_user(teacher.id)

    assert resolved is not None
    assert resolved.id == teacher_user.id
    assert resolved.username == "teacher"


def test_role_lookups_return_none_for_plain_user(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    user = db.create_user("nobody", "hash")
    assert user.id is not None

    assert db.get_teacher_by_user_id(user.id) is None
    assert db.get_student_by_user_id(user.id) is None


def test_get_teacher_by_user_id_returns_teacher(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    teacher_user = db.create_user("teacher", "hash")
    student_user = db.create_user("student", "hash")
    assert teacher_user.id is not None
    assert student_user.id is not None
    teacher = db.create_teacher(teacher_user.id)
    assert teacher.id is not None
    db.create_student(student_user.id, teacher.id)

    assert db.get_teacher_by_user_id(teacher_user.id) is not None
    found_student = db.get_student_by_user_id(student_user.id)
    assert found_student is not None
    assert found_student.teacher_id == teacher.id
