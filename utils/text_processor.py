"""
Advanced text processing utilities for TalentScout AI
Comprehensive text analysis, keyword extraction, and communication quality assessment
"""

import re
import logging
from typing import List, Dict, Set, Tuple, Any
from collections import Counter
import string

logger = logging.getLogger(__name__)

class TextProcessor:
    """Advanced text processing for conversation analysis and content understanding"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us'
        }
        
        self.technical_keywords = {
            'programming': [
                'python', 'javascript', 'java', 'c++', 'react', 'angular', 'vue',
                'node', 'django', 'flask', 'fastapi', 'spring', 'ruby', 'php'
            ],
            'cloud_devops': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
                'terraform', 'ansible', 'git', 'ci/cd', 'devops'
            ],
            'data_ml': [
                'machine learning', 'ai', 'tensorflow', 'pytorch', 'pandas', 'numpy',
                'scikit-learn', 'data science', 'analytics', 'sql', 'nosql'
            ],
            'web_mobile': [
                'html', 'css', 'responsive', 'mobile', 'ios', 'android',
                'react native', 'flutter', 'webapp', 'frontend', 'backend'
            ]
        }
        
        self.sentiment_words = {
            'positive': [
                'excellent', 'great', 'amazing', 'wonderful', 'fantastic', 'love', 
                'enjoy', 'excited', 'passionate', 'thrilled', 'outstanding', 'perfect',
                'good', 'nice', 'happy', 'pleased', 'satisfied', 'confident'
            ],
            'negative': [
                'terrible', 'awful', 'horrible', 'bad', 'worst', 'hate', 'dislike',
                'frustrated', 'disappointed', 'upset', 'difficult', 'challenging',
                'struggle', 'problem', 'issue', 'worry', 'stress', 'confused'
            ],
            'neutral': [
                'okay', 'fine', 'average', 'normal', 'standard', 'typical',
                'usual', 'regular', 'common', 'ordinary'
            ]
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\;\:\-\'\"]', ' ', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def extract_key_topics(self, text: str, max_topics: int = 8) -> List[Tuple[str, int]]:
        """Extract key topics from text using frequency analysis with scores"""
        if not text:
            return []
        
        # Clean and tokenize
        words = self._tokenize(text.lower())
        
        # Remove stop words and short words
        meaningful_words = [
            word for word in words 
            if len(word) > 2 and word not in self.stop_words and word.isalpha()
        ]
        
        # Count frequencies
        word_counts = Counter(meaningful_words)
        
        # Get top words with their counts
        top_words = word_counts.most_common(max_topics)
        
        return top_words
    
    def detect_technical_depth(self, text: str) -> Dict[str, Any]:
        """Analyze technical depth and complexity of response"""
        if not text:
            return {"depth_score": 0, "technical_terms": [], "complexity": "low"}
        
        text_lower = text.lower()
        
        # Count technical terms by category
        technical_terms = {}
        total_tech_terms = 0
        
        for category, terms in self.technical_keywords.items():
            found_terms = [term for term in terms if term in text_lower]
            if found_terms:
                technical_terms[category] = found_terms
                total_tech_terms += len(found_terms)
        
        # Calculate text metrics
        word_count = len(text.split())
        unique_words = len(set(text.lower().split()))
        avg_word_length = sum(len(word) for word in text.split()) / max(word_count, 1)
        sentence_count = len(self.split_sentences(text))
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Technical jargon ratio
        tech_ratio = total_tech_terms / max(word_count, 1)
        
        # Vocabulary diversity
        vocabulary_diversity = unique_words / max(word_count, 1)
        
        # Depth scoring algorithm
        depth_score = min(1.0, (
            tech_ratio * 0.4 +                    # Technical term density
            vocabulary_diversity * 0.25 +         # Vocabulary richness
            min((avg_word_length - 4) / 3, 0.2) * 0.15 +  # Word complexity
            min((avg_sentence_length - 10) / 15, 0.2) * 0.1 +  # Sentence complexity
            (total_tech_terms >= 3) * 0.1        # Multiple tech domains
        ))
        
        # Complexity assessment
        if depth_score > 0.75:
            complexity = "very_high"
        elif depth_score > 0.6:
            complexity = "high"
        elif depth_score > 0.4:
            complexity = "medium"
        elif depth_score > 0.2:
            complexity = "low"
        else:
            complexity = "very_low"
        
        return {
            "depth_score": round(depth_score, 3),
            "technical_terms": technical_terms,
            "complexity": complexity,
            "metrics": {
                "word_count": word_count,
                "unique_words": unique_words,
                "avg_word_length": round(avg_word_length, 2),
                "sentence_count": sentence_count,
                "avg_sentence_length": round(avg_sentence_length, 1),
                "tech_term_count": total_tech_terms,
                "vocabulary_diversity": round(vocabulary_diversity, 3)
            }
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text with detailed breakdown"""
        if not text:
            return {"sentiment": "neutral", "confidence": 0, "scores": {}}
        
        text_lower = text.lower()
        
        # Count sentiment words
        sentiment_counts = {}
        for sentiment_type, words in self.sentiment_words.items():
            count = sum(1 for word in words if word in text_lower)
            sentiment_counts[sentiment_type] = count
        
        total_sentiment_words = sum(sentiment_counts.values())
        
        if total_sentiment_words == 0:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "scores": {"positive": 0, "negative": 0, "neutral": 1}
            }
        
        # Calculate sentiment scores
        positive_score = sentiment_counts['positive'] / total_sentiment_words
        negative_score = sentiment_counts['negative'] / total_sentiment_words
        neutral_score = sentiment_counts['neutral'] / total_sentiment_words
        
        # Determine dominant sentiment
        scores = {"positive": positive_score, "negative": negative_score, "neutral": neutral_score}
        dominant_sentiment = max(scores, key=scores.get)
        confidence = scores[dominant_sentiment]
        
        # Adjust for exclamation marks and question marks
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        if exclamation_count > 0:
            confidence = min(1.0, confidence + 0.1)
        
        return {
            "sentiment": dominant_sentiment,
            "confidence": round(confidence, 3),
            "scores": {k: round(v, 3) for k, v in scores.items()},
            "word_counts": sentiment_counts,
            "modifiers": {
                "exclamations": exclamation_count,
                "questions": question_count
            }
        }
    
    def extract_experience_indicators(self, text: str) -> List[Dict[str, Any]]:
        """Extract indicators of professional experience with context"""
        experience_patterns = [
            {
                "pattern": r'(\d+)\s+years?\s+(?:of\s+)?experience',
                "type": "years_experience",
                "weight": 1.0
            },
            {
                "pattern": r'worked\s+(?:for|at|with)\s+([A-Za-z0-9\s]+?)(?:\s|,|\.)',
                "type": "company",
                "weight": 0.8
            },
            {
                "pattern": r'(?:led|managed|developed|built|implemented|created|designed)\s+([^.]+)',
                "type": "achievement",
                "weight": 0.9
            },
            {
                "pattern": r'responsible\s+for\s+([^.]+)',
                "type": "responsibility",
                "weight": 0.7
            },
            {
                "pattern": r'(?:proficient|experienced|skilled)\s+(?:in|with)\s+([^.]+)',
                "type": "skill_claim",
                "weight": 0.6
            }
        ]
        
        indicators = []
        for pattern_info in experience_patterns:
            matches = re.findall(pattern_info["pattern"], text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                
                indicators.append({
                    "type": pattern_info["type"],
                    "content": match.strip(),
                    "weight": pattern_info["weight"],
                    "confidence": self._calculate_experience_confidence(match, pattern_info["type"])
                })
        
        # Sort by weight and confidence
        indicators.sort(key=lambda x: (x["weight"], x["confidence"]), reverse=True)
        
        return indicators[:10]  # Return top 10
    
    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences with improved accuracy"""
        if not text:
            return []
        
        # Handle common abbreviations that shouldn't trigger sentence breaks
        text = re.sub(r'\b(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr)\.', r'\g<0>~', text)
        
        # Split on sentence terminators
        sentences = re.split(r'[.!?]+\s+', text)
        
        # Restore abbreviated titles
        sentences = [s.replace('~', '.') for s in sentences if s.strip()]
        
        return sentences
    
    def extract_keywords(self, text: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Extract keywords with context and frequency"""
        if not text or not keywords:
            return []
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Count occurrences
            count = text_lower.count(keyword_lower)
            
            if count > 0:
                # Find contexts (sentences containing the keyword)
                contexts = []
                sentences = self.split_sentences(text)
                
                for sentence in sentences:
                    if keyword_lower in sentence.lower():
                        contexts.append(sentence.strip())
                
                found_keywords.append({
                    "keyword": keyword,
                    "count": count,
                    "contexts": contexts[:3],  # First 3 contexts
                    "relevance_score": self._calculate_keyword_relevance(keyword, text, count)
                })
        
        # Sort by relevance score
        found_keywords.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return found_keywords
    
    def analyze_communication_style(self, text: str) -> Dict[str, Any]:
        """Comprehensive analysis of communication style"""
        if not text:
            return {"style": "unclear", "confidence": 0, "characteristics": {}}
        
        # Style indicators
        formal_indicators = len(re.findall(
            r'\b(?:therefore|however|furthermore|moreover|consequently|nevertheless|nonetheless)\b', 
            text, re.IGNORECASE
        ))
        
        casual_indicators = len(re.findall(
            r'\b(?:gonna|wanna|kinda|yeah|okay|cool|awesome|totally|basically)\b', 
            text, re.IGNORECASE
        ))
        
        technical_indicators = sum(
            len(terms) for terms in self.technical_keywords.values() 
            for term in terms if term in text.lower()
        )
        
        professional_indicators = len(re.findall(
            r'\b(?:utilize|implement|facilitate|optimize|collaborate|coordinate|execute)\b',
            text, re.IGNORECASE
        ))
        
        # Text structure analysis
        sentences = self.split_sentences(text)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        word_count = len(text.split())
        
        # Calculate style scores
        formal_score = (formal_indicators + professional_indicators) / max(word_count / 10, 1)
        casual_score = casual_indicators / max(word_count / 10, 1)
        technical_score = technical_indicators / max(word_count / 10, 1)
        
        # Determine dominant style
        style_scores = {
            "formal": formal_score,
            "casual": casual_score,
            "technical": technical_score
        }
        
        # Consider sentence length
        if avg_sentence_length > 20:
            style_scores["formal"] += 0.2
        elif avg_sentence_length < 10:
            style_scores["casual"] += 0.1
        
        dominant_style = max(style_scores, key=style_scores.get)
        confidence = min(1.0, style_scores[dominant_style])
        
        # If scores are close, classify as balanced
        if max(style_scores.values()) - min(style_scores.values()) < 0.3:
            dominant_style = "balanced"
            confidence = 0.6
        
        return {
            "style": dominant_style,
            "confidence": round(confidence, 3),
            "characteristics": {
                "avg_sentence_length": round(avg_sentence_length, 1),
                "formal_indicators": formal_indicators,
                "casual_indicators": casual_indicators,
                "technical_indicators": technical_indicators,
                "professional_indicators": professional_indicators,
                "word_count": word_count,
                "sentence_count": len(sentences)
            },
            "style_scores": {k: round(v, 3) for k, v in style_scores.items()}
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text)
        return [word for word in text.split() if word]
    
    def _calculate_experience_confidence(self, content: str, indicator_type: str) -> float:
        """Calculate confidence score for experience indicators"""
        if not content:
            return 0.0
        
        # Base confidence by type
        base_confidence = {
            "years_experience": 0.9,
            "company": 0.7,
            "achievement": 0.8,
            "responsibility": 0.6,
            "skill_claim": 0.5
        }
        
        confidence = base_confidence.get(indicator_type, 0.5)
        
        # Adjust based on content length and specificity
        if len(content) > 50:
            confidence += 0.1
        elif len(content) < 10:
            confidence -= 0.1
        
        # Check for specific technical terms
        tech_term_count = sum(
            1 for category_terms in self.technical_keywords.values()
            for term in category_terms if term in content.lower()
        )
        
        if tech_term_count > 0:
            confidence += min(0.2, tech_term_count * 0.05)
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_keyword_relevance(self, keyword: str, text: str, count: int) -> float:
        """Calculate relevance score for a keyword"""
        text_length = len(text.split())
        
        # Base relevance from frequency
        frequency_score = min(1.0, count / max(text_length / 50, 1))
        
        # Boost if keyword appears in important positions (beginning/end)
        position_boost = 0.0
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        if text_lower.startswith(keyword_lower) or text_lower.endswith(keyword_lower):
            position_boost = 0.2
        
        # Boost if keyword is a technical term
        tech_boost = 0.0
        if any(keyword_lower in terms for terms in self.technical_keywords.values()):
            tech_boost = 0.3
        
        relevance_score = frequency_score + position_boost + tech_boost
        
        return min(1.0, relevance_score)

# Global instance
text_processor = TextProcessor()
