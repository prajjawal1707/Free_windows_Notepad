import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, dashboard, notes, settings as settings_api, users
from app.core.config import ALLOWED_ORIGINS, APP_VERSION, settings
from app.core.logging import setup_logging
from app.core.security import require_api_token
from app.db.database import init_db

log = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    setup_logging()
    init_db(settings.db_path)
    log.info("Backend ready (db=%s)", settings.db_path)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Desktop App API", version=APP_VERSION, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_methods=["*"],
        allow_headers=["Authorization", "Content-Type", "X-API-Token"],
    )
    guard = [Depends(require_api_token)]
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"], dependencies=guard)
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"], dependencies=guard)
    app.include_router(notes.router, prefix="/api/v1/notes", tags=["notes"], dependencies=guard)
    app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"], dependencies=guard)
    app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["settings"], dependencies=guard)

    @app.get("/health")
    def health():
        return {"status": "running", "version": APP_VERSION}

    return app


app = create_app()
