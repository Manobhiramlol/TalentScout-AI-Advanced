"""
API routes for TalentScout AI
FastAPI-based routes for external integrations and API access
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json 
from fastapi import APIRouter


router = APIRouter()

# Request/Response Models
class ChatMessage(BaseModel):
    session_id: str = Field(..., description="Interview session ID")
    message: str = Field(..., description="User message content")
    role: str = Field(default="user", description="Message role")

class ChatResponse(BaseModel):
    session_id: str
    response: str
    stage: str
    timestamp: str

class InterviewSession(BaseModel):
    session_id: str
    candidate_name: Optional[str] = None
    current_stage: str = "greeting"
    progress_percentage: int = 0

class CandidateProfile(BaseModel):
    name: str
    email: str
    experience: str
    position: str
    tech_stack: List[str]

# Chat API Endpoints
@router.post("/chat/message", response_model=ChatResponse)
async def send_chat_message(message: ChatMessage):
    """Send message to AI interviewer and get response"""
    try:
        # Process message with AI manager
        from core.ai_manager import advanced_ai_manager
        
        # Generate AI response based on message
        response_content = f"AI response to: {message.message}"
        
        return ChatResponse(
            session_id=message.session_id,
            response=response_content,
            stage="technical_assessment",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@router.post("/chat/generate-question")
async def generate_ai_question(session_id: str, context: Dict[str, Any]):
    """Generate AI question based on context"""
    try:
        from core.ai_manager import advanced_ai_manager
        
        question_result = advanced_ai_manager.generate_dynamic_question_sync(context)
        
        if question_result["success"]:
            return {
                "question": question_result["question"],
                "type": question_result["type"],
                "success": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=question_result.get("error", "Question generation failed")
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Session Management Endpoints
@router.post("/session/create", response_model=InterviewSession)
async def create_interview_session():
    """Create new interview session"""
    try:
        session_id = f"session_{int(datetime.now().timestamp())}"
        
        # Create session in database
        from database import session_crud
        session_crud.create_session(session_id)
        
        return InterviewSession(session_id=session_id)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )

@router.get("/session/{session_id}")
async def get_interview_session(session_id: str):
    """Get interview session details"""
    try:
        from database import session_crud
        session_data = session_crud.get_session(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return session_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Candidate Management Endpoints
@router.post("/candidate/profile")
async def save_candidate_profile(session_id: str, profile: CandidateProfile):
    """Save candidate profile"""
    try:
        from database import candidate_crud
        
        candidate_data = profile.dict()
        success = candidate_crud.create_candidate(session_id, candidate_data)
        
        if success:
            return {"message": "Candidate profile saved", "success": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to save candidate profile"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/candidate/{session_id}")
async def get_candidate_profile(session_id: str):
    """Get candidate profile"""
    try:
        from database import candidate_crud
        candidate = candidate_crud.get_candidate(session_id)
        
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        return candidate
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Analytics Endpoints
@router.get("/analytics/session/{session_id}")
async def get_session_analytics(session_id: str):
    """Get analytics for specific session"""
    try:
        from database import analytics_crud
        analytics = analytics_crud.get_session_analytics(session_id)
        
        return {"session_id": session_id, "analytics": analytics}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "TalentScout AI API"
    }
