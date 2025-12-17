from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.deps import get_db
from src.modules.users.infrastructure.persistence.repositories import SqlAlchemyUserRepository
from src.modules.auth.application.commands.login import LoginCommand
from src.modules.auth.application.handlers.login_handler import LoginHandler

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    repo = SqlAlchemyUserRepository(db)
    handler = LoginHandler(repo)
    command = LoginCommand(email=request.email, password=request.password)
    
    try:
        token_data = await handler.handle(command)
        return token_data
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
