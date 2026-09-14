

from sqlalchemy import select
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.config.database import get_session
from app.models.product import Product
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.responses.product import ProductResponse
from app.utils.pagination import offset_pagination

product_router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}},
)


@product_router.get(
    "/",status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[list[ProductResponse]]
)
def get_products_offset(
    request: Request,
    session: Session = Depends(get_session),
    pagination: PaginationParams = Depends(),
):
   query = select(Product).order_by(Product.id)

   return offset_pagination(
        session=session,
        query=query,
        request=request,
        offset=pagination.offset,
        limit=pagination.limit,
    )