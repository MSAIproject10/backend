# uvicorn main:app --reload
from fastapi import FastAPI
from backend.app.routers import auth, parking, vehicle, usage, search

app = FastAPI()
app.include_router(auth.router, prefix="/auth")
app.include_router(usage.router, prefix="/usage")
app.include_router(parking.router, prefix="/parking")
app.include_router(vehicle.router, prefix="/vehicle")
app.include_router(search, prefix="/search")
