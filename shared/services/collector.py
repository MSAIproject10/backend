# shared/services/ingest.py
import sys, os, logging
from datetime import datetime
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from shared.db import get_db
from backend.app.models.schemas.parking import Parking, ParkingFeePolicy, ParkingSchedulePolicy, ParkingStatus
from shared.services.openapi import fetch_parking_info
from shared.services.geocode import geocode_address

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def normalize_time(value):
    return str(value).zfill(4)
    
def parse_pay_type(value: str) -> bool:
    return str(value).strip() == "유료"

# 엑셀파일입력으로 사설 주차장 등록(일반화)
def insert_dummy_ocr_parking(db: Session):
    csv_path='../file/private_parking.csv'
    logger.info(f"CSV 파일에서 더미 주차장 데이터 로딩: {csv_path}")
    df = pd.read_csv(csv_path)
    for idx, row in df.iterrows():
        try:
            addr = row["address"]
            _, lat, lon = geocode_address(addr)
            parking = Parking(
                external_id=row["external_id"],
                parking_name=row["parking_name"],
                address=addr,
                parking_type=row["parking_type"],
                phone_number=row["phone_number"],
                latitude=lat, # 위도
                longitude=lon, # 경도
                operation_type=row["operation_type"],
                provide_status=True,
                total_capacity=int(row["total_capacity"]),
                ocr_linked=True
            )
            db.add(parking)
            db.flush()

            dummy_fee = ParkingFeePolicy(
                parking_id=parking.id,
                monthly_fee=row["monthly_fee"],
                base_fee=row["base_fee"],
                base_time_min=row["base_time_min"],
                extra_fee=row["extra_fee"],
                extra_time_min=row["extra_time_min"],
                daily_max_fee=row["daily_max_fee"],
                weekday_pay_type=row["weekday_pay_type"],
                saturday_pay_type=row["saturday_pay_type"],
                holiday_pay_type=row["holiday_pay_type"],
            )
            db.add(dummy_fee)

            dummy_schedule = ParkingSchedulePolicy(
                parking_id=parking.id,
                weekday_open=row["weekday_open"],
                weekday_close=row["weekday_close"],
                weekend_open=row["weekend_open"],
                weekend_close=row["weekend_close"],
                holiday_open=row["holiday_open"],
                holiday_close=row["holiday_close"],
            )
            db.add(dummy_schedule)
        except Exception as e:
            logger.error("e")

def run_collect():
    logger.info("주차장 데이터 수집 시작")
    db: Session = next(get_db())

    db.query(ParkingStatus).delete() # Parking Status는 참조 관계이므로 미리 삭제해야함
    db.query(ParkingSchedulePolicy).delete()
    db.query(ParkingFeePolicy).delete()
    db.query(Parking).delete()
    db.commit()
    logger.info("기존 parking 테이블 삭제 완료 ✅")

    data_list = fetch_parking_info()
    logger.info(f"OpenAPI로부터 {len(data_list)}건 데이터 수신 ✅")

    address_list = [item["ADDR"] for item in data_list]
    geocode_results = {}

    logger.info("주소 -> 위도/경도 변환")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(geocode_address, addr): addr for addr in address_list} # Future 객체 -> addr 매핑으로 구성
        for future in as_completed(futures):
            try:
                addr, lat, lon = future.result()
                geocode_results[addr] = (lat, lon)
            except Exception as e:
                logger.warning(f"지오코딩 실패: {futures[future]} → {e}")

    for i, item in enumerate(data_list):
        try:
            lat, lon = geocode_results.get(item["ADDR"], (None, None))  # 주소별 위경도 추출

            tel = item.get("TELNO")
            phone_number = tel if tel and str(tel).lower() != "nan" else ""
            is_provide_status = item.get("PRK_STTS_NM", "") == "현재~20분이내 연계데이터 존재(현재 주차대수 표현)"

            parking = Parking(
                external_id =item["PKLT_CD"],
                parking_name=item["PKLT_NM"],                   # 주차장 이름
                address=item["ADDR"],                           # 주소
                parking_type=item["PRK_TYPE_NM"],               # 주차장 유형 (ex.노외 주차장)
                phone_number=phone_number,                      # 전화번호

                latitude=lat,                                   # 위도
                longitude=lon,                                  # 경도
                
                operation_type=item["OPER_SE_NM"],              # 운영 유형 (ex. 시간제 주차장)
                provide_status=is_provide_status,           # 현황 연계 여부(ex. 미연계중)
                total_capacity=int(float(item["TPKCT"])),        # 총 주차 가능 대수(float로 응답오기 때문에 float->int) 
                ocr_linked=False
            )
            db.add(parking)
            db.flush()  # 변경사항을 DB에 반영하지만, 트랜잭션은 커밋하지 않고 유지하는 함수(FK를 위해 parking_id 확보)

            fee_policy = ParkingFeePolicy(
                parking_id=parking.id,

                monthly_fee=int(float(v)) if (v := item.get("PRD_AMT")) and not pd.isna(v) else -1, # NaN일 때 -1로 표기 
                base_fee=int(float(v)) if (v := item.get("BSC_PRK_CRG")) and not pd.isna(v) else -1,
                base_time_min=int(float(v)) if (v := item.get("BSC_PRK_HR")) and not pd.isna(v) else -1,
                extra_fee=int(float(v)) if (v := item.get("ADD_PRK_CRG")) and not pd.isna(v) else -1,
                extra_time_min=int(float(v)) if (v := item.get("ADD_PRK_HR")) and not pd.isna(v) else -1,
                daily_max_fee=int(float(v)) if (v := item.get("DAY_MAX_CRG")) and not pd.isna(v) else -1,

                weekday_pay_type=parse_pay_type(item.get("PAY_YN_NM")),
                saturday_pay_type=parse_pay_type(item.get("SAT_CHGD_FREE_NM")),
                holiday_pay_type=parse_pay_type(item.get("LHLDY_CHGD_FREE_SE_NAME")),
            )
            db.add(fee_policy)

            schedule_policy = ParkingSchedulePolicy(
                parking_id=parking.id,

                weekday_open=normalize_time(item.get("WD_OPER_BGNG_TM", 0)),
                weekday_close=normalize_time(item.get("WD_OPER_END_TM", 2400)),

                weekend_open=normalize_time(item.get("WE_OPER_BGNG_TM", 0)),
                weekend_close=normalize_time(item.get("WE_OPER_END_TM", 2400)),

                holiday_open=normalize_time(item.get("LHLDY_OPER_BGNG_TM", 0)),
                holiday_close=normalize_time(item.get("LHLDY_OPER_END_TM", 2400)),
            )
            db.add(schedule_policy)
            logger.info(f"[{i + 1}/{len(data_list)}] '{parking.parking_name}' 주차장 등록 완료 ✅")
        except Exception as e:
            logger.error(f"[{i + 1}] 에러 발생: {e}", exc_info=True)
    logger.info("차량 탐지 시스템용 더미 데이터 추가 ✅")
    insert_dummy_ocr_parking(db)
    db.commit()
    logger.info("주차장 데이터 커밋 완료 ✅")
run_collect()