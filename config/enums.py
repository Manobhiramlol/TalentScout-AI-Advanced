"""
Enums and constants for TalentScout AI
Centralized definitions for interview stages, roles, and system states
"""

from enum import Enum
# At top of config/enums.py
from .settings import Settings

# Or remove this line completely if not needed:
# settings = Settings()  ← Remove this line


class InterviewStage(str, Enum):
    """Interview progression stages"""
    GREETING = "greeting"
    INFO_COLLECTION = "info_collection"
    TECHNICAL_ASSESSMENT = "technical_assessment"
    BEHAVIORAL_ASSESSMENT = "behavioral_assessment"
    PROBLEM_SOLVING = "problem_solving"
    WRAP_UP = "wrap_up"
    COMPLETED = "completed"

class MessageRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class PersonalityType(str, Enum):
    """AI interviewer personality types"""
    ANALYTICAL = "analytical"
    EMPATHETIC = "empathetic"
    DIRECT = "direct"
    COLLABORATIVE = "collaborative"
    INNOVATIVE = "innovative"

class QuestionType(str, Enum):
    """Types of interview questions"""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PROBLEM_SOLVING = "problem_solving"
    CULTURAL_FIT = "cultural_fit"
    FOLLOW_UP = "follow_up"

class SessionStatus(str, Enum):
    """Interview session status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

# System Constants
SYSTEM_CONSTANTS = {
    "APP_NAME": "TalentScout AI Advanced",
    "VERSION": "2.0.0",
    "MAX_SESSION_DURATION_HOURS": 2,
    "MIN_RESPONSE_LENGTH": 5,
    "MAX_RESPONSE_LENGTH": 5000,
    "DEFAULT_AI_TEMPERATURE": 0.7,
    "DEFAULT_MAX_TOKENS": 600
}

# Interview Configuration
INTERVIEW_CONFIG = {
    "STAGES": {
        InterviewStage.GREETING: {"min_questions": 1, "max_questions": 2},
        InterviewStage.INFO_COLLECTION: {"min_questions": 4, "max_questions": 6},
        InterviewStage.TECHNICAL_ASSESSMENT: {"min_questions": 3, "max_questions": 8},
        InterviewStage.BEHAVIORAL_ASSESSMENT: {"min_questions": 2, "max_questions": 5},
        InterviewStage.PROBLEM_SOLVING: {"min_questions": 1, "max_questions": 3},
        InterviewStage.WRAP_UP: {"min_questions": 1, "max_questions": 2}
    },
    "PROGRESS_WEIGHTS": {
        InterviewStage.GREETING: 5,
        InterviewStage.INFO_COLLECTION: 20,
        InterviewStage.TECHNICAL_ASSESSMENT: 40,
        InterviewStage.BEHAVIORAL_ASSESSMENT: 25,
        InterviewStage.PROBLEM_SOLVING: 8,
        InterviewStage.WRAP_UP: 2
    }
}

# Technical skill categories for dynamic question generation
TECHNICAL_SKILLS = {
    "programming_languages": [
        "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", 
        "TypeScript", "PHP", "Ruby", "Swift", "Kotlin"
    ],
    "web_frameworks": [
        "React", "Angular", "Vue.js", "Django", "Flask", "FastAPI",
        "Express.js", "Spring", "Rails", "Laravel"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", 
        "Oracle", "Cassandra", "DynamoDB", "Elasticsearch"
    ],
    "cloud_platforms": [
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes",
        "Terraform", "Jenkins", "GitLab CI", "GitHub Actions"
    ],
    "data_science": [
        "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch",
        "Jupyter", "R", "Matplotlib", "Plotly", "Apache Spark"
    ]
}

def get_settings():
    """Get settings instance"""
    return Settings()

# Global settings
settings = get_settings()
