import hashlib
import json
import logging

import asyncpg

from app.models.scenarios import AdminScenarioResponse, ScenarioResponse

logger = logging.getLogger(__name__)

LEVEL_ORDER = ["a1", "a2", "b1", "b2", "c1", "c2"]


def _resolve_locale(jsonb, locale: str):
    """Extract locale from JSONB, fallback to 'en'."""
    if isinstance(jsonb, str):
        jsonb = json.loads(jsonb)
    return jsonb.get(locale, jsonb.get("en", ""))


def _parse_public_row(row: asyncpg.Record, locale: str) -> ScenarioResponse:
    name_json = row["name"] if isinstance(row["name"], dict) else json.loads(row["name"])
    goals_json = (
        row["goals"] if isinstance(row["goals"], dict) else json.loads(row["goals"])
    )
    return ScenarioResponse(
        id=row["id"],
        icon=row["icon"],
        category=row["category"],
        minimum_level=row["minimum_level"],
        maximum_level=row["maximum_level"],
        system_prompt_addition=row["system_prompt_addition"],
        name=_resolve_locale(name_json, locale),
        goals=_resolve_locale(goals_json, locale),
        sort_order=row["sort_order"],
    )


def _parse_admin_row(row: asyncpg.Record) -> AdminScenarioResponse:
    return AdminScenarioResponse(
        id=row["id"],
        icon=row["icon"],
        category=row["category"],
        minimum_level=row["minimum_level"],
        maximum_level=row["maximum_level"],
        system_prompt_addition=row["system_prompt_addition"],
        sort_order=row["sort_order"],
        is_active=row["is_active"],
        name=row["name"] if isinstance(row["name"], dict) else json.loads(row["name"]),
        goals=(
            row["goals"]
            if isinstance(row["goals"], dict)
            else json.loads(row["goals"])
        ),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# --- Public queries ---


async def get_scenarios_for_level(
    pool: asyncpg.Pool, level: str, locale: str
) -> list[ScenarioResponse]:
    """Get active scenarios appropriate for user's level, with resolved locale."""
    if level not in LEVEL_ORDER:
        level = "b1"

    rows = await pool.fetch(
        "SELECT * FROM scenarios WHERE is_active = true ORDER BY sort_order, id"
    )

    # Filter in Python since TEXT comparison doesn't respect CEFR ordering
    level_idx = LEVEL_ORDER.index(level)
    filtered = []
    for r in rows:
        min_idx = LEVEL_ORDER.index(r["minimum_level"]) if r["minimum_level"] in LEVEL_ORDER else 0
        max_idx = LEVEL_ORDER.index(r["maximum_level"]) if r["maximum_level"] in LEVEL_ORDER else 5
        if min_idx <= level_idx <= max_idx:
            filtered.append(r)

    return [_parse_public_row(r, locale) for r in filtered]


async def get_scenarios_hash(pool: asyncpg.Pool) -> str:
    """Hash for ETag based on active scenario timestamps."""
    row = await pool.fetchrow(
        "SELECT md5(string_agg(updated_at::text, ',' ORDER BY id)) AS hash "
        "FROM scenarios WHERE is_active = true"
    )
    raw = row["hash"] if row and row["hash"] else ""
    return hashlib.md5(raw.encode()).hexdigest()[:12]


# --- Admin queries ---


async def get_all_scenarios_admin(
    pool: asyncpg.Pool,
) -> list[AdminScenarioResponse]:
    """Get all scenarios (including inactive) for admin."""
    rows = await pool.fetch("SELECT * FROM scenarios ORDER BY sort_order, id")
    return [_parse_admin_row(r) for r in rows]


async def get_scenario_admin(
    pool: asyncpg.Pool, scenario_id: str
) -> AdminScenarioResponse | None:
    row = await pool.fetchrow("SELECT * FROM scenarios WHERE id = $1", scenario_id)
    return _parse_admin_row(row) if row else None


async def create_scenario(pool: asyncpg.Pool, data: dict) -> bool:
    try:
        await pool.execute(
            """
            INSERT INTO scenarios (id, icon, category, minimum_level, maximum_level,
                                   system_prompt_addition, sort_order, name, goals)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb)
            """,
            data["id"],
            data["icon"],
            data["category"],
            data["minimum_level"],
            data["maximum_level"],
            data["system_prompt_addition"],
            data["sort_order"],
            json.dumps(data["name"]),
            json.dumps(data["goals"]),
        )
        return True
    except asyncpg.UniqueViolationError:
        return False


async def update_scenario(pool: asyncpg.Pool, scenario_id: str, data: dict) -> bool:
    sets = []
    values = []
    idx = 1
    for key, val in data.items():
        if val is not None:
            if key in ("name", "goals"):
                sets.append(f"{key} = ${idx}::jsonb")
                values.append(json.dumps(val))
            else:
                sets.append(f"{key} = ${idx}")
                values.append(val)
            idx += 1
    if not sets:
        return False
    sets.append("updated_at = now()")
    values.append(scenario_id)
    query = f"UPDATE scenarios SET {', '.join(sets)} WHERE id = ${idx}"
    result = await pool.execute(query, *values)
    return result == "UPDATE 1"


async def delete_scenario(pool: asyncpg.Pool, scenario_id: str) -> bool:
    result = await pool.execute(
        "UPDATE scenarios SET is_active = false, updated_at = now() WHERE id = $1",
        scenario_id,
    )
    return result == "UPDATE 1"
