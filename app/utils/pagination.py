# app/utils/pagination.py
import base64
from typing import Any, Optional

from fastapi import Request
from sqlalchemy import Select, asc, desc, select
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


# cursor_pagination


def cursor_pagination(
   session: Session,
    query: Select,
    model: Any,
    cursor_column: Any,
    request: Request,
    cursor: Optional[str],
    limit: int,
)  -> dict[str, Any] :
    
    cursor_id = None

    # -------------------------
    # NEXT PAGE
    # -------------------------

    if cursor is not None:
        cursor_id = decode_cursor(cursor)

        query = query.where(
            cursor_column > cursor_id
        )

    rows = (
        session.execute(
            query.limit(limit + 1)
        )
        .scalars()
        .all()
    )

    has_next = len(rows) > limit

    data = rows[:limit]

    base_url = str(request.url).split("?")[0]

    if has_next:
        next_cursor = encode_cursor(
            getattr(data[-1], cursor_column.key)
        )

        next_url = (
            f"{base_url}"
            f"?cursor={next_cursor}"
            f"&limit={limit}"
        )
    else:
        next_url = None

    # -------------------------
    # PREVIOUS PAGE
    # -------------------------

    if cursor is not None:

        backward_query = (
            select(model)
            .where(cursor_column < cursor_id)
            .order_by(desc(cursor_column))
            .limit(limit)
        )

        previous_rows = (
            session.execute(backward_query)
            .scalars()
            .all()
        )

        if len(previous_rows) == limit - 1:

            prev_url = (
                f"{base_url}"
                f"?limit={limit}"
            )

        elif len(previous_rows) < limit - 1:

            prev_url = None

        else:

            prev_cursor = encode_cursor(
                getattr(previous_rows[-1], cursor_column.key)
            )

            prev_url = (
                f"{base_url}"
                f"?cursor={prev_cursor}"
                f"&limit={limit}"
            )

    else:
        prev_url = None

    return {
        "data": data,
        "next": next_url,
        "prev": prev_url,
    }


def encode_cursor(value: int) -> str:
    return base64.urlsafe_b64encode(
        str(value).encode()
    ).decode()


def decode_cursor(cursor: str) -> int:
    return int(
        base64.urlsafe_b64decode(
            cursor.encode()
        ).decode()
    )