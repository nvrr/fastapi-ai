from fastapi import Depends, Query, Request
from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class PaginationOffsetParams(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    data: T
    next: Optional[str] = None
    prev: Optional[str] = None

class PaginationCursorParams(BaseModel):
    cursor: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)    