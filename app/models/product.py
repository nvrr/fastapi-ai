
from sqlalchemy import Column, Boolean, DateTime, Integer, String, func, ForeignKey
from datetime import datetime
from app.config.database import Base


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150))
    description = Column(String(400))
    is_active = Column(Boolean, default=False)
    updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.now)
    created_at = Column(DateTime, nullable=False, server_default=func.now())



