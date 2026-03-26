import requests
from app.config import settings

def text_to_speech(text: str) -> str:
    if not settings.elevenlabs_api_key:
        return "https://dummy-audio-url.com/audio.mp3"

    url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"

    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, headers=headers, json=data)

    # For demo → return fake URL
    return "Audio generated (binary response)"
