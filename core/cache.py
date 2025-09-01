import redis
from core.config import settings
import json
from typing import Any

# Initialize Redis client
redis_client = None

def initialize_cache():
    global redis_client
    if settings.REDIS_ENABLED:
        try:
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=0,
                decode_responses=False
            )
            # Test connection
            redis_client.ping()
            print("✅ Connected to Redis cache")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            redis_client = None

def get_cache(key: str) -> Any:
    if not redis_client:
        return None
    
    try:
        cached_data = redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
    except Exception as e:
        print(f"Cache get error: {e}")
    return None

def set_cache(key: str, value: Any, ttl: int = 300) -> bool:
    if not redis_client:
        return False
    
    try:
        serialized = json.dumps(value)
        redis_client.setex(key, ttl, serialized)
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False

# Initialize on import
initialize_cache()