from dataclasses import dataclass
from uuid import UUID

@dataclass
class GetOrderQuery:
    order_id: UUID
    owner_id: UUID | None = None
