"""
Logging configuration for TalentScout AI
Structured logging with file and console output
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
LOG_FILE = LOGS_DIR / f"talentscout_{datetime.now().strftime('%Y%m%d')}.log"
ERROR_LOG_FILE = LOGS_DIR / f"errors_{datetime.now().strftime('%Y%m%d')}.log"

# Log formats
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
SIMPLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

def setup_logging(log_level: str = "INFO", enable_file_logging: bool = True) -> logging.Logger:
    """
    Setup comprehensive logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        enable_file_logging: Whether to log to files
    
    Returns:
        Configured logger instance
    """
    
    # Set log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("TalentScoutAI")
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(SIMPLE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    if enable_file_logging:
        # File handler for all logs
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(DETAILED_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler(ERROR_LOG_FILE, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(DETAILED_FORMAT)
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)
    
    # Prevent duplicate logging
    logger.propagate = False
    
    logger.info(f"✅ Logging configured - Level: {log_level}, File logging: {enable_file_logging}")
    
    return logger

def get_logger(name: str = "TalentScoutAI") -> logging.Logger:
    """Get logger instance for specific module"""
    return logging.getLogger(name)

def log_interview_event(session_id: str, event: str, details: Optional[Dict] = None):
    """Log interview-specific events"""
    logger = get_logger("TalentScoutAI.Interview")
    
    log_message = f"Session {session_id}: {event}"
    if details:
        log_message += f" - Details: {details}"
    
    logger.info(log_message)

def log_ai_interaction(session_id: str, question_type: str, success: bool, 
                      model: str = "llama-3.3", response_time: float = 0.0):
    """Log AI interaction events"""
    logger = get_logger("TalentScoutAI.AI")
    
    status = "SUCCESS" if success else "FAILED"
    log_message = f"AI {status} - Session: {session_id}, Type: {question_type}, Model: {model}, Time: {response_time:.2f}s"
    
    if success:
        logger.info(log_message)
    else:
        logger.error(log_message)

def log_error(error: Exception, context: Optional[str] = None):
    """Log error with context"""
    logger = get_logger("TalentScoutAI.Error")
    
    error_message = f"ERROR: {str(error)}"
    if context:
        error_message = f"{context} - {error_message}"
    
    logger.error(error_message, exc_info=True)

# Configure logging on module import
main_logger = setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    enable_file_logging=os.getenv("ENABLE_FILE_LOGGING", "True").lower() == "true"
)
