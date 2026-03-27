import requests
from app.config import settings

SYSTEM_PROMPT = """তুমি একজন বন্ধুসুলভ AI assistant। নাম 'জয়'।
ব্যবহারকারী বাংলায় কথা বললে অবশ্যই বাংলায় উত্তর দাও।
ইংরেজিতে বললে ইংরেজিতে, মিশিয়ে বললে বাংলায়।
উত্তর সংক্ষিপ্ত রাখো — ২-৩ বাক্যের মধ্যে।
স্বাভাবিক কথোপকথনের ভাষায় কথা বলো, বেশি formal না।"""


def generate_reply(messages: list) -> str:
    """
    messages = [{"role": "user"/"assistant", "content": "..."}]
    Groq LLaMA দিয়ে বাংলা উত্তর তৈরি করে।
    """
    if not settings.groq_api_key:
        print("LLM Error: Groq API key নেই")
        return "দুঃখিত, API key সেট করা নেই।"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "max_tokens": 300,
        "temperature": 0.7,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"].strip()
        print(f"LLM reply: '{reply[:80]}...'")
        return reply
    except Exception as e:
        print(f"Groq LLM error: {e}")
        return "দুঃখিত, এখন উত্তর দিতে পারছি না।"
