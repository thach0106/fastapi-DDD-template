from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import List

from .events.events import DomainEvent, OrderCreated

@dataclass
class Order:
    id: UUID
    customer_id: UUID
    total_amount: float
    status: str
    _events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)

    @staticmethod
    def create(customer_id: UUID, total_amount: float) -> Order:
        order_id = uuid4()
        order = Order(
            id=order_id,
            customer_id=customer_id,
            total_amount=total_amount,
            status="PENDING"
        )
        order._record_event(OrderCreated(
            event_id=uuid4(),
            occurred_on=datetime.utcnow(),
            order_id=order_id,
            customer_id=customer_id,
            total_amount=total_amount
        ))
        return order

    def _record_event(self, event: DomainEvent) -> None:
        self._events.append(event)
    
    def pull_events(self) -> List[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events
