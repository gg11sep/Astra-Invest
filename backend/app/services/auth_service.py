"""Authentication service."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.schemas.auth import Token, UserCreate, UserRead
from app.services.user_repository import UserRepository


class AuthService:
    """Handles registration and login."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def register(self, data: UserCreate) -> UserRead:
        existing = await self._repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        hashed = hash_password(data.password)
        user = await self._repo.create(data, hashed)
        return UserRead.model_validate(user)

    async def login(self, email: str, password: str) -> Token:
        user = await self._repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
        token = create_access_token(subject=str(user.id))
        return Token(access_token=token)
