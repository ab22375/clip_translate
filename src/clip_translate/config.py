"""Configuration management for clip_translate."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class Config:
    """Configuration manager for translation settings."""
    
    DEFAULT_CONFIG = {
        "engine": "google",  # Default to Google Translate
        "openai": {
            "api_key": "",
            "model": "gpt-4o-mini"
        },
        "deepl": {
            "api_key": ""
        },
        "claude": {
            "api_key": "",
            "model": "claude-3-haiku-20240307"
        },
        "google": {
            # No config needed for Google Translate
        },
        "default_source": "ja",
        "default_target": "en",
        "cache_enabled": True,
        "show_romaji": False,
        "show_hiragana": False
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager."""
        if config_path is None:
            # Default to ~/.clip_translate/config.json
            self.config_dir = Path.home() / ".clip_translate"
            self.config_path = self.config_dir / "config.json"
        else:
            self.config_path = Path(config_path)
            self.config_dir = self.config_path.parent
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                config = self.DEFAULT_CONFIG.copy()
                self._deep_update(config, loaded_config)
                return config
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            # Create directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Save config
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Config saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def _deep_update(self, base: dict, update: dict) -> dict:
        """Deep update dictionary."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
        return base
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def get_engine_config(self, engine: str) -> Dict[str, Any]:
        """Get configuration for specific engine."""
        return self.config.get(engine, {})
    
    def set_engine(self, engine: str) -> None:
        """Set the active translation engine."""
        self.config["engine"] = engine
    
    def get_engine(self) -> str:
        """Get the active translation engine."""
        return self.config.get("engine", "google")
    
    def set_api_key(self, engine: str, api_key: str) -> None:
        """Set API key for specific engine."""
        if engine not in self.config:
            self.config[engine] = {}
        self.config[engine]["api_key"] = api_key
    
    def get_api_key(self, engine: str) -> Optional[str]:
        """Get API key for specific engine."""
        # First check config file
        engine_config = self.config.get(engine, {})
        api_key = engine_config.get("api_key", "")
        
        # If not in config, check environment variables
        if not api_key:
            env_map = {
                "openai": "OPENAI_API_KEY",
                "deepl": "DEEPL_API_KEY",
                "claude": "ANTHROPIC_API_KEY"
            }
            env_var = env_map.get(engine)
            if env_var:
                api_key = os.getenv(env_var, "")
        
        return api_key if api_key else None
    
    def validate_engine_config(self, engine: str) -> bool:
        """Validate that engine has required configuration."""
        if engine == "google":
            return True  # No config needed
        
        api_key = self.get_api_key(engine)
        return bool(api_key)
    
    def get_available_engines(self) -> list[str]:
        """Get list of available (configured) engines."""
        engines = ["google"]  # Always available
        
        for engine in ["openai", "deepl", "claude"]:
            if self.validate_engine_config(engine):
                engines.append(engine)
        
        return engines