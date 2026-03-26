# 🎙️ Live Voice AI Agent

বাংলায় কথা বলুন — AI সাথে সাথে voice-এ উত্তর দেবে।

## Features
- 🎤 Browser mic থেকে সরাসরি কথা বলা যায়
- 🗣️ AI বাংলায় voice-এ reply দেয় (ElevenLabs TTS)
- 💬 Conversation history মনে রাখে
- ⌨️ Text chat-ও করা যায়

## Tech Stack
| Layer | Technology |
|-------|-----------|
| STT | Deepgram Nova-2 (বাংলা সাপোর্ট) |
| LLM | Groq — llama-3.3-70b |
| TTS | ElevenLabs multilingual v2 |
| Backend | FastAPI → Render |
| Frontend | Vanilla JS → Vercel |

## Deploy করার ধাপ

### Step 1 — Backend → Render
1. `backend/` ফোল্ডার GitHub-এ push করো
2. Render-এ **Web Service** তৈরি করো
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
3. Environment Variables:
   - `GROQ_API_KEY`
   - `DEEPGRAM_API_KEY`
   - `ELEVENLABS_API_KEY`
   - `ELEVENLABS_VOICE_ID` (optional, default: Rachel)
4. Deploy → URL পাবে: `https://voice-ai-live-backend.onrender.com`

### Step 2 — Frontend → Vercel
1. `frontend/app.js` এর প্রথম লাইনে Render URL বসাও:
   ```js
   const API_URL = "https://voice-ai-live-backend.onrender.com";
   ```
2. `frontend/` ফোল্ডার GitHub push করো
3. Vercel-এ deploy করো (Root Directory: `frontend`)

## Local Development
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # API keys বসাও
uvicorn app.main:app --reload --port 8000
```
`frontend/app.js`-এ: `const API_URL = "http://localhost:8000";`
তারপর `index.html` browser-এ open করো।
