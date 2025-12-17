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

router = APIRouter()

# Global Event Store instance for simplicity in this template
# In prod, inject via DI container
event_store_instance = InMemoryEventStore()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    item: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    repository = SqlAlchemyOrderRepository(db)
    handler = CreateOrderHandler(order_repository=repository, event_store=event_store_instance)
    
    command = CreateOrderCommand(
        customer_id=UUID(current_user["id"]), # Using Authenticated User ID
        total_amount=item.total_amount
    )
    
    order_id = await handler.handle(command)
    
    # Refresh to return
    # In CQRS, commands usually return only ID. Here we query back for convenience OR return just ID.
    # Let's query back.
    query_handler = GetOrderHandler(order_repository=repository)
    order = await query_handler.handle(GetOrderQuery(order_id))
    return order

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    repository = SqlAlchemyOrderRepository(db)
    handler = GetOrderHandler(order_repository=repository)
    
    # Pass current_user ID to strictly enforce RLAC at the infrastructure level
    query = GetOrderQuery(order_id=order_id, owner_id=UUID(current_user["id"]))
    order = await handler.handle(query) 

    if not order:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Order not found")
        
    return order
