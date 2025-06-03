# routers/user.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.schemas.parking.parking import Parking, ParkingResponse, ParkingSimple
from backend.app.models.schemas.parking.parking_favorite import FavoriteParking
from backend.app.models.schemas.usage import Usage, UsageResponse
from backend.app.models.schemas.user import User, UserResponse
from backend.app.models.schemas.vehicle import Vehicle, VehicleResponse
from backend.app.routers.auth import get_current_user
from shared.db import get_db

router = APIRouter()

# 현재 로그인한 사용자의 정보를 토큰을 통해 가져오는 API
@router.get("/me", response_model=UserResponse) # response_mode : 사용자에게 적절히 변환하여 응답
def get_me(current_user = Depends(get_current_user)):
    return current_user

@router.get("/vehicles", response_model=List[VehicleResponse])
def get_vehicles_by_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vehicles = db.query(Vehicle).filter(Vehicle.uid == current_user.uid).all()
    if not vehicles:
        raise HTTPException(status_code=404, detail="No vehicles found for this user")
    return vehicles

@router.get("/usages", response_model=List[UsageResponse])
def get_user_usages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    usage_records = (
        db.query(
            Parking.parking_name, # 사용자 사용기록을 주차장 이름과 함께 JOIN 조회
            Usage.entry_time,
            Usage.exit_time,
            Usage.total_fee
        )
        .join(Parking, Parking.id == Usage.parking_id)
        .filter(Usage.uid == current_user.uid)
        .order_by(Usage.entry_time.desc())
        .all()
    )
    response = [
        UsageResponse(
            parking_name=record.parking_name,
            entry_time=record.entry_time,
            exit_time=record.exit_time,
            total_fee=record.total_fee
        )
        for record in usage_records
    ]
    return response

# Favorite Update 
@router.post("/favorites/toggle")
def toggle_favorite_parking(
    parking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    favorite = db.query(FavoriteParking).filter_by(
        uid=current_user.uid,
        parking_id=parking_id
    ).first()

    if favorite:
        db.delete(favorite)
        db.commit()
        return {"message": "Removed from favorites.", "is_favorite": False}

    new_favorite = FavoriteParking(uid=current_user.uid, parking_id=parking_id) # 기존에 없다면 새롭게 favorite parking 테이블로 등록 
    db.add(new_favorite)
    db.commit()
    return {"message": "Added to favorites.", "is_favorite": True}

# Favorite Read 
@router.get("/favorites", response_model=List[ParkingSimple])
def get_favorite_parkings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    favorites = (
        db.query(Parking)
        .join(FavoriteParking, FavoriteParking.parking_id == Parking.id)
        .filter(FavoriteParking.uid == current_user.uid)
        .all()
    )
    return [ParkingSimple.from_orm(p) for p in favorites]
