"""
Application configuration module.

This module provides access to application settings and configuration
from various sources including environment variables and YAML files.
"""
from backend.app.config.settings import Settings, get_settings
from backend.app.config.openai_settings import (
    openai_settings,
    OPENAI_API_KEY,
    OPENAI_MODEL, 
    OPENAI_REASONING_MODEL,
    OPENAI_EMBEDDING_MODEL
)

__all__ = [
    "Settings", 
    "get_settings",
    "openai_settings",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "OPENAI_REASONING_MODEL",
    "OPENAI_EMBEDDING_MODEL"
] 