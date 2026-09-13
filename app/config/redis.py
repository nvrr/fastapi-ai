from redis.asyncio import Redis
from app.config.settings import get_settings


settings = get_settings()


redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
    socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
)
# This gives your application a shared Redis connection pool.