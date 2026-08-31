from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session, sessionmaker

from mathwizard.db.repositories.figure import SqlAlchemyFigureRepository
from mathwizard.db.repositories.question import SqlAlchemyQuestionRepository
from mathwizard.db.repositories.roster import SqlAlchemyRosterRepository
from mathwizard.db.repositories.session import SqlAlchemySessionRepository
from mathwizard.db.repositories.user import SqlAlchemyUserRepository
from mathwizard.ports.unit_of_work import UnitOfWork, UnitOfWorkFactory

_REPOSITORY_ATTRIBUTES = ("users", "sessions", "roster", "questions", "figures")


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(self) -> Self:
        if self._session is not None:
            raise RuntimeError(
                "UnitOfWork is already open; nested transactions are not supported"
            )
        session = self._session_factory()
        self._session = session
        self.users = SqlAlchemyUserRepository(session)
        self.sessions = SqlAlchemySessionRepository(session)
        self.roster = SqlAlchemyRosterRepository(session)
        self.questions = SqlAlchemyQuestionRepository(session)
        self.figures = SqlAlchemyFigureRepository(session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        session = self._session
        if session is None:
            return
        self._session = None
        # A closed Session quietly opens a fresh transaction when it is used again,
        # so the repositories are dropped with the block that created them. Reaching
        # for one afterwards then fails instead of writing where nobody commits.
        for name in _REPOSITORY_ATTRIBUTES:
            self.__dict__.pop(name, None)
        try:
            session.rollback()
        finally:
            session.close()

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork is not open; use `with uow:` first")
        self._session.commit()

    def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork is not open; use `with uow:` first")
        self._session.rollback()


class SqlAlchemyUnitOfWorkFactory(UnitOfWorkFactory):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def __call__(self) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(self._session_factory)
