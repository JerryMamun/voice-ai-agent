from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, field_validator

from app.services.stt import speech_to_text
from app.services.llm import generate_reply
from app.services.tts import text_to_speech

router = APIRouter()

class TextRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v

@router.post("/chat")
async def voice_chat(file: UploadFile = File(...)):
    try:
        audio = await file.read()
        if not audio:
            raise HTTPException(status_code=400, detail="Empty audio")

        text = speech_to_text(audio)
        reply = generate_reply(text)
        audio_url = text_to_speech(reply)

        return {
            "user_text": text,
            "ai_reply": reply,
            "audio_url": audio_url
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text")
def text_chat(req: TextRequest):
    reply = generate_reply(req.text)
    audio_url = text_to_speech(reply)

   from app.utils.response import success_response

return success_response({
    "ai_reply": reply,
    "audio_url": audio_url
})
