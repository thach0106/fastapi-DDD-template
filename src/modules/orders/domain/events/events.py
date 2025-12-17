from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID
    occurred_on: datetime

@dataclass(frozen=True)
class OrderCreated(DomainEvent):
    order_id: UUID
    customer_id: UUID
    total_amount: float
