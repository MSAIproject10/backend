# routers/vehicles.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.schemas.user import User
from backend.app.models.schemas.vehicle import Vehicle, VehicleCreate, VehicleResponse, VehicleUpdate
from backend.app.routers.auth import get_current_user
from shared.db import get_db

router = APIRouter()

# Vehicle Create
## TODO : Maximum 요청 create 안되도록 
@router.post("/", response_model=VehicleResponse)
def create_vehicle(
    data: VehicleCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_plate = db.query(Vehicle).filter(Vehicle.license_plate == data.license_plate).first()
    if existing_plate:
        raise HTTPException(status_code=409, detail="This is a registered vehicle number.")

    existing_vehicles = db.query(Vehicle).filter(Vehicle.uid == current_user.uid).all() # 사용자 자동차 목록 가져오기 
    is_default = False
    if len(existing_vehicles) == 0:
        is_default = True
    vehicle = Vehicle(
        **data.model_dump(exclude={"default_type", "uid"}),
        uid=current_user.uid,
        default_type=is_default
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

# Vehicle Read All
# @router.get("/", response_model=List[VehicleResponse])
# def get_all_vehicles(db: Session = Depends(get_db)):
#     return db.query(Vehicle).all()

# Vehicle Update
@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first() # update 요청한 차량 가져오기 
    if not vehicle or vehicle.uid != current_user.uid:
        raise HTTPException(status_code=404, detail="Vehicle not found or unauthorized")
    
    update_data = data.model_dump(exclude_unset=True, exclude={"default_type"})
    for key, value in update_data.items():
        setattr(vehicle, key, value)

    if data.default_type is True: # 기본 차량으로 설정하고자 하는 경우
        db.query(Vehicle).filter(
            Vehicle.uid == current_user.uid,
            Vehicle.vehicle_id != vehicle_id
        ).update({Vehicle.default_type: False})
        vehicle.default_type = True
    db.commit()
    db.refresh(vehicle)
    return vehicle

# Vehicle Delete
@router.delete("/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == vehicle_id,
        Vehicle.uid == current_user.uid
    ).first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or unauthorized") # 이미 vehicle id에 해당하는 차량이 삭제된 경우 

    is_default = vehicle.default_type
    db.delete(vehicle)
    db.commit()

    if is_default:
        new_default = db.query(Vehicle).filter( # 다른 차량 중 하나를 기본 차량으로 지정 
            Vehicle.uid == current_user.uid
        ).first()
        if new_default:
            new_default.default_type = True
            db.commit()
    return {"message": "Vehicle deleted successfully"}
