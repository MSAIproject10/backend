# 사용자 단위로 책임이 나뉘는 경우 router로 나누기 
# routers/user.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shared.db import get_db
from app.crud import user_crud
from app.models.schemas.user import UserResponse
from .auth import get_current_user

router = APIRouter()

# @router.patch("/update-profile", response_model=UserResponse)
# def update_profile(updated: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     return user_crud.update_user(db, current_user.uid, updated)

# @router.delete("/delete")
# def delete_account(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     return user_crud.delete_user(db, current_user.uid)
