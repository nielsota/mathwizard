from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from mathwizard.app.auth import router as auth_router
from mathwizard.app.routes.practice import router as practice_router
from mathwizard.db.client import DBClient
import mathwizard.services.bootstrap as bootstrap
from mathwizard.services.auth import AuthService
from mathwizard.services.question import QuestionService
from mathwizard.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()
    db = DBClient(settings.database_url)

    app.state.settings = settings

    bootstrap.run_all(db, settings.practice_dir)
    app.state.auth_service = AuthService(db, settings)
    app.state.question_service = QuestionService(db)

    yield

    db.engine.dispose()


app = FastAPI(title="MathWizard", version="0.1.0", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(practice_router)


@app.get("/")
def health():
    return {"message": "OK"}
