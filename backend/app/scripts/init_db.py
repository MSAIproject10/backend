# scripts/init_db.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))
from shared.db import Base, engine
from backend.app import models

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("데이터베이스 테이블 생성 완료")
