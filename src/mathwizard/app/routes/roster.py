from fastapi import APIRouter, HTTPException, status

from mathwizard.app.auth import CurrentUserDep
from mathwizard.app.dependencies import UserServiceDep
from mathwizard.exceptions import AuthorizationError
from mathwizard.models.user import MyTeacherResponse, StudentsResponse


router = APIRouter(prefix="/api/v1/roster", tags=["roster"])


@router.get("/students")
def list_students(
    user: CurrentUserDep,
    user_service: UserServiceDep,
) -> StudentsResponse:
    try:
        return user_service.list_students(user)
    except AuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get("/my-teacher")
def my_teacher(
    user: CurrentUserDep,
    user_service: UserServiceDep,
) -> MyTeacherResponse:
    try:
        return user_service.get_my_teacher(user)
    except AuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
