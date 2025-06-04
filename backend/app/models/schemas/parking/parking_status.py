# models/schemas/parking_status.py
from typing import Optional
from sqlalchemy import Column, Integer, Unicode, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from shared.db import Base
from pydantic import BaseModel

class ParkingStatus(Base):
    __tablename__ = "parking_status"

    id = Column(Integer, primary_key=True, autoincrement=True)

    parking_id = Column(Integer, ForeignKey("parking.id"))

    current_occupancy = Column(Integer) # 현재 주차 차량 수(305)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    congestion_level = Column(Unicode(5))  # 혼잡도 

    entry_count = Column(Integer)     # 입차대수
    exit_count = Column(Integer)      # 출차대수

    parking = relationship("Parking", back_populates="status")


class ParkingStatusResponse(BaseModel):
    current_occupancy: Optional[int]
    congestion_level: Optional[str]
    class Config:
        from_attributes = True 
