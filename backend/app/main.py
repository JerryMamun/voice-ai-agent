from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.voice import router as voice_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router, prefix="/voice")

@app.get("/")
def root():
    return {"status": "Voice AI Agent Running"}
