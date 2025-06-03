from fastapi import APIRouter
from shared.services.collector import run_collect
from shared.services.updater import run_update

router = APIRouter()

@router.post("/sync", status_code=200)
def trigger_data_sync():
    run_collect()
    return {"message": "Parking data sync completed."}

@router.post("/status", status_code=200)
def trigger_status_update():
    run_update()
    return {"message": "Parking status update completed."}
