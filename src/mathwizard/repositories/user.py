from collections.abc import Sequence
from typing import Protocol

from mathwizard.models.domain.user import User, UserDraft


class UserRepository(Protocol):
    def add(self, draft: UserDraft) -> User: ...

    def get(self, user_id: int) -> User: ...

    def get_by_username(self, username: str) -> User | None: ...

    def get_many(self, user_ids: Sequence[int]) -> list[User]: ...
