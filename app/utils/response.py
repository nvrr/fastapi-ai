from typing import Generic, TypeVar
from pydantic import BaseModel


# generic response
T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    data: T


# response_model=Response[ProductResponse],

# Result

# FastAPI now understands:

# Response[ProductResponse]

# {
#     "data": ProductResponse
# }


# So your API response will be:

#{
#   "data": {
#     "id": 6,
#     "name": "Test Product 6",
#     "description": "Dummy Product description 6",
#     "is_active": true,
#     "created_at": "2026-09-14T10:01:41"
#   }
# }
# 

# Your service is fine. The problem is the route's response_model.


