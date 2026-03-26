# Location: backend/app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    deepgram_api_key: str = ""
    elevenlabs_api_key: str = ""
    groq_api_key: str = ""

    model_config = {"env_file": ".env"}  # pydantic v2 style

settings = Settings()
