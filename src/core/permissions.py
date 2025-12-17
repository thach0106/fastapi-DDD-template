from typing import List, Callable
from fastapi import HTTPException, Depends, status
from src.core.deps import get_current_user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: dict = Depends(get_current_user)):
        if user["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Operation not permitted"
            )

# Usage example: Depends(allow_admin)
allow_admin = RoleChecker(["admin"])
allow_user = RoleChecker(["user", "admin"])
