from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.voice import router as voice_router

app = FastAPI(title="Voice AI Agent")

# CORS - allow Vercel frontend (and localhost for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Voice API router
app.include_router(voice_router, prefix="/voice")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Voice AI Agent is running"}
