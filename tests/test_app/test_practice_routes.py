from tests.app_client import make_test_client
from tests.fakes import FakePasswordHasher, FakeUnitOfWorkFactory

from mathwizard.app.routes.practice import router as practice_router
from mathwizard.models.domain.question import QuestionDraft, QuestionSource
from mathwizard.ports.unit_of_work import UnitOfWorkFactory


def authenticate(client, uow_factory: UnitOfWorkFactory) -> None:
    hasher = FakePasswordHasher()
    with uow_factory() as uow:
        user = uow.users.add(username="root", password_hash=hasher.hash("secret"))
        uow.roster.add_teacher(user.id)
        uow.commit()
    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )
    assert response.status_code == 200


def seed_question(
    uow_factory: UnitOfWorkFactory,
    *,
    topic: str,
    title: str,
    difficulty: int,
) -> None:
    with uow_factory() as uow:
        uow.questions.add(
            QuestionDraft(
                topic=topic,
                title=title,
                stem=f"Stem for {title}",
                source=QuestionSource.PRACTICE,
                tags=["practice", topic],
                difficulty=difficulty,
                calculator_allowed=False,
                parts=[{"text": f"Part for {title}", "points": difficulty}],
            )
        )
        uow.commit()


def test_get_practice_topic_requires_authentication() -> None:
    client = make_test_client(FakeUnitOfWorkFactory(), practice_router)

    response = client.get("/api/v1/practice/derivatives")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_practice_topic_returns_the_filtered_response() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_question(uow_factory, topic="derivatives", title="Hard", difficulty=5)
    seed_question(uow_factory, topic="derivatives", title="Easy", difficulty=1)
    client = make_test_client(uow_factory, practice_router)
    authenticate(client, uow_factory)

    response = client.get("/api/v1/practice/derivatives")

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "practice"
    assert data["topic"] == "derivatives"
    assert [question["title"] for question in data["questions"]] == ["Easy", "Hard"]
    assert data["questions"][0]["question_text"] == "Stem for Easy"
    assert data["questions"][0]["max_marks"] == 1
    assert data["questions"][0]["parts"] == [
        {"label": "a", "text": "Part for Easy", "points": 1}
    ]
    assert data["questions"][0]["figure_images"] == []


def test_get_practice_topic_omits_internal_fields() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_question(uow_factory, topic="derivatives", title="Easy", difficulty=1)
    client = make_test_client(uow_factory, practice_router)
    authenticate(client, uow_factory)

    response = client.get("/api/v1/practice/derivatives")

    question = response.json()["questions"][0]
    assert "stem" not in question
    assert "exam_id" not in question
    assert "number" not in question
    assert "part_details" not in question


def test_get_practice_topic_can_disable_difficulty_sort() -> None:
    uow_factory = FakeUnitOfWorkFactory()
    seed_question(uow_factory, topic="derivatives", title="Hard", difficulty=5)
    seed_question(uow_factory, topic="derivatives", title="Easy", difficulty=1)
    client = make_test_client(uow_factory, practice_router)
    authenticate(client, uow_factory)

    response = client.get("/api/v1/practice/derivatives?sort_by_difficulty=false")

    assert response.status_code == 200
    data = response.json()
    assert [question["title"] for question in data["questions"]] == ["Hard", "Easy"]
