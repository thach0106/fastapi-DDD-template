from typing import List, Dict
from uuid import UUID
from src.modules.orders.domain.repositories.event_store import EventStore
from src.modules.orders.domain.events.events import DomainEvent

class InMemoryEventStore(EventStore):
    def __init__(self):
        self._store: Dict[UUID, List[DomainEvent]] = {}

    async def append(self, stream_id: UUID, events: List[DomainEvent]) -> None:
        if stream_id not in self._store:
            self._store[stream_id] = []
        self._store[stream_id].extend(events)

    async def load(self, stream_id: UUID) -> List[DomainEvent]:
        return self._store.get(stream_id, [])
