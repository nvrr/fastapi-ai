from fastapi import Request

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config.database import get_session
from app.core.rate_limit import rate_limit, user_rate_limit
from app.models.user import Role, User
from app.responses.user import UserResponse, LoginResponse
from app.schemas.user import RegisterUserRequest, ResetRequest, VerifyUserRequest, EmailRequest
from app.services import user
from app.config.security import get_current_user, oauth2_scheme, require_roles

# redis
from app.config.redis import redis_client

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

auth_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme), Depends(get_current_user)]
)

guest_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)


@user_router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(data: RegisterUserRequest,  background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    return await user.create_user_account(data, session, background_tasks)


@user_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user_account(data: VerifyUserRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    await user.activate_user_account(data, session, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})

@guest_router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse )
async def user_login(request: Request, data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    client_ip = request.client.host

# username --> email
    key = f"login:{client_ip}:{data.username}"

    current = redis_client.incr(key)

    if current == 1:
        redis_client.expire(key, 60)

    if current > 2:
        ttl = redis_client.ttl(key)

        raise HTTPException(
            status_code=429,
            detail={
                "message": "Too many login attempts",
                "retry_after": ttl,
            },
            headers={
                "Retry-After": str(ttl)
            },
        )

    # end redis
    return await user.get_login_token(data, session)

@guest_router.post("/refresh", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def refresh_token(refresh_token = Header(), session: Session = Depends(get_session)):
    return await user.get_refresh_token(refresh_token, session)

@guest_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data: EmailRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    await user.email_forgot_password_link(data, background_tasks, session)
    return JSONResponse({"message": "A email with password reset link has been sent to you."})

@guest_router.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: ResetRequest, session: Session = Depends(get_session)):
    await user.reset_user_password(data, session)
    return JSONResponse({"message": "Your password has been updated."})

@auth_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse, dependencies=[
        Depends(
            user_rate_limit(
                limit=10,
                window=60,
                key_prefix="me",
            )
        )
    ])
async def fetch_user(user = Depends(get_current_user)):
    return user


@auth_router.get("/{pk}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_info(pk, session: Session = Depends(get_session)):
    return await user.fetch_user_detail(pk, session)

# Protecting Routes with Role Guards
@auth_router.get("/mee", status_code=status.HTTP_200_OK, response_model=UserResponse, dependencies=[Depends(require_roles(Role.admin))])
async def fetch_a_user(user = Depends(get_current_user)):
    return user

# A route open to any authenticated user
# @router.get("/", dependencies=[Depends(get_current_user)])
# def get_tasks(...):

@auth_router.get("/meee", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def fetch_aa_user(user = Depends(get_current_user)):
    return user

# Promoting a User's Role
@auth_router.patch("/{user_id}/role", response_model=UserResponse, dependencies=[Depends(require_roles(Role.admin))],
)
def update_user_role(
    user_id: int,
    new_role: Role,
    session: Session = Depends(get_session),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@auth_router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    dependencies=[Depends(require_roles(Role.admin))],
)
def activate_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@auth_router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    dependencies=[Depends(require_roles(Role.admin))],
)
def deactivate_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    session.add(user)
    session.commit()
    session.refresh(user)
    return user