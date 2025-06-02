# shared/services/ingest.py
import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from shared.db import get_db
from backend.app.models.schemas.parking import Parking, ParkingFeePolicy, ParkingSchedulePolicy
from shared.services.openapi import fetch_parking_info
from shared.services.geocode import geocode_address
import time
# lat, lon = geocode_address("서울특별시 종로구 세종로 80-1")
# print(f"위도: {lat}, 경도: {lon}")
def log_time(stage, start):
    print(f"[{stage}] 경과 시간: {time.time() - start:.2f}초")

def normalize_time(value):
    return str(value).zfill(4)

def safe_int(value, default=0):
    try:
        if pd.isna(value) or value in [None, '', 'NaN']:
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default
    
def run_ingest():
    db: Session = next(get_db())

    db.query(ParkingSchedulePolicy).delete()
    db.query(ParkingFeePolicy).delete()
    db.query(Parking).delete()
    print('delete all of db')
    db.commit() # 기존 데이터 삭제

    data_list = fetch_parking_info() # 'row' 리스트로 openAPI 응답 받아오기 

    address_list = [item["ADDR"] for item in data_list]

    geocode_results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(geocode_address, addr): addr for addr in address_list} # Future 객체 -> addr 매핑으로 구성
        for future in as_completed(futures):
            addr, lat, lon = future.result()
            geocode_results[addr] = (lat, lon)

    for i, item in enumerate(data_list):
        print('start of db')
        lat, lon = geocode_results.get(item["ADDR"], (None, None))  # 주소별 위경도 추출
        tel = item.get("TELNO")
        phone_number = tel if tel and str(tel).lower() != "nan" else ""
        status_text = item.get("PRK_STTS_NM", "")
        is_provide_status = status_text == "현재~20분이내 연계데이터 존재(현재 주차대수 표현)"

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
            total_capacity=int(float(item["TPKCT"]))        # 총 주차 가능 대수(float로 응답오기 때문에 float->int) 
        )
        db.add(parking)
        db.flush()  # 변경사항을 DB에 반영하지만, 트랜잭션은 커밋하지 않고 유지하는 함수(FK를 위해 parking_id 확보)

        fee_policy = ParkingFeePolicy(
            parking_id=parking.id,

            # monthly_fee=safe_int(item.get("PRD_AMT")),        # 월 정기권 금액
            # base_fee=safe_int(item.get("BSC_PRK_CRG")),       # 기본 요금
            # base_time_min=safe_int(item.get("BSC_PRK_HR")),   # 기본 시간

            # extra_fee=safe_int(item.get("ADD_PRK_CRG")),      # 추가 요금
            # extra_time_min=safe_int(item.get("ADD_PRK_HR")),  # 추가 시간
            # daily_max_fee=safe_int(item.get("DAY_MAX_CRG")),  # 일 최대 금액
            monthly_fee=int(float(v)) if (v := item.get("PRD_AMT")) and not pd.isna(v) else 0,
            base_fee=int(float(v)) if (v := item.get("BSC_PRK_CRG")) and not pd.isna(v) else 0,
            base_time_min=int(float(v)) if (v := item.get("BSC_PRK_HR")) and not pd.isna(v) else 0,
            extra_fee=int(float(v)) if (v := item.get("ADD_PRK_CRG")) and not pd.isna(v) else 0,
            extra_time_min=int(float(v)) if (v := item.get("ADD_PRK_HR")) and not pd.isna(v) else 0,
            daily_max_fee=int(float(v)) if (v := item.get("DAY_MAX_CRG")) and not pd.isna(v) else 0,

            weekday_pay_type=item.get("PAY_YN_NM", "정보없음"),              # 평일 요금유무
            saturday_pay_type=item.get("SAT_CHGD_FREE_NM", "정보없음"),     # 토요일 요금유무
            holiday_pay_type=item.get("LHLDY_CHGD_FREE_SE_NAME", "정보없음") # 공휴일 요금유무
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
        print(f" - {i}개 주차장 삽입 완료...")

    db.commit()

run_ingest()

