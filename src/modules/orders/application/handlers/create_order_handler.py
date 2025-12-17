from uuid import UUID
from src.modules.orders.domain.aggregates.order import Order
from src.modules.orders.domain.repositories.order_repository import OrderRepository
from src.modules.orders.domain.repositories.event_store import EventStore
from src.modules.orders.application.commands.create_order import CreateOrderCommand

from src.modules.orders.application.tasks import process_order_created

class CreateOrderHandler:
    def __init__(self, order_repository: OrderRepository, event_store: EventStore):
        self.order_repository = order_repository
        self.event_store = event_store

    async def handle(self, command: CreateOrderCommand) -> UUID:
        order = Order.create(
            customer_id=command.customer_id,
            total_amount=command.total_amount
        )
        
        await self.order_repository.save(order)
        
        events = order.pull_events()
        await self.event_store.append(order.id, events)
        
        # Publish events to integration bus / celery
        # In a real app, this should be an Outbox Pattern pattern or listening to EventStoreDB
        # For this template, we dispatch directly for simplicity
        for event in events:
            if type(event).__name__ == "OrderCreated":
                # Convert to dict manually or use library
                payload = {
                    "order_id": str(event.order_id),
                    "customer_id": str(event.customer_id),
                    "total_amount": event.total_amount
                }
                process_order_created.delay(payload)
        
        return order.id
