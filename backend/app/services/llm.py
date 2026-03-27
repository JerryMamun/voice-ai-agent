import requests
from app.config import settings

SYSTEM_PROMPT = """তুমি 'জয়' — একজন বাংলাভাষী AI voice assistant।

নির্দেশনা:
- সবসময় বাংলায় কথা বলো। ব্যবহারকারী ইংরেজিতে লিখলেও বাংলায় উত্তর দাও।
- উত্তর সংক্ষিপ্ত রাখো — সর্বোচ্চ ২-৩ বাক্য। এটা voice chat।
- স্বাভাবিক কথোপকথনের ভাষায় বলো, formal বা লেখার ভাষা নয়।
- কোনো bullet point, markdown, বা তালিকা ব্যবহার করো না — শুধু স্বাভাবিক বাক্য।
- বন্ধুসুলভ এবং উষ্ণ স্বরে কথা বলো।"""

GREETING_PROMPT = """ব্যবহারকারী এইমাত্র voice chat শুরু করেছে। তাকে বাংলায় স্বাগত জানাও।
একটি সংক্ষিপ্ত, উষ্ণ greeting দাও — ১ বাক্যে। যেমন: 'হ্যালো! আমি জয়, আপনাকে কীভাবে সাহায্য করতে পারি?'"""


def generate_reply(messages: list) -> str:
    if not settings.groq_api_key:
        return "দুঃখিত, API key সেট করা নেই।"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "max_tokens": 200,
        "temperature": 0.7,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"].strip()
        print(f"LLM reply: '{reply}'")
        return reply
    except Exception as e:
        print(f"Groq LLM error: {e}")
        return "দুঃখিত, এখন উত্তর দিতে পারছি না।"


def generate_greeting() -> str:
    """মাইক চালু হলে প্রথম greeting তৈরি করে।"""
    if not settings.groq_api_key:
        return "হ্যালো! আমি জয়। বলুন, কীভাবে সাহায্য করতে পারি?"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": GREETING_PROMPT},
        ],
        "max_tokens": 60,
        "temperature": 0.8,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        greeting = response.json()["choices"][0]["message"]["content"].strip()
        print(f"Greeting: '{greeting}'")
        return greeting
    except Exception:
        return "হ্যালো! আমি জয়। বলুন, কীভাবে সাহায্য করতে পারি?"
