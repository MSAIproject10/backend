# shared/services/updater.py
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from shared.db import get_db
from backend.app.models.schemas.parking import ParkingStatus
from shared.services.openopi import fetch_parking_info

def update_parking_status():
    db: Session = next(get_db())
    data_list = fetch_parking_info()

    for item in data_list:
        status = ParkingStatus(
            parking_id=item["parking_id"],
            current_occupancy=item["current_occupancy"],
            last_updated=datetime.now()
        )
        db.add(status)

    db.commit()
