# 사용자 단위로 책임이 나뉘는 경우 router로 나누기 
# routers/user.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shared.db import get_db

router = APIRouter()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.schemas.vehicle import Vehicle, VehicleCreate, VehicleResponse
from shared.db import get_db

router = APIRouter()

# Vehicle Create
@router.post("/", response_model=VehicleResponse)
def create_vehicle(data: VehicleCreate, db: Session = Depends(get_db)):
    vehicle = Vehicle(**data.dict())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

# ✅ Read All
@router.get("/", response_model=List[VehicleResponse])
def get_all_vehicles(db: Session = Depends(get_db)):
    return db.query(Vehicle).all()

# ✅ Read by ID
@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

# ✅ Update
@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: int, data: VehicleCreate, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(vehicle, key, value)
    db.commit()
    db.refresh(vehicle)
    return vehicle

# ✅ Delete
@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted successfully"}

# ✅ Set as default vehicle for user
@router.post("/{vehicle_id}/set-default")
def set_default_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.uid is None:
        raise HTTPException(status_code=400, detail="Vehicle has no associated user")

    # 같은 사용자의 다른 차량들 default 해제
    db.query(Vehicle)\
        .filter(Vehicle.uid == vehicle.uid, Vehicle.vehicle_id != vehicle_id)\
        .update({Vehicle.default_type: False})

    # 현재 차량 default 설정
    vehicle.default_type = True
    db.commit()
    db.refresh(vehicle)

    return {"message": f"Vehicle {vehicle_id} is now the default vehicle for user {vehicle.uid}"}
# ✅ Get default vehicle for user
@router.get("/user/{uid}/default", response_model=VehicleResponse)
def get_default_vehicle(uid: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.uid == uid, Vehicle.default_type == True).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="No default vehicle found for this user")
    return vehicle
