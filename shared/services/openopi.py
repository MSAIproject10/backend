# shared/services/openapi.py
import requests
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("SEOUL_API_KEY")  # .env에서 로드

def fetch_parking_info(start=1, end=1000) -> List[Dict[str, Any]]:
    url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/json/GetParkingInfo/{start}/{end}/"

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        
        return data.get("GetParkingInfo", {}).get("row", [])
    except Exception as e:
        print(f"[{datetime.now()}] Error fetching parking info: {e}")
        return []

