from fastapi import FastAPI
from backend.app.routers import auth, parkings, search_logs, usages, vehicles, user
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:8080",     
    "http://127.0.0.1:8080",
    "https://tenrian-web-app-fnb0djb2dygpbse0.koreasouth-01.azurewebsites.net",  
    "https://lively-water-0a1c2c800.6.azurestaticapps.net",      # Flutter Web 개발 서버
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # 허용할 출처 목록
    allow_credentials=True,            # credential 허용 
    allow_methods=["*"],               # 허용할 HTTP 메서드 (GET, POST 등)
    allow_headers=["*"],               # 허용할 요청 헤더
)

@app.get("/")
def read_root():
    return {"message": "API test!"}

app.include_router(auth.router, prefix="/auth")
app.include_router(usages.router, prefix="/usages")
app.include_router(parkings.router, prefix="/parkings")
app.include_router(vehicles.router, prefix="/vehicles")
app.include_router(search_logs.router, prefix="/search-logs")
app.include_router(user.router, prefix="/user")

