"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(session)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    data: UserCreate,
    service: AuthService = Depends(get_auth_service),
) -> UserRead:
    """Create a new user account."""
    return await service.register(data)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and obtain access token",
)
async def login(
    data: UserLogin,
    service: AuthService = Depends(get_auth_service),
) -> Token:
    """Authenticate and return a JWT access token."""
    return await service.login(data.email, data.password)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user",
)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    """Return the currently authenticated user."""
    return UserRead.model_validate(current_user)
