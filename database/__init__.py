"""
TalentScout AI Database Package
CRUD operations and database models
"""

__version__ = "2.0.0"
__author__ = "TalentScout AI Team"

from .crud import (
    MessageCRUD,
    CandidateCRUD, 
    SessionCRUD,
    AnalyticsCRUD,
    message_crud,
    candidate_crud,
    session_crud,
    analytics_crud
)

from .models import (
    Message,
    Candidate,
    InterviewSession,
    AnalyticsEvent,
    InterviewSummary,
    InterviewStage,
    MessageRole,
    SessionStatus
)

__all__ = [
    # CRUD classes and instances
    'MessageCRUD',
    'CandidateCRUD',
    'SessionCRUD', 
    'AnalyticsCRUD',
    'message_crud',
    'candidate_crud',
    'session_crud',
    'analytics_crud',
    
    # Models
    'Message',
    'Candidate',
    'InterviewSession',
    'AnalyticsEvent',
    'InterviewSummary',
    
    # Enums
    'InterviewStage',
    'MessageRole',
    'SessionStatus'
]
