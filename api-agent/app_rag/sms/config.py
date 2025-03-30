import os
import logging
import json
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class Config:
    """
    Configuration management for SpeakWise.
    Loads configuration from environment variables or .env file.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config = {}
        self._load_from_env()
        
        # If config file provided, load it
        if config_file:
            self._load_from_file(config_file)
            
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Core configuration
        self.config["core"] = {
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "debug": os.environ.get("DEBUG", "False").lower() in ("true", "1", "t"),
            "log_level": os.environ.get("LOG_LEVEL", "INFO"),
        }
        
        # Telephony configuration
        self.config["telephony"] = {
            "api_key": os.environ.get("PINDO_API_KEY", ""),
            "webhook_url": os.environ.get("TELEPHONY_WEBHOOK_URL", ""),
            "sender_id": os.environ.get("PINDO_SENDER_ID", "PindoTest"),
        }
        
        # Messaging configuration
        self.config["messaging"] = {
            "api_key": os.environ.get("PINDO_API_KEY", "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4Mzc4OTQ5NzQsImlhdCI6MTc0MzIwMDU3NCwiaWQiOiJ1c2VyXzAxSlFFRDBZSFk2OEc2WkVDSkpIN1dFOUpBIiwicmV2b2tlZF90b2tlbl9jb3VudCI6MH0.ejo81tPmq2Qsd1o-REVpq2C2lY5P_HOFsja-TwahZstLEutg93JUR1WOhp5seqBF9OaITHKHt9--srvdM6DtPw"),
            "sender_id": os.environ.get("PINDO_SENDER_ID", "PindoTest"),
        }
        
        # Database configuration
        self.config["database"] = {
            "url": os.environ.get("DATABASE_URL", "sqlite:///speakwise.db"),
        }
        
        # LLM configuration
        self.config["llm"] = {
            "api_key": os.environ.get("LLM_API_KEY", ""),
            "model": os.environ.get("LLM_MODEL", "gpt-3.5-turbo"),
        }
            
    def _load_from_file(self, file_path: str):
        """
        Load configuration from JSON file.
        
        Args:
            file_path: Path to configuration file
        """
        try:
            with open(file_path, 'r') as f:
                file_config = json.load(f)
                
            # Merge with existing config
            for section, values in file_config.items():
                if section not in self.config:
                    self.config[section] = {}
                self.config[section].update(values)
                
            logger.info(f"Loaded configuration from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {str(e)}")
            
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        try:
            return self.config.get(section, {}).get(key, default)
        except Exception:
            return default
            
    def set(self, section: str, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        
    def save(self, file_path: str):
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save configuration
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved configuration to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {file_path}: {str(e)}")
            
    def __str__(self) -> str:
        """String representation of configuration"""
        # Filter out sensitive keys
        filtered_config = {}
        sensitive_keys = ["api_key", "password", "secret"]
        
        for section, values in self.config.items():
            filtered_config[section] = {}
            for key, value in values.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    filtered_config[section][key] = "***REDACTED***"
                else:
                    filtered_config[section][key] = value
                    
        return json.dumps(filtered_config, indent=2)