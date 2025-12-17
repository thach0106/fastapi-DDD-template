from dataclasses import dataclass
from uuid import UUID

@dataclass
class CreateOrderCommand:
    customer_id: UUID
    total_amount: float
