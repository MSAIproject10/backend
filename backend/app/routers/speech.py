# routers/speech.py
from fastapi import APIRouter, UploadFile, File
import shutil
import uuid
from app.services.stt_service import transcribe_audio
import os

router = APIRouter()

@router.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...)):
    temp_filename = f"temp_{uuid.uuid4()}.wav"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = transcribe_audio(temp_filename)
        return {"transcription": text}
    finally:
        os.remove(temp_filename)
