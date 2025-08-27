"""
API models for TalentScout AI
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class InterviewStage(str, Enum):
    GREETING = "greeting"
    INFO_COLLECTION = "info_collection"
    TECHNICAL_ASSESSMENT = "technical_assessment"
    BEHAVIORAL_ASSESSMENT = "behavioral_assessment"
    COMPLETED = "completed"

class ChatMessageRequest(BaseModel):
    session_id: str = Field(..., description="Interview session ID")
    message: str = Field(..., min_length=1, description="User message content")
    role: MessageRole = Field(default=MessageRole.USER, description="Message role")

class ChatMessageResponse(BaseModel):
    session_id: str
    response: str
    stage: InterviewStage
    timestamp: datetime
    success: bool = True

class QuestionGenerationRequest(BaseModel):
    session_id: str
    context: Dict[str, Any] = Field(..., description="Context for question generation")
    question_type: str = Field(default="technical", description="Type of question to generate")

class QuestionGenerationResponse(BaseModel):
    question: str
    type: str
    model_used: str
    success: bool = True

class CandidateProfileRequest(BaseModel):
    name: str = Field(..., min_length=2, description="Candidate full name")
    email: EmailStr = Field(..., description="Candidate email address")
    experience: str = Field(..., description="Years of experience")
    position: str = Field(..., description="Desired position")
    tech_stack: List[str] = Field(..., min_items=1, description="Technical skills")

class SessionCreateResponse(BaseModel):
    session_id: str
    created_at: datetime
    status: str = "active"

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    service: str = "TalentScout AI API"
    version: str = "2.0.0"
