from pydantic import BaseModel

from mathwizard.enums import UserRole


class User(BaseModel):
    id: int
    username: str
    password_hash: str


class UserWithRole(BaseModel):
    id: int
    username: str
    role: UserRole
