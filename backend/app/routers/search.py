from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from backend.app.models.schemas.parking.parking import ParkingResponse, Parking
from backend.app.models.schemas.searchlog import SearchLog
from shared.db import get_db
from shared.services.collector import run_collect
from shared.services.updater import run_update
import math

router = APIRouter()

@router.get("/popular", response_model=List[str])
def get_popular_keywords(limit: int = 10, db: Session = Depends(get_db)):
    results = (
        db.query(SearchLog.keyword, func.count(SearchLog.keyword).label("count"))
        .group_by(SearchLog.keyword)
        .order_by(func.count(SearchLog.keyword).desc())
        .limit(limit)
        .all()
    )
    return [r.keyword for r in results]

@router.get("/search", response_model=List[ParkingResponse])
def search_parking_by_keyword(
    keyword: str = Query(...),
    uid: int = Query(None),
    db: Session = Depends(get_db)
):
    # 로그 저장
    db.add(SearchLog(uid=uid, keyword=keyword))
    db.commit()

    results = (
        db.query(Parking)
        .filter(Parking.parking_name.ilike(f"%{keyword}%"))
        .all()
    )
    return results

