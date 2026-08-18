import pytest

from mathwizard.db.repositories.figure import SqlAlchemyFigureRepository
from mathwizard.db.repositories.question import SqlAlchemyQuestionRepository
from mathwizard.db.repositories.roster import SqlAlchemyRosterRepository
from mathwizard.db.repositories.session import SqlAlchemySessionRepository
from mathwizard.db.repositories.user import SqlAlchemyUserRepository
from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory


def test_entering_wires_every_repository_to_the_same_session(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    with uow_factory() as uow:
        assert isinstance(uow.users, SqlAlchemyUserRepository)
        assert isinstance(uow.sessions, SqlAlchemySessionRepository)
        assert isinstance(uow.roster, SqlAlchemyRosterRepository)
        assert isinstance(uow.questions, SqlAlchemyQuestionRepository)
        assert isinstance(uow.figures, SqlAlchemyFigureRepository)


def test_commit_persists_across_units_of_work(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    with uow_factory() as uow:
        uow.users.add(username="root", password_hash="hash")
        uow.commit()

    with uow_factory() as uow:
        assert uow.users.get_by_username("root") is not None


def test_leaving_the_block_without_commit_discards_the_write(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    with uow_factory() as uow:
        uow.users.add(username="root", password_hash="hash")

    with uow_factory() as uow:
        assert uow.users.get_by_username("root") is None


def test_an_exception_rolls_back_the_transaction(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    with pytest.raises(RuntimeError):
        with uow_factory() as uow:
            uow.users.add(username="root", password_hash="hash")
            raise RuntimeError("boom")

    with uow_factory() as uow:
        assert uow.users.get_by_username("root") is None


def test_a_write_committed_before_a_later_failure_survives(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    with pytest.raises(RuntimeError):
        with uow_factory() as uow:
            uow.users.add(username="root", password_hash="hash")
            uow.commit()
            raise RuntimeError("boom")

    with uow_factory() as uow:
        assert uow.users.get_by_username("root") is not None


def test_the_same_unit_of_work_can_be_reused_sequentially(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    uow = uow_factory()

    with uow:
        uow.users.add(username="root", password_hash="hash")
        uow.commit()
    with uow:
        found = uow.users.get_by_username("root")

    assert found is not None


def test_nested_entry_is_rejected(uow_factory: SqlAlchemyUnitOfWorkFactory) -> None:
    uow = uow_factory()

    with uow:
        with pytest.raises(RuntimeError, match="nested"):
            with uow:
                pass


def test_commit_outside_a_block_is_rejected(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    uow = uow_factory()

    with pytest.raises(RuntimeError, match="not open"):
        uow.commit()


def test_rollback_outside_a_block_is_rejected(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    uow = uow_factory()

    with pytest.raises(RuntimeError, match="not open"):
        uow.rollback()


def test_repositories_are_unreachable_outside_the_block(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    uow = uow_factory()

    with pytest.raises(AttributeError):
        uow.users

    with uow:
        pass

    with pytest.raises(AttributeError):
        uow.users


def test_the_factory_returns_a_new_unit_of_work_each_call(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
) -> None:
    assert uow_factory() is not uow_factory()
