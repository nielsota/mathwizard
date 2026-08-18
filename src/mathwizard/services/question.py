from mathwizard.enums import QuestionSource
from mathwizard.models.domain.question import Question
from mathwizard.ports.unit_of_work import QuestionUnitOfWork


def _difficulty_key(question: Question) -> tuple[bool, int, str]:
    return (
        question.difficulty is None,
        question.difficulty if question.difficulty is not None else 0,
        question.title,
    )


class QuestionService:
    def list_questions(
        self,
        uow: QuestionUnitOfWork,
        *,
        topic: str | None,
        source: QuestionSource,
        sort_by_difficulty: bool,
    ) -> list[Question]:
        with uow:
            questions = uow.questions.list(topic=topic, source=source)
        if sort_by_difficulty:
            questions.sort(key=_difficulty_key)
        return questions
