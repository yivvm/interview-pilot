"""Application settings.

All configurable values live here, loaded from environment variables
(or a local .env file) via pydantic-settings. Import `settings` anywhere:

    from app.config import settings
    settings.model_name
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Ollama (local LLM runtime) ---
    ollama_host: str = "http://localhost:11434"
    model_name: str = "llama3.1:8b"
    request_timeout: float = 60.0  # seconds to wait on an LLM call

    # --- Database ---
    database_url: str = "sqlite:///./interview_pilot.db"

    # --- Uploads ---
    max_upload_mb: int = 5  # reject resumes larger than this

    # Load values from a .env file in the backend folder if present.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

# Single shared instance imported throughout the app.
settings = Settings()