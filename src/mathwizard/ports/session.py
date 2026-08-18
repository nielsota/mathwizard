from datetime import datetime
from typing import Protocol

from mathwizard.models.domain.session import AuthSession


class SessionRepository(Protocol):
    def add(
        self,
        *,
        token: str,
        user_id: int,
        created_at: datetime,
        expires_at: datetime,
    ) -> AuthSession: ...

    def get(self, token: str) -> AuthSession | None: ...

    def revoke(self, token: str, revoked_at: datetime) -> None: ...
