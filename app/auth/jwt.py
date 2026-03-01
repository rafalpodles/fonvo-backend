import logging

import httpx
import jwt

from app.config import settings

logger = logging.getLogger(__name__)

_jwks_cache: dict | None = None


async def get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
        logger.info("Fetching JWKS from %s", url)
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


def invalidate_jwks_cache() -> None:
    global _jwks_cache
    _jwks_cache = None


async def verify_supabase_jwt(token: str) -> dict:
    jwks = await get_jwks()
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
        raise ValueError("JWT header missing kid")

    matching_key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if matching_key is None:
        # Key might have rotated — refetch once
        invalidate_jwks_cache()
        jwks = await get_jwks()
        matching_key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if matching_key is None:
            raise ValueError(f"No matching JWK for kid={kid}")

    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(matching_key)
    payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )
    return payload
