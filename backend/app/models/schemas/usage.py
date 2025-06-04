# models/schemas/usage.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, Unicode
from sqlalchemy.sql import func
from shared.db import Base

class Usage(Base):
    __tablename__ = "parking_usage_table"

    usage_id = Column(Integer, primary_key=True, autoincrement=True) # 사용 내역 고유 ID

    uid = Column(Integer, ForeignKey("user_table.uid", ondelete="CASCADE"))  # 사용자 삭제 시 사용기록도 삭제
    vehicle_id = Column(Integer, ForeignKey("vehicle_table.vehicle_id", ondelete="SET NULL"), nullable=True)
    parking_id = Column(Integer, ForeignKey("parking.id", ondelete="SET NULL"), nullable=True)
    
    ocr_detected = Column(Unicode(15), nullable=True)  # OCR로 인식한 번호판(확장시 사용)
    is_verified = Column(Boolean, default=False, nullable=False)  # OCR과 일치 여부(확장시 사용)
    log_id = Column(Integer, nullable=True) # 외부 차량 감지 시스템 DB의 ParkingLog 테이블의 (LOG)ID

    entry_time = Column(DateTime, nullable=True) # 입차 시간
    exit_time = Column(DateTime, nullable=True) # 출차 시간
    
    total_fee = Column(Integer, nullable=True) # 사용 요금
    fee_status = Column(Boolean, default=False, nullable=False) # 정산 여부 

class UsageResponse(BaseModel):
    parking_name: str
    entry_time: Optional[datetime]
    exit_time: Optional[datetime]
    total_fee: Optional[int]
    class Config:
        from_attributes = True 

class DetectedResult(BaseModel):
    vehicle_id: int
    parking_id: str  
    entry_time: datetime
    log_id : str # 입력 및 응답용 모델(Pydantic) 이기 때문에 log_id 추가 가능