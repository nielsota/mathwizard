from enum import StrEnum

from pydantic import BaseModel


class UserRole(StrEnum):
    TEACHER = "teacher"
    STUDENT = "student"


class User(BaseModel):
    id: int
    username: str
    password_hash: str


class UserWithRole(BaseModel):
    id: int
    username: str
    role: UserRole
