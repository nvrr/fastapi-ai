

from typing import Optional

from sqlalchemy import desc, select
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session
from app.config.database import get_session
from app.models.product import Product
from app.schemas.pagination import PaginatedResponse, PaginationOffsetParams
from app.responses.product import ProductResponse
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import create_product, delete_product, get_product, update_product
from app.utils.pagination import offset_pagination,cursor_pagination
from app.utils.response import Response

product_router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}},
)


@product_router.get(
    "/offset-products",status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[list[ProductResponse]]
)
def get_offset_products(
    request: Request,
    session: Session = Depends(get_session),
    pagination: PaginationOffsetParams = Depends(),
):
   query = select(Product).order_by(Product.id)

   return offset_pagination(
        session=session,
        query=query,
        request=request,
        offset=pagination.offset,
        limit=pagination.limit,
    )



@product_router.get(
    "/cursor-products",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[list[ProductResponse]],
)
def get_cursor_products(
    request: Request,
    session: Session = Depends(get_session),
    cursor: Optional[str] = Query(None),
    limit: int = Query(5, ge=1),
):
    query = select(Product).order_by(Product.id)
    
    return cursor_pagination(
        session=session,
        query=query,
        model=Product,
        cursor_column=Product.id,
        request=request,
        cursor=cursor,
        limit=limit,
    )
# version - 2
# from app.schemas.pagination import PaginationCursorParams, PaginatedResponse, PaginationOffsetParams
# def get_cursor_products(
#     request: Request,
#     session: Session = Depends(get_session),
#     pagination: PaginationCursorParams = Depends(),
# ):
#     query = select(Product).order_by(Product.id)

#     return cursor_pagination(
#         session=session,
#         query=query,
#         model=Product,
#         cursor_column=Product.id,
#         request=request,
#         cursor=pagination.cursor,
#         limit=pagination.limit,
#     )





# //req`s`


@product_router.get(
    "/get_product_by_id/{id}",
    response_model=Response[ProductResponse],
)
def read_product(
    id: int,
    session: Session = Depends(get_session)
):
    return {"data": get_product(session, id)}


@product_router.post(
    "/create_product",
    status_code=status.HTTP_201_CREATED,
    response_model=Response[ProductResponse]
)
def create(
    product: ProductCreate,
    session: Session = Depends(get_session)
):
    return {"data": create_product(session, product)}


@product_router.put(
    "/update_product/{id}",
    response_model=Response[ProductResponse]
)
def update(
    id: int,
    product: ProductUpdate,
    session: Session = Depends(get_session)
):
    return {"data": update_product(id, product,session)}


@product_router.delete(
    "/delete_product/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
    id: int,
    session: Session = Depends(get_session)
):
    delete_product(session, id)