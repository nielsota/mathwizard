import pytest

from mathwizard.exceptions import QuestionNotFoundError, UserNotFoundError
from mathwizard.models.domain.figure import FigureDraft, FigureSpec, Viewport
from mathwizard.models.domain.question import QuestionDraft
from mathwizard.ports.unit_of_work import UnitOfWork
from tests.fakes import FakeUnitOfWork


def _spec() -> FigureSpec:
    return FigureSpec(viewport=Viewport(x=(-5.0, 5.0)))


def test_fake_unit_of_work_satisfies_the_unit_of_work_protocol() -> None:
    uow: UnitOfWork = FakeUnitOfWork()

    assert uow is not None


def test_fake_unit_of_work_reports_commit() -> None:
    uow = FakeUnitOfWork()

    with uow:
        uow.users.add(username="root", password_hash="hash")
        uow.commit()

    assert uow.committed is True


def test_fake_unit_of_work_resets_commit_flag_on_reentry() -> None:
    uow = FakeUnitOfWork()

    with uow:
        uow.commit()
    with uow:
        pass

    assert uow.committed is False


def test_fake_user_repository_assigns_incrementing_ids() -> None:
    uow = FakeUnitOfWork()

    with uow:
        first = uow.users.add(username="a", password_hash="h")
        second = uow.users.add(username="b", password_hash="h")

    assert (first.id, second.id) == (1, 2)


def test_fake_user_repository_get_raises_for_unknown_id() -> None:
    uow = FakeUnitOfWork()

    with uow, pytest.raises(UserNotFoundError):
        uow.users.get(99)


def test_fake_user_repository_get_many_returns_id_order() -> None:
    uow = FakeUnitOfWork()

    with uow:
        uow.users.add(username="a", password_hash="h")
        uow.users.add(username="b", password_hash="h")
        found = uow.users.get_many([2, 1])

    assert [user.id for user in found] == [1, 2]


def test_fake_question_repository_filters_by_topic() -> None:
    uow = FakeUnitOfWork()

    with uow:
        uow.questions.add(QuestionDraft(topic="derivatives", title="A", stem="s"))
        uow.questions.add(QuestionDraft(topic="goniometrie", title="B", stem="s"))
        found = uow.questions.list(topic="derivatives")

    assert [question.title for question in found] == ["A"]


def test_fake_question_repository_replace_raises_for_unknown_id() -> None:
    uow = FakeUnitOfWork()

    with uow, pytest.raises(QuestionNotFoundError):
        uow.questions.replace(99, QuestionDraft(topic="t", title="A", stem="s"))


def test_fake_figure_repository_upsert_updates_existing_slug() -> None:
    uow = FakeUnitOfWork()

    with uow:
        created = uow.figures.add(FigureDraft(slug="parabola", title="Old", spec=_spec()))
        updated = uow.figures.upsert(FigureDraft(slug="parabola", title="New", spec=_spec()))

    assert updated.id == created.id
    assert updated.title == "New"
