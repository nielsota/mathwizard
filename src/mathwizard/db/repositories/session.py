from datetime import datetime

from sqlalchemy.orm import Session

from mathwizard.db.tables.session import SessionSchema
from mathwizard.models.domain.session import AuthSession


def _to_domain(row: SessionSchema) -> AuthSession:
    return AuthSession(
        token=row.token,
        user_id=row.user_id,
        created_at=row.created_at,
        expires_at=row.expires_at,
        revoked_at=row.revoked_at,
    )


class SqlAlchemySessionRepository:
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
        return _to_domain(row)

    def get(self, token: str) -> AuthSession | None:
        row = self._session.get(SessionSchema, token)
        return None if row is None else _to_domain(row)

    def revoke(self, token: str, revoked_at: datetime) -> None:
        row = self._session.get(SessionSchema, token)
        if row is not None and row.revoked_at is None:
            row.revoked_at = revoked_at
            self._session.flush()
