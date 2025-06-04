# models/schemas/parking_fee_policy.py
from typing import Optional
from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from shared.db import Base
from pydantic import BaseModel

class ParkingFeePolicy(Base):
    __tablename__ = "parking_fee_policy"

    id = Column(Integer, primary_key=True, autoincrement=True)

    parking_id = Column(Integer, ForeignKey("parking.id")) # DB에서의 참조 무결성 보장을 위한 키

    base_fee = Column(Integer) # 기본 주차 요금(430)
    base_time_min = Column(Integer) # 기본 시간 (분 단위)(5)
    extra_fee = Column(Integer) # 추가 단위 요금(430)
    extra_time_min = Column(Integer) # 추가 시간 단위 (분 단위)

    monthly_fee = Column(Integer) # 월 정기권 금액(176000)
    daily_max_fee = Column(Integer) # 일 최대 요금(30900)

    weekday_pay_type = Column(Boolean, nullable=False, default=True) # True = 유료, False = 무료
    saturday_pay_type = Column(Boolean, nullable=False, default=True)
    holiday_pay_type = Column(Boolean, nullable=False, default=True)

    parking = relationship("Parking", back_populates="fee_policy") # SQLAlchemy에서 객체 간 연결을 자동화

class ParkingFeeResponse(BaseModel):
    base_fee : Optional[int]
    base_time_min: Optional[int]
    class Config:
        from_attributes = True 