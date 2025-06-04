# models/schemas/parking_fee_policy.py
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
from shared.db import Base

class FavoriteParking(Base):
    __tablename__ = "favorite_parking"

    id = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("user_table.uid", ondelete="CASCADE"), nullable=False)
    parking_id = Column(Integer, ForeignKey("parking.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("uid", "parking_id", name="uq_user_parking"),) # FavoriteParking 테이블에서 uid와 parking_id의 쌍이 유일(unique)해야 함
    
    user = relationship("User", back_populates="favorite_parkings")