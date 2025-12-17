import redis.asyncio as redis
from typing import Optional, Any
import json
from src.core.config import settings

class RedisCache:
    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def initialize(self):
        self._redis = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    async def close(self):
        if self._redis:
            await self._redis.close()

    async def get(self, key: str) -> Optional[Any]:
        if not self._redis: raise RuntimeError("Redis not initialized")
        value = await self._redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, expire: int = 60):
        if not self._redis: raise RuntimeError("Redis not initialized")
        await self._redis.set(key, json.dumps(value), ex=expire)

redis_cache = RedisCache()
