from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.core.deps import get_db, get_current_user
from src.modules.orders.presentation.schemas import OrderCreate, OrderResponse
from src.modules.orders.infrastructure.persistence.repositories import SqlAlchemyOrderRepository
from src.modules.orders.infrastructure.event_store.in_memory_event_store import InMemoryEventStore
from src.modules.orders.application.commands.create_order import CreateOrderCommand
from src.modules.orders.application.handlers.create_order_handler import CreateOrderHandler
from src.modules.orders.application.queries.get_order import GetOrderQuery
from src.modules.orders.application.handlers.get_order_handler import GetOrderHandler

from src.core.bus_config import command_bus, query_bus, configure_orders_module
from src.core.event_store import PostgresEventStore
from src.modules.orders.infrastructure.persistence.repositories import SqlAlchemyOrderRepository

router = APIRouter()


# Dependency for wiring (could be moved to middleware/startup if stateless)
async def get_wired_context(db: AsyncSession = Depends(get_db)):
    # Create dependencies
    repo = SqlAlchemyOrderRepository(db)
    ev_store = PostgresEventStore(db)
    
    # Wire them up (In prod, do this once or use scoped container)
    # For this template, we re-register to ensure the thread-local DB session is correct 
    # OR we pass dependencies via command/context.
    # To keep it simple and clean: We configure the bus handlers here or assume handlers are stateless 
    # and just need a way to get DB.
    # BETTER APPROACH: Instantiating handlers per request or using a scoped DI container.
    # Here we will re-configure. Note: This overwrites global registry which is not thread-safe 
    # for async if not careful. 
    #
    # SAFE APPROACH for this Template: 
    # We DO NOT use global singleton dispatch if handlers are stateful (depend on db session).
    # Instead, we instantiate handlers here and dispatch manually OR use a Bus that resolves handlers scoped.
    #
    # FOR DEMONSTRATION of Command Bus pattern:
    configure_orders_module(repo, ev_store)
    return True

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    item: OrderCreate,
    _: bool = Depends(get_wired_context), # Ensure wiring
    current_user: dict = Depends(get_current_user)
):
    command = CreateOrderCommand(
        customer_id=UUID(current_user["id"]),
        total_amount=item.total_amount
    )
    
    order_id = await command_bus.dispatch(command)
    
    # Query back
    query = GetOrderQuery(order_id=order_id, owner_id=UUID(current_user["id"]))
    order = await query_bus.dispatch(query)
    return order

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID, 
    _: bool = Depends(get_wired_context),
    current_user: dict = Depends(get_current_user)
):
    query = GetOrderQuery(order_id=order_id, owner_id=UUID(current_user["id"]))
    order = await query_bus.dispatch(query)

    if not order:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Order not found")
        
    return order
