from typing import Any
from redis.asyncio import Redis, RedisError

from src.core.logger import logger
from src.core.exceptions import CacheError, AppError


class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str):
        try:
            value = await self.redis.get(key)
            if value is None:
                raise CacheError()
            return value
        except RedisError as e:
            logger.error(f"Error getting key {key}: {e}")
            raise AppError(f"Error getting key for {key}")

    async def set(self, key: str, value: Any, ttl: int = 3600):
        try:
            await self.redis.set(key, value, ex=ttl)
        except RedisError as e:
            logger.error(f"Error setting key {key}: {e}")
            raise AppError(f"Error set key {key}")

    async def delete(self, key: str):
        try:
            delete_count = await self.redis.delete(key)
            if delete_count == 0:
                raise CacheError()
        except RedisError as e:
            logger.error(f"Error deleting key {key}: {e}")
            raise AppError(f"Error delete key {key}")

    async def delete_pattern(self, pattern: str):
        try:
            keys = await self.redis.keys(pattern)
            if not keys:
                raise CacheError()
            await self.redis.delete(*keys)
        except RedisError as e:
            logger.error(f"Error deleting keys with pattern {pattern}: {e}")
            raise AppError(f"Error delete keys with pattern {pattern}")
