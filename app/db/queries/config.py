import json
import logging

import asyncpg

from app.models.config import (
    ModelConfigResponse,
    ModelConfigUpdateRequest,
    PromptResponse,
    PromptUpdateRequest,
)

logger = logging.getLogger(__name__)


def _parse_prompt_row(row: asyncpg.Record) -> PromptResponse:
    return PromptResponse(
        key=row["key"],
        prompt_text=row["prompt_text"],
        description=row["description"],
        placeholders=row["placeholders"] or [],
        version=row["version"],
        updated_at=row["updated_at"],
    )


def _parse_model_row(row: asyncpg.Record) -> ModelConfigResponse:
    extra = row["extra_config"]
    if isinstance(extra, str):
        extra = json.loads(extra)
    return ModelConfigResponse(
        key=row["key"],
        provider=row["provider"],
        model_id=row["model_id"],
        display_name=row["display_name"],
        extra_config=extra or {},
    )


async def get_all_active_prompts(pool: asyncpg.Pool) -> list[PromptResponse]:
    rows = await pool.fetch(
        "SELECT key, prompt_text, description, placeholders, version, updated_at "
        "FROM ai_prompts WHERE is_active = true ORDER BY key"
    )
    return [_parse_prompt_row(r) for r in rows]


async def get_all_active_models(pool: asyncpg.Pool) -> list[ModelConfigResponse]:
    rows = await pool.fetch(
        "SELECT key, provider, model_id, display_name, extra_config "
        "FROM ai_model_config WHERE is_active = true ORDER BY key"
    )
    return [_parse_model_row(r) for r in rows]


async def get_config_hash(pool: asyncpg.Pool) -> str:
    row = await pool.fetchrow(
        "SELECT md5(string_agg(updated_at::text, ',' ORDER BY key)) AS hash "
        "FROM ("
        "  SELECT key, updated_at FROM ai_prompts WHERE is_active = true "
        "  UNION ALL "
        "  SELECT key, updated_at FROM ai_model_config WHERE is_active = true"
        ") sub"
    )
    return row["hash"] if row and row["hash"] else ""


async def update_prompt(
    pool: asyncpg.Pool, key: str, data: PromptUpdateRequest
) -> bool:
    sets = ["prompt_text = $2", "updated_at = now()"]
    params: list = [key, data.prompt_text]
    idx = 3

    if data.description is not None:
        sets.append(f"description = ${idx}")
        params.append(data.description)
        idx += 1

    if data.placeholders is not None:
        sets.append(f"placeholders = ${idx}")
        params.append(data.placeholders)
        idx += 1

    # Bump version on every update
    sets.append("version = version + 1")

    query = f"UPDATE ai_prompts SET {', '.join(sets)} WHERE key = $1 AND is_active = true"
    result = await pool.execute(query, *params)
    return result == "UPDATE 1"


async def update_model_config(
    pool: asyncpg.Pool, key: str, data: ModelConfigUpdateRequest
) -> bool:
    sets = ["updated_at = now()"]
    params: list = [key]
    idx = 2

    if data.provider is not None:
        sets.append(f"provider = ${idx}")
        params.append(data.provider)
        idx += 1

    if data.model_id is not None:
        sets.append(f"model_id = ${idx}")
        params.append(data.model_id)
        idx += 1

    if data.display_name is not None:
        sets.append(f"display_name = ${idx}")
        params.append(data.display_name)
        idx += 1

    if data.extra_config is not None:
        sets.append(f"extra_config = ${idx}")
        params.append(json.dumps(data.extra_config))
        idx += 1

    query = f"UPDATE ai_model_config SET {', '.join(sets)} WHERE key = $1 AND is_active = true"
    result = await pool.execute(query, *params)
    return result == "UPDATE 1"


async def create_model_config(
    pool: asyncpg.Pool, key: str, data: ModelConfigUpdateRequest
) -> bool:
    try:
        await pool.execute(
            "INSERT INTO ai_model_config (key, provider, model_id, display_name, extra_config) "
            "VALUES ($1, $2, $3, $4, $5)",
            key,
            data.provider or "",
            data.model_id or "",
            data.display_name,
            json.dumps(data.extra_config) if data.extra_config else "{}",
        )
        return True
    except asyncpg.UniqueViolationError:
        return False


async def delete_prompt(pool: asyncpg.Pool, key: str) -> bool:
    result = await pool.execute(
        "UPDATE ai_prompts SET is_active = false, updated_at = now() WHERE key = $1 AND is_active = true",
        key,
    )
    return result == "UPDATE 1"


async def delete_model_config(pool: asyncpg.Pool, key: str) -> bool:
    result = await pool.execute(
        "UPDATE ai_model_config SET is_active = false, updated_at = now() WHERE key = $1 AND is_active = true",
        key,
    )
    return result == "UPDATE 1"
