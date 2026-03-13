import logging
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db.connection import close_pool, init_pool
from app.middleware.error_handler import global_exception_handler
from app.middleware.logging import RequestLoggingMiddleware
from app.routers import admin, ai, config, conversations, health, preferences, profiles, scenarios, streaks, vocabulary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_pool()
    except Exception as e:
        logger.error("Failed to initialize database pool: %s", e)
        # App still starts — health endpoint works, DB endpoints will fail gracefully
    yield
    await close_pool()


app = FastAPI(title="Fonvo API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(health.router)
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(vocabulary.router, prefix="/api/v1")
app.include_router(streaks.router, prefix="/api/v1")
app.include_router(preferences.router, prefix="/api/v1")
app.include_router(profiles.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(config.router, prefix="/api/v1")
app.include_router(scenarios.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

# Serve admin UI static files
_static_dir = Path(__file__).resolve().parent.parent / "static" / "admin"
if _static_dir.is_dir():
    app.mount("/admin", StaticFiles(directory=str(_static_dir), html=True), name="admin")
