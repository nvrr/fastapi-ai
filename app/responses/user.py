from typing import Union
from datetime import datetime
from pydantic import EmailStr
from app.responses.base import BaseResponse


class UserResponse(BaseResponse):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: Union[str, None, datetime] = None # type: ignore


class LoginResponse(BaseResponse):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"