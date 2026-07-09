from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from mathwizard.settings import get_settings
from mathwizard.db.client import DBClient
import mathwizard.services.bootstrap as bootstrap


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()

    app.state.settings = settings
    app.state.db = DBClient(settings.database_url)

    bootstrap.run_all(app.state.db, settings.practice_dir)

    yield

    app.state.db.engine.dispose()


app = FastAPI(title="MathWizard", version="0.1.0", lifespan=lifespan)


@app.get("/")
def health():
    return {"message": "OK"}
