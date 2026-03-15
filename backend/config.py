"""
Advanced AI Interview Simulator - Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "AI Interview Simulator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./data/interview_simulator.db"

    # LLM Configuration
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048

    # Speech Processing
    WHISPER_MODEL: str = "base"

    # Interview Settings
    DEFAULT_NUM_QUESTIONS: int = 10
    MAX_FOLLOW_UPS: int = 3
    DIFFICULTY_LEVELS: list[str] = ["easy", "medium", "hard", "expert"]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
