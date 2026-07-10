from sqlmodel import Session as DBSession
from sqlmodel import select

from mathwizard.db.mixins.base import NeedsEngine
from mathwizard.exceptions import UserNotFoundError
from mathwizard.models.db import User


class UserMixin(NeedsEngine):

    def create_user(self, username: str, password_hash: str) -> User:
        with DBSession(self.engine) as session:
            user = User(username=username, password_hash=password_hash)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_user(self, user_id: int) -> User:
        with DBSession(self.engine) as session:
            user = session.get(User, user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    def get_user_by_username(self, username: str) -> User | None:
        with DBSession(self.engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()
            return user
