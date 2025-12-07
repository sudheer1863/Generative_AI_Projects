"""Configuration settings for Meeting Steward A2A."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Ollama Configuration
    ollama_host: str = Field(default="http://localhost:11434", description="Ollama API endpoint")
    model_name: str = Field(default="llama3.2", description="Default LLM model name")
    
    # Database Configuration
    db_path: str = Field(default="data/db.sqlite3", description="SQLite database path")
    
    # Audio Processing
    whisper_model: str = Field(default="base", description="Whisper model size (tiny/base/small/medium/large)")
    sample_rate: int = Field(default=16000, description="Audio sample rate for processing")
    use_whisperx: bool = Field(default=True, description="Use WhisperX for diarization")
    
    # Optional HuggingFace token
    hf_token: Optional[str] = Field(default=None, description="HuggingFace token for pyannote models")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/meeting_steward.log", description="Log file path")
    
    # LLM Parameters
    default_temperature: float = Field(default=0.1, description="Default temperature for LLM calls")
    max_retries: int = Field(default=3, description="Max retries for LLM calls")
    
    @property
    def db_url(self) -> str:
        """Get SQLAlchemy database URL."""
        return f"sqlite:///{self.db_path}"
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            Path(self.db_path).parent,
            Path(self.log_file).parent,
            "data/uploads",
            "data/models",
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
