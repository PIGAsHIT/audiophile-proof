import json
import logging
import redis
from src.core.config import settings

logger = logging.getLogger("uvicorn")

class RedisCacheManager:
    def __init__(self):
        self._pool = None
        self._client = None
        self.expire_seconds = getattr(settings, "REDIS_CACHE_EXPIRE", 3600)

    @property
    def client(self):
        if self._client is None:
            try:
                redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
                self._pool = redis.ConnectionPool.from_url(
                    redis_url, 
                    decode_responses=True, 
                    socket_timeout=5
                )
                self._client = redis.Redis(connection_pool=self._pool)
                logger.info(f"🚀 Redis Connection Pool initialized at {settings.REDIS_HOST}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Redis: {e}")
                return None
        return self._client

    def get_cached_recommendation(self, brand: str, model: str):
        if not self.client:
            return None
            
        key = f"rec:{brand.lower()}:{model.lower()}"
        try:
            data = self.client.get(key)
            if data:
                logger.info(f"⚡ Cache Hit: {key}")
                return json.loads(data)
        except (redis.exceptions.ConnectionError, json.JSONDecodeError) as e:
            logger.warning(f"⚠️ Cache Miss (Redis Error): {e}")
        return None

    def set_cached_recommendation(self, brand: str, model: str, data: dict):
        if not self.client:
            return
            
        key = f"rec:{brand.lower()}:{model.lower()}"
        try:
            self.client.setex(key, self.expire_seconds, json.dumps(data))
            logger.info(f"💾 Cache Set: {key}")
        except Exception as e:
            logger.error(f"❌ Failed to save cache for {key}: {e}")

cache_manager = RedisCacheManager()

def get_cached_recommendation(brand: str, model: str):
    return cache_manager.get_cached_recommendation(brand, model)

def set_cached_recommendation(brand: str, model: str, data: dict):
    cache_manager.set_cached_recommendation(brand, model, data)
