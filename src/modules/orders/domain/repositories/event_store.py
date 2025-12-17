from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from src.modules.orders.domain.events.events import DomainEvent

class EventStore(ABC):
    @abstractmethod
    async def append(self, stream_id: UUID, events: List[DomainEvent]) -> None:
        pass

    @abstractmethod
    async def load(self, stream_id: UUID) -> List[DomainEvent]:
        pass
