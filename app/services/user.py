from app.models.user import User
from app.config.security import hash_password, is_password_strong_enough
from fastapi import HTTPException

async def create_user_account(data, session):
    # print("PASSWORD:", repr(data.password))
    # print("PASSWORD LENGTH:", len(data.password))
    # print("PASSWORD BYTES:", len(data.password.encode("utf-8")))
    user_exist = session.query(User).filter(User.email == data.email).first()

    if user_exist:
        raise HTTPException(status_code=400, detail="Email is already exists.")

    if not is_password_strong_enough(data.password):
            raise HTTPException(status_code=400, detail="Please provide strong password.")

    # print("Password passed validation")

    user = User()
    user.name = data.name
    user.email = data.email
    user.password = hash_password(data.password)
    user.is_active = False
    session.add(user)
    session.commit()
    session.refresh(user)

    return user



