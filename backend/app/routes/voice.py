from fastapi import APIRouter, UploadFile, File
from app.services.stt import transcribe_audio

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    content = await file.read()
    text = transcribe_audio(content)
    return {"text": text}
