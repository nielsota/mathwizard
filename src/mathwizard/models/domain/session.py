from datetime import datetime

from pydantic import BaseModel


class AuthSessionDraft(BaseModel):
    token: str
    user_id: int
    created_at: datetime
    expires_at: datetime


class AuthSession(BaseModel):
    token: str
    user_id: int
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None

    def is_active(self, now: datetime) -> bool:
        return self.revoked_at is None and self.expires_at > now
