from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from mathwizard.app.auth import router as auth_router
from mathwizard.ports.unit_of_work import UnitOfWorkFactory
from mathwizard.services.auth import AuthService
from mathwizard.services.figure import FigureService
from mathwizard.services.question import QuestionService
from mathwizard.services.user import UserService
from mathwizard.settings import (
    BootstrapSettings,
    DatabaseSettings,
    Settings,
    WebSettings,
)
from tests.fakes import FakePasswordHasher


def make_settings(*, session_cookie_name: str = "mw_session") -> Settings:
    return Settings(
        db=DatabaseSettings(url="sqlite:///unused.db"),
        web=WebSettings(
            session_cookie_name=session_cookie_name,
            cookie_secure=False,
            session_ttl_days=7,
        ),
        bootstrap=BootstrapSettings(username="niels", password="root"),
    )


def make_test_client(
    uow_factory: UnitOfWorkFactory,
    *routers: APIRouter,
    settings: Settings | None = None,
) -> TestClient:
    settings = settings or make_settings()
    app = FastAPI()
    app.state.uow_factory = uow_factory
    app.state.auth_service = AuthService(settings, hasher=FakePasswordHasher())
    app.state.question_service = QuestionService()
    app.state.figure_service = FigureService()
    app.state.user_service = UserService()
    app.include_router(auth_router)
    for router in routers:
        app.include_router(router)
    return TestClient(app)
