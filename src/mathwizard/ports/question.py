from abc import abstractmethod
from typing import Protocol

from mathwizard.models.domain.question import Question, QuestionDraft, QuestionSource


class QuestionRepository(Protocol):
    @abstractmethod
    def add(self, draft: QuestionDraft) -> Question: ...

    @abstractmethod
    def get(self, question_id: int) -> Question: ...

    @abstractmethod
    def replace(self, question_id: int, draft: QuestionDraft) -> Question: ...

    @abstractmethod
    def list(
        self,
        *,
        topic: str | None = None,
        source: QuestionSource | None = None,
    ) -> list[Question]: ...
