# scripts/init_db.py
from shared.db import Base, engine
from backend.app import models

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("데이터베이스 테이블 생성 완료")
