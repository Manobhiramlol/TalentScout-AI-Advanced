"""
Advanced conversation engine for TalentScout AI
Manages interview flow, context, and state transitions
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from config.enums import InterviewStage, MessageRole
from .ai_manager import AdvancedAIManager
from .persona_manager import PersonaManager

logger = logging.getLogger(__name__)

class ConversationState(str, Enum):
    """Conversation state management"""
    INITIALIZED = "initialized"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class ConversationContext:
    """Context for conversation management"""
    session_id: str
    current_stage: InterviewStage = InterviewStage.GREETING
    conversation_state: ConversationState = ConversationState.INITIALIZED
    candidate_data: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    stage_progress: Dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

class ConversationEngine:
    """Advanced conversation engine with state management and flow control"""
    
    def __init__(self):
        self.ai_manager = AdvancedAIManager()
        self.persona_manager = PersonaManager()
        
        # Stage configuration
        self.stage_config = {
            InterviewStage.GREETING: {
                "min_exchanges": 1,
                "max_exchanges": 3,
                "auto_advance": True,
                "required_data": ["name"]
            },
            InterviewStage.INFO_COLLECTION: {
                "min_exchanges": 3,
                "max_exchanges": 8,
                "auto_advance": True,
                "required_data": ["email", "experience", "position", "tech_stack"]
            },
            InterviewStage.TECHNICAL_ASSESSMENT: {
                "min_exchanges": 3,
                "max_exchanges": 10,
                "auto_advance": False,
                "required_data": []
            },
            InterviewStage.BEHAVIORAL_ASSESSMENT: {
                "min_exchanges": 2,
                "max_exchanges": 6,
                "auto_advance": False,
                "required_data": []
            },
            InterviewStage.WRAP_UP: {
                "min_exchanges": 1,
                "max_exchanges": 3,
                "auto_advance": True,
                "required_data": []
            }
        }
        
        # Conversation patterns
        self.conversation_patterns = {
            "greeting_responses": [
                "Hello! Welcome to TalentScout AI. I'm excited to learn about your background.",
                "Hi there! I'm your AI interviewer. Let's have a great conversation today.",
                "Welcome! I'm here to conduct a personalized interview tailored to your skills."
            ],
            "transition_phrases": [
                "That's great! Let's move on to",
                "Excellent. Now I'd like to explore",
                "Thank you for that insight. Let's discuss",
                "Perfect! Next, we'll cover"
            ],
            "encouragement": [
                "That's a thoughtful response.",
                "I appreciate your detailed explanation.",
                "Great example! Your experience really shows.",
                "Excellent problem-solving approach."
            ]
        }
    
    def initialize_conversation(self, session_id: str) -> ConversationContext:
        """Initialize new conversation context"""
        
        context = ConversationContext(
            session_id=session_id,
            current_stage=InterviewStage.GREETING,
            conversation_state=ConversationState.INITIALIZED
        )
        
        # Add initial greeting message
        greeting_message = self._generate_greeting_message(context)
        context.conversation_history.append({
            "role": MessageRole.ASSISTANT,
            "content": greeting_message,
            "timestamp": datetime.now().isoformat(),
            "stage": InterviewStage.GREETING,
            "message_id": 1
        })
        
        context.conversation_state = ConversationState.ACTIVE
        context.last_updated = datetime.now()
        
        logger.info(f"✅ Conversation initialized for session {session_id}")
        return context
    
    def process_user_input(self, context: ConversationContext, user_input: str) -> Tuple[str, ConversationContext]:
        """
        Process user input and generate appropriate response
        
        Returns:
            Tuple of (ai_response, updated_context)
        """
        
        # Validate input
        if not user_input or not user_input.strip():
            return "I didn't catch that. Could you please respond?", context
        
        # Add user message to history
        user_message = {
            "role": MessageRole.USER,
            "content": user_input.strip(),
            "timestamp": datetime.now().isoformat(),
            "stage": context.current_stage,
            "message_id": len(context.conversation_history) + 1
        }
        context.conversation_history.append(user_message)
        
        try:
            # Process based on current stage
            ai_response = self._process_stage_specific_input(context, user_input)
            
            # Add AI response to history
            ai_message = {
                "role": MessageRole.ASSISTANT,
                "content": ai_response,
                "timestamp": datetime.now().isoformat(),
                "stage": context.current_stage,
                "message_id": len(context.conversation_history) + 1
            }
            context.conversation_history.append(ai_message)
            
            # Update context
            context.last_updated = datetime.now()
            
            # Check for stage advancement
            if self._should_advance_stage(context):
                context = self._advance_to_next_stage(context)
            
            logger.info(f"Processed user input for session {context.session_id}, stage: {context.current_stage}")
            
            return ai_response, context
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            error_response = "I apologize, but I encountered an issue. Could you please try again?"
            return error_response, context
    
    def _process_stage_specific_input(self, context: ConversationContext, user_input: str) -> str:
        """Process input based on current interview stage"""
        
        stage = context.current_stage
        
        if stage == InterviewStage.GREETING:
            return self._process_greeting_stage(context, user_input)
        elif stage == InterviewStage.INFO_COLLECTION:
            return self._process_info_collection_stage(context, user_input)
        elif stage == InterviewStage.TECHNICAL_ASSESSMENT:
            return self._process_technical_stage(context, user_input)
        elif stage == InterviewStage.BEHAVIORAL_ASSESSMENT:
            return self._process_behavioral_stage(context, user_input)
        elif stage == InterviewStage.WRAP_UP:
            return self._process_wrap_up_stage(context, user_input)
        else:
            return "Thank you for your response. Let's continue our conversation."
    
    def _process_greeting_stage(self, context: ConversationContext, user_input: str) -> str:
        """Process greeting stage input"""
        
        # Extract name from input
        name = self._extract_name(user_input)
        if name:
            context.candidate_data["name"] = name
            
            return f"""Nice to meet you, **{name}**! 🎯

I'm your AI interviewer powered by advanced language models. I'll be conducting an adaptive interview that adjusts based on your responses and technical background.

Could you please share your **email address** so we can keep in touch?"""
        else:
            return "I'd love to get to know you better! What should I call you?"
    
    def _process_info_collection_stage(self, context: ConversationContext, user_input: str) -> str:
        """Process information collection stage"""
        
        candidate_data = context.candidate_data
        
        if "email" not in candidate_data:
            if "@" in user_input and "." in user_input:
                candidate_data["email"] = user_input.strip()
                return "Perfect! Now, **how many years of professional experience** do you have?"
            else:
                return "Please provide a valid email address (e.g., john@example.com)"
        
        elif "experience" not in candidate_data:
            candidate_data["experience"] = user_input.strip()
            return "Great! **What type of position** are you interested in? (e.g., Software Engineer, Data Scientist, Product Manager)"
        
        elif "position" not in candidate_data:
            candidate_data["position"] = user_input.strip()
            return """Excellent! Now for the key part - **what programming languages, frameworks, and technologies** are you proficient with?

Please list your main technical skills separated by commas (e.g., Python, React, AWS, PostgreSQL)"""
        
        else:
            # Parse tech stack
            tech_skills = [skill.strip().title() for skill in user_input.split(",") if skill.strip()]
            candidate_data["tech_stack"] = tech_skills
            
            return f"""Perfect! I now have your complete profile:

**👤 Candidate Profile:**
- **Name:** {candidate_data.get('name', 'N/A')}
- **Position:** {candidate_data.get('position', 'N/A')}
- **Experience:** {candidate_data.get('experience', 'N/A')}
- **Tech Stack:** {', '.join(tech_skills)}

Now I'll use **advanced AI** to generate technical questions specifically tailored to your {tech_skills[0] if tech_skills else 'technical'} background. 

Let's begin the technical assessment! 🚀

**Technical Question 1:**

Describe a challenging technical problem you've solved using {tech_skills[0] if tech_skills else 'your preferred technology'}. Walk me through your approach, the obstacles you faced, and how you overcame them."""
    
    def _process_technical_stage(self, context: ConversationContext, user_input: str) -> str:
        """Process technical assessment stage"""
        
        # Track questions asked in this stage
        stage_questions = context.stage_progress.get("technical_questions", 0) + 1
        context.stage_progress["technical_questions"] = stage_questions
        
        # Provide feedback and ask follow-up
        feedback = self._generate_encouragement_feedback(user_input)
        
        if stage_questions <= 3:
            # Generate next technical question
            tech_stack = context.candidate_data.get("tech_stack", ["programming"])
            next_question = self._generate_technical_question(tech_stack, stage_questions)
            
            return f"""{feedback}

**Technical Question {stage_questions + 1}:**

{next_question}"""
        else:
            # Transition to behavioral assessment
            return f"""{feedback}

🎉 **Technical Assessment Complete!**

You've demonstrated solid technical knowledge and problem-solving skills. Now let's explore your soft skills and behavioral competencies.

**Behavioral Question 1:**

Tell me about a time when you had to work with a difficult team member or resolve a conflict in your team. How did you handle the situation?

Please structure your response using the **STAR method**:
- **Situation:** What was the context?
- **Task:** What was your responsibility?
- **Action:** What steps did you take?
- **Result:** What was the outcome?"""
    
    def _process_behavioral_stage(self, context: ConversationContext, user_input: str) -> str:
        """Process behavioral assessment stage"""
        
        stage_questions = context.stage_progress.get("behavioral_questions", 0) + 1
        context.stage_progress["behavioral_questions"] = stage_questions
        
        feedback = self._generate_encouragement_feedback(user_input)
        
        if stage_questions <= 2:
            behavioral_questions = [
                "Describe a time when you had to learn a new technology or skill quickly for a project. How did you approach the learning process?",
                "Tell me about a project where you had to meet a tight deadline. How did you ensure quality while working under pressure?",
                "Give me an example of when you had to explain a complex technical concept to a non-technical stakeholder. How did you make it understandable?"
            ]
            
            next_question = behavioral_questions[min(stage_questions-1, len(behavioral_questions)-1)]
            
            return f"""{feedback}

**Behavioral Question {stage_questions + 1}:**

{next_question}

Please continue using the **STAR method** in your response."""
        else:
            # Complete interview
            return self._generate_interview_completion(context)
    
    def _process_wrap_up_stage(self, context: ConversationContext, user_input: str) -> str:
        """Process wrap-up stage"""
        
        return """Thank you for your thoughtful questions! 

Our interview process is now complete. You've successfully demonstrated both technical competency and strong communication skills.

**Next Steps:**
1. Our team will review your comprehensive responses
2. We'll be in touch within 2-3 business days
3. If selected, you'll be invited for the next round

Have a wonderful day, and thank you for your interest in our company! 🚀"""
    
    def _generate_technical_question(self, tech_stack: List[str], question_number: int) -> str:
        """Generate technical questions based on tech stack"""
        
        primary_skill = tech_stack[0] if tech_stack else "programming"
        
        questions = {
            1: f"How would you optimize the performance of a {primary_skill} application that's running slowly in production? What steps would you take to identify and fix bottlenecks?",
            2: f"Describe how you would design a scalable system architecture using {primary_skill} that needs to handle thousands of concurrent users.",
            3: f"What are the key security considerations you'd implement when building a {primary_skill} application that handles sensitive user data?"
        }
        
        return questions.get(question_number, f"Can you explain the best practices you follow when working with {primary_skill}?")
    
    def _generate_encouragement_feedback(self, response: str) -> str:
        """Generate encouraging feedback based on response quality"""
        
        response_length = len(response.split())
        
        if response_length > 80:
            return "**Excellent!** I appreciate the comprehensive explanation and the depth of detail you provided."
        elif response_length > 40:
            return "**Great response!** You've clearly thought through this problem systematically."
        elif response_length > 20:
            return "**Good insight!** Your experience in this area is evident."
        else:
            return "**Thank you for sharing that.** Your practical experience is valuable."
    
    def _generate_interview_completion(self, context: ConversationContext) -> str:
        """Generate interview completion message"""
        
        name = context.candidate_data.get("name", "")
        technical_q = context.stage_progress.get("technical_questions", 0)
        behavioral_q = context.stage_progress.get("behavioral_questions", 0)
        
        duration = (datetime.now() - context.created_at).total_seconds() / 60
        
        context.current_stage = InterviewStage.COMPLETED
        context.conversation_state = ConversationState.COMPLETED
        
        return f"""🎯 **Interview Complete!**

Thank you for your time today, **{name}**!

**Interview Summary:**
- ✅ **Technical Questions:** {technical_q}
- ✅ **Behavioral Questions:** {behavioral_q}
- ✅ **Total Duration:** {duration:.0f} minutes
- ✅ **Completion Status:** 100%

You've successfully completed our AI-powered interview featuring:
- 🤖 Personalized questions based on your {', '.join(context.candidate_data.get('tech_stack', ['technical'])[:2])} background
- 📊 Real-time conversation adaptation
- 🎯 Comprehensive skill assessment

**Next Steps:**
1. Review your responses in the analytics dashboard
2. Our team will evaluate your comprehensive answers
3. Expect feedback within 2-3 business days

Thank you for demonstrating your technical expertise and communication skills. Best of luck! 🚀

**Final Question:** Do you have any questions about our company, team, or the role that I can help answer?"""
    
    def _should_advance_stage(self, context: ConversationContext) -> bool:
        """Determine if conversation should advance to next stage"""
        
        current_stage = context.current_stage
        stage_config = self.stage_config.get(current_stage, {})
        
        # Check if auto-advance is enabled
        if not stage_config.get("auto_advance", False):
            return False
        
        # Check if minimum exchanges are met
        stage_messages = [msg for msg in context.conversation_history if msg.get("stage") == current_stage]
        exchanges = len([msg for msg in stage_messages if msg.get("role") == MessageRole.USER])
        
        min_exchanges = stage_config.get("min_exchanges", 1)
        if exchanges < min_exchanges:
            return False
        
        # Check if required data is collected
        required_data = stage_config.get("required_data", [])
        for field in required_data:
            if field not in context.candidate_data:
                return False
        
        return True
    
    def _advance_to_next_stage(self, context: ConversationContext) -> ConversationContext:
        """Advance conversation to the next stage"""
        
        stage_progression = {
            InterviewStage.GREETING: InterviewStage.INFO_COLLECTION,
            InterviewStage.INFO_COLLECTION: InterviewStage.TECHNICAL_ASSESSMENT,
            InterviewStage.TECHNICAL_ASSESSMENT: InterviewStage.BEHAVIORAL_ASSESSMENT,
            InterviewStage.BEHAVIORAL_ASSESSMENT: InterviewStage.WRAP_UP,
            InterviewStage.WRAP_UP: InterviewStage.COMPLETED
        }
        
        next_stage = stage_progression.get(context.current_stage, InterviewStage.COMPLETED)
        context.current_stage = next

conversation_engine = ConversationEngine()

