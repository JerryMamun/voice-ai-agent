from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from app.services.stt import transcribe_audio
from app.services.llm import generate_reply
from app.utils.response import success_response, error_response
from app.utils.helpers import is_empty

router = APIRouter()


class TextRequest(BaseModel):
    text: str


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Accepts an audio file and returns transcribed text (placeholder)."""
    content = await file.read()
    text = transcribe_audio(content)
    return success_response({"text": text})


@router.post("/text")
async def text_to_reply(body: TextRequest):
    """Accepts plain text, sends to LLM, returns AI reply."""
    if is_empty(body.text):
        return error_response("Text cannot be empty")
    reply = generate_reply(body.text)
    return success_response({"ai_reply": reply})


@router.post("/voice")
async def voice_to_reply(file: UploadFile = File(...)):
    """Full pipeline: audio → STT → LLM → returns AI reply."""
    content = await file.read()
    text = transcribe_audio(content)
    if is_empty(text):
        return error_response("Could not transcribe audio")
    reply = generate_reply(text)
    return success_response({"transcription": text, "ai_reply": reply})
