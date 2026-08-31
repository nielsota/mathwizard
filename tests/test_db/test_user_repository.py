import pytest
from sqlalchemy.orm import Session, sessionmaker

from mathwizard.db.repositories.user import SqlAlchemyUserRepository
from mathwizard.exceptions import UserNotFoundError


def test_add_returns_a_domain_user_with_an_id(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        user = SqlAlchemyUserRepository(session).add(
            username="root", password_hash="hash"
        )

    assert user.id == 1
    assert user.username == "root"
    assert user.password_hash == "hash"


def test_add_does_not_commit(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        SqlAlchemyUserRepository(session).add(username="root", password_hash="hash")
        session.rollback()

    with session_factory() as session:
        assert SqlAlchemyUserRepository(session).get_by_username("root") is None


def test_get_raises_when_the_user_is_missing(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session, pytest.raises(UserNotFoundError):
        SqlAlchemyUserRepository(session).get(99)


def test_get_by_username_returns_none_when_missing(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        assert SqlAlchemyUserRepository(session).get_by_username("nobody") is None


def test_get_many_returns_requested_users_in_id_order(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        repository = SqlAlchemyUserRepository(session)
        repository.add(username="a", password_hash="h")
        repository.add(username="b", password_hash="h")
        repository.add(username="c", password_hash="h")
        session.commit()

    with session_factory() as session:
        found = SqlAlchemyUserRepository(session).get_many([3, 1])

    assert [user.username for user in found] == ["a", "c"]


def test_get_many_returns_empty_list_for_no_ids(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        assert SqlAlchemyUserRepository(session).get_many([]) == []
