# models/schemas/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from shared.db import Base
from pydantic import BaseModel
from datetime import datetime

class User(Base):
    __tablename__ = "user_table"

    uid = Column(Integer, primary_key=True, autoincrement=True) # 고유 사용자 ID

    username = Column(String(50), nullable=False, unique=True) # 아이디
    password_hash = Column(String(255), nullable=False) # 해시된 비밀번호
    created_at = Column(DateTime, default=func.now()) # 가입일
    service_count = Column(Integer, default=0) # 서비스 이용 횟수


class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    uid: int
    username: str
    created_at: datetime
    service_count: int

    class Config:
        orm_mode = True






