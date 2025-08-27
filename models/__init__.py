"""
TalentScout AI Models Package
Advanced AI models for interview processing and analysis
"""

__version__ = "2.0.0"
__author__ = "TalentScout AI Team"

from .sentiment_analyzer import SentimentAnalyzer, sentiment_analyzer
from .scoring_models import CandidateScorer, candidate_scorer
from .llm_providers import LLMProvider, GroqProvider, OpenAIProvider

__all__ = [
    'SentimentAnalyzer',
    'sentiment_analyzer', 
    'CandidateScorer',
    'candidate_scorer',
    'LLMProvider',
    'GroqProvider',
    'OpenAIProvider'
]
