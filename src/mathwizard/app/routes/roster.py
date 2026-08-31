from typing import Any

from fastapi import APIRouter, HTTPException, status

from mathwizard.app.auth import CurrentUserDep
from mathwizard.app.dependencies import UnitOfWorkDep, UserServiceDep
from mathwizard.exceptions import AuthorizationError
from mathwizard.models.api.user import MyTeacherResponse, StudentsResponse

router = APIRouter(prefix="/api/v1/roster", tags=["roster"])


@router.get("/students", response_model=StudentsResponse)
def list_students(
    uow: UnitOfWorkDep,
    user: CurrentUserDep,
    user_service: UserServiceDep,
) -> dict[str, Any]:
    try:
        return {"students": user_service.list_student_users(uow, user)}
    except AuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get("/my-teacher", response_model=MyTeacherResponse)
def my_teacher(
    uow: UnitOfWorkDep,
    user: CurrentUserDep,
    user_service: UserServiceDep,
) -> dict[str, Any]:
    try:
        return {"teacher": user_service.get_teacher_user(uow, user)}
    except AuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
