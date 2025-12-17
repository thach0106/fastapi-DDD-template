from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from src.modules.orders.domain.aggregates.order import Order

class OrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, order_id: UUID, owner_id: Optional[UUID] = None) -> Optional[Order]:
        pass
