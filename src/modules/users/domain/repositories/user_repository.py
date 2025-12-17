from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from src.modules.users.domain.aggregates.user import User

class UserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> None:
        pass
