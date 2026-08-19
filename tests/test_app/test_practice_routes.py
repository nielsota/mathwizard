from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from mathwizard.app.auth import router as auth_router
from mathwizard.app.routes.practice import router as practice_router
from mathwizard.db.base import Base
from mathwizard.db.client import DBClient
from mathwizard.db.engine import create_db_engine, create_session_factory
from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory
from mathwizard.enums import QuestionSource
from mathwizard.models.domain.question import QuestionDraft
from mathwizard.services.auth import AuthService, hash_password
from mathwizard.services.question import QuestionService
from mathwizard.services.user import UserService
from mathwizard.settings import Settings


def make_db(tmp_path: Path) -> DBClient:
    return DBClient(f"sqlite:///{tmp_path / 'legacy.db'}")


def make_uow_factory(tmp_path: Path) -> SqlAlchemyUnitOfWorkFactory:
    engine: Engine = create_db_engine(f"sqlite:///{tmp_path / 'api.db'}")
    Base.metadata.create_all(engine)
    return SqlAlchemyUnitOfWorkFactory(create_session_factory(engine))


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'legacy.db'}",
        cookie_secure=False,
        session_ttl_days=7,
    )


def make_client(
    db: DBClient,
    uow_factory: SqlAlchemyUnitOfWorkFactory,
    tmp_path: Path,
) -> TestClient:
    app = FastAPI()
    app.state.uow_factory = uow_factory
    app.state.auth_service = AuthService(db, make_settings(tmp_path))
    app.state.question_service = QuestionService()
    app.state.user_service = UserService(db)
    app.include_router(auth_router)
    app.include_router(practice_router)
    return TestClient(app)


def authenticate(client: TestClient, db: DBClient) -> None:
    user = db.create_user("root", hash_password("secret"))
    assert user.id is not None
    db.create_teacher(user.id)
    response = client.post(
        "/auth/login",
        json={"username": "root", "password": "secret"},
    )
    assert response.status_code == 200


def seed_question(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
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


def test_get_practice_topic_requires_authentication(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, make_uow_factory(tmp_path), tmp_path)

    response = client.get("/api/v1/practice/derivatives")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_practice_topic_returns_the_filtered_response(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    uow_factory = make_uow_factory(tmp_path)
    seed_question(uow_factory, topic="derivatives", title="Hard", difficulty=5)
    seed_question(uow_factory, topic="derivatives", title="Easy", difficulty=1)
    client = make_client(db, uow_factory, tmp_path)
    authenticate(client, db)

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


def test_get_practice_topic_omits_internal_fields(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    uow_factory = make_uow_factory(tmp_path)
    seed_question(uow_factory, topic="derivatives", title="Easy", difficulty=1)
    client = make_client(db, uow_factory, tmp_path)
    authenticate(client, db)

    response = client.get("/api/v1/practice/derivatives")

    question = response.json()["questions"][0]
    assert "stem" not in question
    assert "exam_id" not in question
    assert "number" not in question
    assert "part_details" not in question


def test_get_practice_topic_can_disable_difficulty_sort(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    uow_factory = make_uow_factory(tmp_path)
    seed_question(uow_factory, topic="derivatives", title="Hard", difficulty=5)
    seed_question(uow_factory, topic="derivatives", title="Easy", difficulty=1)
    client = make_client(db, uow_factory, tmp_path)
    authenticate(client, db)

    response = client.get("/api/v1/practice/derivatives?sort_by_difficulty=false")

    assert response.status_code == 200
    data = response.json()
    assert [question["title"] for question in data["questions"]] == ["Hard", "Easy"]
