from tests.fakes import FakeUnitOfWork

from mathwizard.models.domain.question import QuestionDraft, QuestionSource
from mathwizard.services.question import QuestionService


def _seed(
    uow: FakeUnitOfWork,
    *,
    title: str,
    difficulty: int | None,
    topic: str = "derivatives",
) -> None:
    with uow:
        uow.questions.add(
            QuestionDraft(
                topic=topic,
                title=title,
                stem=f"Stem for {title}",
                source=QuestionSource.PRACTICE,
                tags=["practice", topic],
                difficulty=difficulty,
                calculator_allowed=False,
                parts=[{"text": f"Part for {title}", "points": 2}],
            )
        )
        uow.commit()


def test_list_questions_sorts_by_difficulty_then_title() -> None:
    uow = FakeUnitOfWork()
    _seed(uow, title="Hard", difficulty=5)
    _seed(uow, title="Easy", difficulty=1)
    _seed(uow, title="Unknown", difficulty=None)

    questions = QuestionService().list_questions(
        uow,
        topic="derivatives",
        source=QuestionSource.PRACTICE,
        sort_by_difficulty=True,
    )

    assert [question.title for question in questions] == ["Easy", "Hard", "Unknown"]


def test_list_questions_preserves_insertion_order_when_sorting_is_off() -> None:
    uow = FakeUnitOfWork()
    _seed(uow, title="Hard", difficulty=5)
    _seed(uow, title="Easy", difficulty=1)

    questions = QuestionService().list_questions(
        uow,
        topic="derivatives",
        source=QuestionSource.PRACTICE,
        sort_by_difficulty=False,
    )

    assert [question.title for question in questions] == ["Hard", "Easy"]


def test_list_questions_filters_by_topic() -> None:
    uow = FakeUnitOfWork()
    _seed(uow, title="Derivative", difficulty=1)
    _seed(uow, title="Trig", difficulty=1, topic="goniometrie")

    questions = QuestionService().list_questions(
        uow,
        topic="derivatives",
        source=QuestionSource.PRACTICE,
        sort_by_difficulty=True,
    )

    assert [question.title for question in questions] == ["Derivative"]


def test_list_questions_returns_domain_entities_with_max_marks() -> None:
    uow = FakeUnitOfWork()
    _seed(uow, title="Easy", difficulty=1)

    questions = QuestionService().list_questions(
        uow,
        topic="derivatives",
        source=QuestionSource.PRACTICE,
        sort_by_difficulty=True,
    )

    assert questions[0].max_marks == 2
    assert questions[0].stem == "Stem for Easy"


def test_list_questions_does_not_commit_for_a_read() -> None:
    uow = FakeUnitOfWork()

    QuestionService().list_questions(
        uow,
        topic="derivatives",
        source=QuestionSource.PRACTICE,
        sort_by_difficulty=True,
    )

    assert uow.committed is False
