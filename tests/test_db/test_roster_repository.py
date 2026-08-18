from sqlalchemy.orm import Session, sessionmaker

from mathwizard.db.repositories.roster import SqlAlchemyRosterRepository
from mathwizard.db.repositories.user import SqlAlchemyUserRepository
from mathwizard.ports.roster import RosterRepository


def _add_user(session: Session, username: str) -> int:
    return SqlAlchemyUserRepository(session).add(
        username=username, password_hash="hash"
    ).id


def test_repository_satisfies_the_roster_repository_protocol(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository: RosterRepository = SqlAlchemyRosterRepository(session)

    assert repository is not None


def test_add_teacher_and_lookup_by_user_id(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        user_id = _add_user(session, "root")
        repository = SqlAlchemyRosterRepository(session)
        created = repository.add_teacher(user_id)
        session.commit()

    with session_factory() as session:
        found = SqlAlchemyRosterRepository(session).get_teacher_by_user_id(user_id)

    assert found is not None
    assert found.id == created.id
    assert found.user_id == user_id


def test_get_teacher_by_user_id_returns_none_when_absent(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        assert SqlAlchemyRosterRepository(session).get_teacher_by_user_id(99) is None


def test_get_teacher_returns_the_teacher_row(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = SqlAlchemyRosterRepository(session)
        teacher = repository.add_teacher(_add_user(session, "root"))
        session.commit()

    with session_factory() as session:
        found = SqlAlchemyRosterRepository(session).get_teacher(teacher.id)

    assert found is not None
    assert found.user_id == teacher.user_id


def test_add_student_links_to_a_teacher(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = SqlAlchemyRosterRepository(session)
        teacher = repository.add_teacher(_add_user(session, "root"))
        student_user_id = _add_user(session, "student1")
        repository.add_student(student_user_id, teacher.id)
        session.commit()

    with session_factory() as session:
        found = SqlAlchemyRosterRepository(session).get_student_by_user_id(
            student_user_id
        )

    assert found is not None
    assert found.teacher_id == teacher.id


def test_list_students_for_teacher_returns_only_that_teachers_students(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = SqlAlchemyRosterRepository(session)
        teacher = repository.add_teacher(_add_user(session, "root"))
        other = repository.add_teacher(_add_user(session, "other"))
        first = _add_user(session, "student1")
        second = _add_user(session, "student2")
        outsider = _add_user(session, "student3")
        repository.add_student(first, teacher.id)
        repository.add_student(second, teacher.id)
        repository.add_student(outsider, other.id)
        session.commit()

    with session_factory() as session:
        students = SqlAlchemyRosterRepository(session).list_students_for_teacher(
            teacher.id
        )

    assert [student.user_id for student in students] == [first, second]


def test_list_students_for_teacher_is_empty_without_students(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = SqlAlchemyRosterRepository(session)
        teacher = repository.add_teacher(_add_user(session, "root"))
        session.commit()

    with session_factory() as session:
        students = SqlAlchemyRosterRepository(session).list_students_for_teacher(
            teacher.id
        )

    assert students == []
