"""
Database models for TalentScout AI
Pydantic-style dataclasses for type safety and validation
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class InterviewStage(str, Enum):
    GREETING = "greeting"
    INFO_COLLECTION = "info_collection"
    TECHNICAL_ASSESSMENT = "technical_assessment"
    BEHAVIORAL_ASSESSMENT = "behavioral_assessment"
    PROBLEM_SOLVING = "problem_solving"
    WRAP_UP = "wrap_up"
    COMPLETED = "completed"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

@dataclass
class Message:
    """Message model"""
    id: Optional[int] = None
    session_id: str = ""
    message_id: int = 0
    role: MessageRole = MessageRole.USER
    content: str = ""
    timestamp: str = ""
    stage: InterviewStage = InterviewStage.GREETING
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message_id': self.message_id,
            'role': self.role.value if isinstance(self.role, MessageRole) else self.role,
            'content': self.content,
            'timestamp': self.timestamp,
            'stage': self.stage.value if isinstance(self.stage, InterviewStage) else self.stage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class Candidate:
    """Candidate model"""
    session_id: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""
    experience: str = ""
    position: str = ""
    tech_stack: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'session_id': self.session_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'experience': self.experience,
            'position': self.position,
            'tech_stack': self.tech_stack,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_complete(self) -> bool:
        """Check if candidate profile is complete"""
        required_fields = [self.name, self.email, self.experience, self.position]
        return all(field.strip() for field in required_fields) and len(self.tech_stack) > 0

@dataclass
class InterviewSession:
    """Interview session model"""
    session_id: str = ""
    current_stage: InterviewStage = InterviewStage.GREETING
    progress_percentage: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: SessionStatus = SessionStatus.ACTIVE
    ai_questions_generated: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'session_id': self.session_id,
            'current_stage': self.current_stage.value if isinstance(self.current_stage, InterviewStage) else self.current_stage,
            'progress_percentage': self.progress_percentage,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status.value if isinstance(self.status, SessionStatus) else self.status,
            'ai_questions_generated': self.ai_questions_generated
        }
    
    def calculate_duration(self) -> Optional[int]:
        """Calculate session duration in minutes"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() // 60
        elif self.start_time:
            delta = datetime.now() - self.start_time
            return delta.total_seconds() // 60
        return None

@dataclass
class AnalyticsEvent:
    """Analytics event model"""
    id: Optional[int] = None
    session_id: str = ""
    event_type: str = ""
    event_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'event_type': self.event_type,
            'event_data': self.event_data,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

@dataclass
class InterviewSummary:
    """Complete interview summary"""
    session: InterviewSession
    candidate: Candidate
    messages: List[Message]
    analytics: List[AnalyticsEvent]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'session': self.session.to_dict(),
            'candidate': self.candidate.to_dict(),
            'messages': [msg.to_dict() for msg in self.messages],
            'analytics': [event.to_dict() for event in self.analytics],
            'summary_stats': {
                'total_messages': len(self.messages),
                'user_messages': len([m for m in self.messages if m.role == MessageRole.USER]),
                'ai_messages': len([m for m in self.messages if m.role == MessageRole.ASSISTANT]),
                'duration_minutes': self.session.calculate_duration(),
                'completion_percentage': self.session.progress_percentage
            }
        }

# Utility functions for model conversion
def dict_to_message(data: Dict[str, Any]) -> Message:
    """Convert dictionary to Message model"""
    return Message(
        id=data.get('id'),
        session_id=data.get('session_id', ''),
        message_id=data.get('message_id', 0),
        role=MessageRole(data.get('role', 'user')),
        content=data.get('content', ''),
        timestamp=data.get('timestamp', ''),
        stage=InterviewStage(data.get('stage', 'greeting')),
        created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
    )

def dict_to_candidate(data: Dict[str, Any]) -> Candidate:
    """Convert dictionary to Candidate model"""
    return Candidate(
        session_id=data.get('session_id', ''),
        name=data.get('name', ''),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        experience=data.get('experience', ''),
        position=data.get('position', ''),
        tech_stack=data.get('tech_stack', []),
        created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
        updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
    )

def dict_to_session(data: Dict[str, Any]) -> InterviewSession:
    """Convert dictionary to InterviewSession model"""
    return InterviewSession(
        session_id=data.get('session_id', ''),
        current_stage=InterviewStage(data.get('current_stage', 'greeting')),
        progress_percentage=data.get('progress_percentage', 0),
        start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
        end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
        status=SessionStatus(data.get('status', 'active')),
        ai_questions_generated=data.get('ai_questions_generated', 0)
    )

# Model registry for easy access
MODEL_REGISTRY = {
    'message': Message,
    'candidate': Candidate,
    'session': InterviewSession,
    'analytics': AnalyticsEvent,
    'summary': InterviewSummary
}
