"""
Configuration module for the FastAPI backend.
Manages environment variables and application settings.
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    groq_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    
    # LLM Configuration
    groq_model: str = "llama-3.1-8b-instant"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # Search Configuration
    tavily_max_results: int = 5
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS Configuration
    cors_origins: list = ["*"]
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the current settings instance."""
    return settings