from __future__ import annotations
import redis.asyncio as redis
import asyncio
from Elara.config.config import RedisConfig
from Elara.console.logging import logger

class RedisEngine:
    def __init__(self):
        self.url = RedisConfig.URL
        self.password = RedisConfig.PASSWORD
        self._redis = None
        self._fallback_cache = {} # Fallback if Redis is unavailable

    async def connect(self):
        try:
            if self.password:
                self._redis = await redis.from_url(self.url, password=self.password, decode_responses=True)
            else:
                self._redis = await redis.from_url(self.url, decode_responses=True)
            
            # Test connection
            await self._redis.ping()
            logger.success("Connected to Redis (Replish) successfully.")
        except Exception as e:
            logger.warning(f"Redis connection failed (falling back to local memory): {e}")
            self._redis = None

    async def set(self, key: str, value: str, expire: int = None):
        if self._redis:
            await self._redis.set(key, value, ex=expire)
        else:
            self._fallback_cache[key] = value
            if expire:
                async def _expire():
                    await asyncio.sleep(expire)
                    if key in self._fallback_cache and self._fallback_cache[key] == value:
                        del self._fallback_cache[key]
                asyncio.create_task(_expire())

    async def get(self, key: str):
        if self._redis:
            return await self._redis.get(key)
        return self._fallback_cache.get(key)

    async def delete(self, key: str):
        if self._redis:
            await self._redis.delete(key)
        else:
            self._fallback_cache.pop(key, None)

    async def close(self):
        if self._redis:
            await self._redis.close()
        self._fallback_cache.clear()

# Singleton instance
redis_client = RedisEngine()
