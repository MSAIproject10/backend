from fastapi import FastAPI
from backend.app.routers import auth, parkings, search_logs, usages, vehicles, user

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