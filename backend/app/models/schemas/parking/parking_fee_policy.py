# models/schemas/parking_fee_policy.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from shared.db import Base

class ParkingFeePolicy(Base):
    __tablename__ = "parking_fee_policy"

    id = Column(Integer, primary_key=True, autoincrement=True)

    parking_id = Column(Integer, ForeignKey("parking.id"))

    monthly_fee = Column(Integer) # 월 정기권 금액(176000)
    base_fee = Column(Integer) # 기본 주차 요금(430)
    base_time_min = Column(Integer) # 기본 시간 (분 단위)(5)

    extra_fee = Column(Integer) # 추가 단위 요금(430)
    extra_time_min = Column(Integer) # 추가 시간 단위 (분 단위)
    daily_max_fee = Column(Integer) # 일 최대 요금(30900)

    weekday_pay_type = Column(String(10)) # 유무료 구분명(유료, 무료)
    saturday_pay_type = Column(String(10)) # 토요일 유/무료(유료, 무료)
    holiday_pay_type = Column(String(10)) # 공휴일 유/무료(유료, 무료)

    parking = relationship("Parking", back_populates="fee_policy")
