from fastapi import FastAPI
from backend.app.routers import auth, parkings, search_logs, usages, vehicles, user
from shared.services.scheduler import start_scheduler
import time

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API test!"}
app.include_router(auth.router, prefix="/auth")
app.include_router(usages.router, prefix="/usages")
app.include_router(parkings.router, prefix="/parkings")
app.include_router(vehicles.router, prefix="/vehicles")
app.include_router(search_logs.router, prefix="/search-logs")
app.include_router(user.router, prefix="/user")

time.sleep(5)
start_scheduler()

