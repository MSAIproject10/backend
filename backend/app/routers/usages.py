# routers/usages.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.schemas.parking.parking import Parking
from backend.app.models.schemas.usage import DetectedResult, Usage
from backend.app.models.schemas.vehicle import Vehicle
from backend.app.routers.auth import get_current_user
from shared.db import get_db
from backend.app.models.schemas.user import User
from shared.powerbidb import fetch_parking_entry, fetch_parking_exit
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

router = APIRouter()

# 1. 네비게이션 종료 이벤트 발생 → 차량 감지 시스템으로부터 입차 로그 감지
@router.get("/entry", response_model=DetectedResult)
def get_detected_entry(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.uid == current_user.uid, Vehicle.default_type == True) # 현재 로그인된 uid 확인 & default인 차량 불러옴 
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="There is no vehicle information.")
    
    logs = fetch_parking_entry(vehicle.license_plate) # 외부 차량 감지 시스템 DB 접근 => ID(주차장 externel id), 입차시간 리턴
    if not logs:
        logger.warning(f"❗[ENTRY] No detection logs found for car number {vehicle.license_plate}")
        raise HTTPException(status_code=404, detail="There are no vehicle detection records.")

    latest = logs[0] # 가장 최근의 기록을 사용 
    parking = db.query(Parking).filter(Parking.external_id == latest["주차장ID"]).first()
    if not parking:
        raise HTTPException(status_code=404, detail="This is a parking lot that is not registered in the DB.")

    return DetectedResult(
        vehicle_id=vehicle.vehicle_id,
        parking_id=latest["주차장ID"],
        entry_time=latest["입차시간"],
        log_id=latest["ID"]
    )

# 2. 입차 기록 확정 → DetectedResult 기반으로 Usage 생성
@router.post("/confirm")
def confirm_usage_entry(
    detected: DetectedResult,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_usage = Usage(
        uid=current_user.uid,
        vehicle_id=detected.vehicle_id,
        external_id=detected.parking_id,
        entry_time=detected.entry_time,
        log_id=detected.log_id,
        fee_status=False
    )
    db.add(new_usage)
    db.commit()
    db.refresh(new_usage)
    return {"message": "The entry record has been confirmed.", "usage_id": new_usage.usage_id}


# 3. 출차 처리 확정 → Usage 완료 처리 + User 정보 갱신
@router.patch("/exit")
def update_exit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    usage = db.query(Usage).filter(   # 미출차 상태인 usage 중 가장 최근 항목 조회
        Usage.uid == current_user.uid,
        Usage.exit_time == None
    ).order_by(Usage.entry_time.desc()).first()
    if not usage:
        raise HTTPException(status_code=404, detail="There is no Usage to process the car-out.")

    log = fetch_parking_exit(usage.log_id)  # log_id를 인자로 하는 남은 Usage 정보 조회 함수
    if not log or not log.get("출차시간"):
        raise HTTPException(status_code=404, detail="The parking log was not found.")

    usage.exit_time = log["출차시간"]
    usage.total_fee = log.get("총정산요금", 0)
    usage.fee_status = True if log.get("정산상태") in ("완료", "결제") else False

    current_user.service_count += 1
    db.commit()
    db.refresh(usage)
    return {
        "message": "Came out of the parking lot.",
    }
