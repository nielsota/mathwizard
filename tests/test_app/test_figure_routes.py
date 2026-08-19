from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from mathwizard.app.auth import router as auth_router
from mathwizard.app.routes.figures import router as figures_router
from mathwizard.db.base import Base
from mathwizard.db.client import DBClient
from mathwizard.db.engine import create_db_engine, create_session_factory
from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory
from mathwizard.models.domain.figure import FigureDraft, FigureSpec, Viewport
from mathwizard.services.auth import AuthService, hash_password
from mathwizard.services.figure import FigureService
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
    app.state.figure_service = FigureService()
    app.state.user_service = UserService(db)
    app.include_router(auth_router)
    app.include_router(figures_router)
    return TestClient(app)


def authenticate(client: TestClient, db: DBClient) -> None:
    user = db.create_user("root", hash_password("secret"))
    db.create_teacher(user.id)
    response = client.post("/auth/login", json={"username": "root", "password": "secret"})
    assert response.status_code == 200


def seed_figure(
    uow_factory: SqlAlchemyUnitOfWorkFactory,
    *,
    slug: str,
    title: str,
) -> int:
    with uow_factory() as uow:
        figure = uow.figures.add(
            FigureDraft(
                slug=slug,
                title=title,
                spec=FigureSpec(viewport=Viewport(x=(-5.0, 5.0))),
            )
        )
        uow.commit()
    return figure.id


VALID_BODY = {
    "slug": "parabool",
    "title": "Parabool",
    "spec": {
        "viewport": {"x": [-5, 5]},
        "elements": [{"type": "functionGraph", "fn": "x^2"}],
    },
}


def test_list_requires_authentication(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, make_uow_factory(tmp_path), tmp_path)
    assert client.get("/api/v1/figures").status_code == 401


def test_post_then_list_and_get(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, make_uow_factory(tmp_path), tmp_path)
    authenticate(client, db)

    created = client.post("/api/v1/figures", json=VALID_BODY)
    assert created.status_code == 201
    figure_id = created.json()["id"]

    listing = client.get("/api/v1/figures")
    assert listing.status_code == 200
    assert [f["slug"] for f in listing.json()["figures"]] == ["parabool"]

    detail = client.get(f"/api/v1/figures/{figure_id}")
    assert detail.status_code == 200
    assert detail.json()["spec"]["elements"][0]["fn"] == "x^2"


def test_list_figures_omits_spec_and_description(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    uow_factory = make_uow_factory(tmp_path)
    seed_figure(uow_factory, slug="parabola", title="Parabola")
    client = make_client(db, uow_factory, tmp_path)
    authenticate(client, db)

    response = client.get("/api/v1/figures")

    summary = response.json()["figures"][0]
    assert summary == {
        "id": 1,
        "slug": "parabola",
        "title": "Parabola",
        "question_id": None,
        "part_id": None,
    }


def test_post_duplicate_slug_conflicts(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, make_uow_factory(tmp_path), tmp_path)
    authenticate(client, db)
    client.post("/api/v1/figures", json=VALID_BODY)
    assert client.post("/api/v1/figures", json=VALID_BODY).status_code == 409


def test_post_malformed_spec_is_422(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, make_uow_factory(tmp_path), tmp_path)
    authenticate(client, db)
    bad = {"slug": "x", "title": "x", "spec": {"viewport": {"x": [-5, 5]},
           "elements": [{"type": "banana"}]}}
    assert client.post("/api/v1/figures", json=bad).status_code == 422


def test_get_missing_is_404(tmp_path: Path) -> None:
    db = make_db(tmp_path)
    client = make_client(db, make_uow_factory(tmp_path), tmp_path)
    authenticate(client, db)
    assert client.get("/api/v1/figures/999").status_code == 404
