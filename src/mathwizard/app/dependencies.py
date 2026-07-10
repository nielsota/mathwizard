from typing import Annotated

from fastapi import Depends
from fastapi import Request

from mathwizard.services.question import QuestionService


def get_question_service(request: Request) -> QuestionService:
    return request.app.state.question_service


QuestionServiceDep = Annotated[QuestionService, Depends(get_question_service)]
