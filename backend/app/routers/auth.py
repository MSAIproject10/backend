# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from shared.db import get_db
from backend.app.models.schemas.user import UserCreate, UserResponse, User
from backend.app.crud import user_crud

from dotenv import load_dotenv
import os
load_dotenv()

# 환경변수
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()

# Utils
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = user_crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Endpoints
# POST /auth/register HTTP/1.1
# Content-Type: application/json
# {
#   "username": "harim",
#   "password": "abc123"
# }
@router.post("/register", status_code=201, response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    user_data = UserCreate(username=user.username, password=hashed_password)
    return user_crud.create_user(db, user_data)

# Content-Type: application/x-www-form-urlencoded 방식으로 POST
# POST /auth/login HTTP/1.1
# Content-Type: application/x-www-form-urlencoded
# username=harim&password=abc123
@router.post("/login") 
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password") # 401 : Unauthroized

    access_token = create_access_token(data={"sub": user.username}) # access 토큰 생성 
    return {"access_token": access_token, "token_type": "bearer"}
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }

@router.post("/logout")
def logout():
    # JWT 기반은 서버 상태가 없음 → 클라이언트에서 토큰 삭제 필요
    return {"message": "Logout successful. Please delete token on client side."}

@router.get("/me", response_model=UserResponse) # response_mode : 사용자에게 적절히 변환하여 응답
def get_me(current_user = Depends(get_current_user)):
    return current_user