from types import TracebackType
from typing import Protocol, Self

from mathwizard.ports.figure import FigureRepository
from mathwizard.ports.question import QuestionRepository
from mathwizard.ports.roster import RosterRepository
from mathwizard.ports.session import SessionRepository
from mathwizard.ports.user import UserRepository


class Transaction(Protocol):
    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class AuthUnitOfWork(Transaction, Protocol):
    users: UserRepository
    sessions: SessionRepository


class RosterUnitOfWork(Transaction, Protocol):
    users: UserRepository
    roster: RosterRepository


class QuestionUnitOfWork(Transaction, Protocol):
    questions: QuestionRepository


class FigureUnitOfWork(Transaction, Protocol):
    figures: FigureRepository


class BootstrapUnitOfWork(Transaction, Protocol):
    users: UserRepository
    roster: RosterRepository
    questions: QuestionRepository
    figures: FigureRepository


class UnitOfWork(Transaction, Protocol):
    users: UserRepository
    sessions: SessionRepository
    roster: RosterRepository
    questions: QuestionRepository
    figures: FigureRepository


class UnitOfWorkFactory(Protocol):
    def __call__(self) -> UnitOfWork: ...
