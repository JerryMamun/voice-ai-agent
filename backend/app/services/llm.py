import requests
from app.config import settings

SYSTEM_PROMPT = """তুমি একজন বন্ধুসুলভ AI assistant। 
ব্যবহারকারী বাংলায় কথা বললে বাংলায় উত্তর দাও, ইংরেজিতে বললে ইংরেজিতে।
উত্তর সংক্ষিপ্ত ও স্বাভাবিক কথোপকথনের মতো রাখো।"""


def generate_reply(messages: list) -> str:
    """
    messages = [{"role": "user"/"assistant", "content": "..."}]
    Conversation history সহ Groq-এ পাঠায়।
    """
    if not settings.groq_api_key:
        return "Groq API key নেই।"

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
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Groq error: {e}")
        return "দুঃখিত, এখন উত্তর দিতে পারছি না।"
