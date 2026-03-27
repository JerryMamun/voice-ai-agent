from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from app.services.stt import transcribe_audio
from app.services.llm import generate_reply, generate_greeting
from app.services.tts import synthesize_speech
import json, base64

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str

class TextRequest(BaseModel):
    text: str
    history: list[Message] = []


@router.post("/greet")
async def greet():
    """মাইক চালু হলে agent নিজে থেকে greeting দেয়।"""
    greeting = generate_greeting()
    audio_bytes = synthesize_speech(greeting)
    audio_b64 = base64.b64encode(audio_bytes).decode() if audio_bytes else ""
    print(f"Greeting sent: '{greeting}', audio: {len(audio_bytes)} bytes")
    return {
        "ai_text": greeting,
        "audio_base64": audio_b64,
    }


@router.post("/talk")
async def voice_talk(
    file: UploadFile = File(...),
    history: str = "[]",
):
    audio_bytes = await file.read()
    filename = file.filename or "audio.webm"
    print(f"Voice talk: file={filename}, size={len(audio_bytes)} bytes")

    if len(audio_bytes) < 500:
        return {"error": "অডিও খুব ছোট। আরেকটু জোরে বলুন।"}

    transcription = transcribe_audio(audio_bytes, filename)
    if not transcription or not transcription.strip():
        return {"error": "কথা বোঝা যায়নি। আবার বলুন।"}

    print(f"Transcription: '{transcription}'")

    try:
        hist = [Message(**m) for m in json.loads(history)]
    except Exception:
        hist = []

    messages = [{"role": m.role, "content": m.content} for m in hist]
    messages.append({"role": "user", "content": transcription})

    ai_text = generate_reply(messages)
    audio_bytes_out = synthesize_speech(ai_text)
    audio_b64 = base64.b64encode(audio_bytes_out).decode() if audio_bytes_out else ""

    return {
        "transcription": transcription,
        "ai_text": ai_text,
        "audio_base64": audio_b64,
    }


@router.post("/text")
async def text_talk(body: TextRequest):
    print(f"Text talk: '{body.text}'")

    messages = [{"role": m.role, "content": m.content} for m in body.history]
    messages.append({"role": "user", "content": body.text})

    ai_text = generate_reply(messages)
    audio_bytes = synthesize_speech(ai_text)
    audio_b64 = base64.b64encode(audio_bytes).decode() if audio_bytes else ""

    return {
        "transcription": body.text,
        "ai_text": ai_text,
        "audio_base64": audio_b64,
    }
