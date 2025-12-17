from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from src.core.database import Base
import uuid

class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(PG_UUID(as_uuid=True), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="PENDING")
