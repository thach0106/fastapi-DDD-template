import pytest
from httpx import AsyncClient
from src.modules.users.domain.aggregates.user import User
from decimal import Decimal

# Since we haven't implemented a Users API router yet (only used by Auth internally),
# we will test the Auth login flow which exercises the Users module infrastructure.

@pytest.mark.asyncio
async def test_login_flow(client: AsyncClient, db):
    # 1. Setup - Create User directly in DB (using Repository or SQL)
    # We need to manually insert a user because we don't have a registration endpoint yet (it's in the plans but not implemented in code yet),
    # or we can use the repository if we can access it.
    
    # For integration test, it's better to use the Repository.
    from src.modules.users.infrastructure.persistence.repositories import SqlAlchemyUserRepository
    from src.core.security import get_password_hash
    
    repo = SqlAlchemyUserRepository(db)
    email = "test@example.com"
    password = "password123"
    
    user = User.create(email=email, password_hash=get_password_hash(password))
    await repo.save(user)
    
    # 2. Execute - Logical Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    
    # 3. Verify
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrong"}
    )
    assert response.status_code == 401
