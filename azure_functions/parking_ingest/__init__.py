# azure_functions/parking_ingest/__init__.py
import datetime
import logging
import azure.functions as func
from shared.services.ingest import run_ingest  # Shared logic import

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info(f"[parking_ingest] Function triggered at {utc_timestamp}")
    run_ingest()