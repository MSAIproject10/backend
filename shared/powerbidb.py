from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

username = os.getenv('MYSQL_USERNAME2')
raw_password = os.getenv('MYSQL_PW2')
password = quote_plus(raw_password)
server = os.getenv('MYSQL_SERVER2')
database = os.getenv('MYSQL_DBNAME2')
driver = os.getenv('MYSQL_DRIVER')

print("[DEBUG] USERNAME:", repr(username))
print("[DEBUG] RAW PASSWORD:", repr(raw_password))
print("[DEBUG] ENCODED PASSWORD:", repr(password))
print("[DEBUG] ENCODED DB:", database)
print("[DEBUG] ENCODED SERVER:", server)

MYSQL_URL2 = (
    f"mssql+pyodbc://{username}:{password}@{server}:1433/{database}"
    f"?driver={driver.replace(' ', '+')}&Encrypt=yes&TrustServerCertificate=no"
)

engine2 = create_engine(MYSQL_URL2, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine2, autoflush=False, autocommit=False)
Base2 = declarative_base()

with engine2.connect() as conn:
    result = conn.execute(text("SELECT GETDATE();"))
    for row in result:
        print("현재 SQL 서버 시간:", row[0])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ParkingLog 테이블에서 ID=1인 레코드의 입차대수와 출차대수를 반환
def fetch_entry_exit() -> tuple[int, int]:
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT 
                    CAST([입차대수] AS INT) AS entry_count,
                    CAST([출차대수] AS INT) AS exit_count
                FROM dbo.ParkingLog
                WHERE ID = 1
            """)
        ).fetchone()

        if result:
            return int(result.entry_count or 0), int(result.exit_count or 0)
        else:
            return 0, 0

    except Exception as e:
        print(f"[ERROR] fetch_entry_exit() 실패: {e}")
        return 0, 0

    finally:
        db.close()

def fetch_capacity() -> int:
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT 
                    CAST([남은주차면적수] AS INT) AS capacity
                FROM dbo.ParkingLog
                WHERE ID = 1
            """)
        ).fetchone()

        if result:
            return int(result.capacity)
        else:
            return -1

    except Exception as e:
        print(f"[ERROR] fetch_capacity 실패: {e}")
        return -1

    finally:
        db.close()