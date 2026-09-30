from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import APP_NAME, APP_VERSION
from .database import init_db
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    # Create SQLite tables on startup.
    init_db()

    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "AI-powered personalized fitness plan generator "
        "using FastAPI, Gemini and SQLite."
    ),
    lifespan=lifespan
)


# Static files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# Routes
app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": "FitBuddy"
    }