import logging

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.auth.dependencies import get_user_or_guest
from app.db.connection import get_pool
from app.db.queries import scenarios as queries
from app.middleware.admin_auth import require_admin
from app.models.scenarios import (
    AdminScenarioResponse,
    ScenarioCreateRequest,
    ScenarioListResponse,
    ScenarioUpdateRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["scenarios"])


# ── Public endpoint ──────────────────────────────────────────


@router.get("/scenarios", response_model=ScenarioListResponse)
async def list_scenarios(
    request: Request,
    level: str = "b1",
    locale: str = "en",
    pool: asyncpg.Pool = Depends(get_pool),
    _caller=Depends(get_user_or_guest),
):
    """Get scenarios for a user's level with locale-resolved strings."""
    hash_val = await queries.get_scenarios_hash(pool)

    if_none_match = request.headers.get("if-none-match")
    if if_none_match and if_none_match.strip('"') == hash_val:
        return Response(status_code=304)

    scenarios = await queries.get_scenarios_for_level(pool, level, locale)
    response = ScenarioListResponse(scenarios=scenarios, hash=hash_val)
    return Response(
        content=response.model_dump_json(),
        media_type="application/json",
        headers={"ETag": f'"{hash_val}"'},
    )


# ── Admin endpoints ──────────────────────────────────────────


@router.get("/admin/scenarios", response_model=list[AdminScenarioResponse])
async def admin_list_scenarios(
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """List all scenarios including inactive (admin)."""
    return await queries.get_all_scenarios_admin(pool)


@router.get("/admin/scenarios/{scenario_id}", response_model=AdminScenarioResponse)
async def admin_get_scenario(
    scenario_id: str,
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """Get single scenario with full JSONB (admin)."""
    scenario = await queries.get_scenario_admin(pool, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.post("/admin/scenarios", status_code=201)
async def admin_create_scenario(
    data: ScenarioCreateRequest,
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """Create a new scenario (admin)."""
    success = await queries.create_scenario(pool, data.model_dump())
    if not success:
        raise HTTPException(
            status_code=409, detail="Scenario with this ID already exists"
        )
    return {"status": "created", "id": data.id}


@router.put("/admin/scenarios/{scenario_id}")
async def admin_update_scenario(
    scenario_id: str,
    data: ScenarioUpdateRequest,
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """Update a scenario (admin)."""
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    success = await queries.update_scenario(pool, scenario_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"status": "updated"}


@router.delete("/admin/scenarios/{scenario_id}")
async def admin_delete_scenario(
    scenario_id: str,
    pool: asyncpg.Pool = Depends(get_pool),
    _admin: str = Depends(require_admin),
):
    """Soft-delete a scenario (admin)."""
    success = await queries.delete_scenario(pool, scenario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"status": "deleted"}
