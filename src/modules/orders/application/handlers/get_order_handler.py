from typing import Optional
from src.modules.orders.domain.aggregates.order import Order
from src.modules.orders.domain.repositories.order_repository import OrderRepository
from src.modules.orders.application.queries.get_order import GetOrderQuery

class GetOrderHandler:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def handle(self, query: GetOrderQuery) -> Optional[Order]:
        return await self.order_repository.get_by_id(query.order_id, owner_id=query.owner_id)
