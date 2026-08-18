from typing import Protocol

from mathwizard.enums import QuestionSource
from mathwizard.models.domain.question import Question, QuestionDraft


class QuestionRepository(Protocol):
    def add(self, draft: QuestionDraft) -> Question: ...

    def get(self, question_id: int) -> Question: ...

    def replace(self, question_id: int, draft: QuestionDraft) -> Question: ...

    def list(
        self,
        *,
        topic: str | None = None,
        source: QuestionSource | None = None,
    ) -> list[Question]: ...
