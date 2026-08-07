"""User repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import UserCreate


class UserRepository:
    """Data access for User."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: UserCreate, hashed_password: str) -> User:
        user = User(
            email=data.email.lower().strip(),
            hashed_password=hashed_password,
            full_name=data.full_name,
        )
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()
