from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from mathwizard.models.domain.user import UserRole


class LoginRequest(BaseModel):
    username: str
    password: str = Field(max_length=64)


class SignupRequest(BaseModel):
    username: str
    password: str = Field(min_length=8, max_length=64)
    password_confirm: str

    @field_validator("username")
    @classmethod
    def username_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Username is required")
        return stripped

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
