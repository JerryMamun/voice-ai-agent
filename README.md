# Voice AI Agent

একটি শিক্ষামূলক Voice AI Agent — FastAPI (Render) + Vanilla JS (Vercel)।

## Architecture

```
Frontend (Vercel)  →  Backend (Render)  →  Groq LLM API
     HTML/JS              FastAPI              llama-3.3-70b
```

## API Endpoints

| Method | Endpoint           | কাজ                              |
|--------|--------------------|----------------------------------|
| GET    | `/`                | Health check                     |
| POST   | `/voice/text`      | Text পাঠাও, AI reply পাও         |
| POST   | `/voice/transcribe`| Audio আপলোড করো, text পাও        |
| POST   | `/voice/voice`     | Audio → STT → LLM → reply পাও   |

## Deploy করার ধাপ

### Step 1: Backend → Render

1. GitHub-এ `backend/` ফোল্ডারটি push করো
2. [render.com](https://render.com) এ নতুন **Web Service** তৈরি করো
3. Repository connect করো, root directory = `backend`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
6. Environment Variables যোগ করো:
   - `GROQ_API_KEY` = তোমার Groq API key ([console.groq.com](https://console.groq.com))
   - `DEEPGRAM_API_KEY` = (optional)
   - `ELEVENLABS_API_KEY` = (optional)
7. Deploy করো — URL পাবে: `https://voice-ai-backend.onrender.com`

### Step 2: Frontend → Vercel

1. `frontend/app.js` এর প্রথম লাইনে Render URL বসাও:
   ```js
   const API_URL = "https://voice-ai-backend.onrender.com";
   ```
2. GitHub-এ `frontend/` ফোল্ডারটি push করো
3. [vercel.com](https://vercel.com) এ নতুন Project তৈরি করো
4. Root directory = `frontend` সেট করো
5. Framework = **Other** রাখো
6. Deploy করো!

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env   # এবং API key বসাও
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
# index.html সরাসরি browser-এ open করো অথবা VS Code Live Server ব্যবহার করো
# app.js-এ API_URL = "http://localhost:8000" করো
```
