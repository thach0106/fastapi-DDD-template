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

# 1. SQLAlchemy Model for Events
class StoredEventModel(Base):
    __tablename__ = "domain_events"

    event_id = Column(PG_UUID(as_uuid=True), primary_key=True)
    stream_id = Column(PG_UUID(as_uuid=True), index=True, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)
    occurred_on = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(Integer, nullable=True) # Optimistic locking support

# 2. Postgres Implementation
class PostgresEventStore(EventStore):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def append(self, stream_id: UUID, events: List[DomainEvent]) -> None:
        for event in events:
            # Basic serialization - In prod use a proper serializer (like marshmallow or pydantic)
            # Here we assume events are dataclasses or Pydantic models
            payload = event.__dict__ if hasattr(event, "__dict__") else event.model_dump()
            
            # Handle UUIDs and Dates in payload for JSON
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
        # Loading requires mapping back to Domain Class. 
        # This implementation requires a registry of event types.
        # For this template, we will return raw dicts or handle mapping later.
        # Ideally: EventMapper.to_domain(model)
        raise NotImplementedError("Load requires Event Registry mapping")

    def _clean_payload(self, payload: dict) -> dict:
        # Helper to make dict JSON serializable
        new_payload = {}
        for k, v in payload.items():
            if isinstance(v, UUID):
                new_payload[k] = str(v)
            elif isinstance(v, datetime):
                new_payload[k] = v.isoformat()
            else:
                new_payload[k] = v
        return new_payload
