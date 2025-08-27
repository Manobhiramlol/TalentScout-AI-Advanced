"""
Advanced AI persona management system for creating dynamic interview personalities
with adaptive questioning styles, emotional intelligence, and context awareness.
Streamlit Production Compatible Version
"""

import logging
import json
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import streamlit as st

logger = logging.getLogger(__name__)

class PersonalityType(str, Enum):
    ANALYTICAL = "analytical"
    EMPATHETIC = "empathetic"
    DIRECT = "direct"
    COLLABORATIVE = "collaborative"
    INNOVATIVE = "innovative"

class DifficultyPreference(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    ADAPTIVE = "adaptive"

@dataclass
class PersonaBehavior:
    """Defines specific behavior patterns for a persona"""
    encouragement_phrases: List[str]
    follow_up_patterns: List[str]
    feedback_style: str
    question_transition_phrases: List[str]
    difficulty_adjustment_threshold: float
    patience_level: int  # 1-10 scale

@dataclass
class InterviewPersona:
    """Comprehensive interview persona with dynamic behavior patterns"""
    
    id: str
    name: str
    title: str
    avatar: str
    personality_type: PersonalityType
    communication_style: str
    specialties: List[str]
    behavior: PersonaBehavior
    current_mood: float = field(default=0.7)
    session_stats: Dict[str, Any] = field(default_factory=dict)

class PersonaManager:
    """Advanced persona management with dynamic adaptation and learning - Streamlit Compatible"""
    
    def __init__(self):
        self.personas: Dict[str, InterviewPersona] = {}
        
        # Use Streamlit session state for active personas
        if "active_personas" not in st.session_state:
            st.session_state.active_personas = {}
        
        self._load_default_personas()
        logger.info(f"PersonaManager initialized with {len(self.personas)} personas")
    
    def _load_default_personas(self):
        """Load and configure default interview personas"""
        
        # Technical Lead Persona
        self.personas["technical_lead"] = InterviewPersona(
            id="technical_lead",
            name="Alex Thompson",
            title="Senior Technical Lead",
            avatar="👨‍💻",
            personality_type=PersonalityType.ANALYTICAL,
            communication_style="Direct but supportive, focuses on technical depth and problem-solving approach",
            specialties=["system_design", "algorithms", "performance_optimization", "code_quality", "architecture"],
            behavior=PersonaBehavior(
                encouragement_phrases=[
                    "That's a solid approach!",
                    "Good thinking on that solution.",
                    "I like your systematic approach.",
                    "Excellent consideration of edge cases.",
                    "That shows good architectural thinking."
                ],
                follow_up_patterns=[
                    "Can you elaborate on {topic}?",
                    "How would you handle {scenario}?",
                    "What if we had {constraint}?",
                    "Have you considered {alternative}?",
                    "Can you walk me through your reasoning?"
                ],
                feedback_style="constructive_technical",
                question_transition_phrases=[
                    "Let's dive deeper into",
                    "Moving on to a related topic",
                    "Here's a scenario that builds on that",
                    "Let's explore another aspect"
                ],
                difficulty_adjustment_threshold=0.7,
                patience_level=6
            )
        )
        
        # HR Manager Persona
        self.personas["friendly_hr"] = InterviewPersona(
            id="friendly_hr",
            name="Sarah Chen",
            title="People Operations Manager",
            avatar="👩‍💼",
            personality_type=PersonalityType.EMPATHETIC,
            communication_style="Warm and encouraging, focuses on cultural fit and interpersonal skills",
            specialties=["team_collaboration", "communication", "adaptability", "leadership", "conflict_resolution"],
            behavior=PersonaBehavior(
                encouragement_phrases=[
                    "I really appreciate your honesty.",
                    "That's a great example of teamwork.",
                    "You show excellent self-awareness.",
                    "I can see you're passionate about this.",
                    "Your experience really shines through."
                ],
                follow_up_patterns=[
                    "Can you tell me more about how you felt during {situation}?",
                    "What did you learn from {experience}?",
                    "How did your team react to {decision}?",
                    "What would you do differently if {scenario} happened again?",
                    "Can you give me another example of {behavior}?"
                ],
                feedback_style="supportive_developmental",
                question_transition_phrases=[
                    "That leads me to another question about",
                    "I'd love to hear about",
                    "Let's talk about a different situation",
                    "Speaking of teamwork"
                ],
                difficulty_adjustment_threshold=0.6,
                patience_level=9
            )
        )
    
    def get_persona(self, persona_id: str) -> Optional[InterviewPersona]:
        """Get persona by ID"""
        return self.personas.get(persona_id)
    
    def get_available_personas(self) -> List[Dict[str, Any]]:
        """Get list of available personas with their basic info"""
        return [
            {
                "id": persona.id,
                "name": persona.name,
                "title": persona.title,
                "avatar": persona.avatar,
                "personality_type": persona.personality_type.value,
                "specialties": persona.specialties,
                "communication_style": persona.communication_style
            }
            for persona in self.personas.values()
        ]
    
    def select_optimal_persona(
        self, 
        candidate_skills: List[str],
        interview_type: str = "technical",
        experience_level: str = "intermediate"
    ) -> str:
        """Select the most appropriate persona based on candidate profile"""
        
        if not candidate_skills:
            candidate_skills = ["general"]
        
        skill_matches = {}
        
        for persona_id, persona in self.personas.items():
            # Calculate skill overlap
            overlap = len(set(candidate_skills) & set(persona.specialties))
            skill_matches[persona_id] = overlap
        
        # Find personas with highest skill overlap
        max_overlap = max(skill_matches.values()) if skill_matches.values() else 0
        best_personas = [pid for pid, overlap in skill_matches.items() if overlap == max_overlap]
        
        # Default selection logic
        if best_personas:
            selected = random.choice(best_personas)
        else:
            selected = "technical_lead"  # Default fallback
        
        logger.info(f"Selected persona {selected} for skills {candidate_skills}")
        return selected
    
    def generate_persona_response(
        self,
        persona_id: str,
        context: str,
        response_type: str = "question",
        candidate_answer: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a response in the persona's voice and style - Streamlit Compatible"""
        
        persona = self.get_persona(persona_id)
        if not persona:
            raise ValueError(f"Persona {persona_id} not found")
        
        # Update session tracking using Streamlit session state
        if session_id or "session_id" in st.session_state:
            session_key = session_id or st.session_state.get("session_id", "default")
            st.session_state.active_personas[session_key] = persona_id
        
        response_data = {
            "persona_id": persona_id,
            "persona_name": persona.name,
            "avatar": persona.avatar,
            "response_type": response_type,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            if response_type == "greeting":
                response_data["content"] = self._generate_greeting(persona)
            elif response_type == "encouragement":
                response_data["content"] = self._generate_encouragement(persona)
            else:
                response_data["content"] = "I'd like to continue our conversation."
        
        except Exception as e:
            logger.error(f"Error generating persona response: {e}")
            response_data["content"] = "Let me ask you another question to continue our discussion."
        
        return response_data
    
    def _generate_greeting(self, persona: InterviewPersona) -> str:
        """Generate persona-specific greeting"""
        
        greetings = {
            PersonalityType.ANALYTICAL: [
                f"Hello! I'm {persona.name}, {persona.title}. I'm looking forward to discussing your technical background.",
                f"Hi there! {persona.name} here. I'll be evaluating your technical skills today.",
                f"Welcome! I'm {persona.name}. Let's dive into some technical challenges."
            ],
            PersonalityType.EMPATHETIC: [
                f"Hi! I'm {persona.name}, {persona.title}. I'm excited to learn about your background.",
                f"Hello! {persona.name} here. I want to understand your experiences and motivations.",
                f"Welcome! I'm {persona.name}. Let's have a conversation about your journey."
            ]
        }
        
        greeting_options = greetings.get(persona.personality_type, greetings[PersonalityType.ANALYTICAL])
        return random.choice(greeting_options)
    
    def _generate_encouragement(self, persona: InterviewPersona) -> str:
        """Generate persona-specific encouragement"""
        return random.choice(persona.behavior.encouragement_phrases)
