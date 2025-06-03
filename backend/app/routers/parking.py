from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from backend.app.models.schemas.parking.parking import ParkingResponse, Parking
from shared.db import get_db
from shared.services.collector import run_collect
from shared.services.updater import run_update
import math

router = APIRouter()

@router.post("/sync", status_code=200)
def trigger_data_sync():
    run_collect()
    return {"message": "Parking data sync completed."}

@router.post("/status", status_code=200)
def trigger_status_update():
    run_update()
    return {"message": "Parking status update completed."}


# Haversine 공식으로 거리 계산
def haversine(lat1, lng1, lat2, lng2):
    R = 6371  # km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# TODO : 그리드로 나눈 후 계산
# @router.get("/nearby", response_model=List[ParkingResponse])
# def get_nearby_parking(
#     lat: float = Query(...), 
#     lng: float = Query(...), 
#     radius: float = Query(1.0), 
#     db: Session = Depends(get_db)
# ):
#     parkings = db.query(Parking)\
#         .options(joinedload(Parking.fee_policy), joinedload(Parking.status))\
#         .all()

#     results = []
#     for p in parkings:
#         if p.latitude is None or p.longitude is None:
#             continue
#         if haversine(lat, lng, p.latitude, p.longitude) <= radius:
#             results.append(p)
#     return results

@router.get("/parking/all", response_model=List[ParkingResponse])
def get_all_parking(db: Session = Depends(get_db)):
    # SQLAlchemy ORM을 통해 Parking 테이블에서 모든 주차장 정보를 쿼리하면서,
    # 주차장에 연결된 fee_policy과 status를 한 번에 함께 불러오는 
    parkings = db.query(Parking)\
        .options(joinedload(Parking.fee_policy), joinedload(Parking.status))\
        .all()
    return parkings


