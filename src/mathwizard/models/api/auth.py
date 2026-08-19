from pydantic import BaseModel

from mathwizard.enums import UserRole


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
