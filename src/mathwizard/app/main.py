from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from mathwizard.app.routes.practice import router as practice_router
from mathwizard.db.client import DBClient
import mathwizard.services.bootstrap as bootstrap
from mathwizard.services.question import QuestionService
from mathwizard.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()

    app.state.settings = settings
    app.state.db = DBClient(settings.database_url)

    bootstrap.run_all(app.state.db, settings.practice_dir)
    app.state.question_service = QuestionService(app.state.db)

    yield

    app.state.db.engine.dispose()


app = FastAPI(title="MathWizard", version="0.1.0", lifespan=lifespan)
app.include_router(practice_router)


@app.get("/")
def health():
    return {"message": "OK"}
