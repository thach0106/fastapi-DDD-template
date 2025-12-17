from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.modules.users.domain.aggregates.user import User
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.modules.users.infrastructure.persistence.models import UserModel

class SqlAlchemyUserRepository(BaseRepository[UserModel], UserRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(UserModel, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        # Using BaseRepository logic if compatible, but mapping needs to happen
        model = await super().get_by_id(user_id)
        return self._to_domain(model) if model else None

    async def save(self, user: User) -> None:
        # Check update vs insert logic
        existing = await super().get_by_id(user.id)
        if existing:
            existing.email = str(user.email)
            existing.password_hash = str(user.password_hash)
            existing.is_active = user.is_active
            existing.role = user.role
        else:
            new_model = UserModel(
                id=user.id,
                email=str(user.email),
                password_hash=str(user.password_hash),
                is_active=user.is_active,
                role=user.role
            )
            self.session.add(new_model)
        await self.session.flush()

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            email=Email(model.email),
            password_hash=PasswordHash(model.password_hash),
            is_active=model.is_active,
            role=model.role
        )
