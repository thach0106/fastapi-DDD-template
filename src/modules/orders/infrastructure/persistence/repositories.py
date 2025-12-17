from typing import Optional
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.orders.domain.aggregates.order import Order
from src.modules.orders.domain.repositories.order_repository import OrderRepository
from src.modules.orders.infrastructure.persistence.models import OrderModel

from src.core.repository import BaseRepository

class SqlAlchemyOrderRepository(BaseRepository[OrderModel], OrderRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(OrderModel, session)


    async def save(self, order: Order) -> None:
        # Check if exists
        result = await self.session.execute(select(OrderModel).filter_by(id=order.id))
        db_order = result.scalars().first()
        
        if db_order:
            db_order.status = order.status
            db_order.total_amount = order.total_amount
            # Map other fields...
        else:
            db_order = OrderModel(
                id=order.id,
                customer_id=order.customer_id,
                total_amount=order.total_amount,
                status=order.status
            )
            self.session.add(db_order)
        
        await self.session.flush()

    async def get_by_id(self, order_id: UUID, owner_id: Optional[UUID] = None) -> Optional[Order]:
        model = await super().get_by_id(order_id, owner_id=owner_id)
        if not model:
            return None
        return Order(
            id=model.id,
            customer_id=model.customer_id,
            total_amount=model.total_amount,
            status=model.status
        )
