from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol

from mathwizard.models.domain.user import User


class UserRepository(Protocol):
    @abstractmethod
    def add(self, *, username: str, password_hash: str) -> User: ...

    @abstractmethod
    def get(self, user_id: int) -> User: ...

    @abstractmethod
    def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def get_many(self, user_ids: Sequence[int]) -> list[User]: ...
