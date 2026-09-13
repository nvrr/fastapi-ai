# app/core/rate_limit.py

from fastapi import HTTPException, Request, status, Depends
from app.config.redis import redis_client

from app.config.security import get_current_user           



def user_rate_limit(
    limit: int,
    window: int,
    key_prefix: str = "user_rate_limit",
):
    async def dependency(
        request: Request,
        user=Depends(get_current_user),
    ):
        user_id = user.id

        key = f"{key_prefix}:{request.url.path}:user:{user_id}"

        current = redis_client.incr(key)

        if current == 1:
            redis_client.expire(key, window)

        if current > limit:
            ttl = redis_client.ttl(key)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Too many requests",
                    "retry_after": ttl,
                },
                headers={
                    "Retry-After": str(ttl),
                },
            )

    return dependency



def rate_limit(
    limit: int,
    window: int,
    key_prefix: str = "rate_limit",
):
    async def dependency(request: Request):

        client_ip = request.client.host

        key = f"{key_prefix}:{request.url.path}:{client_ip}"

        current = redis_client.incr(key)

        if current == 1:
            redis_client.expire(key, window)

        if current > limit:
            ttl = redis_client.ttl(key)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Too many requests",
                    "retry_after": ttl,
                },
                headers={
                    "Retry-After": str(ttl),
                },
            )

    return dependency