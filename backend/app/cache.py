import json
import logging
from redis import Redis
from redis.exceptions import RedisError
from app.config import get_settings

logger = logging.getLogger(__name__)
_client: Redis | None = None


def client() -> Redis | None:
    global _client
    if _client is None:
        try:
            candidate = Redis.from_url(get_settings().redis_url, decode_responses=True, socket_timeout=0.5)
            candidate.ping()
            _client = candidate
        except RedisError:
            logger.warning("Redis unavailable; dashboard cache disabled")
            return None
    return _client


def get_json(key: str):
    redis = client()
    if redis is None:
        return None
    try:
        value = redis.get(key)
        return json.loads(value) if value else None
    except (RedisError, ValueError):
        return None


def set_json(key: str, value: dict, ttl_seconds: int = 60) -> None:
    redis = client()
    if redis is None:
        return
    try:
        redis.setex(key, ttl_seconds, json.dumps(value))
    except RedisError:
        logger.warning("Could not write dashboard cache")


def invalidate_user_dashboard(user_id: int) -> None:
    redis = client()
    if redis is None:
        return
    try:
        redis.delete(f"dashboard:{user_id}")
    except RedisError:
        logger.warning("Could not invalidate dashboard cache")
