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

# ID를 인자로 받아 해당 레코드의 입차대수와 출차대수를 반환(parking table용)
def fetch_entry_exit(parking_log_id: int) -> tuple[int, int]:
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT 
                    CAST([입차대수] AS INT) AS entry_count,
                    CAST([출차대수] AS INT) AS exit_count
                FROM dbo.ParkingLog
                WHERE ID = :id
            """),
            {"id": parking_log_id}
        ).fetchone()

        if result:
            return int(result.entry_count or -1), int(result.exit_count or -1)
        else:
            return -1, -1

    except Exception as e:
        print(f"[ERROR] fetch_entry_exit() 실패: {e}")
        return -1, -1

    finally:
        db.close()

# ID를 인자로 받아 해당 레코드의 남은 주차 면적 수를 반환(parking table용)
def fetch_capacity(parking_log_id: int) -> int:
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT 
                    CAST([남은주차면적수] AS INT) AS capacity
                FROM dbo.ParkingLog
                WHERE ID = :id
            """),
            {"id": parking_log_id}
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

# 차량번호를 인자로 받아 해당 차량의 입출차 기록을 반환
def fetch_parking_logs(car_number: str):
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT 
                [차량번호] AS car_number,
                [입차시간] AS entry_time,
                [출차시간] AS exit_time,
                [요금] AS fee,
                [정산상태] AS payment_status,
                [총정산요금] AS total_fee
            FROM dbo.ParkingLog
            WHERE [차량번호] = :car_number
            ORDER BY [입차시간] DESC
        """), {"car_number": car_number}).fetchall()

        log_list = []
        for row in result:
            displayed_fee = row.fee if row.payment_status in ('미완료', '미결제') else row.total_fee
            log_list.append({
                "차량번호": row.car_number,
                "입차시간": row.entry_time,
                "출차시간": row.exit_time,
                "요금": displayed_fee,
                "정산상태": row.payment_status
            })
        return log_list

    except Exception as e:
        print(f"[ERROR] fetch_parking_logs 실패: {e}")
        return []
    
    finally:
        db.close()