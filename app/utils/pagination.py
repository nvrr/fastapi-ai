# app/utils/pagination.py

from typing import Any

from fastapi import Request
from sqlalchemy import Select
from sqlalchemy.orm import Session


def offset_pagination(
    session: Session,
    query: Select,
    request: Request,
    offset: int,
    limit: int,
) -> dict[str, Any]:

    items = (
        session.execute(
            query
            .offset(offset)
            .limit(limit + 1)
        )
        .scalars()
        .all()
    )

    has_next = len(items) > limit

    data = items[:limit]

    base_url = str(request.url).split("?")[0]

    next_url = (
        f"{base_url}?offset={offset + limit}&limit={limit}"
        if has_next
        else None
    )

    prev_url = (
        f"{base_url}?offset={max(0, offset - limit)}&limit={limit}"
        if offset > 0
        else None
    )

    return {
        "data": data,
        "next": next_url,
        "prev": prev_url,
    }