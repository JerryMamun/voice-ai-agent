# Location: backend/app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    deepgram_api_key: str = ""
    elevenlabs_api_key: str = ""
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379

    model_config = {"env_file": ".env"}  # pydantic v2 style

settings = Settings()
