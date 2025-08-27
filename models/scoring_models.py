"""
Advanced scoring models for candidate evaluation
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ScoreCategory(str, Enum):
    TECHNICAL = "technical"
    COMMUNICATION = "communication"
    PROBLEM_SOLVING = "problem_solving"
    CULTURAL_FIT = "cultural_fit"
    LEADERSHIP = "leadership"

@dataclass
class ScoreMetrics:
    """Individual score metrics"""
    category: ScoreCategory
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    evidence: List[str]
    feedback: str

class CandidateScorer:
    """Advanced candidate scoring system"""
    
    def __init__(self):
        self.weights = {
            ScoreCategory.TECHNICAL: 0.4,
            ScoreCategory.COMMUNICATION: 0.2,
            ScoreCategory.PROBLEM_SOLVING: 0.2,
            ScoreCategory.CULTURAL_FIT: 0.1,
            ScoreCategory.LEADERSHIP: 0.1
        }
        
        self.technical_keywords = {
            'algorithms', 'data structures', 'system design', 'debugging',
            'optimization', 'scalability', 'architecture', 'best practices',
            'testing', 'security', 'performance', 'deployment'
        }
        
        self.soft_skill_indicators = {
            'communication': ['explained', 'communicated', 'presented', 'discussed'],
            'leadership': ['led', 'managed', 'coordinated', 'mentored', 'guided'],
            'problem_solving': ['solved', 'analyzed', 'investigated', 'debugged', 'optimized'],
            'teamwork': ['collaborated', 'worked with', 'team', 'together', 'shared']
        }
    
    def score_technical_response(self, response: str, question_context: str) -> ScoreMetrics:
        """Score technical competency from response"""
        if not response:
            return ScoreMetrics(
                category=ScoreCategory.TECHNICAL,
                score=0.0,
                confidence=0.9,
                evidence=[],
                feedback="No response provided"
            )
        
        response_lower = response.lower()
        evidence = []
        score_factors = []
        
        # Technical depth analysis
        tech_terms = [term for term in self.technical_keywords if term in response_lower]
        if tech_terms:
            evidence.append(f"Used technical terms: {', '.join(tech_terms[:3])}")
            score_factors.append(min(0.4, len(tech_terms) * 0.1))
        
        # Response length and structure
        word_count = len(response.split())
        if word_count > 100:
            evidence.append("Provided detailed explanation")
            score_factors.append(0.2)
        elif word_count > 50:
            evidence.append("Gave adequate explanation")
            score_factors.append(0.1)
        
        # Specific examples or code mentions
        if any(keyword in response_lower for keyword in ['example', 'implemented', 'built', 'developed']):
            evidence.append("Provided concrete examples")
            score_factors.append(0.2)
        
        # Problem-solving approach
        if any(keyword in response_lower for keyword in ['approach', 'method', 'solution', 'strategy']):
            evidence.append("Demonstrated systematic thinking")
            score_factors.append(0.15)
        
        # Calculate final score
        base_score = sum(score_factors)
        final_score = min(1.0, base_score)
        
        # Generate feedback
        if final_score > 0.8:
            feedback = "Excellent technical depth with clear examples and systematic approach"
        elif final_score > 0.6:
            feedback = "Good technical understanding with room for more detail"
        elif final_score > 0.4:
            feedback = "Basic technical knowledge demonstrated"
        else:
            feedback = "Limited technical detail provided"
        
        return ScoreMetrics(
            category=ScoreCategory.TECHNICAL,
            score=final_score,
            confidence=0.8,
            evidence=evidence,
            feedback=feedback
        )
    
    def score_communication(self, response: str) -> ScoreMetrics:
        """Score communication skills from response"""
        if not response:
            return ScoreMetrics(
                category=ScoreCategory.COMMUNICATION,
                score=0.0,
                confidence=0.9,
                evidence=[],
                feedback="No response to evaluate"
            )
        
        evidence = []
        score_factors = []
        
        # Clarity indicators
        sentences = response.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
        
        if 10 <= avg_sentence_length <= 25:
            evidence.append("Clear sentence structure")
            score_factors.append(0.2)
        
        # Organization
        if len(sentences) > 3 and any(word in response.lower() for word in ['first', 'second', 'then', 'finally', 'also']):
            evidence.append("Well-organized response")
            score_factors.append(0.3)
        
        # Professional language
        formal_words = ['therefore', 'however', 'furthermore', 'additionally', 'consequently']
        if any(word in response.lower() for word in formal_words):
            evidence.append("Professional communication style")
            score_factors.append(0.2)
        
        # Completeness
        if len(response.split()) > 50:
            evidence.append("Comprehensive response")
            score_factors.append(0.2)
        
        final_score = min(1.0, sum(score_factors))
        
        if final_score > 0.7:
            feedback = "Strong communication with clear structure and professional tone"
        elif final_score > 0.5:
            feedback = "Good communication skills with room for improvement"
        else:
            feedback = "Communication could be clearer and more detailed"
        
        return ScoreMetrics(
            category=ScoreCategory.COMMUNICATION,
            score=final_score,
            confidence=0.7,
            evidence=evidence,
            feedback=feedback
        )
    
    def calculate_overall_score(self, individual_scores: List[ScoreMetrics]) -> Dict[str, Any]:
        """Calculate weighted overall score"""
        if not individual_scores:
            return {
                "overall_score": 0.0,
                "weighted_score": 0.0,
                "category_scores": {},
                "strengths": [],
                "areas_for_improvement": [],
                "confidence": 0.0
            }
        
        # Calculate weighted score
        weighted_sum = 0.0
        total_weight = 0.0
        category_scores = {}
        
        for score_metric in individual_scores:
            weight = self.weights.get(score_metric.category, 0.1)
            weighted_sum += score_metric.score * weight
            total_weight += weight
            category_scores[score_metric.category.value] = {
                "score": score_metric.score,
                "feedback": score_metric.feedback,
                "evidence": score_metric.evidence
            }
        
        overall_score = weighted_sum / max(total_weight, 1.0)
        
        # Identify strengths and areas for improvement
        strengths = []
        areas_for_improvement = []
        
        for score_metric in individual_scores:
            if score_metric.score > 0.7:
                strengths.append(f"{score_metric.category.value}: {score_metric.feedback}")
            elif score_metric.score < 0.5:
                areas_for_improvement.append(f"{score_metric.category.value}: {score_metric.feedback}")
        
        # Calculate confidence (average of individual confidences)
        avg_confidence = sum(score.confidence for score in individual_scores) / len(individual_scores)
        
        return {
            "overall_score": round(overall_score, 2),
            "weighted_score": round(overall_score * 100, 1),
            "category_scores": category_scores,
            "strengths": strengths,
            "areas_for_improvement": areas_for_improvement,
            "confidence": round(avg_confidence, 2),
            "total_responses_evaluated": len(individual_scores)
        }

# Global scorer instance
candidate_scorer = CandidateScorer()
