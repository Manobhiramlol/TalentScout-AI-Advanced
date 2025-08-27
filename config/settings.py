"""
Settings configuration for TalentScout AI
Environment variables and application configuration
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings with environment variable support"""
    
    def __init__(self):
        self.groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
        self.debug: bool = os.getenv("DEBUG", "False").lower() == "true"
        self.secret_key: str = os.getenv("SECRET_KEY", "talentscout-ai-secret-key")
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///talentscout.db")
        self.enable_voice: bool = os.getenv("ENABLE_VOICE", "True").lower() == "true"
        
        # AI Configuration
        self.ai_model: str = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")
        self.ai_temperature: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.max_tokens: int = int(os.getenv("MAX_TOKENS", "600"))
        
        # Interview Configuration
        self.max_questions_per_stage: int = int(os.getenv("MAX_QUESTIONS_PER_STAGE", "5"))
        self.session_timeout_minutes: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
        
        # Rate Limiting
        self.api_rate_limit: int = int(os.getenv("API_RATE_LIMIT", "30"))
        self.rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        
        # Feature Flags
        self.enable_analytics: bool = os.getenv("ENABLE_ANALYTICS", "True").lower() == "true"
        self.enable_dashboard: bool = os.getenv("ENABLE_DASHBOARD", "True").lower() == "true"
        self.enable_api: bool = os.getenv("ENABLE_API", "False").lower() == "true"
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration settings"""
        issues = []
        
        if not self.groq_api_key:
            issues.append("GROQ_API_KEY is required")
        
        if self.ai_temperature < 0.1 or self.ai_temperature > 1.0:
            issues.append("AI_TEMPERATURE must be between 0.1 and 1.0")
        
        if self.max_tokens < 50 or self.max_tokens > 2000:
            issues.append("MAX_TOKENS must be between 50 and 2000")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)"""
        return {
            "debug": self.debug,
            "ai_model": self.ai_model,
            "ai_temperature": self.ai_temperature,
            "max_tokens": self.max_tokens,
            "max_questions_per_stage": self.max_questions_per_stage,
            "session_timeout_minutes": self.session_timeout_minutes,
            "api_rate_limit": self.api_rate_limit,
            "enable_analytics": self.enable_analytics,
            "enable_dashboard": self.enable_dashboard,
            "enable_api": self.enable_api
        }

def get_settings() -> Settings:
    """Get application settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()

# Legacy compatibility classes
class DatabaseManager:
    """Simple database manager for backward compatibility"""
    def __init__(self):
        pass

# Interview personas list
INTERVIEW_PERSONAS = ["technical_lead", "friendly_hr", "senior_manager", "creative_director"]

# Skill categories for dynamic question generation
SKILL_CATEGORIES = {
    "programming": ["python", "javascript", "java", "c++", "go", "rust"],
    "frontend": ["react", "angular", "vue", "html", "css", "typescript"],
    "backend": ["django", "flask", "fastapi", "express", "spring", "rails"],
    "database": ["mysql", "postgresql", "mongodb", "redis", "elasticsearch"],
    "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "serverless"],
    "tools": ["git", "jenkins", "jira", "confluence", "slack"]
}

# Default conversation templates
CONVERSATION_TEMPLATES = {
    "greeting": "Hello! Welcome to TalentScout AI. What's your name?",
    "info_collection": "Thanks {name}! Could you share your email address?",
    "technical_start": "Let's discuss your technical background with {skills}.",
    "behavioral_start": "Now let's explore some behavioral scenarios using STAR method.",
    "conclusion": "Thank you for your time today! We'll be in touch soon."
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
