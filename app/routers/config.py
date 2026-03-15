import logging
import time

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.db.connection import get_pool
from app.db.queries import config as queries
from app.auth.dependencies import get_user_or_guest
from app.middleware.admin_auth import require_admin
from app.models.config import (
    ConfigBundle,
    ModelConfigResponse,
    ModelConfigUpdateRequest,
    PromptResponse,
    PromptUpdateRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/config", tags=["config"])

# In-memory cache for the config bundle
_cache: dict = {"bundle": None, "hash": None, "expires_at": 0.0}
_CACHE_TTL = 60  # seconds


def _invalidate_cache() -> None:
    _cache["bundle"] = None
    _cache["hash"] = None
    _cache["expires_at"] = 0.0


async def _get_bundle(pool: asyncpg.Pool) -> ConfigBundle:
    now = time.monotonic()
    if _cache["bundle"] is not None and now < _cache["expires_at"]:
        return _cache["bundle"]

    prompts_list = await queries.get_all_active_prompts(pool)
    models_list = await queries.get_all_active_models(pool)
    config_hash = await queries.get_config_hash(pool)

    bundle = ConfigBundle(
        prompts={p.key: p.prompt_text for p in prompts_list},
        models={m.key: m for m in models_list},
        hash=config_hash,
    )

    _cache["bundle"] = bundle
    _cache["hash"] = config_hash
    _cache["expires_at"] = now + _CACHE_TTL

    return bundle


# ── Bundle endpoint ──────────────────────────────────────────


@router.get("/bundle", response_model=ConfigBundle)
async def get_config_bundle(
    request: Request,
    pool: asyncpg.Pool = Depends(get_pool),
    _caller=Depends(get_user_or_guest),
):
    """Return all active prompts and model configs with an ETag for caching."""
    bundle = await _get_bundle(pool)

    # Support If-None-Match for 304 responses
    if_none_match = request.headers.get("if-none-match")
    if if_none_match and if_none_match.strip('"') == bundle.hash:
        return Response(status_code=304)

    return Response(
        content=bundle.model_dump_json(),
        media_type="application/json",
        headers={"ETag": f'"{bundle.hash}"'},
    )


# ── Prompt endpoints ─────────────────────────────────────────


@router.get("/prompts", response_model=list[PromptResponse])
async def list_prompts(
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """List all active prompts with full details (admin)."""
    return await queries.get_all_active_prompts(pool)


@router.put("/prompts/{key:path}", response_model=PromptResponse)
async def update_prompt(
    key: str,
    body: PromptUpdateRequest,
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """Update a prompt by key (admin)."""
    updated = await queries.update_prompt(pool, key, body)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Prompt '{key}' not found")
    _invalidate_cache()

    # Return the updated prompt
    prompts = await queries.get_all_active_prompts(pool)
    prompt = next((p for p in prompts if p.key == key), None)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt '{key}' not found")
    return prompt


@router.delete("/prompts/{key:path}", status_code=204)
async def delete_prompt(
    key: str,
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """Soft-delete a prompt by key (admin)."""
    deleted = await queries.delete_prompt(pool, key)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Prompt '{key}' not found")
    _invalidate_cache()


# ── Model config endpoints ───────────────────────────────────


@router.get("/models", response_model=list[ModelConfigResponse])
async def list_models(
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """List all active model configs (admin)."""
    return await queries.get_all_active_models(pool)


@router.post("/models/{key:path}", response_model=ModelConfigResponse, status_code=201)
async def create_model_config(
    key: str,
    body: ModelConfigUpdateRequest,
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """Create a new model config (admin)."""
    created = await queries.create_model_config(pool, key, body)
    if not created:
        raise HTTPException(status_code=409, detail=f"Model config '{key}' already exists")
    _invalidate_cache()

    models = await queries.get_all_active_models(pool)
    model = next((m for m in models if m.key == key), None)
    if not model:
        raise HTTPException(status_code=500, detail="Created but not found")
    return model


@router.put("/models/{key:path}", response_model=ModelConfigResponse)
async def update_model_config(
    key: str,
    body: ModelConfigUpdateRequest,
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """Update a model config by key (admin)."""
    updated = await queries.update_model_config(pool, key, body)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Model config '{key}' not found")
    _invalidate_cache()

    # Return the updated model config
    models = await queries.get_all_active_models(pool)
    model = next((m for m in models if m.key == key), None)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model config '{key}' not found")
    return model


@router.delete("/models/{key:path}", status_code=204)
async def delete_model_config(
    key: str,
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """Soft-delete a model config by key (admin)."""
    deleted = await queries.delete_model_config(pool, key)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Model config '{key}' not found")
    _invalidate_cache()
