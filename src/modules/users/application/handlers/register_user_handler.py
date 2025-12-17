from uuid import UUID
from src.modules.users.application.commands.register_user import RegisterUserCommand
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.modules.users.domain.aggregates.user import User
from src.modules.users.domain.value_objects import Email, PasswordHash
from src.core.security import PasswordService

class RegisterUserHandler:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(self, command: RegisterUserCommand) -> UUID:
        existing_user = await self.user_repository.get_by_email(command.email)
        if existing_user:
            raise ValueError("Email already registered")

        hashed_pwd = PasswordService.get_password_hash(command.password)
        
        user = User.create(
            email=Email(command.email),
            password_hash=PasswordHash(hashed_pwd),
            role=command.role
        )

        await self.user_repository.save(user)
        # In a real system, we'd also publish events here (UserRegistered) via EventBus
        return user.id.value if hasattr(user.id, "value") else user.id
