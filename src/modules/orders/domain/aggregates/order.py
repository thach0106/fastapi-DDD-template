from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import List

from src.modules.orders.domain.events.events import DomainEvent, OrderCreated

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

    def apply(self, event: DomainEvent) -> None:
        """Apply event to current state."""
        if isinstance(event, OrderCreated):
            self.id = event.order_id
            self.customer_id = event.customer_id
            self.total_amount = event.total_amount
            self.status = "PENDING"
        # Handle other events like OrderPaid, OrderShipped, etc.

    @classmethod
    def replay(cls, events: List[DomainEvent]) -> Order:
        """Reconstruct aggregate from event stream."""
        if not events:
            raise ValueError("Cannot replay from empty event stream")
            
        # Create empty instance (bypass init if needed, or use dummy)
        # Here we rely on the first event being 'OrderCreated' to populate fields
        # A cleaner way in Python is to have a base class that handles this, 
        # or separate 'State' object.
        # For this template:
        obj = cls.__new__(cls) # Bypass __init__
        obj._events = []
        
        for event in events:
            obj.apply(event)
            
        return obj

    def pull_events(self) -> List[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events
