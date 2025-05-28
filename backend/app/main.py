# uvicorn main:app --reload
from fastapi import FastAPI
from routers import auth, user, speech

app = FastAPI()
app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, prefix="/user")
app.include_router(speech.router, prefix="/speech") 
