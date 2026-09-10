import logging
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
import base64
from datetime import datetime
from sqlalchemy.orm import joinedload, Session
from datetime import datetime, timedelta
from app.config import settings
from app.config.database import get_session
from app.config.settings import get_settings
from app.models.user import Role, User, UserToken

SPECIAL_CHARACTERS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>']

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# tokenUrl="/auth/login" -does not mean OAuth2PasswordBearer calls /auth/login
# "The endpoint where the client can obtain an OAuth2 token is /auth/login."
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def is_password_strong_enough(password: str) -> bool:
    if len(password) < 8:
        return False

    if not any(char.isupper() for char in password):
        return False

    if not any(char.islower() for char in password):
        return False

    if not any(char.isdigit() for char in password):
        return False

    if not any(char in SPECIAL_CHARACTERS for char in password):
        return False

    return True







def str_encode(string: str) -> str:
    return base64.b85encode(string.encode('ascii')).decode('ascii')


def str_decode(string: str) -> str:
    return base64.b85decode(string.encode('ascii')).decode('ascii')

# decode token
def get_token_payload(token: str, secret: str, algo: str):
    try:
        payload = jwt.decode(token, secret, algorithms=algo)
    except Exception as jwt_exec:
        logging.debug(f"JWT Error: {str(jwt_exec)}")
        payload = None
    return payload

# generatin encoded token
def generate_token(payload: dict, secret: str, algo: str, expiry: timedelta):
    expire = datetime.utcnow() + expiry
    payload.update({"exp": expire})
    return jwt.encode(payload, secret, algorithm=algo)

# get user after decode by decode token methode: get_token_payload
async def get_token_user(token: str, db):
    # # decode token - get_token_payload:  
    payload = get_token_payload(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    if payload:
        user_token_id = str_decode(payload.get('r'))
        user_id = str_decode(payload.get('sub'))
        access_key = payload.get('a')
        user_token = db.query(UserToken).options(joinedload(UserToken.user)).filter(UserToken.access_key == access_key,
                                                 UserToken.id == user_token_id,
                                                 UserToken.user_id == user_id,
                                                 UserToken.expires_at > datetime.utcnow()
                                                 ).first()
        if user_token:
            return user_token.user
    return None

# load user
async def load_user(email: str, db):
    from app.models.user import User
    try:
        user = db.query(User).filter(User.email == email).first()
    except Exception as user_exec:
        logging.info(f"User Not Found, Email: {email}")
        user = None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    user = await get_token_user(token=token, db=db)
    if user:
        return user
    raise HTTPException(status_code=401, detail="Not authorised.")

# Role - admin or user
def require_roles(*allowed_roles: Role) -> Callable:
    """
    Dependency factory that enforces role-based access control.

    Usage:
        @router.get("/admin/users", dependencies=[Depends(require_roles(Role.admin))])
        @router.get("/reports", dependencies=[Depends(require_roles(Role.admin, Role.editor))])
    """
    def role_guard(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(r.value for r in allowed_roles)}",
            )
        return user
    return role_guard
