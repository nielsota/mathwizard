from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from mathwizard.app.auth import router as auth_router
from mathwizard.app.routes.figures import router as figures_router
from mathwizard.app.routes.practice import router as practice_router
from mathwizard.app.routes.roster import router as roster_router
from mathwizard.db.engine import create_db_engine, create_session_factory
from mathwizard.db.unit_of_work import SqlAlchemyUnitOfWorkFactory
from mathwizard.services.auth import AuthService
from mathwizard.services.bootstrap import BootstrapService
from mathwizard.services.figure import FigureService
from mathwizard.services.question import QuestionService
from mathwizard.services.user import UserService
from mathwizard.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()
    engine = create_db_engine(settings.database_url)
    uow_factory = SqlAlchemyUnitOfWorkFactory(create_session_factory(engine))

    BootstrapService(settings).run_all(uow_factory())

    app.state.uow_factory = uow_factory
    app.state.auth_service = AuthService(settings)
    app.state.question_service = QuestionService()
    app.state.figure_service = FigureService()
    app.state.user_service = UserService()

    yield

    engine.dispose()


app = FastAPI(title="MathWizard", version="0.1.0", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(practice_router)
app.include_router(figures_router)
app.include_router(roster_router)


@app.get("/")
def health():
    return {"message": "OK"}
