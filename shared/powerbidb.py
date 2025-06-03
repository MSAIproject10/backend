from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os, math
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
    with SessionLocal() as db:
        try:
            # ===========주차장을 식별할 수 있는 필드가 PowerBIDB에 존재할 경우 ===========
            # result = db.execute(
            #     text("""
            #         SELECT 
            #             CAST([입차대수] AS INT) AS entry_count,
            #             CAST([출차대수] AS INT) AS exit_count
            #         FROM dbo.ParkingLog
            #         WHERE ID = :id
            #     """),
            #     {"id": parking_log_id} 
            # ).fetchone()  
            result = db.execute(
                text("""
                    SELECT TOP 1
                        CAST([입차대수] AS INT) AS entry_count,
                        CAST([출차대수] AS INT) AS exit_count
                    FROM dbo.ParkingLog
                    ORDER BY [입차시간] DESC
                """)
            ).fetchone()
            if result:
                entry = result.entry_count if result.entry_count is not None else -1
                exit_ = result.exit_count if result.exit_count is not None else -1
                return entry, exit_
            return -1, -1
        except Exception as e:
            print(f"[ERROR] fetch_entry_exit() 실패: {e}")
            return -1, -1

# ID를 인자로 받아 해당 레코드의 남은 주차 면적 수를 반환(parking table용)
def fetch_capacity(parking_log_id: int) -> int:
    db = SessionLocal()
    try:
        # ===========주차장을 식별할 수 있는 필드가 PowerBIDB에 존재할 경우 ===========
        # result = db.execute(
        #     text("""
        #         SELECT 
        #             CAST([남은주차면적수] AS INT) AS capacity
        #         FROM dbo.ParkingLog
        #         WHERE ID = :id
        #     """),
        #     {"id": parking_log_id}
        # ).fetchone()
        result = db.execute(
            text("""
                SELECT TOP 1
                    CAST([남은주차면적수] AS INT) AS capacity
                FROM dbo.ParkingLog
                ORDER BY [입차시간] DESC
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

# 차량번호를 인자로 받아 해당 차량의 입출차 기록을 반환
def fetch_parking_entry(car_number: str):
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT 
                [ID] AS id,
                [입차시간] AS entry_time
            FROM dbo.ParkingLog
            WHERE [차량번호] = :car_number
            ORDER BY [입차시간] DESC
        """), {"car_number": car_number}).fetchall()

        log_list = []
        for row in result:
            log_list.append({
                "ID" : row.id,
                "입차시간": row.entry_time,
                "주차장ID" : "DUMMY1"
            })
        return log_list
    except Exception as e:
        print(f"[ERROR] fetch_parking_logs 실패: {e}")
        return []
    finally:
        db.close()

def fetch_parking_exit(log_id: int):
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT 
                [출차시간] AS exit_time,
                [총정산요금] AS total_fee,
                [정산상태] AS payment_status
            FROM dbo.ParkingLog
            WHERE [ID] = :log_id
        """), {"log_id": log_id}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail=f"ID가 {log_id}인 출차 로그를 찾을 수 없습니다.")

        return {
            "출차시간": result.exit_time,
            "총정산요금": result.total_fee,
            "정산상태": result.payment_status
        }

    except Exception as e:
        print(f"[ERROR] fetch_parking_exit_by_id 실패: {e}")
        return {}
    finally:
        db.close()
