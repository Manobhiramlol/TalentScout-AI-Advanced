"""
TalentScout AI Configuration Package
Settings, database initialization, and logging configuration
"""

__version__ = "2.0.0"
__author__ = "TalentScout AI Team"

from .settings import get_settings, Settings, settings
from .enums import (
    TECHNICAL_SKILLS,
    InterviewStage,
    MessageRole,
    PersonalityType,
    QuestionType,
    SessionStatus
)
from .database import init_database, get_db_connection
from .logging_config import setup_logging, get_logger, main_logger

__all__ = [
    # Settings
    'get_settings',
    'Settings',
    'settings',
    'Settings',


    # Enums and Constants
    'TECHNICAL_SKILLS',
    'InterviewStage',
    'MessageRole',
    'PersonalityType',
    'QuestionType',
    'SessionStatus',
    
    # Database
    'init_database',
    'get_db_connection',
    
    # Logging
    'setup_logging',
    'get_logger',
    'main_logger'
]
