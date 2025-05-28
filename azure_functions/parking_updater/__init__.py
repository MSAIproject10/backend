# azure_functions/parking_updater/__init__.py
import datetime
import logging
import azure.functions as func
from shared.services.updater import run_update  # Shared logic import

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info(f"[parking_updater] Function triggered at {utc_timestamp}")
    run_update()