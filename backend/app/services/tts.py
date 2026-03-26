import requests
from app.config import settings


def synthesize_speech(text: str) -> bytes:
    """
    ElevenLabs TTS — text থেকে audio bytes তৈরি করে।
    বাংলা text সাপোর্ট করে (multilingual v2 model)।
    """
    if not settings.elevenlabs_api_key:
        return b""

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}"
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.content  # raw MP3 bytes
    except Exception as e:
        print(f"ElevenLabs error: {e}")
        return b""
