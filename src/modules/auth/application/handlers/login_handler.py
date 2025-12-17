from src.modules.auth.application.commands.login import LoginCommand
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.core.security import verify_password, create_access_token, create_refresh_token
from typing import Dict

class LoginHandler:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(self, command: LoginCommand) -> Dict[str, str]:
        user = await self.user_repository.get_by_email(command.email)
        if not user or not verify_password(command.password, user.password_hash):
            raise ValueError("Invalid credentials") # In real app, use specific Exception

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
