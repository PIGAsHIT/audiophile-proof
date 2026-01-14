import os
import json
import redis
import logging
from dotenv import load_dotenv

load_dotenv()

# 建議改用與 K8s YAML 一致的變數名
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# 初始化連線池
try:
    pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True, socket_timeout=5)
    client = redis.Redis(connection_pool=pool)
except Exception as e:
    logging.error(f"Redis Connection Pool Error: {e}")

CACHE_EXPIRE_SECONDS = 3600

def get_cached_recommendation(brand: str, model: str):
    key = f"rec:{brand.lower()}:{model.lower()}"
    try:
        data = client.get(key)
        if data:
            return json.loads(data)
    except (redis.exceptions.ConnectionError, json.JSONDecodeError) as e:
        # 當 Redis 掛掉或資料格式錯誤，僅記錄 Log，不中斷主程式
        logging.warning(f"Cache Miss due to Redis error: {e}")
    return None

def set_cached_recommendation(brand: str, model: str, data: dict):
    key = f"rec:{brand.lower()}:{model.lower()}"
    try:
        # 使用 try 確保即使寫入快取失敗，主流程依然能完成
        client.setex(key, CACHE_EXPIRE_SECONDS, json.dumps(data))
    except Exception as e:
        logging.error(f"Failed to save cache for {key}: {e}")