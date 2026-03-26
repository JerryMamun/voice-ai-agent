from fastapi import FastAPI
from app.routes.voice import router as voice_router

app = FastAPI(title="Voice AI Agent")

# Voice API router
app.include_router(voice_router, prefix="/voice")
