from sqlalchemy import select
from sqlalchemy.orm import Session

from mathwizard.db.mapping import apply_question_draft, question_to_domain
from mathwizard.db.tables.question import QuestionSchema
from mathwizard.exceptions import QuestionNotFoundError
from mathwizard.models.domain.question import Question, QuestionDraft, QuestionSource
from mathwizard.ports.question import QuestionRepository


class SqlAlchemyQuestionRepository(QuestionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, draft: QuestionDraft) -> Question:
        row = QuestionSchema()
        apply_question_draft(row, draft)
        self._session.add(row)
        self._session.flush()
        return question_to_domain(row)

    def get(self, question_id: int) -> Question:
        row = self._session.get(QuestionSchema, question_id)
        if row is None:
            raise QuestionNotFoundError(question_id)
        return question_to_domain(row)

    def replace(self, question_id: int, draft: QuestionDraft) -> Question:
        row = self._session.get(QuestionSchema, question_id)
        if row is None:
            raise QuestionNotFoundError(question_id)
        apply_question_draft(row, draft)
        self._session.flush()
        return question_to_domain(row)

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
        return [
            question_to_domain(row) for row in self._session.scalars(statement).all()
        ]
