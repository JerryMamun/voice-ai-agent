# 🎤 Voice AI Agent

A real-time AI voice assistant built with:

* Speech-to-Text → Deepgram
* LLM → Groq (LLaMA 3.3)
* Text-to-Speech → ElevenLabs

---

## 🚀 Features

* 🎤 Voice input (audio → text)
* 🤖 AI conversation (Groq LLM)
* 🔊 Voice response (text → speech)
* 🌐 Web-based UI
* ⚡ FastAPI backend (Render ready)

---

## 🧠 Architecture

User → Backend API → STT → LLM → TTS → Response

---

## 📦 Setup (Step-by-Step)

### 1. Clone Repo

```bash
git clone https://github.com/JerryMamun/voice-ai-agent.git
cd voice-ai-agent/backend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Create `.env` file:

```
DEEPGRAM_API_KEY=your_key
GROQ_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
```

### 4. Run Server

```bash
uvicorn app.main:app --reload
```

Server runs at:

```
http://localhost:8000
```

---

## 🔌 API Usage

### 🔹 Text Chat

```bash
curl -X POST http://localhost:8000/voice/text \
-H "Content-Type: application/json" \
-d '{"text": "Hello"}'
```

### 🔹 Voice Chat

```bash
curl -X POST http://localhost:8000/voice/chat \
-F "file=@audio.wav"
```

---

## ⚠️ Notes

* Without API keys → system runs in simulation mode
* ElevenLabs currently returns placeholder audio
* For production → streaming required

---

## 📁 Project Structure

backend/
frontend/

---

## 🧪 Testing

Basic manual testing via curl/Postman supported.

---

## 📜 License

MIT License

---

## 🤝 Contributing

Pull requests are welcome. Open an issue first for major changes.

---

## ⭐ Support

If you like this project, give it a star ⭐
