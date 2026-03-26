import requests
from app.config import settings


def transcribe_audio(audio_bytes: bytes, language: str = "bn") -> str:
    """
    Deepgram STT — বাংলা সহ যেকোনো ভাষা সাপোর্ট করে।
    language='bn' মানে বাংলা, 'multi' মানে auto-detect।
    """
    if not settings.deepgram_api_key:
        return "Deepgram API key নেই।"

    url = "https://api.deepgram.com/v1/listen"
    params = {
        "model": "nova-2",
        "language": language,
        "smart_format": "true",
        "punctuate": "true",
    }
    headers = {
        "Authorization": f"Token {settings.deepgram_api_key}",
        "Content-Type": "audio/webm",
    }

    try:
        response = requests.post(url, params=params, headers=headers, data=audio_bytes, timeout=30)
        response.raise_for_status()
        result = response.json()
        transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
        return transcript.strip() if transcript.strip() else ""
    except Exception as e:
        print(f"Deepgram error: {e}")
        return ""
