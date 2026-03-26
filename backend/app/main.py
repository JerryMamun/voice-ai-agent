from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.voice import router as voice_router

app = FastAPI(title="Live Voice AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Vercel URL restrict করতে চাইলে এখানে বসাও
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router, prefix="/voice")

@app.get("/")
def health():
    return {"status": "ok", "message": "Live Voice AI Agent চালু আছে ✅"}
