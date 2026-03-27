from fastapi import APIRouter, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from app.services.stt import transcribe_audio
from app.services.llm import generate_reply
from app.services.tts import synthesize_speech

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str

class TextRequest(BaseModel):
    text: str
    history: list[Message] = []


@router.post("/talk")
async def voice_talk(
    file: UploadFile = File(...),
    history: str = "[]",
):
    import json, base64

    audio_bytes = await file.read()
    filename = file.filename or "audio.webm"
    print(f"Voice talk: file={filename}, size={len(audio_bytes)} bytes")

    if len(audio_bytes) < 1000:
        print("Audio too small, skipping")
        return {"error": "অডিও খুব ছোট। আরেকটু জোরে বলুন।"}

    transcription = transcribe_audio(audio_bytes, filename)
    if not transcription:
        return {"error": "কথা বোঝা যায়নি। আবার বলুন।"}

    print(f"Transcription: '{transcription}'")

    try:
        hist = [Message(**m) for m in json.loads(history)]
    except Exception:
        hist = []

    messages = [{"role": m.role, "content": m.content} for m in hist]
    messages.append({"role": "user", "content": transcription})

    ai_text = generate_reply(messages)
    print(f"AI reply: '{ai_text}'")

    audio_bytes_out = synthesize_speech(ai_text)
    audio_b64 = base64.b64encode(audio_bytes_out).decode() if audio_bytes_out else ""

    if not audio_b64:
        print("Warning: TTS returned empty audio")

    return {
        "transcription": transcription,
        "ai_text": ai_text,
        "audio_base64": audio_b64,
    }


@router.post("/text")
async def text_talk(body: TextRequest):
    import base64
    print(f"Text talk: '{body.text}'")

    messages = [{"role": m.role, "content": m.content} for m in body.history]
    messages.append({"role": "user", "content": body.text})

    ai_text = generate_reply(messages)
    print(f"AI reply: '{ai_text}'")

    audio_bytes = synthesize_speech(ai_text)
    audio_b64 = base64.b64encode(audio_bytes).decode() if audio_bytes else ""

    if not audio_b64:
        print("Warning: TTS returned empty audio")

    return {
        "transcription": body.text,
        "ai_text": ai_text,
        "audio_base64": audio_b64,
    }
