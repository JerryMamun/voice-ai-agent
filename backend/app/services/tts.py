import requests
import io
from app.config import settings

# Groq TTS available voices (PlayAI multilingual — বাংলা সাপোর্ট করে)
# Ref: https://console.groq.com/docs/text-speech
DEFAULT_VOICE = "Cheyenne-PlayAI"   # female, natural, multilingual
# অন্য options: "Atlas-PlayAI", "Briggs-PlayAI", "Orion-PlayAI"


def synthesize_speech(text: str) -> bytes:
    """
    Groq TTS (PlayAI) — text থেকে MP3 audio তৈরি করে।
    বাংলা সহ বহুভাষিক সাপোর্ট। শুধু GROQ_API_KEY লাগে।
    """
    if not settings.groq_api_key:
        print("TTS Error: Groq API key নেই")
        return b""

    url = "https://api.groq.com/openai/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "playai-tts",
        "input": text,
        "voice": DEFAULT_VOICE,
        "response_format": "mp3",
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        audio = response.content
        print(f"TTS (Groq) success: {len(audio)} bytes")
        return audio
    except Exception as e:
        print(f"Groq TTS error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"TTS response: {e.response.text}")
        return b""
