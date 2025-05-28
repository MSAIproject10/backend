# models/schemas/parking.py
from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from shared.db import Base

class Parking(Base):
    __tablename__ = "parking"

    id = Column(Integer, primary_key=True, autoincrement=True)

    parking_name = Column(String(100)) # 주차장명(세종로 공영 주차장(시)
    address = Column(Text) # 주소(종로구 세종로 80-1)
    parking_type = Column(String(20)) # 주차장종류명(노상주차장, 노외주차장)
    phone_number = Column(Text) # 전화번호(02-2290-6566)

    latitude = Column(Float, nullable=True)   # 위도
    longitude = Column(Float, nullable=True)  # 경도
    
    operation_type = Column(String(50)) # 운영구분명(시간제 + 버스전용 주차장)
    provide_status = Column(String(100)) # 주차현황 정보 제공여부(현재~20분이내 연계데이터 존재(현재 주차대수 표현))
    total_capacity = Column(Integer) # 총 주차면(1260)

    status = relationship("ParkingStatus", back_populates="parking", uselist=False)
    fee_policy = relationship("ParkingFeePolicy", back_populates="parking", uselist=False)
    schedule_policy = relationship("ParkingSchedulePolicy", back_populates="parking", uselist=False)







