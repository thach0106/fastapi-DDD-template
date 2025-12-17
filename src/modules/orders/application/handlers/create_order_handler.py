from uuid import UUID
from src.modules.orders.domain.aggregates.order import Order
from src.modules.orders.domain.repositories.order_repository import OrderRepository
from src.modules.orders.domain.repositories.event_store import EventStore
from src.modules.orders.application.commands.create_order import CreateOrderCommand

class CreateOrderHandler:
    def __init__(self, order_repository: OrderRepository, event_store: EventStore):
        self.order_repository = order_repository
        self.event_store = event_store

    async def handle(self, command: CreateOrderCommand) -> UUID:
        order = Order.create(
            customer_id=command.customer_id,
            total_amount=command.total_amount
        )
        
        # Persist state (CQRS - implementation detail: we might just save events, 
        # or save state + events. Here we do both for simplicity/robustness).
        await self.order_repository.save(order)
        
        # Persist events for Event Sourcing
        events = order.pull_events()
        await self.event_store.append(order.id, events)
        
        return order.id
