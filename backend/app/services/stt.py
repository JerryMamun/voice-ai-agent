import requests
from app.config import settings

def speech_to_text(audio_bytes: bytes) -> str:
    if not settings.deepgram_api_key:
        return "Simulated speech text"

    url = "https://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {settings.deepgram_api_key}",
        "Content-Type": "audio/wav"
    }

    response = requests.post(url, headers=headers, data=audio_bytes)

    try:
        return response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
    except:
        return "Could not transcribe"
