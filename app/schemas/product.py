# app/schemas/product.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

# in response folder 
# class ProductResponse(BaseModel):
#     id: int
#     name: str
#     description: str
#     is_active: bool
#     created_at: datetime

    model_config = ConfigDict(from_attributes=True)