import secrets
from datetime import timedelta

from sqlmodel import Session as DBSession

from mathwizard.db.mixins.base import NeedsEngine
from mathwizard.models.db import Session, _utcnow


class SessionsMixin(NeedsEngine):
    def create_session(self, user_id: int, ttl: timedelta) -> Session:
        token = secrets.token_urlsafe(32)
        now = _utcnow()
        user_session = Session(
            id=token,
            user_id=user_id,
            created_at=now,
            expires_at=now + ttl,
        )
        with DBSession(self.engine) as session:
            session.add(user_session)
            session.commit()
            session.refresh(user_session)
            return user_session

    def get_session(self, token: str) -> Session | None:
        with DBSession(self.engine) as session:
            user_session = session.get(Session, token)
            if user_session is None:
                return None
            if user_session.revoked_at is not None:
                return None
            if user_session.expires_at <= _utcnow():
                return None
            return user_session

    def revoke_session(self, token: str) -> None:
        with DBSession(self.engine) as session:
            user_session = session.get(Session, token)
            if user_session is not None and user_session.revoked_at is None:
                user_session.revoked_at = _utcnow()
                session.add(user_session)
                session.commit()
