# models/schemas/usage.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from shared.db import Base

class Usage(Base):
    __tablename__ = "parking_usage_table"

    usage_id = Column(Integer, primary_key=True, autoincrement=True) # 사용 내역 고유 ID

    # parking_usage_table
    uid = Column(Integer, ForeignKey("user_table.uid", ondelete="CASCADE"))  # 사용자 삭제 시 사용기록도 삭제
    vehicle_id = Column(Integer, ForeignKey("vehicle_table.vehicle_id", ondelete="SET NULL"), nullable=True)
    parking_id = Column(Integer, ForeignKey("parking.id", ondelete="SET NULL"), nullable=True)
    
    entry_time = Column(DateTime, nullable=False) # 입차 시간
    exit_time = Column(DateTime, nullable=False) # 출차 시간
    total_fee = Column(Integer, nullable=False) # 사용 요금
