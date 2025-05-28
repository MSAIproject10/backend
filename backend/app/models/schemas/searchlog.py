# models/schemas/search.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from shared.db import Base

class SearchLog(Base):
    __tablename__ = "search_log_table"

    log_id = Column(Integer, primary_key=True, autoincrement=True) # searchlog 고유 ID

    uid = Column(Integer, ForeignKey("user_table.uid", ondelete="SET NULL"), nullable=True) # 로그인하여 검색한 사용자

    keyword = Column(String(100), nullable=False) # 사용자가 검색한 키워드
    searched_at = Column(DateTime, default=func.now()) # 사용자가 검색한 시간
