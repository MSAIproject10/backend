import sys, os
from datetime import datetime
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from shared.db import get_db
from shared.services.openapi import fetch_parking_info
from backend.app.models.schemas.parking import Parking, ParkingStatus

STATUS_THRESHOLDS = [
    (0.1, "여유"),
    (0.5, "보통"),
    (0.7, "약간 혼잡"),
    (0.9, "혼잡"),
    (1.0, "매우 혼잡"),
]

def get_status_text(occupancy: float) -> str:
    for threshold, label in STATUS_THRESHOLDS:
        if occupancy <= threshold:
            return label
    return "정보없음"  

def run_update():
    db: Session = next(get_db())
    print(f"[INFO] 🕐 업데이트 시작: {datetime.now()}")

    # 기존 상태 삭제
    deleted = db.query(ParkingStatus).delete()
    db.commit()
    print(f"[INFO] 🧹 ParkingStatus 전체 삭제 완료 (총 {deleted}건)")

    # 실시간 데이터 수집
    api_data = fetch_parking_info()
    print(f"[INFO] 📦 수신된 주차장 실시간 데이터 수: {len(api_data)}")

    api_map = {item["PKLT_CD"]: item for item in api_data}
    target_ids = list(api_map.keys())

    # 2. DB에서 external_id가 있는 것만 조회
    parkings = db.query(Parking).filter(Parking.external_id.in_(target_ids)).all()
    print(f"[INFO] 🔍 DB에서 매칭된 주차장 수: {len(parkings)}")
    matched, skipped = 0, 0

    for parking in parkings:
        pklt_cd = parking.external_id
        item = api_map.get(pklt_cd)

        if not item:
            skipped += 1
            continue

        try:
            now_cnt = int(float(item.get("NOW_PRK_VHCL_CNT", 0.0)))
            total_cnt = int(float(item.get("TPKCT", 0.0)))

            if total_cnt == 0:
                print(f"[SKIP] {parking.parking_name} (용량 0)")
                continue

            occupancy = now_cnt / total_cnt
            status_text = get_status_text(occupancy)

            occ = ParkingStatus(
                parking_id=parking.id,
                occupancy_rate=occupancy,
                current_vehicle_count=now_cnt,
                status_text=status_text
            )
            db.add(occ)
            matched += 1

        except Exception as e:
            print(f"[WARN] {parking.parking_name} 상태 업데이트 실패: {e}")

    db.commit()
    print(f"[INFO] ✅ 업데이트 완료: {datetime.now()}")
    print(f"[INFO] 🧮 성공 {matched}개, 실패 또는 매칭 불가 {skipped}개")
