"""
Enhanced AI Manager with Dynamic Question Generation using Llama 3.3 70B
Fixed for Streamlit Production Environment
"""

import os
from groq import Groq
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st

# Set up logging
logger = logging.getLogger(__name__)

class AdvancedAIManager:
    """AI Manager with Dynamic Question Generation using Llama 3.3 70B - Streamlit Compatible"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Groq client with enhanced error handling
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            st.error("❌ GROQ_API_KEY environment variable is not set")
            raise ValueError("GROQ_API_KEY environment variable is not set")
            
        try:
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.3-70b-versatile"
            logger.info(f"✅ Groq client initialized with model: {self.model}")
        except Exception as e:
            st.error(f"❌ Failed to initialize Groq client: {e}")
            raise
            
        self.current_context = {}
        self.question_history = []
    
    def _make_sync_api_call(self, messages: List[Dict], **kwargs) -> str:
        """Make synchronous API call to Groq"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise
    
    def generate_dynamic_question_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fresh, contextual interview questions (Streamlit-compatible sync version)"""
        
        # Extract context
        position = context.get("position", "Software Developer")
        experience = context.get("experience", "3-5 years")
        skills = context.get("skills", ["Python", "JavaScript"])
        interview_stage = context.get("stage", "technical")
        asked_questions = context.get("asked_questions", [])
        
        # Build dynamic system prompt
        system_prompt = f"""You are an expert interviewer conducting a {interview_stage} interview for a {position} position.

CANDIDATE PROFILE:
- Position: {position}
- Experience: {experience}
- Skills: {', '.join(skills)}
- Questions Already Asked: {len(asked_questions)}

DYNAMIC QUESTION GENERATION RULES:
1. Create ONE unique, challenging question
2. Make it highly specific to their role and experience level
3. Focus on practical, real-world scenarios
4. Avoid repeating similar questions to: {asked_questions[-3:] if asked_questions else 'None'}
5. Match the {interview_stage} assessment type

QUESTION TYPES BY STAGE:
- greeting: Warm introduction, tell me about yourself
- technical: Coding problems, system design, architecture, debugging scenarios
- behavioral: STAR method situations, teamwork, leadership, conflict resolution
- problem_solving: Logic puzzles, analytical challenges, trade-off decisions
- wrap_up: Questions for us, career goals, final thoughts

QUALITY CRITERIA:
- Specific to {position} with {experience} experience
- Tests real competencies they'll use on the job
- Allows for follow-up questions and deeper exploration
- Professional yet engaging tone

Generate ONE exceptional {interview_stage} question now."""

        user_prompt = f"Create a dynamic {interview_stage} interview question for {position} candidate with {experience} experience in {', '.join(skills)}."
        
        try:
            # Use sync API call instead of async
            question = self._make_sync_api_call(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=600,
                top_p=0.9
            )
            
            # Store question in history
            self.question_history.append({
                "question": question,
                "stage": interview_stage,
                "timestamp": datetime.now(),
                "context": context
            })
            
            logger.info(f"✅ Generated {interview_stage} question successfully")
            
            return {
                "question": question,
                "type": interview_stage,
                "model_used": self.model,
                "success": True,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            
            fallback_questions = {
                "greeting": "Tell me about yourself and what interests you about this position.",
                "technical": f"Describe a challenging {skills[0] if skills else 'technical'} problem you solved recently.",
                "behavioral": "Tell me about a time you had to work with a difficult team member.",
                "problem_solving": "How would you approach debugging a system that's running slowly?",
                "wrap_up": "What questions do you have about our team and company culture?"
            }
            
            return {
                "question": fallback_questions.get(interview_stage, "Tell me about a project you're proud of."),
                "type": interview_stage,
                "error": str(e),
                "success": False
            }
    
    def generate_followup_question_sync(self, original_question: str, candidate_answer: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent follow-up questions (Streamlit-compatible sync version)"""
        
        system_prompt = """You are an expert interviewer. Generate ONE insightful follow-up question that:

1. Builds directly on their previous response
2. Digs deeper into their technical understanding or experience
3. Tests the depth of their knowledge
4. Reveals their problem-solving approach
5. Is conversational but probing

FOLLOW-UP STRATEGIES:
- If they mentioned a technology: Ask about specific implementation details
- If they described a problem: Ask about alternative approaches or trade-offs
- If they gave a high-level answer: Ask for concrete examples
- If they showed expertise: Increase complexity and explore edge cases
- If they struggled: Offer guidance and test foundational concepts

Keep the follow-up natural and engaging."""

        user_prompt = f"""
ORIGINAL QUESTION: {original_question}

CANDIDATE'S ANSWER: {candidate_answer}

Generate a targeted follow-up question that explores their response deeper:"""

        try:
            followup = self._make_sync_api_call(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return {
                "question": followup,
                "type": "follow_up",
                "original_question": original_question,
                "success": True
            }
            
        except Exception as e:
            return {
                "question": "Can you elaborate on that approach and walk me through your thought process?",
                "type": "follow_up",
                "error": str(e),
                "success": False
            }
    
    def advance_interview_stage_sync(self, current_stage: str, message_count: int, context: Dict[str, Any]) -> str:
        """Determine next interview stage (Streamlit-compatible sync version)"""
        
        # Stage progression logic
        stage_mapping = {
            0: "greeting",
            1: "greeting", 
            2: "info_collection",
            3: "technical_assessment",
            4: "technical_assessment",
            5: "technical_assessment",
            6: "behavioral_assessment",
            7: "behavioral_assessment", 
            8: "behavioral_assessment",
            9: "problem_solving",
            10: "problem_solving",
            11: "wrap_up"
        }
        
        suggested_stage = stage_mapping.get(message_count, "wrap_up")
        
        # AI-powered stage decision for advanced cases
        if message_count > 3:
            decision_prompt = f"""Based on this interview progress, what should be the next interview stage?

CURRENT STAGE: {current_stage}
MESSAGE COUNT: {message_count}
CONTEXT: {context}

AVAILABLE STAGES: info_collection, technical_assessment, behavioral_assessment, problem_solving, wrap_up

Consider:
- Have we covered enough technical questions? 
- Is it time for behavioral assessment?
- Should we test problem-solving skills?
- Are we ready to wrap up?

Respond with just the stage name: info_collection/technical_assessment/behavioral_assessment/problem_solving/wrap_up"""

            try:
                ai_suggestion = self._make_sync_api_call(
                    messages=[{"role": "user", "content": decision_prompt}],
                    temperature=0.3,
                    max_tokens=50
                ).strip().lower()
                
                # Validate AI suggestion
                valid_stages = ["info_collection", "technical_assessment", "behavioral_assessment", "problem_solving", "wrap_up"]
                if ai_suggestion in valid_stages:
                    return ai_suggestion
                    
            except Exception as e:
                logger.warning(f"AI stage decision failed, using default: {e}")
        
        return suggested_stage
    
    def get_question_history(self) -> List[Dict]:
        """Get history of generated questions"""
        return self.question_history
    
    def clear_question_history(self):
        """Clear question history for new interview"""
        self.question_history = []
        self.current_context = {}

# Global instance with error handling
try:
    advanced_ai_manager = AdvancedAIManager()
    logger.info("✅ Advanced AI Manager initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize AI Manager: {e}")
    # Create a dummy manager to prevent import errors
    advanced_ai_manager = None
