from dataclasses import dataclass
from typing import NewType
from uuid import UUID
import re

UserId = NewType("UserId", UUID)

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.value):
            raise ValueError("Invalid email format")

    def __str__(self):
        return self.value

@dataclass(frozen=True)
class PasswordHash:
    value: str

    def __str__(self):
        return self.value
