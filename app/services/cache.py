import json
import logging
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError
from app.config.redis import redis_client

logger = logging.getLogger(__name__)


class CacheService:

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Any | None:

        try:
            value = await self.redis.get(key)

            if value is None:
                return None

            return json.loads(value)

        except RedisError as exc:
            logger.error(
                "Redis GET failed for key=%s: %s",
                key,
                exc,
            )

            return None

        except json.JSONDecodeError as exc:
            logger.error(
                "Invalid cached JSON for key=%s: %s",
                key,
                exc,
            )

            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int,
    ) -> bool:

        try:
            serialized = json.dumps(value)

            await self.redis.set(
                key,
                serialized,
                ex=ttl,
            )

            return True

        except (RedisError, TypeError) as exc:
            logger.error(
                "Redis SET failed for key=%s: %s",
                key,
                exc,
            )

            return False

    async def delete(self, key: str) -> bool:

        try:
            await self.redis.delete(key)
            return True

        except RedisError as exc:
            logger.error(
                "Redis DELETE failed for key=%s: %s",
                key,
                exc,
            )

            return False

    async def exists(self, key: str) -> bool:

        try:
            return bool(
                await self.redis.exists(key)
            )

        except RedisError as exc:
            logger.error(
                "Redis EXISTS failed for key=%s: %s",
                key,
                exc,
            )

            return False

    async def clear_pattern(
        self,
        pattern: str,
    ) -> int:

        deleted = 0

        try:
            async for key in self.redis.scan_iter(
                match=pattern
            ):
                deleted += await self.redis.delete(key)

            return deleted

        except RedisError as exc:
            logger.error(
                "Redis pattern deletion failed: %s",
                exc,
            )

            return deleted


cache = CacheService(redis_client)



# ow your application doesn't need to know Redis commands.

# Instead of:

# await redis_client.set(...)
# await redis_client.get(...)
# await redis_client.delete(...)

# you use:

# await cache.set(...)
# await cache.get(...)
# await cache.delete(...)

# That's the maintainable part.







# async def get_user(user_id: int, db):

#     key = f"user:{user_id}"

#     cached_user = await cache.get(key)

#     if cached_user is not None:
#         return cached_user

#     user = await get_user_from_database(
#         user_id,
#         db,
#     )

#     if user is None:
#         return None

#     user_data = {
#         "id": user.id,
#         "name": user.name,
#         "email": user.email,
#     }

#     await cache.set(
#         key,
#         user_data,
#         ttl=300,
#     )

#     return user_data





# --------------------

# async def update_user(user_id: int, name: str, db):

#     user = await get_user_from_database(
#         user_id,
#         db,
#     )

#     user.name = name

#     await db.commit()
#     await db.refresh(user)

#     await cache.delete(
#         f"user:{user_id}"
#     )

#     return user










# -------------------------


# Use key namespaces

# Don't create random Redis keys throughout your application.

# Bad:

# "user25"

# Better:

# "user:25"

# Even better for larger applications:

# user:25
# user:25:profile
# user:25:permissions
# product:100
# product:100:details
# campaign:55

# You can centralize key generation too.

# Create:

# app/services/cache_keys.py
# class CacheKeys:

#     @staticmethod
#     def user(user_id: int) -> str:
#         return f"user:{user_id}"

#     @staticmethod
#     def user_profile(user_id: int) -> str:
#         return f"user:{user_id}:profile"

#     @staticmethod
#     def user_permissions(user_id: int) -> str:
#         return f"user:{user_id}:permissions"

#     @staticmethod
#     def product(product_id: int) -> str:
#         return f"product:{product_id}"

# Then:

# key = CacheKeys.user(user.id)

# await cache.set(
#     key,
#     user_data,
#     ttl=300,
# )

# This becomes very easy to maintain.

# 11. Health check

# Add a health endpoint:

# from fastapi import APIRouter

# from app.config.redis import redis_client


# router = APIRouter()


# @router.get("/health/redis")
# async def redis_health():

#     try:

#         await redis_client.ping()

#         return {
#             "status": "healthy",
#             "redis": "connected",
#         }

#     except Exception:

#         return {
#             "status": "unhealthy",
#             "redis": "disconnected",
#         }