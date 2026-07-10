from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mathwizard.app.auth import router as auth_router
from mathwizard.app.routes.practice import router as practice_router
from mathwizard.db.client import DBClient
from mathwizard.enums import QuestionSource
from mathwizard.services.auth import AuthService, hash_password
from mathwizard.services.question import QuestionService
from mathwizard.settings import Settings


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'api.db'}")


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        openai_api_key="dummy",
        session_secret_key="dummy",
        database_url=f"sqlite:///{tmp_path / 'api.db'}",
        cognito_domain="unused",
        cognito_client_id="unused",
        cognito_client_secret="unused",
        cognito_user_pool_id="unused",
        cookie_secure=False,
        session_ttl_days=7,
    )


def make_client(db: DBClient, tmp_path: Path) -> TestClient:
    app = FastAPI()
    app.state.auth_service = AuthService(db, make_settings(tmp_path))
    app.state.question_service = QuestionService(db)
    app.include_router(auth_router)
    app.include_router(practice_router)
    return TestClient(app)


def authenticate(client: TestClient, db: DBClient) -> None:
    db.create_user("root", hash_password("secret"))
    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )
    assert response.status_code == 200


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


def test_get_practice_topic_requires_authentication(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, tmp_path)

    response = client.get("/api/v1/practice/derivatives")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_practice_topic_returns_service_response(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    seed_question(db, topic="derivatives", title="Hard", difficulty=5)
    seed_question(db, topic="derivatives", title="Easy", difficulty=1)
    client = make_client(db, tmp_path)
    authenticate(client, db)

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
    client = make_client(db, tmp_path)
    authenticate(client, db)

    response = client.get("/api/v1/practice/derivatives?sort_by_difficulty=false")

    assert response.status_code == 200
    data = response.json()
    assert [question["title"] for question in data["questions"]] == ["Hard", "Easy"]
