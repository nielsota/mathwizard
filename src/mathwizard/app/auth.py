from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from mathwizard.app.dependencies import AuthServiceDep
from mathwizard.exceptions import AuthenticationError
from mathwizard.models.auth import LoginRequest, UserResponse
from mathwizard.models.db import User
from mathwizard.services.auth import user_response


def _set_session_cookie(
    response: Response,
    *,
    cookie_name: str,
    token: str,
    max_age_seconds: int,
    secure: bool,
) -> None:
    response.set_cookie(
        key=cookie_name,
        value=token,
        max_age=max_age_seconds,
        httponly=True,
        secure=secure,
        samesite="lax",
    )


def get_current_user(
    request: Request,
    auth_service: AuthServiceDep,
) -> User:
    session_token = request.cookies.get(auth_service.session_cookie_name)
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
        cookie_name=auth_service.session_cookie_name,
        token=result.session_token,
        max_age_seconds=result.max_age_seconds,
        secure=result.cookie_secure,
    )
    return result.user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    auth_service: AuthServiceDep,
) -> None:
    cookie_name = auth_service.session_cookie_name
    session_token = request.cookies.get(cookie_name)
    auth_service.logout(session_token)
    response.delete_cookie(cookie_name)


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUserDep) -> UserResponse:
    return user_response(user)
