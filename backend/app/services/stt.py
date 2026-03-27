import requests
from app.config import settings


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Deepgram STT — mobile soh sob format support.
    filename theke content-type auto-detect kore.
    """
    if not settings.deepgram_api_key:
        return "Deepgram API key nei."

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
        "model": "nova-2",
        "language": "multi",
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
        return transcript.strip() if transcript.strip() else ""
    except Exception as e:
        print(f"Deepgram error: {e}")
        return ""