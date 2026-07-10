from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from mathwizard.app.dependencies import AuthServiceDep
from mathwizard.exceptions import AuthenticationError
from mathwizard.models.auth import LoginRequest
from mathwizard.models.auth import UserResponse
from mathwizard.models.db import User
from mathwizard.services.auth import user_response

SESSION_COOKIE_NAME = "mw_session"


def _set_session_cookie(
    response: Response,
    *,
    token: str,
    max_age_seconds: int,
    secure: bool,
) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=max_age_seconds,
        httponly=True,
        secure=secure,
        samesite="lax",
    )


def get_current_user(
    auth_service: AuthServiceDep,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> User:
    try:
        return auth_service.get_current_user(session_token)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


CurrentUserDep = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserResponse)
def login(
    body: LoginRequest,
    response: Response,
    auth_service: AuthServiceDep,
) -> UserResponse:
    try:
        result = auth_service.login(body)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    _set_session_cookie(
        response,
        token=result.session_token,
        max_age_seconds=result.max_age_seconds,
        secure=result.cookie_secure,
    )
    return result.user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    auth_service: AuthServiceDep,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> None:
    auth_service.logout(session_token)
    response.delete_cookie(SESSION_COOKIE_NAME)


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUserDep) -> UserResponse:
    return user_response(user)
