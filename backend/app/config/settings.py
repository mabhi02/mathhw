from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import os
import logging
from typing import Dict, List, Optional, Any, Callable
from watchfiles import awatch
import asyncio

from backend.app.config.yaml_loader import get_config_loader, ConfigLoader
from backend.app.config.schemas import (
    SettingsConfig,
    AgentDefinitionsConfig,
    QuestionRulesConfig,
    LLMProviderEnum
)

# Setup logger
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "ABTS Unified Generator"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    API_VERSION: str = "v1"
    
    # Paths for configuration files
    CONFIG_DIR: str = "config"
    AGENT_DEFS_FILE: str = "agent_definitions.yml"
    SETTINGS_FILE: str = "settings.yml"
    QUESTION_RULES_FILE: str = "question_rules.yml"
    PIPELINES_DIR: str = "pipelines"
    TEMPLATE_PATH: str = "backend/app/templates"
    STORAGE_DIR: str = "storage"
    
    # CORS settings
    CORS_ORIGINS: str = "*"
    
    # Security settings
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "development_secret_key")
    
    # Database settings
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", "sqlite:///./abts_unified_generator.db"
    )
    
    # Redis cache settings
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "redis")  # Changed from localhost to redis for Docker
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.environ.get("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.environ.get("REDIS_PASSWORD")
    REDIS_PREFIX: str = os.environ.get("REDIS_PREFIX", "abts")
    
    # LLM provider settings (will be overridden by settings.yml)
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o"
    
    # Callbacks for config change notifications
    _config_change_callbacks: Dict[str, List[Callable]] = {}
    
    # Hot reload flag
    ENABLE_HOT_RELOAD: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in the settings

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._config_loader = get_config_loader(self.CONFIG_DIR)
        self._cached_config = {}
        self._hot_reload_task = None
    
    async def _watch_config_files(self):
        """Watch config files for changes and reload when needed"""
        config_dir = os.path.abspath(self.CONFIG_DIR)
        logger.info(f"Watching config directory: {config_dir}")
        
        try:
            async for changes in awatch(config_dir):
                logger.info(f"Config file changes detected: {changes}")
                changed_files = self._config_loader.reload_all()
                
                # Clear cached configs
                for filename in changed_files:
                    if filename in self._cached_config:
                        del self._cached_config[filename]
                
                # Notify callbacks
                for filename in changed_files:
                    for callback in self._config_change_callbacks.get(filename, []):
                        try:
                            callback()
                        except Exception as e:
                            logger.error(f"Error in config change callback: {str(e)}")
        except TypeError as e:
            # Handle the case where structlog has an issue with tuple deletion
            # This is a workaround for the error in the watchfiles library with structlog
            if "'tuple' object does not support item deletion" in str(e):
                logger.error("Known structlog-watchfiles compatibility issue encountered. Continuing operation.")
            else:
                logger.error(f"TypeError in file watcher: {str(e)}")
        except Exception as e:
            logger.error(f"Error in file watcher: {str(e)}")
    
    def start_hot_reload(self):
        """Start watching config files for changes"""
        if not self.ENABLE_HOT_RELOAD:
            return
            
        if self._hot_reload_task is None:
            loop = asyncio.get_event_loop()
            self._hot_reload_task = loop.create_task(self._watch_config_files())
            logger.info("Started configuration hot-reloading")
    
    def stop_hot_reload(self):
        """Stop watching config files"""
        if self._hot_reload_task:
            self._hot_reload_task.cancel()
            self._hot_reload_task = None
            logger.info("Stopped configuration hot-reloading")
    
    def register_config_change_callback(self, filename: str, callback: Callable):
        """Register a callback to be called when a config file changes"""
        if filename not in self._config_change_callbacks:
            self._config_change_callbacks[filename] = []
        self._config_change_callbacks[filename].append(callback)
    
    def get_settings_config(self) -> Dict[str, Any]:
        """Get validated settings from settings.yml"""
        if self.SETTINGS_FILE not in self._cached_config:
            self._cached_config[self.SETTINGS_FILE] = self._config_loader.load_config(
                self.SETTINGS_FILE, SettingsConfig
            )
        return self._cached_config[self.SETTINGS_FILE]
    
    def get_agent_definitions(self) -> Dict[str, Any]:
        """Get validated agent definitions from agent_definitions.yml"""
        if self.AGENT_DEFS_FILE not in self._cached_config:
            self._cached_config[self.AGENT_DEFS_FILE] = self._config_loader.load_config(
                self.AGENT_DEFS_FILE, AgentDefinitionsConfig
            )
        return self._cached_config[self.AGENT_DEFS_FILE]
    
    def get_question_rules(self) -> Dict[str, Any]:
        """Get validated question rules from question_rules.yml"""
        if self.QUESTION_RULES_FILE not in self._cached_config:
            self._cached_config[self.QUESTION_RULES_FILE] = self._config_loader.load_config(
                self.QUESTION_RULES_FILE, QuestionRulesConfig
            )
        return self._cached_config[self.QUESTION_RULES_FILE]
    
    def get_pipeline_config(self, pipeline_name: str) -> List[Dict[str, Any]]:
        """Get pipeline configuration from the pipelines directory
        
        Args:
            pipeline_name: Name of the pipeline config file (without .yml extension)
            
        Returns:
            List of pipeline step configurations
        """
        pipeline_file = f"{self.PIPELINES_DIR}/{pipeline_name}.yml"
        cache_key = f"pipeline_{pipeline_name}"
        
        if cache_key not in self._cached_config:
            config = self._config_loader.load_config(pipeline_file)
            if not config or "steps" not in config:
                logger.error(f"Invalid pipeline configuration in {pipeline_file}")
                return []
            self._cached_config[cache_key] = config["steps"]
        
        return self._cached_config[cache_key]
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get the LLM configuration from settings.yml"""
        settings = self.get_settings_config()
        return settings.get("llm", {})
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration settings"""
        settings = self.get_settings_config()
        redis_config = settings.get("redis", {})
        
        # Override with env vars if set
        config = {
            "host": self.REDIS_HOST,
            "port": self.REDIS_PORT,
            "db": self.REDIS_DB,
            "password": self.REDIS_PASSWORD,
            "prefix": self.REDIS_PREFIX
        }
        
        # Update with values from settings.yml if present
        if redis_config:
            config.update(redis_config)
            
        return config

    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS from string to list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        elif "," in self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        elif self.CORS_ORIGINS:
            return [self.CORS_ORIGINS]
        else:
            return ["*"]  # Default fallback


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance"""
    return Settings()


# For testing, this will prepare a settings instance
if __name__ == "__main__":
    settings = get_settings()
    print(f"Loaded settings: {settings.APP_NAME}")
    print(f"LLM config: {settings.get_llm_config()}")
    print(f"Agent definitions: {settings.get_agent_definitions()}")
    print(f"Question rules: {settings.get_question_rules()}")
    print(f"Redis config: {settings.get_redis_config()}") 