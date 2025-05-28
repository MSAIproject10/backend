# models/schemas/parking_status.py
from sqlalchemy import Column, Integer, TIMESTAMP, String, ForeignKey
from sqlalchemy.orm import relationship
from shared.db import Base

class ParkingStatus(Base):
    __tablename__ = "parking_status"

    id = Column(Integer, primary_key=True, autoincrement=True)

    parking_id = Column(Integer, ForeignKey("parking.id"))

    current_occupancy = Column(Integer) # 현재 주차 차량 수(305)
    last_updated = Column(TIMESTAMP) # 현재 주차 차량 수 업데이트 시간(2025-05-27  9:26:30 PM)
    congestion_level = Column(String(10))  # 혼잡도 

    parking = relationship("Parking", back_populates="status")