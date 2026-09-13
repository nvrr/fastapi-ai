

import select
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.config.database import get_session
from app.models.product import Product
from app.schemas.pagination import PaginatedResponse, PaginationParams


product_router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}},
)


@product_router.get(
    "/products",
    response_model=PaginatedResponse[list[Product]]
)
def read_campaigns(
    request: Request,
    session: Session = Depends(get_session),
    pagination: PaginationParams = Depends(),
):
    offset = pagination.offset
    limit = pagination.limit

    rows = session.exec(
        select(Product)
        .order_by(Product.product_id)
        .offset(offset)
        .limit(limit + 1)
    ).all()

    has_next = len(rows) > limit

    data = rows[:limit]

    base_url = str(request.url).split("?")[0]

    next_url = None

    if has_next:
        next_url = (
            f"{base_url}"
            f"?offset={offset + limit}"
            f"&limit={limit}"
        )

    prev_url = None

    if offset > 0:
        prev_url = (
            f"{base_url}"
            f"?offset={max(0, offset - limit)}"
            f"&limit={limit}"
        )

    return {
        "data": data,
        "next": next_url,
        "prev": prev_url,
    }