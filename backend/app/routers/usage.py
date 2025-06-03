# 사용자 단위로 책임이 나뉘는 경우 router로 나누기 
# routers/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.schemas.usage import CreateUsageRequest, Usage, UsageResponse
from backend.app.models.schemas.vehicle import Vehicle
from shared.db import get_db
from backend.app.crud import user_crud
from backend.app.models.schemas.user import User, UserResponse
from shared.powerbidb import fetch_parking_logs

router = APIRouter()

# TODO : 추가할떄 fetch_parkings_logs사용해서 DB조회
@router.post("/usage", response_model=UsageResponse)
def create_usage(req: CreateUsageRequest, db: Session = Depends(get_db)):
    # 사용자 차량 확인
    vehicle = db.query(Vehicle).filter_by(vehicle_id=req.vehicle_id, uid=req.uid).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="해당 차량이 사용자 소유가 아닙니다.")

    # Usage 생성
    usage = Usage(
        uid=req.uid,
        vehicle_id=req.vehicle_id,
        parking_id=req.parking_id,
        entry_time=req.entry_time,
        ocr_detected=req.ocr_detected,
        is_verified=True
    )
    db.add(usage)

    # 사용자 사용 count 증가
    user = db.query(User).filter_by(uid=req.uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자 없음")
    user.usage_count = (user.usage_count or 0) + 1

    db.commit()
    db.refresh(usage)
    return usage

# ============================
# 사용자별 Usage 기록 조회
# ============================
@router.get("/usage/user/{uid}", response_model=List[UsageResponse])
def get_user_usages(uid: int, db: Session = Depends(get_db)):
    usage_list = db.query(Usage).filter_by(uid=uid).order_by(Usage.entry_time.desc()).all()
    return usage_list
