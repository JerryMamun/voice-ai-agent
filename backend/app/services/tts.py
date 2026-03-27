import requests
from app.config import settings

# ElevenLabs Multilingual বাংলা-সক্ষম voice ID গুলো:
# - Aria  : "9BWtsMINqrJLrRacOk9x"  (multilingual, natural)
# - Laura : "FGY2WhTYpPnrIDTdsKH5"  (multilingual, warm)
# - Charlie: "IKne3meq5aSn9XLyUdCD" (multilingual, male)
# config.py তে ELEVENLABS_VOICE_ID এনভায়রনমেন্ট ভেরিয়েবল দিয়ে বদলানো যাবে

DEFAULT_MULTILINGUAL_VOICE = "9BWtsMINqrJLrRacOk9x"  # Aria — multilingual


def synthesize_speech(text: str) -> bytes:
    """
    ElevenLabs TTS — বাংলা text থেকে audio তৈরি করে।
    eleven_multilingual_v2 model ব্যবহার করে (বাংলা সাপোর্ট)।
    """
    if not settings.elevenlabs_api_key:
        print("TTS Error: ElevenLabs API key নেই")
        return b""

    # কনফিগে voice ID থাকলে সেটা, না হলে multilingual default
    voice_id = settings.elevenlabs_voice_id
    if not voice_id or voice_id == "21m00Tcm4TlvDq8ikWAM":  # Rachel = ইংরেজি only
        voice_id = DEFAULT_MULTILINGUAL_VOICE

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",  # বাংলা সাপোর্টেড মডেল
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        print(f"TTS success: {len(response.content)} bytes, voice: {voice_id}")
        return response.content  # raw MP3 bytes
    except Exception as e:
        print(f"ElevenLabs TTS error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"TTS response body: {e.response.text}")
        return b""
