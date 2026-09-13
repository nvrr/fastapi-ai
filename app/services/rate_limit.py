# app/core/rate_limit.py

import logging

from fastapi import HTTPException, Request, status, Depends
from app.config.redis import redis_client
from redis.exceptions import RedisError

from app.config.security import get_current_user           


logger = logging.getLogger(__name__)



RATE_LIMIT_SCRIPT = """
local current = redis.call("INCR", KEYS[1])

if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end

return current
"""

class RateLimiter:

    def __init__(self, redis):
        self.redis = redis
        self.script = redis.register_script(RATE_LIMIT_SCRIPT)

    async def check(
        self,
        key: str,
        limit: int,
        window: int,
    ):
        try:

            current = await self.script(
                keys=[key],
                args=[window],
            )

            if current > limit:

                ttl = await self.redis.ttl(key)

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": "Too many requests",
                        "retry_after": ttl,
                    },
                    headers={
                        "Retry-After": str(max(ttl, 0))
                    },
                )

            return current

        except HTTPException:
            raise

        except RedisError:

            # Fail-open:
            # If Redis is unavailable, allow the request.
            #
            # In production you should also log/monitor this event.

            return None


rate_limiter = RateLimiter(redis_client)





# def user_rate_limit(
#     limit: int,
#     window: int,
#     key_prefix: str = "user_rate_limit",
# ):
#     async def dependency(
#         request: Request,
#         user=Depends(get_current_user),
#     ):
#         user_id = user.id

#         key = f"{key_prefix}:{request.url.path}:user:{user_id}"

#         current = redis_client.incr(key)

#         if current == 1:
#             redis_client.expire(key, window)

#         if current > limit:
#             ttl = redis_client.ttl(key)

#             raise HTTPException(
#                 status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#                 detail={
#                     "message": "Too many requests",
#                     "retry_after": ttl,
#                 },
#                 headers={
#                     "Retry-After": str(ttl),
#                 },
#             )

#     return dependency



# def rate_limit(
#     limit: int,
#     window: int,
#     key_prefix: str = "rate_limit",
# ):
#     async def dependency(request: Request):

#         client_ip = request.client.host

#         key = f"{key_prefix}:{request.url.path}:{client_ip}"

#         current = redis_client.incr(key)

#         if current == 1:
#             redis_client.expire(key, window)

#         if current > limit:
#             ttl = redis_client.ttl(key)

#             raise HTTPException(
#                 status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#                 detail={
#                     "message": "Too many requests",
#                     "retry_after": ttl,
#                 },
#                 headers={
#                     "Retry-After": str(ttl),
#                 },
#             )

#     return dependency