# models/schemas/vehiclerecord.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Unicode
from shared.db import Base

class ParkingRecord(Base):
    __tablename__ = "parking_record_table"

    id = Column(Integer, primary_key=True)
    parking_id = Column(Integer, ForeignKey("parking.id"), nullable=False)

    vehicle_id = Column(Integer, ForeignKey("vehicle_table.vehicle_id"), nullable=True) # 로그인 차량일 경우 연동, 아닐 경우 Null
    ocr_detected = Column(Unicode(15), nullable=False)  # OCR로 인식한 번호판
    is_verified = Column(Boolean, default=False, nullable=False)  
    
    entry_time = Column(DateTime, nullable=False) # 입차시간
    exit_time = Column(DateTime, nullable=True) # 출차시간

