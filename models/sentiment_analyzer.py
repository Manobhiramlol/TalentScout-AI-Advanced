"""
Advanced sentiment analysis for TalentScout AI
Real-time emotion and engagement detection from candidate responses
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class SentimentLabel(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class EmotionLabel(str, Enum):
    EXCITED = "excited"
    CONFIDENT = "confident"
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"

@dataclass
class SentimentResult:
    """Comprehensive sentiment analysis result"""
    sentiment: SentimentLabel
    confidence: float
    score: float  # -1.0 to 1.0
    emotions: List[EmotionLabel]
    engagement_level: str  # high, medium, low
    key_indicators: List[str]
    analysis_timestamp: str

class AdvancedSentimentAnalyzer:
    """Advanced sentiment analyzer for interview responses"""
    
    def __init__(self):
        self.positive_words = {
            'excellent', 'great', 'amazing', 'wonderful', 'fantastic', 'love', 'enjoy',
            'excited', 'passionate', 'thrilled', 'delighted', 'impressed', 'outstanding',
            'brilliant', 'perfect', 'awesome', 'superb', 'terrific', 'marvelous',
            'good', 'nice', 'happy', 'pleased', 'satisfied', 'comfortable', 'confident'
        }
        
        self.negative_words = {
            'terrible', 'awful', 'horrible', 'bad', 'worst', 'hate', 'dislike',
            'frustrated', 'annoyed', 'disappointed', 'upset', 'angry', 'sad',
            'difficult', 'challenging', 'struggle', 'problem', 'issue', 'concern',
            'worry', 'stress', 'anxious', 'nervous', 'uncomfortable', 'confused'
        }
        
        self.confidence_indicators = {
            'certain', 'sure', 'confident', 'definitely', 'absolutely', 'clearly',
            'obviously', 'undoubtedly', 'without doubt', 'positive', 'convinced'
        }
        
        self.uncertainty_indicators = {
            'maybe', 'perhaps', 'might', 'could', 'unsure', 'uncertain', 'doubt',
            'think', 'guess', 'suppose', 'probably', 'possibly', 'not sure'
        }
        
        self.engagement_indicators = {
            'high': ['excited', 'passionate', 'love', 'enjoy', 'interested', 'fascinated'],
            'medium': ['like', 'good', 'okay', 'fine', 'decent', 'reasonable'],
            'low': ['bored', 'tired', 'whatever', 'don\'t care', 'not interested']
        }
    
    async def analyze(self, text: str) -> SentimentResult:
        """Comprehensive sentiment analysis"""
        return self.analyze_sync(text)
    
    def analyze_sync(self, text: str) -> SentimentResult:
        """Synchronous sentiment analysis"""
        
        if not text or not text.strip():
            return SentimentResult(
                sentiment=SentimentLabel.NEUTRAL,
                confidence=0.0,
                score=0.0,
                emotions=[EmotionLabel.NEUTRAL],
                engagement_level="low",
                key_indicators=[],
                analysis_timestamp=datetime.now().isoformat()
            )
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Basic sentiment scoring
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Calculate base score
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            base_score = 0.0
        else:
            base_score = (positive_count - negative_count) / total_sentiment_words
        
        # Adjust for text length and complexity
        word_count = len(words)
        if word_count > 50:
            # Longer responses tend to be more neutral
            base_score *= 0.8
        elif word_count < 10:
            # Very short responses are harder to analyze
            confidence_penalty = 0.5
        else:
            confidence_penalty = 1.0
        
        # Analyze confidence level
        confidence_count = sum(1 for word in words if word in self.confidence_indicators)
        uncertainty_count = sum(1 for word in words if word in self.uncertainty_indicators)
        
        confidence_score = (confidence_count - uncertainty_count * 0.5) / max(word_count / 10, 1)
        
        # Determine sentiment label
        if base_score > 0.6:
            sentiment = SentimentLabel.VERY_POSITIVE
        elif base_score > 0.2:
            sentiment = SentimentLabel.POSITIVE
        elif base_score > -0.2:
            sentiment = SentimentLabel.NEUTRAL
        elif base_score > -0.6:
            sentiment = SentimentLabel.NEGATIVE
        else:
            sentiment = SentimentLabel.VERY_NEGATIVE
        
        # Analyze emotions
        emotions = self._analyze_emotions(text_lower, words)
        
        # Analyze engagement level
        engagement_level = self._analyze_engagement(text_lower, word_count)
        
        # Extract key indicators
        key_indicators = self._extract_key_indicators(text_lower, positive_count, negative_count)
        
        # Calculate final confidence
        base_confidence = min(1.0, abs(base_score) + 0.3)
        final_confidence = base_confidence * confidence_penalty
        
        return SentimentResult(
            sentiment=sentiment,
            confidence=round(final_confidence, 2),
            score=round(base_score, 2),
            emotions=emotions,
            engagement_level=engagement_level,
            key_indicators=key_indicators,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _analyze_emotions(self, text_lower: str, words: List[str]) -> List[EmotionLabel]:
        """Analyze emotional content"""
        emotions = []
        
        # Excitement indicators
        if any(word in text_lower for word in ['excited', 'thrilled', 'amazing', 'awesome']):
            emotions.append(EmotionLabel.EXCITED)
        
        # Confidence indicators
        if any(word in text_lower for word in ['confident', 'sure', 'certain', 'definitely']):
            emotions.append(EmotionLabel.CONFIDENT)
        
        # Anxiety indicators
        if any(word in text_lower for word in ['nervous', 'worried', 'anxious', 'stress']):
            emotions.append(EmotionLabel.ANXIOUS)
        
        # Frustration indicators
        if any(word in text_lower for word in ['frustrated', 'annoyed', 'difficult', 'struggle']):
            emotions.append(EmotionLabel.FRUSTRATED)
        
        # Confusion indicators
        if any(word in text_lower for word in ['confused', 'unclear', 'don\'t understand', 'not sure']):
            emotions.append(EmotionLabel.CONFUSED)
        
        # Default to neutral if no specific emotions detected
        if not emotions:
            emotions.append(EmotionLabel.NEUTRAL)
        
        return emotions[:3]  # Limit to top 3 emotions
    
    def _analyze_engagement(self, text_lower: str, word_count: int) -> str:
        """Analyze engagement level"""
        
        # Check for high engagement indicators
        high_engagement = sum(1 for indicator in self.engagement_indicators['high'] if indicator in text_lower)
        
        # Check for medium engagement indicators
        medium_engagement = sum(1 for indicator in self.engagement_indicators['medium'] if indicator in text_lower)
        
        # Check for low engagement indicators
        low_engagement = sum(1 for indicator in self.engagement_indicators['low'] if indicator in text_lower)
        
        # Consider response length
        if word_count > 100:
            length_bonus = 1
        elif word_count > 30:
            length_bonus = 0.5
        else:
            length_bonus = 0
        
        # Calculate engagement score
        engagement_score = (high_engagement * 2 + medium_engagement + length_bonus) - (low_engagement * 2)
        
        if engagement_score >= 2:
            return "high"
        elif engagement_score >= 0.5:
            return "medium"
        else:
            return "low"
    
    def _extract_key_indicators(self, text_lower: str, positive_count: int, negative_count: int) -> List[str]:
        """Extract key indicators that influenced the sentiment"""
        indicators = []
        
        if positive_count > negative_count:
            # Find specific positive words used
            found_positive = [word for word in self.positive_words if word in text_lower]
            indicators.extend([f"Positive: {word}" for word in found_positive[:3]])
        
        if negative_count > 0:
            # Find specific negative words used
            found_negative = [word for word in self.negative_words if word in text_lower]
            indicators.extend([f"Negative: {word}" for word in found_negative[:2]])
        
        # Check for specific patterns
        if '!' in text_lower:
            indicators.append("Exclamation marks indicate emphasis")
        
        if '?' in text_lower:
            indicators.append("Questions indicate engagement or uncertainty")
        
        return indicators[:5]  # Limit to top 5 indicators
    
    def analyze_conversation_sentiment_trend(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment trend across conversation"""
        
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        
        if not user_messages:
            return {
                "trend": "neutral",
                "average_sentiment": 0.0,
                "engagement_trend": "stable",
                "sentiment_history": []
            }
        
        sentiment_scores = []
        engagement_levels = []
        
        for msg in user_messages:
            result = self.analyze_sync(msg.get('content', ''))
            sentiment_scores.append(result.score)
            engagement_levels.append(result.engagement_level)
        
        # Calculate trend
        if len(sentiment_scores) >= 2:
            if sentiment_scores[-1] > sentiment_scores[0]:
                trend = "improving"
            elif sentiment_scores[-1] < sentiment_scores[0]:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Calculate average sentiment
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Analyze engagement trend
        engagement_trend = self._analyze_engagement_trend(engagement_levels)
        
        return {
            "trend": trend,
            "average_sentiment": round(avg_sentiment, 2),
            "engagement_trend": engagement_trend,
            "sentiment_history": sentiment_scores,
            "total_messages_analyzed": len(user_messages)
        }
    
    def _analyze_engagement_trend(self, engagement_levels: List[str]) -> str:
        """Analyze trend in engagement levels"""
        if not engagement_levels:
            return "unknown"
        
        level_values = {"low": 1, "medium": 2, "high": 3}
        numeric_levels = [level_values.get(level, 2) for level in engagement_levels]
        
        if len(numeric_levels) >= 2:
            if numeric_levels[-1] > numeric_levels[0]:
                return "increasing"
            elif numeric_levels[-1] < numeric_levels[0]:
                return "decreasing"
            else:
                return "stable"
        else:
            return "stable"

# Create global instances
sentiment_analyzer = AdvancedSentimentAnalyzer()

# Legacy compatibility
class SentimentAnalyzer(AdvancedSentimentAnalyzer):
    """Legacy class for backward compatibility"""
    pass
