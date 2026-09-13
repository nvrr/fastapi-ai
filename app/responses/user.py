from typing import Union
from datetime import datetime
from pydantic import EmailStr, BaseModel
from app.responses.base import BaseResponse
from app.models.user import Role

class UserResponse(BaseResponse):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: Union[str, None, datetime] = None # type: ignore
    role: Role


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"