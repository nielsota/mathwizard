from typing import Annotated, Any

from fastapi import APIRouter, Query

from mathwizard.app.auth import CurrentUserDep
from mathwizard.app.dependencies import QuestionServiceDep, UnitOfWorkDep
from mathwizard.enums import QuestionSource
from mathwizard.models.api.question import QuestionListResponse

router = APIRouter(prefix="/api/v1/practice", tags=["practice"])


@router.get("/{topic}", response_model=QuestionListResponse)
def get_practice_topic(
    topic: str,
    uow: UnitOfWorkDep,
    question_service: QuestionServiceDep,
    current_user: CurrentUserDep,
    sort_by_difficulty: Annotated[bool, Query()] = True,
) -> dict[str, Any]:
    questions = question_service.list_questions(
        uow,
        topic=topic,
        source=QuestionSource.PRACTICE,
        sort_by_difficulty=sort_by_difficulty,
    )
    return {
        "source": QuestionSource.PRACTICE,
        "topic": topic,
        "questions": questions,
    }
