from fastapi import Depends, Request

from app.services.rate_limit import rate_limiter
from app.config.security import get_current_user 

def ip_rate_limit(
    limit: int,
    window: int,
    key_prefix: str,
):

    async def dependency(request: Request):
# request.client.host

# may give you the proxy/load-balancer IP instead of the actual client IP.

# You may eventually use forwarded headers, but do not blindly trust X-Forwarded-For.

# Your proxy must be configured as a trusted proxy.

# For now, keep:

# request.client.host

# while learning locally

        client_ip = request.client.host

        key = f"{key_prefix}:ip:{client_ip}"

        await rate_limiter.check(
            key=key,
            limit=limit,
            window=window,
        )

    return dependency
# Depends(
    # ip_rate_limit(
    #     limit=100,
    #     window=60,
    #     key_prefix="api",
    # )
# )


# For authenticated APIs, use the user.id.


def user_rate_limit(
    limit: int,
    window: int,
    key_prefix: str,
):

    async def dependency(
        request: Request,
        user=Depends(get_current_user),
    ):

        key = (
            f"{key_prefix}:"
            f"user:{user.id}:"
            f"{request.url.path}"
        )

        await rate_limiter.check(
            key=key,
            limit=limit,
            window=window,
        )

    return dependency










