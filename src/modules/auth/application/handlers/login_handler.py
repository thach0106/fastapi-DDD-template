from src.modules.auth.application.commands.login import LoginCommand
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.core.security import PasswordService
from src.modules.auth.application.services.jwt_service import JWTService
from typing import Dict

class LoginHandler:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(self, command: LoginCommand) -> Dict[str, str]:
        user = await self.user_repository.get_by_email(command.email)
        if not user or not PasswordService.verify_password(command.password, str(user.password_hash)):
            raise ValueError("Invalid credentials")

        # user.id might be UserId(UUID) wrapper
        user_id = str(user.id)
        
        access_token = JWTService.create_access_token(subject=user_id, claims={"role": user.role})
        refresh_token = JWTService.create_refresh_token(subject=user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
