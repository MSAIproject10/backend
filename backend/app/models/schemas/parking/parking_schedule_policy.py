# models/schemas/parking_schedule_policy.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from shared.db import Base

class ParkingSchedulePolicy(Base):
    __tablename__ = "parking_schedule_policy"

    id = Column(Integer, primary_key=True, autoincrement=True)

    parking_id = Column(Integer, ForeignKey("parking.id"))

    weekday_open = Column(String(4))  # 평일 운영 시작시각(900)
    weekday_close = Column(String(4))  # 평일 운영 종료시각(2100)

    weekend_open = Column(String(4))  # 주말 운영 시작시각(0)
    weekend_close = Column(String(4))  # 주말 운영 종료시각(2400)

    holiday_open = Column(String(4))  # 공휴일 운영 시작시각(0)
    holiday_close = Column(String(4))  # 공휴일 운영 종료시각(2400)

    parking = relationship("Parking", back_populates="schedule_policy")
