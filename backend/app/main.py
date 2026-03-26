# Location: backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.voice import router as voice_router
from app.utils.logger import logger

app = FastAPI(title="Voice AI Agent")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Prod: specific origins
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Backend server starting...")

# Include routes
app.include_router(voice_router)
logger.info("Routes loaded successfully")
