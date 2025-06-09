import sys, os, logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_ 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from shared.db import get_db
from shared.services.openapi import fetch_parking_info
from shared.powerbidb import fetch_entry_exit, fetch_capacity
from backend.app.models.schemas.parking import Parking, ParkingStatus
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

STATUS_THRESHOLDS = [
    (0.1, "여유"),(0.5, "보통"),(0.7, "약간 혼잡"),(0.9, "혼잡"),(1.0, "매우 혼잡"),
]

def get_status_text(occupancy: float) -> str:
    for threshold, label in STATUS_THRESHOLDS:
        if occupancy <= threshold:
            return label
    print()
    return "정보없음"  

def run_update():
    try:
        logger.info("ParkingStatus 업데이트 시작")
        db: Session = next(get_db())
        with db.begin():
            deleted = db.query(ParkingStatus).delete()
            # db.commit()
            logger.info(f"ParkingStatus 삭제 완료 (총 {deleted}건)✅")

            api_data = fetch_parking_info() # 실시간 데이터 수집
            logger.info(f"수신된 주차장 실시간 데이터 수: {len(api_data)}")
            api_map = {item["PKLT_CD"]: item for item in api_data}
            target_ids = list(api_map.keys())

            parkings = db.query(Parking).filter( # DB에서 external_id가 있는 것만 조회
                and_(
                    Parking.external_id.in_(target_ids),
                    Parking.provide_status == True
                )
            ).all()
            logger.info(f"DB에서 매칭된 주차장 수: {len(parkings)}")

            dummy_parkings = db.query(Parking).filter(Parking.external_id.like("DUMMY%")).all() # DUMMY로 시작하는 데이터들 가져오기 
            if dummy_parkings:
                parkings.extend(dummy_parkings)
                logger.info("DUMMY 주차장 추가됨 ✅")

            logger.info(f"추가된 주차장 수: {len(parkings)}")
            for idx, parking in enumerate(parkings):
                logger.info(f"🔁 Processing [{idx + 1}/{len(parkings)}] {parking.parking_name} (external_id={parking.external_id})")

                pklt_cd = parking.external_id
                item = api_map.get(pklt_cd)

                if not item and not parking.ocr_linked:
                    logger.warning(f"⚠️ API 데이터 없음, OCR 연동도 안됨 → skip: {pklt_cd}")
                    continue
                try:
                    if parking.ocr_linked:
                        logger.info(f"[DEBUG] {parking.parking_name}는 ocr_linked=True 입니다.")
                        logger.info(f"[DEBUG] Parking external_id : {parking.external_id}")
                        dummy_id = int(parking.external_id.replace("DUMMY", ""))
                        logger.info(f"[DEBUG] Dummy id : {dummy_id}")
                        now_cnt = fetch_capacity(dummy_id)
                        entry, exit = fetch_entry_exit(dummy_id)
                        logger.info(f"[DEBUG] fetch_entry_exit() = {entry}, {exit},  fetch_capacity() = {now_cnt}")
                        logger.info(f"↙️ {parking.parking_name}: OCR 연동됨 → 남은 주차면수 = {now_cnt}")
                    else:
                        now_cnt = int(float(item.get("NOW_PRK_VHCL_CNT", 0.0)))
                        entry, exit = -1, -1
                        # logger.info(f"❇️{parking.parking_name}: 공공API → 현재 주차 차량 수 = {now_cnt}")

                    total_cnt = parking.total_capacity
                    if total_cnt == 0:
                        logger.warning(f"[SKIP] {parking.parking_name} (총 주차면 0)")
                        continue

                    occupancy = now_cnt / total_cnt
                    status_text = get_status_text(occupancy)
                    logger.info(f"{parking.parking_name}: 총 주차면={parking.total_capacity}, 남은 주차면={now_cnt},혼잡도={status_text}, 입차={entry}, 출차={exit}")

                    occ = ParkingStatus(
                        parking_id=parking.id,
                        current_occupancy=now_cnt,
                        last_updated= datetime.now(),
                        congestion_level = status_text,
                        entry_count=entry, 
                        exit_count=exit,
                    )
                    db.add(occ)

                except Exception as e:
                    logger.warning(f"[ERROR] {parking.parking_name} 상태 업데이트 실패: {e}")
        logger.info(f"✅ 업데이트 완료: {datetime.now()}")
    except Exception as e:
        logger.error(f"run_collect 내부 예외 발생: {e}", exc_info=True)

# run_update()