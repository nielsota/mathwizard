from datetime import datetime

from sqlalchemy.orm import Session

from mathwizard.db.mapping import session_to_domain
from mathwizard.db.tables.session import SessionSchema
from mathwizard.models.domain.session import AuthSession
from mathwizard.ports.session import SessionRepository


class SqlAlchemySessionRepository(SessionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        *,
        token: str,
        user_id: int,
        created_at: datetime,
        expires_at: datetime,
    ) -> AuthSession:
        row = SessionSchema(
            token=token,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
        )
        self._session.add(row)
        self._session.flush()
        return session_to_domain(row)

    def get(self, token: str) -> AuthSession | None:
        row = self._session.get(SessionSchema, token)
        return None if row is None else session_to_domain(row)

    def revoke(self, token: str, revoked_at: datetime) -> None:
        row = self._session.get(SessionSchema, token)
        if row is not None and row.revoked_at is None:
            row.revoked_at = revoked_at
            self._session.flush()
