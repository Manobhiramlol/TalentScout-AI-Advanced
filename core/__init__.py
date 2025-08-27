"""
TalentScout AI Core Package
AI management, conversation engine, and security components
"""

__version__ = "2.0.0"
__author__ = "TalentScout AI Team"

from .ai_manager import AdvancedAIManager, advanced_ai_manager
from .persona_manager import PersonaManager, InterviewPersona
from .conversation_engine import ConversationEngine, conversation_engine
from .security_manager import SecurityManager, security_manager

__all__ = [
    # AI Management
    'AdvancedAIManager',
    'advanced_ai_manager',
    
    # Persona Management
    'PersonaManager',
    'InterviewPersona',
    
    # Conversation Engine
    'ConversationEngine',
    'conversation_engine',
    
    # Security Management
    'SecurityManager',
    'security_manager'
]
