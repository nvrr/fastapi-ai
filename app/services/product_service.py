from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError



def get_product(
    session: Session,
    product_id: int,
) -> Product:

    data = session.get(Product, product_id)

    if not data:
        raise HTTPException(status_code=404)

    return data


def create_product(
    session: Session,
    product: ProductCreate,
    ) -> Product:

    try:
    #     db_product = Product(
    #     name=product.name,
    #     description=product.description,
    #     is_active=product.is_active
    # )
        
    # db_product = Product.model_validate(product)
    
        db_product = Product(**product.model_dump())

        session.add(db_product)
        session.commit()
        session.refresh(db_product)

        return db_product

    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
        status_code=409,
        detail=str(exc.orig),
    )

    except SQLAlchemyError:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )


def update_product(
    product_id: int,
    product: ProductUpdate,
    session: Session,
) -> Product:

    data = session.get(Product, product_id)

    if not data:
        raise HTTPException(status_code=404)

    # data.name = product.name
    # data.description = product.description
    # data.is_active = product.is_active
    
    update_data = product.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(data, field, value)
   
    session.add(data)
    session.commit()
    session.refresh(data)

    return data


def delete_product(
    product_id: int,
    session: Session,
) -> None:

    data = session.get(Product, product_id)

    if not data:
        raise HTTPException(status_code=404)

    session.delete(data)
    session.commit()




#     model_dump() — Model → Python data

# Suppose FastAPI receives:

# {
#     "name": "iPhone",
#     "description": "Apple phone",
#     "is_active": true
# }

# Pydantic converts that request into:

# product = ProductCreate(...)

# Now:

# product.model_dump()

# gives:

# {
#     "name": "iPhone",
#     "description": "Apple phone",
#     "is_active": True
# }

# So the basic idea is:

# Pydantic model
#       ↓
#  model_dump()
#       ↓
# Python dict
# Why do we use it in update?

# Your code:

# update_data = product.model_dump(exclude_unset=True)

# Suppose the user sends:

# {
#     "name": "iPhone 17"
# }

# Then:

# product.model_dump()

# could produce:

# {
#     "name": "iPhone 17",
#     "description": None,
#     "is_active": None
# }

# But:

# product.model_dump(exclude_unset=True)

# produces only:

# {
#     "name": "iPhone 17"
# }

# That's why we use it for your partial update logic.









# model_validate() — Data → Pydantic model

# This is the opposite direction.

# Suppose you have:

# data = {
#     "name": "iPhone",
#     "description": "Apple phone",
#     "is_active": True
# }

# You can do:

# product = ProductCreate.model_validate(data)

# Now product is:

# ProductCreate(
#     name="iPhone",
#     description="Apple phone",
#     is_active=True
# )

# So:

# Python data
#     ↓
# model_validate()
#     ↓
# Pydantic model

# It also validates the data.

# For example:

# data = {
#     "name": "iPhone",
#     "description": "Apple phone",
#     "is_active": "hello"
# }

# Then:

# ProductCreate.model_validate(data)

# will fail because "hello" cannot be interpreted as a valid boolean.






# model_copy()

# It creates a copy of a Pydantic model.

# from pydantic import BaseModel

# class Product(BaseModel):
#     name: str
#     is_active: bool

# product = Product(name="iPhone", is_active=True)

# new_product = product.model_copy()

# Now:

# product
#    ↓
# model_copy()
#    ↓
# new_product

# Both contain the same data, but they are separate objects.

# You can also change values while copying
# new_product = product.model_copy(
#     update={"name": "Samsung"}
# )

# Now:

# product.name       # iPhone
# new_product.name   # Samsung

# The original wasn't changed.

# 2. model_json()

# There is an important correction here:

# In Pydantic v2, the normal method is:

# model_dump_json()

# rather than model_json().

# Example:

# product = Product(
#     name="iPhone",
#     is_active=True
# )

# json_data = product.model_dump_json()

# Result:

# {"name":"iPhone","is_active":true}

# So:

# model_dump()
#        ↓
# Python dict

# Example:

# {
#     "name": "iPhone",
#     "is_active": True
# }

# while:

# model_dump_json()
#        ↓
# JSON string

# Example:

# {"name":"iPhone","is_active":true}
# Remember the important Pydantic methods
# Method	Purpose
# model_validate()	Data → Pydantic model
# model_dump()	Pydantic model → Python dict
# model_dump_json()	Pydantic model → JSON string
# model_copy()	Copy a Pydantic model




