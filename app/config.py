"""
Configuration Management - Handles configuration and environment setup
"""

import os
import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Config:
    """Configuration management class"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.json"
        self.config = self._load_default_config()
        self._load_config()
        self._load_env_vars()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            # Bot settings
            'bot_delay': 3,
            'tap_delay': 1.0,
            'swipe_delay': 2.0,
            'text_delay': 0.5,
            
            # Device settings
            'device_ip': None,
            'device_port': 5555,
            'screenshot_dir': 'screenshots',
            
            # AI settings
            'openai_api_key': None,
            'tesseract_config': '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!? ',
            
            # Matching criteria
            'matching_criteria': {
                'min_age': 21,
                'max_age': 35,
                'preferred_interests': [
                    'technology', 'travel', 'fitness', 'music', 'art',
                    'photography', 'cooking', 'reading', 'hiking', 'yoga'
                ],
                'deal_breakers': [
                    'smoking', 'drugs', 'excessive drinking', 'toxic',
                    'narcissist', 'cheater', 'liar'
                ],
                'personality_traits': [
                    'intelligent', 'funny', 'adventurous', 'kind',
                    'creative', 'passionate', 'ambitious', 'empathetic'
                ]
            },
            
            # UI detection settings
            'ui_confidence_threshold': 0.7,
            'template_matching_threshold': 0.6,
            
            # OCR settings
            'ocr_confidence_threshold': 30,
            'text_region_padding': 10,
            
            # Logging settings
            'log_level': 'INFO',
            'log_file': 'hinge_bot.log',
            'max_log_size': 10485760,  # 10MB
            'backup_count': 5
        }
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
                    logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.info(f"Config file {self.config_path} not found, using defaults")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    def _load_env_vars(self) -> None:
        """Load configuration from environment variables"""
        try:
            # OpenAI API key
            if 'OPENAI_API_KEY' in os.environ:
                self.config['openai_api_key'] = os.environ['OPENAI_API_KEY']
            
            # Device IP
            if 'DEVICE_IP' in os.environ:
                self.config['device_ip'] = os.environ['DEVICE_IP']
            
            # Device port
            if 'DEVICE_PORT' in os.environ:
                self.config['device_port'] = int(os.environ['DEVICE_PORT'])
            
            # Bot delay
            if 'BOT_DELAY' in os.environ:
                self.config['bot_delay'] = int(os.environ['BOT_DELAY'])
            
            # Log level
            if 'LOG_LEVEL' in os.environ:
                self.config['log_level'] = os.environ['LOG_LEVEL']
            
            logger.info("Loaded environment variables")
            
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.config.update(updates)
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def validate(self) -> bool:
        """Validate configuration"""
        try:
            # Check required settings
            required_keys = ['openai_api_key']
            for key in required_keys:
                if not self.config.get(key):
                    logger.error(f"Required configuration key missing: {key}")
                    return False
            
            # Validate numeric values
            numeric_keys = ['bot_delay', 'tap_delay', 'swipe_delay', 'text_delay']
            for key in numeric_keys:
                value = self.config.get(key)
                if value is not None and not isinstance(value, (int, float)):
                    logger.error(f"Invalid numeric value for {key}: {value}")
                    return False
            
            # Validate matching criteria
            criteria = self.config.get('matching_criteria', {})
            if not isinstance(criteria, dict):
                logger.error("Invalid matching criteria format")
                return False
            
            # Validate age range
            min_age = criteria.get('min_age', 0)
            max_age = criteria.get('max_age', 0)
            if min_age >= max_age:
                logger.error("Invalid age range: min_age must be less than max_age")
                return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def create_env_template(self, template_path: str = ".env-template") -> bool:
        """Create environment variable template file"""
        try:
            template_content = """# HingeAutoBot Environment Variables
# Copy this file to .env and fill in your values

# OpenAI API Key (required)
OPENAI_API_KEY=your-openai-api-key-here

# Device Connection (optional - defaults to USB)
DEVICE_IP=192.168.1.100
DEVICE_PORT=5555

# Bot Settings (optional)
BOT_DELAY=3
LOG_LEVEL=INFO

# Matching Criteria (optional - can be configured in config.json)
# These are just examples, customize as needed
"""
            
            with open(template_path, 'w') as f:
                f.write(template_content)
            
            logger.info(f"Environment template created: {template_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating environment template: {e}")
            return False
    
    def get_matching_criteria(self) -> Dict[str, Any]:
        """Get matching criteria configuration"""
        return self.config.get('matching_criteria', {})
    
    def update_matching_criteria(self, criteria: Dict[str, Any]) -> None:
        """Update matching criteria"""
        self.config['matching_criteria'] = criteria
        logger.info("Matching criteria updated")
    
    def get_device_config(self) -> Dict[str, Any]:
        """Get device configuration"""
        return {
            'ip': self.config.get('device_ip'),
            'port': self.config.get('device_port', 5555),
            'screenshot_dir': self.config.get('screenshot_dir', 'screenshots')
        }
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration"""
        return {
            'openai_api_key': self.config.get('openai_api_key'),
            'tesseract_config': self.config.get('tesseract_config')
        }
    
    def get_bot_config(self) -> Dict[str, Any]:
        """Get bot configuration"""
        return {
            'bot_delay': self.config.get('bot_delay', 3),
            'tap_delay': self.config.get('tap_delay', 1.0),
            'swipe_delay': self.config.get('swipe_delay', 2.0),
            'text_delay': self.config.get('text_delay', 0.5)
        }
    
    def setup_directories(self) -> bool:
        """Setup required directories"""
        try:
            directories = [
                self.config.get('screenshot_dir', 'screenshots'),
                'templates',
                'logs'
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up directories: {e}")
            return False
