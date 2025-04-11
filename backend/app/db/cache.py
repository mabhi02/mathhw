"""
Redis cache provider for backend services.
Provides an async Redis client for caching operations.
"""
from typing import Optional, Any, TypeVar, Generic
import redis.asyncio as redis_async
import redis.exceptions
from functools import lru_cache
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.app.config import get_settings

logger = logging.getLogger(__name__)
T = TypeVar('T')

@lru_cache()
def get_redis() -> redis_async.Redis:
    """
    Returns an async Redis client instance with connection pooling.
    
    Returns:
        redis_async.Redis: A configured async Redis client instance
    """
    settings = get_settings()
    redis_config = settings.get_redis_config()
    
    return redis_async.Redis(
        host=redis_config.get("host", "redis"),
        port=redis_config.get("port", 6379),
        db=redis_config.get("db", 0),
        password=redis_config.get("password"),
        decode_responses=True
    )

def get_cache_key(prefix: str, *args) -> str:
    """
    Generate a standardized cache key.
    
    Args:
        prefix: The prefix for the cache key
        *args: Additional components to include in the key
        
    Returns:
        str: A formatted cache key
    """
    components = [str(arg) for arg in args if arg is not None]
    return f"{prefix}:{':'.join(components)}"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def cache_get(key: str) -> Optional[str]:
    """
    Get a value from the cache with retry logic.
    
    Args:
        key: Cache key
        
    Returns:
        Optional[str]: Cached value or None if not in cache
    """
    try:
        redis_client = get_redis()
        return await redis_client.get(key)
    except redis.exceptions.RedisError as e:
        logger.error(f"Redis error in cache_get: {str(e)}")
        raise

async def cache_get_json(key: str, default: Optional[T] = None) -> Optional[T]:
    """
    Get and deserialize a JSON value from cache.
    
    Args:
        key: Cache key
        default: Default value to return if key doesn't exist
        
    Returns:
        Optional[T]: Deserialized JSON object or default
    """
    value = await cache_get(key)
    if value is None:
        return default
    
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        logger.warning(f"Failed to decode JSON from cache key: {key}")
        return default

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def cache_set(key: str, value: str, expire: int = 3600) -> bool:
    """
    Set a value in the cache with retry logic.
    
    Args:
        key: Cache key
        value: Value to cache
        expire: Expiration time in seconds (default: 1 hour)
        
    Returns:
        bool: True if successful
    """
    try:
        redis_client = get_redis()
        return await redis_client.set(key, value, ex=expire)
    except redis.exceptions.RedisError as e:
        logger.error(f"Redis error in cache_set: {str(e)}")
        raise

async def cache_set_json(key: str, value: Any, expire: int = 3600) -> bool:
    """
    Serialize and set a JSON value in cache.
    
    Args:
        key: Cache key
        value: Value to serialize and cache
        expire: Expiration time in seconds (default: 1 hour)
        
    Returns:
        bool: True if successful
    """
    try:
        json_value = json.dumps(value)
        return await cache_set(key, json_value, expire)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to encode value to JSON for key {key}: {str(e)}")
        return False

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def cache_delete(key: str) -> int:
    """
    Delete a value from the cache with retry logic.
    
    Args:
        key: Cache key
        
    Returns:
        int: Number of keys deleted
    """
    try:
        redis_client = get_redis()
        return await redis_client.delete(key)
    except redis.exceptions.RedisError as e:
        logger.error(f"Redis error in cache_delete: {str(e)}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def cache_exists(key: str) -> bool:
    """
    Check if a key exists in the cache with retry logic.
    
    Args:
        key: Cache key
        
    Returns:
        bool: True if key exists
    """
    try:
        redis_client = get_redis()
        return await redis_client.exists(key) > 0
    except redis.exceptions.RedisError as e:
        logger.error(f"Redis error in cache_exists: {str(e)}")
        raise

async def check_redis_connection() -> bool:
    """
    Check if Redis connection is healthy.
    
    Returns:
        bool: True if connection is successful
    """
    try:
        redis_client = get_redis()
        return await redis_client.ping()
    except Exception as e:
        logger.error(f"Redis connection check failed: {str(e)}")
        return False 