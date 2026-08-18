from sqlalchemy import select
from sqlalchemy.orm import Session

from mathwizard.db.tables.question import QuestionPartSchema, QuestionSchema
from mathwizard.enums import QuestionSource
from mathwizard.exceptions import QuestionNotFoundError
from mathwizard.models.domain.question import Question, QuestionDraft, QuestionPart


def _to_domain(row: QuestionSchema) -> Question:
    return Question(
        id=row.id,
        topic=row.topic,
        title=row.title,
        stem=row.stem,
        source=row.source,
        tags=list(row.tags),
        exam_id=row.exam_id,
        calculator_allowed=row.calculator_allowed,
        difficulty=row.difficulty,
        parts=[
            QuestionPart(
                id=part.id,
                label=part.label,
                text=part.text,
                points=part.points,
            )
            for part in row.parts
        ],
    )


def _part_rows(draft: QuestionDraft) -> list[QuestionPartSchema]:
    return [
        QuestionPartSchema(label=part.label, text=part.text, points=part.points)
        for part in draft.parts
    ]


class SqlAlchemyQuestionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, draft: QuestionDraft) -> Question:
        row = QuestionSchema(
            topic=draft.topic,
            title=draft.title,
            stem=draft.stem,
            source=draft.source,
            tags=list(draft.tags),
            exam_id=draft.exam_id,
            calculator_allowed=draft.calculator_allowed,
            difficulty=draft.difficulty,
            parts=_part_rows(draft),
        )
        self._session.add(row)
        self._session.flush()
        return _to_domain(row)

    def get(self, question_id: int) -> Question:
        row = self._session.get(QuestionSchema, question_id)
        if row is None:
            raise QuestionNotFoundError(question_id)
        return _to_domain(row)

    def replace(self, question_id: int, draft: QuestionDraft) -> Question:
        row = self._session.get(QuestionSchema, question_id)
        if row is None:
            raise QuestionNotFoundError(question_id)
        row.topic = draft.topic
        row.title = draft.title
        row.stem = draft.stem
        row.source = draft.source
        row.tags = list(draft.tags)
        row.exam_id = draft.exam_id
        row.calculator_allowed = draft.calculator_allowed
        row.difficulty = draft.difficulty
        row.parts = _part_rows(draft)
        self._session.flush()
        return _to_domain(row)

    def list(
        self,
        *,
        topic: str | None = None,
        source: QuestionSource | None = None,
    ) -> list[Question]:
        statement = select(QuestionSchema).order_by(QuestionSchema.id)
        if topic is not None:
            statement = statement.where(QuestionSchema.topic == topic)
        if source is not None:
            statement = statement.where(QuestionSchema.source == source)
        return [_to_domain(row) for row in self._session.scalars(statement).all()]
