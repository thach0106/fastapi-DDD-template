from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class UserDomainEvent:
    event_id: UUID
    occurred_on: datetime

@dataclass(frozen=True)
class UserRegistered(UserDomainEvent):
    user_id: UUID
    email: str
    role: str
