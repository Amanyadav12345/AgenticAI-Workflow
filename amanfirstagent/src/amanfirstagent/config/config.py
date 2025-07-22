"""
Configuration module for the truck booking system
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APIConfig:
    """API configuration"""
    def __init__(self):
        self.trip_api_url: Optional[str] = os.getenv('TRUCK_API_URL')
        self.api_authentication_token: Optional[str] = os.getenv('API_AUTHENTICATION_TOKEN')

class Config:
    """Main configuration class"""
    def __init__(self):
        self.api = APIConfig()
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.authorized_users = os.getenv('AUTHORIZED_USERS', '').split(',')
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        self.simulation_mode = os.getenv('SIMULATION_MODE', 'True').lower() == 'true'

_config_instance = None

def get_config() -> Config:
    """Get configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance