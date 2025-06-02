# models/schemas/parking.py
from sqlalchemy import Column, Integer, Unicode, UnicodeText, Float, Boolean
from sqlalchemy.orm import relationship
from shared.db import Base

class Parking(Base):
    __tablename__ = "parking"

    id = Column(Integer, primary_key=True, autoincrement=True)

    external_id = Column(Unicode(10))  # 주차장 외부 ID
    parking_name = Column(Unicode(50))  # 한글 주차장명
    address = Column(UnicodeText)        # 한글 주소
    parking_type = Column(Unicode(10))   # 노상/노외
    phone_number = Column(Unicode(15))   # 전화번호 (일부 빈 값 존재)

    latitude = Column(Float, nullable=True)   # 위도
    longitude = Column(Float, nullable=True)  # 경도
    
    operation_type = Column(Unicode(20)) # 운영구분명(시간제 + 버스전용 주차장)
    provide_status = Column(Boolean, nullable=False, default=False)  # 주차현황 정보 제공여부(현재~20분이내 연계데이터 존재(현재 주차대수 표현))
    total_capacity = Column(Integer) # 총 주차면(1260)
    ocr_linked = Column(Boolean, nullable=False, default=False) # 차량 감지 시스템 연계 여부(False)

    status = relationship("ParkingStatus", back_populates="parking", uselist=False)
    fee_policy = relationship("ParkingFeePolicy", back_populates="parking", uselist=False)
    schedule_policy = relationship("ParkingSchedulePolicy", back_populates="parking", uselist=False)







