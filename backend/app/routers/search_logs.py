from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.app.models.schemas.parking.parking import ParkingResponse, Parking
from backend.app.models.schemas.searchlog import SearchLog
from backend.app.models.schemas.user import User
from backend.app.routers.auth import get_current_user
from shared.db import get_db

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

@router.post("/search", response_model=List[ParkingResponse])
def search_parking_by_keyword(
    keyword: str = Body(..., embed=True),  # JSON body에서 {"keyword": "검색어"} 형식으로 받음
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword must not be empty.")
    
    db.add(SearchLog(uid=current_user.uid, keyword=keyword))
    db.commit()

    results = (
        db.query(Parking)
        .filter(Parking.parking_name.ilike(f"%{keyword}%"))
        .all()
    )
    return results



