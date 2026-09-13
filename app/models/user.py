
from sqlalchemy import Column, Boolean, DateTime, Integer, String, func, ForeignKey
from datetime import datetime
from app.config.database import Base
from sqlalchemy.orm import mapped_column, relationship


from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum

class Role(str, PyEnum):
    user = "user"
    moderator = "moderator"
    admin = "admin"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(100))
    is_active = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True, default=None)
    updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.now)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

     # Why a string-based enum
        # Mixing str into the Enum base class means Role.admin == "admin" evaluates to True directly, 
        # which is what lets database storage and JSON serialization work without any manual conversion step — SQLModel stores the plain string value of the enum in the database column, 
        # and FastAPI serializes it as a plain string in JSON responses, with no extra code required for either. 
        # role: Role = Role.user sets the default at the model level, enforced simultaneously by Python's type system, 
        # Pydantic's validation, and the database column default — no code path anywhere in the application can assign a role outside the two defined values 
        # without raising a validation error immediately.
        # role: Role = Role.user
    role = Column(SQLEnum(Role), nullable=False, default=Role.user)
    
    
    tokens = relationship("UserToken", back_populates="user")

    
    def get_context_string(self, context: str):
        return f"{context}{self.password[-6:]}{self.updated_at.strftime('%m%d%Y%H%M%S')}".strip()
    
    

class UserToken(Base):
    __tablename__ = "user_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(ForeignKey('users.id'))
    access_key = Column(String(250), nullable=True, index=True, default=None)
    refresh_key = Column(String(250), nullable=True, index=True, default=None)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
      
    user = relationship("User", back_populates="tokens")



    