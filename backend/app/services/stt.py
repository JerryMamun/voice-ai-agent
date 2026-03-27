import requests
import io
from app.config import settings


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Groq Whisper STT — বাংলা সহ সব ভাষা চমৎকার সাপোর্ট করে।
    Groq API key দিয়েই কাজ করে, আলাদা Deepgram key লাগে না।
    """
    if not settings.groq_api_key:
        print("STT Error: Groq API key নেই")
        return ""

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"
    # Groq Whisper supported formats
    mime_map = {
        "webm": "audio/webm",
        "mp4":  "audio/mp4",
        "m4a":  "audio/mp4",
        "ogg":  "audio/ogg",
        "wav":  "audio/wav",
        "mp3":  "audio/mpeg",
        "flac": "audio/flac",
    }
    mime = mime_map.get(ext, "audio/webm")
    safe_name = f"audio.{ext}"

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
    }

    try:
        files = {
            "file": (safe_name, io.BytesIO(audio_bytes), mime),
        }
        data = {
            "model": "whisper-large-v3",
            "language": "bn",          # বাংলা প্রাইমারি
            "response_format": "json",
            "temperature": "0",
        }
        response = requests.post(
            url, headers=headers, files=files, data=data, timeout=30
        )
        response.raise_for_status()
        result = response.json()
        text = result.get("text", "").strip()
        print(f"STT (Groq Whisper) result: '{text}'")
        return text
    except Exception as e:
        print(f"Groq Whisper STT error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"STT response: {e.response.text}")
        return ""
