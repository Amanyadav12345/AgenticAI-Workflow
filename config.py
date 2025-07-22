"""
Configuration management for the agentic AI workflow system
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class TelegramConfig:
    bot_token: str
    authorized_users: List[str]
    chat_id: Optional[str] = None

@dataclass
class DatabaseConfig:
    url: str
    type: str = "sqlite"
    connection_pool_size: int = 5
    timeout: int = 30

@dataclass
class APIConfig:
    google_api_key: str
    gemini_model: str = "gemini-1.5-pro"
    trip_api_url: str = ""
    api_authentication_token: str = ""
    request_timeout: int = 60
    max_retries: int = 3

@dataclass
class SecurityConfig:
    secret_key: str
    audit_log_file: str = "logs/security_audit.log"
    max_message_length: int = 10000
    session_timeout: int = 3600

@dataclass
class LoggingConfig:
    level: str = "INFO"
    log_file: str = "logs/workflow.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class WorkflowConfig:
    max_concurrent_workflows: int = 10
    workflow_timeout: int = 300  # 5 minutes
    enable_memory: bool = True
    enable_planning: bool = True

class ConfigManager:
    """
    Centralized configuration management
    """
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "config.json"
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment and config file"""
        # Load from environment variables
        self.telegram = TelegramConfig(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            authorized_users=self._parse_user_list(os.getenv("AUTHORIZED_USERS", "")),
            chat_id=os.getenv("TELEGRAM_CHAT_ID")
        )
        
        self.database = DatabaseConfig(
            url=os.getenv("DATABASE_URL", "sqlite:///workflow.db"),
            type=os.getenv("DATABASE_TYPE", "sqlite"),
            connection_pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            timeout=int(os.getenv("DB_TIMEOUT", "30"))
        )
        
        self.api = APIConfig(
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
            trip_api_url=os.getenv("TRIP_API_URL", ""),
            api_authentication_token=os.getenv("API_AUTHENTICATION_TOKEN", ""),
            request_timeout=int(os.getenv("API_TIMEOUT", "60")),
            max_retries=int(os.getenv("API_MAX_RETRIES", "3"))
        )
        
        self.security = SecurityConfig(
            secret_key=os.getenv("SECRET_KEY", "default_secret_key_change_in_production"),
            audit_log_file=os.getenv("AUDIT_LOG_FILE", "logs/security_audit.log"),
            max_message_length=int(os.getenv("MAX_MESSAGE_LENGTH", "10000")),
            session_timeout=int(os.getenv("SESSION_TIMEOUT", "3600"))
        )
        
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "logs/workflow.log"),
            max_file_size=int(os.getenv("LOG_MAX_SIZE", str(10 * 1024 * 1024))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5"))
        )
        
        self.workflow = WorkflowConfig(
            max_concurrent_workflows=int(os.getenv("MAX_CONCURRENT_WORKFLOWS", "10")),
            workflow_timeout=int(os.getenv("WORKFLOW_TIMEOUT", "300")),
            enable_memory=os.getenv("ENABLE_MEMORY", "true").lower() == "true",
            enable_planning=os.getenv("ENABLE_PLANNING", "true").lower() == "true"
        )
        
        # Load additional config from file if it exists
        if os.path.exists(self.config_file):
            self._load_from_file()
    
    def _parse_user_list(self, users_str: str) -> List[str]:
        """Parse comma-separated user list"""
        if not users_str:
            return []
        return [user.strip() for user in users_str.split(",") if user.strip()]
    
    def _load_from_file(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                file_config = json.load(f)
            
            # Update configurations with file values
            if 'telegram' in file_config:
                for key, value in file_config['telegram'].items():
                    if hasattr(self.telegram, key):
                        setattr(self.telegram, key, value)
            
            if 'database' in file_config:
                for key, value in file_config['database'].items():
                    if hasattr(self.database, key):
                        setattr(self.database, key, value)
            
            # Similar updates for other config sections...
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load config file {self.config_file}: {e}")
    
    def save_config(self):
        """Save current configuration to file"""
        config_dict = {
            'telegram': asdict(self.telegram),
            'database': asdict(self.database),
            'api': asdict(self.api),
            'security': asdict(self.security),
            'logging': asdict(self.logging),
            'workflow': asdict(self.workflow)
        }
        
        # Remove sensitive information before saving
        config_dict['telegram']['bot_token'] = "***REDACTED***"
        config_dict['api']['openai_api_key'] = "***REDACTED***"
        config_dict['security']['secret_key'] = "***REDACTED***"
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def validate_config(self) -> Dict[str, List[str]]:
        """
        Validate configuration and return any issues
        
        Returns:
            Dictionary with component names as keys and lists of issues as values
        """
        issues = {}
        
        # Validate Telegram config
        telegram_issues = []
        if not self.telegram.bot_token:
            telegram_issues.append("Bot token is required")
        if not self.telegram.authorized_users:
            telegram_issues.append("No authorized users configured (warning: all users will be allowed)")
        
        if telegram_issues:
            issues['telegram'] = telegram_issues
        
        # Validate API config
        api_issues = []
        if not self.api.google_api_key:
            api_issues.append("Google API key is required")
        if not self.api.trip_api_url:
            api_issues.append("Trip API URL is required")
        
        if api_issues:
            issues['api'] = api_issues
        
        # Validate Security config
        security_issues = []
        if self.security.secret_key == "default_secret_key_change_in_production":
            security_issues.append("Default secret key detected - change for production")
        
        if security_issues:
            issues['security'] = security_issues
        
        return issues
    
    def get_external_integrations(self) -> Dict[str, Dict]:
        """
        Get configuration for external integrations
        """
        return {
            'crm_api': {
                'base_url': os.getenv('CRM_API_URL', ''),
                'api_key': os.getenv('CRM_API_KEY', ''),
                'timeout': int(os.getenv('CRM_API_TIMEOUT', '30'))
            },
            'email_service': {
                'smtp_server': os.getenv('SMTP_SERVER', ''),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'username': os.getenv('SMTP_USERNAME', ''),
                'password': os.getenv('SMTP_PASSWORD', '')
            },
            'slack_webhook': {
                'webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
                'channel': os.getenv('SLACK_CHANNEL', '#general')
            },
            'database_connections': {
                'primary': self.database.url,
                'reporting': os.getenv('REPORTING_DB_URL', ''),
                'analytics': os.getenv('ANALYTICS_DB_URL', '')
            }
        }

# Global configuration instance
config = ConfigManager()

def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    return config

def reload_config():
    """Reload configuration from environment and files"""
    global config
    config = ConfigManager()