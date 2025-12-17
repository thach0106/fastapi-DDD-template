from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Type, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseRepository(Generic[ModelType], ABC):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(
        self, 
        id: UUID, 
        owner_id: Optional[UUID] = None, 
        tenant_id: Optional[UUID] = None
    ) -> Optional[ModelType]:
        query = select(self.model).where(getattr(self.model, "id") == id)
        
        # RLAC
        if owner_id and hasattr(self.model, "customer_id"):
             # Assuming 'customer_id' is the owner field, or make it configurable
            query = query.where(getattr(self.model, "customer_id") == owner_id)
            
        # Multi-tenancy
        if tenant_id and hasattr(self.model, "tenant_id"):
            query = query.where(getattr(self.model, "tenant_id") == tenant_id)

        result = await self.session.execute(query)
        return result.scalars().first()

    # Generic definition provided, but concrete repos usually implement domain-specific methods
    # that map Model -> Entity
