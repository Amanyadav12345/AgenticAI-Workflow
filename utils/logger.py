"""
Logging configuration for the agentic AI workflow system
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str = None, level: str = None) -> logging.Logger:
    """
    Set up a logger with both file and console handlers
    
    Args:
        name: Logger name
        log_file: Optional custom log file path
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    # Get log level from environment or use default
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if not log_file:
        log_file = os.getenv("LOG_FILE", f"logs/{name}.log")
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Rotating file handler (10MB max, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logger '{name}' initialized with level {logging.getLevelName(log_level)}")
    
    return logger

def log_workflow_execution(logger: logging.Logger, workflow_id: str, user_id: str, 
                          action: str, status: str, details: str = None):
    """
    Log workflow execution events in a structured format
    """
    log_entry = {
        "workflow_id": workflow_id,
        "user_id": user_id,
        "action": action,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        log_entry["details"] = details
    
    logger.info(f"WORKFLOW: {log_entry}")

def log_security_event(logger: logging.Logger, event_type: str, user_id: str = None, 
                      details: str = None):
    """
    Log security-related events
    """
    log_entry = {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat()
    }
    
    if user_id:
        log_entry["user_id"] = user_id
    
    if details:
        log_entry["details"] = details
    
    logger.warning(f"SECURITY: {log_entry}")

def log_agent_activity(logger: logging.Logger, agent_name: str, task: str, 
                      status: str, execution_time: float = None):
    """
    Log agent execution activities
    """
    log_entry = {
        "agent": agent_name,
        "task": task,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    if execution_time:
        log_entry["execution_time"] = execution_time
    
    logger.info(f"AGENT: {log_entry}")

def log_api_call(logger: logging.Logger, api_name: str, endpoint: str, 
                status_code: int, response_time: float = None):
    """
    Log external API calls
    """
    log_entry = {
        "api": api_name,
        "endpoint": endpoint,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat()
    }
    
    if response_time:
        log_entry["response_time"] = response_time
    
    logger.info(f"API_CALL: {log_entry}")