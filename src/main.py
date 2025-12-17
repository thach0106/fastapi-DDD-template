from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.config import settings
from src.core.database import engine, Base
from src.modules.orders.presentation.router import router as orders_router
from src.modules.auth.presentation.router import router as auth_router
from src.core.logging import setup_logging
from src.infrastructure.cache import redis_cache

# Setup Logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_cache.initialize()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await redis_cache.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(orders_router, prefix=f"{settings.API_V1_STR}/orders", tags=["orders"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
