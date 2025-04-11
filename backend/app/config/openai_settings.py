"""
Configuration settings for OpenAI models and Agent SDK.

This module provides configuration for OpenAI models used across the application,
with support for environment-based overrides.
"""
import os
from pydantic import Field
from pydantic_settings import BaseSettings

class OpenAISettings(BaseSettings):
    """OpenAI API settings configuration."""
    api_key: str = Field(default=os.environ.get("OPENAI_API_KEY", ""), description="OpenAI API key")
    organization: str = Field(default=os.environ.get("OPENAI_ORGANIZATION", ""), description="OpenAI organization ID")
    
    # Model settings
    model: str = Field(
        default=os.environ.get("OPENAI_MODEL", "gpt-4o"), 
        description="Default OpenAI model for general tasks"
    )
    reasoning_model: str = Field(
        default=os.environ.get("OPENAI_REASONING_MODEL", "gpt-4o"), 
        description="OpenAI model for reasoning and evaluation tasks"
    )
    embedding_model: str = Field(
        default=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        description="OpenAI model for embeddings"
    )
    
    # Agent SDK settings
    agents_enabled: bool = Field(
        default=os.environ.get("OPENAI_AGENTS_ENABLED", "True").lower() in ("true", "1", "t"),
        description="Whether to enable the OpenAI Agents SDK"
    )
    
    # Tool settings
    tools_enabled: bool = Field(
        default=os.environ.get("OPENAI_TOOLS_ENABLED", "True").lower() in ("true", "1", "t"),
        description="Whether to enable OpenAI function tools"
    )
    
    # Performance settings
    timeout: int = Field(
        default=int(os.environ.get("OPENAI_TIMEOUT", "120")),
        description="Timeout for OpenAI API calls in seconds"
    )
    max_retries: int = Field(
        default=int(os.environ.get("OPENAI_MAX_RETRIES", "3")),
        description="Maximum number of retries for failed API calls"
    )
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_prefix = "OPENAI_"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields without validation errors

# Create and export settings instance
openai_settings = OpenAISettings()

# Convenience exports
OPENAI_API_KEY = openai_settings.api_key
OPENAI_MODEL = openai_settings.model
OPENAI_REASONING_MODEL = openai_settings.reasoning_model
OPENAI_EMBEDDING_MODEL = openai_settings.embedding_model 