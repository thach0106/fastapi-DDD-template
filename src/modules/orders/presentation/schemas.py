from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class OrderCreate(BaseModel):
    total_amount: float

class OrderResponse(BaseModel):
    id: UUID
    customer_id: UUID
    total_amount: float
    status: str
    
    model_config = ConfigDict(from_attributes=True)
