from fastapi import APIRouter, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from app.services.stt import transcribe_audio
from app.services.llm import generate_reply
from app.services.tts import synthesize_speech

router = APIRouter()


# ── Request / Response models ──────────────────────────────────────────────────

class Message(BaseModel):
    role: str   # "user" or "assistant"
    content: str

class VoiceRequest(BaseModel):
    history: list[Message] = []

class TextRequest(BaseModel):
    text: str
    history: list[Message] = []


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/talk")
async def voice_talk(
    file: UploadFile = File(...),
    history: str = "[]",   # JSON string of history (multipart workaround)
):
    """
    Full live voice pipeline:
    audio → Deepgram STT → Groq LLM → ElevenLabs TTS → MP3 bytes

    Returns JSON: { transcription, ai_text, audio_base64 }
    """
    import json, base64

    audio_bytes = await file.read()

    # 1. STT
    transcription = transcribe_audio(audio_bytes)
    if not transcription:
        return {"error": "কথা বোঝা যায়নি, আবার বলুন।"}

    # 2. Build message history
    try:
        hist = [Message(**m) for m in json.loads(history)]
    except Exception:
        hist = []

    messages = [{"role": m.role, "content": m.content} for m in hist]
    messages.append({"role": "user", "content": transcription})

    # 3. LLM
    ai_text = generate_reply(messages)

    # 4. TTS
    audio_bytes_out = synthesize_speech(ai_text)
    audio_b64 = base64.b64encode(audio_bytes_out).decode() if audio_bytes_out else ""

    return {
        "transcription": transcription,
        "ai_text": ai_text,
        "audio_base64": audio_b64,
    }


@router.post("/text")
async def text_talk(body: TextRequest):
    """
    Text input pipeline:
    text → Groq LLM → ElevenLabs TTS → base64 audio

    History সহ কাজ করে।
    """
    import base64

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
