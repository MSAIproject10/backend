# shared/db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

username = os.getenv('MYSQL_USERNAME')
raw_password = os.getenv('MYSQL_PW')
password = quote_plus(str(raw_password))
server = os.getenv('MYSQL_SERVER')

database = os.getenv('MYSQL_DBNAME')
driver = os.getenv('MYSQL_DRIVER')

print("[DEBUG] USERNAME:", repr(username))
print("[DEBUG] RAW PASSWORD:", repr(raw_password))
print("[DEBUG] ENCODED PASSWORD:", repr(password))
print("[DEBUG] ENCODED DB:", database)
print("[DEBUG] ENCODED SERVER:", server)

MYSQL_URL = (
    f"mssql+pyodbc://{username}:{password}@{server}:1433/{database}"
    f"?driver={driver.replace(' ', '+')}&Encrypt=yes&TrustServerCertificate=no"
)

engine = create_engine(MYSQL_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

with engine.connect() as conn:
    result = conn.execute(text("SELECT GETDATE();"))
    for row in result:
        print("현재 SQL 서버 시간:", row[0])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

