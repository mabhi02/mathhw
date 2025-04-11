import os
import re
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from functools import lru_cache
from pydantic import BaseModel, ValidationError
import logging
from datetime import datetime

# Logger for config operations
logger = logging.getLogger("app.config")

# Regex for finding environment variables in config strings
ENV_VAR_PATTERN = re.compile(r'\${([A-Za-z0-9_]+)}')


def substitute_env_vars(value: str) -> str:
    """
    Replace environment variables in string values
    
    Args:
        value: String that may contain environment variables
        
    Returns:
        String with environment variables replaced
    """
    if not isinstance(value, str):
        return value
        
    def _replace_env_var(match):
        env_var_name = match.group(1)
        env_var_value = os.environ.get(env_var_name)
        if env_var_value is None:
            logger.warning(f"Environment variable '{env_var_name}' not found")
            # Return original placeholder if env var not found
            return f"${{{env_var_name}}}"
        return env_var_value
    
    return ENV_VAR_PATTERN.sub(_replace_env_var, value)


def process_config_values(config: Any) -> Any:
    """
    Recursively process config dictionary to replace env vars
    
    Args:
        config: Configuration section to process
        
    Returns:
        Processed configuration with env vars replaced
    """
    if isinstance(config, dict):
        return {k: process_config_values(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [process_config_values(v) for v in config]
    elif isinstance(config, str):
        return substitute_env_vars(config)
    else:
        return config


class ConfigFile:
    """
    Represents a configuration file with metadata for hot-reloading
    """
    def __init__(self, path: Path):
        self.path = path
        self.last_modified = datetime.fromtimestamp(path.stat().st_mtime)
        self.content = None
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load and process the YAML file"""
        try:
            with open(self.path, 'r') as f:
                raw_config = yaml.safe_load(f)
            
            # Process environment variables
            self.content = process_config_values(raw_config)
            self.last_modified = datetime.fromtimestamp(self.path.stat().st_mtime)
            logger.info(f"Loaded configuration from {self.path}")
            return self.content
        except Exception as e:
            logger.error(f"Error loading configuration from {self.path}: {str(e)}")
            raise
    
    def has_changed(self) -> bool:
        """Check if file has been modified since last load"""
        current_mtime = datetime.fromtimestamp(self.path.stat().st_mtime)
        return current_mtime > self.last_modified
    
    def reload_if_changed(self) -> bool:
        """Reload the file if it has changed"""
        if self.has_changed():
            self.load()
            return True
        return False


class ConfigLoader:
    """
    Configuration loader that supports hot-reloading
    """
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_files: Dict[str, ConfigFile] = {}
        
    def get_config_path(self, filename: str) -> Path:
        """Get full path to a config file"""
        return self.config_dir / filename
    
    def load_config(self, filename: str, schema_model: Optional[BaseModel] = None) -> Dict[str, Any]:
        """
        Load and validate a configuration file
        
        Args:
            filename: Name of the config file
            schema_model: Optional Pydantic model for validation
            
        Returns:
            Validated configuration dictionary
        """
        config_path = self.get_config_path(filename)
        
        # Check if we've already loaded this file
        if filename not in self.config_files:
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
            # Create new config file object
            self.config_files[filename] = ConfigFile(config_path)
        else:
            # Check for changes and reload if needed
            self.config_files[filename].reload_if_changed()
        
        config = self.config_files[filename].content
        
        # Validate against schema if provided
        if schema_model is not None:
            try:
                validated_config = schema_model(**config)
                return validated_config.dict()
            except ValidationError as e:
                logger.error(f"Configuration validation error in {filename}: {str(e)}")
                raise
        
        return config
    
    def reload_all(self) -> List[str]:
        """
        Reload all config files that have changed
        
        Returns:
            List of filenames that were reloaded
        """
        reloaded = []
        for filename, config_file in self.config_files.items():
            if config_file.reload_if_changed():
                reloaded.append(filename)
        
        if reloaded:
            logger.info(f"Reloaded configuration files: {', '.join(reloaded)}")
        
        return reloaded


# Create global config loader instance
@lru_cache()
def get_config_loader(config_dir: str = "config") -> ConfigLoader:
    """Get or create a cached ConfigLoader instance"""
    return ConfigLoader(config_dir) 