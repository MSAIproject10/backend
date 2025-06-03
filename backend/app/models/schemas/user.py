# models/schemas/user.py
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from shared.db import Base
from pydantic import BaseModel
from datetime import datetime
from .parking.parking import ParkingSimple

class User(Base):
    __tablename__ = "user_table"

    uid = Column(Integer, primary_key=True, autoincrement=True) # 고유 사용자 ID

    username = Column(String(50), nullable=False, unique=True) # 아이디
    email = Column(String(20), nullable=True, unique=True) # 사용자 개인정보로 일단 넣겠음(추후 확장성)
    password_hash = Column(String(255), nullable=False) # 해시된 비밀번호
    created_at = Column(DateTime, default=func.now()) # 가입일
    service_count = Column(Integer, default=0) # 서비스 이용 횟수
    favorite_parking = Column(Integer, ForeignKey("parking.id")) # 자주 이용하는 주차장
    
    parking = relationship("Parking", back_populates="user") # SQLAlchemy에서 객체 간 연결을 자동화, 하나의 주차장당 여러 유저 가능 
    favorite_parking = relationship("FavoriteParking", back_populates="user", cascade="all, delete")

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    uid: int
    username: str # 사용자 ID
    email : str # 사용자 email 
    created_at: datetime # 사용자 가입일
    service_count: int # 사용자 이용 횟수 
    favorite_parking : Optional[ParkingSimple]
    class Config:
        orm_mode = True






