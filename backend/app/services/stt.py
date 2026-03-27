import requests
from app.config import settings


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Deepgram STT — whisper-large model দিয়ে বাংলা সহ সব ভাষা সাপোর্ট করে।
    """
    if not settings.deepgram_api_key:
        print("STT Error: Deepgram API key নেই")
        return ""

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"
    content_type_map = {
        "webm": "audio/webm",
        "mp4":  "audio/mp4",
        "m4a":  "audio/mp4",
        "ogg":  "audio/ogg",
        "wav":  "audio/wav",
        "mp3":  "audio/mpeg",
    }
    content_type = content_type_map.get(ext, "audio/webm")

    url = "https://api.deepgram.com/v1/listen"
    params = {
        "model": "whisper-large",   # বাংলা সহ সব ভাষা সাপোর্ট
        "language": "bn",           # বাংলা প্রাইমারি
        "detect_language": "true",  # অটো ডিটেক্ট ব্যাকআপ
        "smart_format": "true",
        "punctuate": "true",
    }
    headers = {
        "Authorization": f"Token {settings.deepgram_api_key}",
        "Content-Type": content_type,
    }

    try:
        response = requests.post(
            url, params=params, headers=headers,
            data=audio_bytes, timeout=30
        )
        response.raise_for_status()
        result = response.json()
        transcript = (
            result["results"]["channels"][0]["alternatives"][0]["transcript"]
        )
        text = transcript.strip()
        print(f"STT result: '{text}'")
        return text
    except Exception as e:
        print(f"Deepgram STT error: {e}")
        return ""
