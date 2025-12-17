from typing import Callable, Type
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.bus import CommandBus, QueryBus, logging_middleware
from src.modules.orders.domain.repositories.order_repository import OrderRepository
from src.modules.orders.domain.repositories.event_store import EventStore

# Commands
from src.modules.orders.application.commands.create_order import CreateOrderCommand
from src.modules.orders.application.handlers.create_order_handler import CreateOrderHandler
# Queries
from src.modules.orders.application.queries.get_order import GetOrderQuery
from src.modules.orders.application.handlers.get_order_handler import GetOrderHandler

# Global Buses
command_bus = CommandBus()
query_bus = QueryBus()

# Middlewares
command_bus.add_middleware(logging_middleware)
query_bus.add_middleware(logging_middleware)

def configure_orders_module(
    order_repository: OrderRepository,
    event_store: EventStore
):
    """
    Dependency Injection wiring.
    In a real app, you might use a DI container library.
    Here we manually register handlers with injected dependencies.
    """
    
    # Handlers instantiation
    create_handler = CreateOrderHandler(order_repository, event_store)
    get_handler = GetOrderHandler(order_repository)
    
    # Registration
    command_bus.register(CreateOrderCommand, create_handler.handle)
    query_bus.register(GetOrderQuery, get_handler.handle)
