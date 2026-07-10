from mathwizard.db.client import DBClient
from mathwizard.models.db import Question
from mathwizard.models.question import (
    QuestionListRequest,
    QuestionListResponse,
    QuestionPartResponse,
    QuestionResponse,
)


def _sort_key(question: Question) -> tuple[bool, int, str]:
    return (
        question.difficulty is None,
        question.difficulty if question.difficulty is not None else 0,
        question.title,
    )


def _question_to_response(
    question: Question,
    *,
    number: int,
) -> QuestionResponse:
    return QuestionResponse(
        id=question.id,
        number=number,
        source=question.source,
        topic=question.topic,
        tags=question.tags,
        title=question.title,
        question_text=question.stem,
        parts=[part.text for part in question.parts],
        part_details=[
            QuestionPartResponse(
                label=part.label,
                text=part.text,
                points=part.points,
            )
            for part in question.parts
        ],
        max_marks=sum(part.points for part in question.parts),
        calculator_allowed=question.calculator_allowed,
        difficulty=question.difficulty,
        figure_images=[],
    )


class QuestionService:
    def __init__(self, db: DBClient) -> None:
        self.db = db

    def list_questions(
        self,
        request: QuestionListRequest,
    ) -> QuestionListResponse:
        questions = self.db.list_questions(
            topic=request.topic,
            source=request.source,
        )
        if request.sort_by_difficulty:
            questions = sorted(questions, key=_sort_key)

        return QuestionListResponse(
            source=request.source,
            topic=request.topic,
            questions=[
                _question_to_response(question, number=i)
                for i, question in enumerate(questions, start=1)
            ],
        )
