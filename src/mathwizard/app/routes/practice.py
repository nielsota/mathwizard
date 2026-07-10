from typing import Annotated

from fastapi import APIRouter, Query

from mathwizard.app.dependencies import QuestionServiceDep
from mathwizard.enums import QuestionSource
from mathwizard.models.question import (
    QuestionListRequest,
    QuestionListResponse,
)


router = APIRouter(prefix="/api/v1/practice", tags=["practice"])


@router.get("/{topic}")
def get_practice_topic(
    topic: str,
    question_service: QuestionServiceDep,
    sort_by_difficulty: Annotated[bool, Query()] = True,
) -> QuestionListResponse:
    return question_service.list_questions(
        QuestionListRequest(
            source=QuestionSource.PRACTICE,
            topic=topic,
            sort_by_difficulty=sort_by_difficulty,
        ),
    )
