from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime

from src.modules.users.domain.value_objects import UserId, Email, PasswordHash
from src.modules.users.domain.events import UserRegistered

@dataclass
class User:
    id: UserId
    email: Email
    password_hash: PasswordHash
    is_active: bool = True
    role: str = "user"
    _events: List[UserRegistered] = field(default_factory=list, init=False, repr=False)

    @staticmethod
    def create(email: Email, password_hash: PasswordHash, role: str = "user") -> 'User':
        user_id = UserId(uuid4())
        user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            is_active=True,
            role=role
        )
        user._record_event(UserRegistered(
            event_id=uuid4(),
            occurred_on=datetime.utcnow(),
            user_id=user_id,
            email=str(email),
            role=role
        ))
        return user

    def _record_event(self, event: UserRegistered) -> None:
        self._events.append(event)
    
    def pull_events(self) -> List[UserRegistered]:
        events = self._events.copy()
        self._events.clear()
        return events
