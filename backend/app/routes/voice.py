# Location: backend/app/routes/voice.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.stt import transcribe_audio
from app.services.tts import synthesize_speech
from app.utils.logger import logger
from pydantic import BaseModel, field_validator

router = APIRouter(prefix="/voice")

# Pydantic model for TTS
class TTSRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("text cannot be empty")
        return v

# STT Endpoint
@router.post("/stt")
async def stt_endpoint(file: UploadFile = File(...)):
    logger.info("STT request received")
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file")
        text = transcribe_audio(audio_bytes)
        logger.info(f"STT success, length={len(text)}")
        return {"text": text}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# TTS Endpoint
@router.post("/tts")
async def tts_endpoint(request: TTSRequest):
    logger.info("TTS request received")
    try:
        audio_url = synthesize_speech(request.text)
        logger.info(f"TTS success: {audio_url}")
        return {"audio_url": audio_url}
    except Exception as e:
        logger.error(f"TTS failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
