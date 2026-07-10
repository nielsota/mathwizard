from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mathwizard.app.routes.practice import router
from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource
from mathwizard.services.question import QuestionService


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'api.db'}")


def make_client(db: DBClient) -> TestClient:
    app = FastAPI()
    app.state.question_service = QuestionService(db)
    app.include_router(router)
    return TestClient(app)


def seed_question(
    db: DBClient,
    *,
    topic: str,
    title: str,
    difficulty: int,
) -> None:
    db.create_question(
        title=title,
        stem=f"Stem for {title}",
        parts=[{"text": f"Part for {title}", "points": difficulty}],
        topic=topic,
        source=QuestionSource.PRACTICE,
        tags=["practice", topic],
        difficulty=difficulty,
        calculator_allowed=False,
    )


def test_get_practice_topic_returns_service_response(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_question(db, topic="derivatives", title="Hard", difficulty=5)
    seed_question(db, topic="derivatives", title="Easy", difficulty=1)
    client = make_client(db)

    response = client.get("/api/v1/practice/derivatives")

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "practice"
    assert data["topic"] == "derivatives"
    assert [question["title"] for question in data["questions"]] == ["Easy", "Hard"]
    assert data["questions"][0]["source"] == "practice"
    assert data["questions"][0]["tags"] == ["practice", "derivatives"]
    assert "exam_id" not in data["questions"][0]


def test_get_practice_topic_can_disable_difficulty_sort(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_question(db, topic="derivatives", title="Hard", difficulty=5)
    seed_question(db, topic="derivatives", title="Easy", difficulty=1)
    client = make_client(db)

    response = client.get("/api/v1/practice/derivatives?sort_by_difficulty=false")

    assert response.status_code == 200
    data = response.json()
    assert [question["title"] for question in data["questions"]] == ["Hard", "Easy"]
