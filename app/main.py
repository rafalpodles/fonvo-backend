import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.connection import close_pool, init_pool
from app.middleware.error_handler import global_exception_handler
from app.middleware.logging import RequestLoggingMiddleware
from app.routers import ai, conversations, health, preferences, profiles, streaks, vocabulary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
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
