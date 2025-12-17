from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.database import Base
from src.modules.orders.domain.repositories.event_store import EventStore
from src.modules.orders.domain.events.events import DomainEvent

# ... (Imports remain same)
from typing import Type, Dict

# Event Registry
class EventRegistry:
    _registry: Dict[str, Type[DomainEvent]] = {}

    @classmethod
    def register(cls, event_cls: Type[DomainEvent]):
        cls._registry[event_cls.__name__] = event_cls

    @classmethod
    def get(cls, name: str) -> Type[DomainEvent]:
        if name not in cls._registry:
            raise ValueError(f"Event type {name} not registered")
        return cls._registry[name]

# Register OrderCreated (Ideally done in module startup)
from src.modules.orders.domain.events.events import OrderCreated
EventRegistry.register(OrderCreated)

class PostgresEventStore(EventStore):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def append(self, stream_id: UUID, events: List[DomainEvent]) -> None:
        for event in events:
            payload = event.__dict__ if hasattr(event, "__dict__") else event.model_dump()
            cleaned_payload = self._clean_payload(payload)

            stored_event = StoredEventModel(
                event_id=event.event_id,
                stream_id=stream_id,
                event_type=type(event).__name__,
                payload=cleaned_payload,
                occurred_on=event.occurred_on
            )
            self.session.add(stored_event)
        
        await self.session.flush()

    async def load(self, stream_id: UUID) -> List[DomainEvent]:
        stmt = select(StoredEventModel).where(StoredEventModel.stream_id == stream_id).order_by(StoredEventModel.occurred_on)
        result = await self.session.execute(stmt)
        stored_events = result.scalars().all()
        
        domain_events = []
        for se in stored_events:
            event_cls = EventRegistry.get(se.event_type)
            # Reconstruct event (Assuming dataclass or pydantic that accepts kwargs)
            # We need to handle UUID/Date deserialization if using Pydantic it might happen auto, 
            # for Dataclasses we might need helper.
            # For this template: simple unpacking + naive fix
            payload = se.payload
            
            # Fix payload types (UUIDs stored as strings in JSON)
            # This logic depends on the event definition. 
            # Ideally use Pydantic for Events to handle this clean.
            # Hack for template:
            if "event_id" in payload: payload["event_id"] = UUID(str(payload["event_id"]))
            if "order_id" in payload: payload["order_id"] = UUID(str(payload["order_id"]))
            if "customer_id" in payload: payload["customer_id"] = UUID(str(payload["customer_id"]))
            # occurred_on is in payload? usually yes.
            if "occurred_on" in payload: payload["occurred_on"] = datetime.fromisoformat(payload["occurred_on"])
            
            event = event_cls(**payload)
            domain_events.append(event)
            
        return domain_events

    def _clean_payload(self, payload: dict) -> dict:
        new_payload = {}
        for k, v in payload.items():
            if isinstance(v, UUID):
                new_payload[k] = str(v)
            elif isinstance(v, datetime):
                new_payload[k] = v.isoformat()
            else:
                new_payload[k] = v
        return new_payload
