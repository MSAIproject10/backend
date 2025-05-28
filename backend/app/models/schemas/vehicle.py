# models/schemas/car.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from shared.db import Base

class Vehicle(Base):
    __tablename__ = "vehicle_table"

    vehicle_id = Column(Integer, primary_key=True, autoincrement=True)

    uid = Column(Integer, ForeignKey("user_table.uid", ondelete="CASCADE"))

    vehicle_year = Column(Integer) # 차량 연식
    mileage_km = Column(Integer) # 주행 거리
    is_commercial = Column(Boolean) # 회사용/자가용
    vehicle_type = Column(String(30)) # 차종(경차, SUV, 전기차 등)