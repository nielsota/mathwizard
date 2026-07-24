from typing import Annotated

from fastapi import Depends
from fastapi import Request

from mathwizard.services.auth import AuthService
from mathwizard.services.figure import FigureService
from mathwizard.services.question import QuestionService
from mathwizard.services.user import UserService


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


def get_question_service(request: Request) -> QuestionService:
    return request.app.state.question_service


def get_figure_service(request: Request) -> FigureService:
    return request.app.state.figure_service


def get_user_service(request: Request) -> UserService:
    return request.app.state.user_service


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
QuestionServiceDep = Annotated[QuestionService, Depends(get_question_service)]
FigureServiceDep = Annotated[FigureService, Depends(get_figure_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
