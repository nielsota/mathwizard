from abc import abstractmethod
from datetime import datetime
from typing import Protocol

from mathwizard.models.domain.session import AuthSession


class SessionRepository(Protocol):
    @abstractmethod
    def add(
        self,
        *,
        token: str,
        user_id: int,
        created_at: datetime,
        expires_at: datetime,
    ) -> AuthSession: ...

    @abstractmethod
    def get(self, token: str) -> AuthSession | None: ...

    @abstractmethod
    def revoke(self, token: str, revoked_at: datetime) -> None: ...
