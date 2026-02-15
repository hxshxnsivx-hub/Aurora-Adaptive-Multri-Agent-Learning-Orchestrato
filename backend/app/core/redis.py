"""
Redis configuration and connection management.
"""

import redis.asyncio as redis
import json
import logging
from typing import Any, Optional, Union
from datetime import timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis connection pool
redis_pool: Optional[redis.ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


async def init_redis() -> None:
    """Initialize Redis connection pool."""
    global redis_pool, redis_client
    
    try:
        redis_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20
        )
        redis_client = redis.Redis(connection_pool=redis_pool)
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        raise


async def close_redis() -> None:
    """Close Redis connections."""
    global redis_pool, redis_client
    
    try:
        if redis_client:
            await redis_client.close()
        if redis_pool:
            await redis_pool.disconnect()
        logger.info("Redis connections closed")
    except Exception as e:
        logger.error(f"Error closing Redis connections: {e}")


async def get_redis() -> redis.Redis:
    """Get Redis client instance."""
    if not redis_client:
        await init_redis()
    return redis_client


class RedisCache:
    """Redis cache utility class."""
    
    def __init__(self):
        self.client = None
    
    async def _get_client(self) -> redis.Redis:
        """Get Redis client, initializing if necessary."""
        if not self.client:
            self.client = await get_redis()
        return self.client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            client = await self._get_client()
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        try:
            client = await self._get_client()
            serialized_value = json.dumps(value, default=str)
            
            if ttl is None:
                ttl = settings.REDIS_CACHE_TTL
            
            await client.set(key, serialized_value, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            client = await self._get_client()
            result = await client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            client = await self._get_client()
            result = await client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache."""
        try:
            client = await self._get_client()
            result = await client.incrby(key, amount)
            return result
        except Exception as e:
            logger.error(f"Redis increment error for key {key}: {e}")
            return None
    
    async def expire(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """Set expiration for existing key."""
        try:
            client = await self._get_client()
            result = await client.expire(key, ttl)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis expire error for key {key}: {e}")
            return False


# Global cache instance
cache = RedisCache()