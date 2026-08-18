from datetime import datetime
from typing import Protocol

from mathwizard.models.domain.session import AuthSession, AuthSessionDraft


class SessionRepository(Protocol):
    def add(self, draft: AuthSessionDraft) -> AuthSession: ...

    def get(self, token: str) -> AuthSession | None: ...

    def revoke(self, token: str, revoked_at: datetime) -> None: ...
