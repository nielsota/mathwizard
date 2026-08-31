from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from mathwizard.db.mapping import user_to_domain
from mathwizard.db.tables.user import UserSchema
from mathwizard.exceptions import UserNotFoundError
from mathwizard.models.domain.user import User
from mathwizard.ports.user import UserRepository


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, *, username: str, password_hash: str) -> User:
        row = UserSchema(username=username, password_hash=password_hash)
        self._session.add(row)
        self._session.flush()
        return user_to_domain(row)

    def get(self, user_id: int) -> User:
        row = self._session.get(UserSchema, user_id)
        if row is None:
            raise UserNotFoundError(user_id)
        return user_to_domain(row)

    def get_by_username(self, username: str) -> User | None:
        statement = select(UserSchema).where(UserSchema.username == username)
        row = self._session.scalars(statement).first()
        return None if row is None else user_to_domain(row)

    def get_many(self, user_ids: Sequence[int]) -> list[User]:
        if not user_ids:
            return []
        statement = (
            select(UserSchema)
            .where(UserSchema.id.in_(user_ids))
            .order_by(UserSchema.id)
        )
        return [user_to_domain(row) for row in self._session.scalars(statement).all()]
