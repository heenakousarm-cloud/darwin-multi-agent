"""
Darwin Multi-Agent System - Configuration Settings
===================================================
Centralized configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Darwin configuration loaded from environment variables."""
    
    # ===================
    # PostHog Configuration
    # ===================
    POSTHOG_API_KEY: str = Field(
        ...,
        description="PostHog Personal API Key (phx_*)"
    )
    POSTHOG_HOST: str = Field(
        default="https://us.posthog.com",
        description="PostHog API host"
    )
    POSTHOG_PROJECT_ID: int = Field(
        default=289987,
        description="PostHog Project ID"
    )
    
    # ===================
    # GitHub Configuration
    # ===================
    GITHUB_TOKEN: str = Field(
        ...,
        description="GitHub Personal Access Token (ghp_*)"
    )
    GITHUB_OWNER: str = Field(
        default="heenakousarm-cloud",
        description="GitHub repository owner"
    )
    GITHUB_REPO: str = Field(
        default="Luxora_ReactNative",
        description="Target repository for fixes"
    )
    
    # ===================
    # Gemini Configuration
    # ===================
    GEMINI_API_KEY: str = Field(
        ...,
        description="Google Gemini API Key (AIza*)"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-2.0-flash",
        description="Gemini model to use"
    )
    
    # ===================
    # MongoDB Configuration
    # ===================
    MONGODB_URI: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI"
    )
    MONGODB_DATABASE: str = Field(
        default="darwin",
        description="MongoDB database name"
    )
    
    # ===================
    # Darwin Settings
    # ===================
    DARWIN_MODE: str = Field(
        default="full",
        description="Pipeline mode: full, analyze, engineer"
    )
    DARWIN_DEBUG: bool = Field(
        default=False,
        description="Enable debug logging"
    )
    
    # ===================
    # Darwin API Settings
    # ===================
    DARWIN_API_KEY: Optional[str] = Field(
        default=None,
        description="API key for Darwin REST API authentication"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Convenience function for quick access
def load_config() -> Settings:
    """Load and return configuration."""
    return get_settings()
