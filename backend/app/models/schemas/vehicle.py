# models/schemas/vehicle.py
from sqlalchemy import Column, Integer, Unicode, Boolean, ForeignKey
from shared.db import Base
from pydantic import BaseModel
from typing import Optional

class Vehicle(Base):
    __tablename__ = "vehicle_table"

    vehicle_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, ForeignKey("user_table.uid", ondelete="SET NULL"), nullable=True)

    license_plate = Column(Unicode(10), unique=True, nullable=False)     # 차량번호
    vehicle_year = Column(Integer) # 차량 연식
    mileage_km = Column(Integer) # 주행 거리
    is_commercial = Column(Boolean) # 회사용/자가용
    vehicle_type = Column(Unicode(15)) # 차종(경차, SUV, 전기차 등)
    default_type = Column(Boolean, nullable=False, default=False) # 기본 차량으로 지정되어 있는지 

class VehicleCreate(BaseModel):
    uid: Optional[int]
    
    license_plate: str
    vehicle_year: Optional[int] = None
    mileage_km: Optional[int] = None
    is_commercial: Optional[bool] 
    vehicle_type: Optional[str] 

class VehicleUpdate(BaseModel):
    vehicle_year: Optional[int] = None
    mileage_km: Optional[int] = None
    is_commercial: Optional[bool] = None
    vehicle_type: Optional[str] = None

    default_type: Optional[bool] = None 

class VehicleResponse(BaseModel):
    vehicle_id: int

    license_plate: str
    vehicle_year: Optional[int] = None
    mileage_km: Optional[int] = None
    is_commercial: Optional[bool] 
    vehicle_type: Optional[str] 
    default_type: bool
    class Config:
        from_attributes = True 
