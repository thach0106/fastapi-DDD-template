from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Optional

@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    is_active: bool = True
    role: str = "user"

    @staticmethod
    def create(email: str, password_hash: str, role: str = "user") -> 'User':
        return User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            is_active=True,
            role=role
        )
