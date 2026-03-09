import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.middleware.admin_auth import create_admin_token, verify_admin_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


@router.post("/login", response_model=LoginResponse)
async def admin_login(body: LoginRequest):
    """Authenticate admin user and return a JWT token."""
    if not verify_admin_password(body.password):
        logger.warning("Failed admin login attempt for user: %s", body.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_admin_token()
    logger.info("Admin login successful for user: %s", body.username)
    return LoginResponse(token=token)
