"""
Comprehensive input validation utilities for TalentScout AI
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class InputValidator:
    """Advanced input validation for chat interface"""
    
    def __init__(self):
        self.min_length = 1
        self.max_length = 5000
        self.blocked_patterns = [
            r'<script.*?>.*?</script>',  # Script tags
            r'javascript:',              # JavaScript protocols
            r'on\w+\s*=',               # Event handlers
        ]
    
    def validate_text_input(self, text: str) -> Dict[str, Any]:
        """Validate text input with comprehensive checks"""
        errors = []
        warnings = []
        
        # Basic checks
        if not text or not text.strip():
            errors.append("Input cannot be empty")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        # Length validation
        if len(text) < self.min_length:
            errors.append(f"Input too short (minimum {self.min_length} characters)")
        
        if len(text) > self.max_length:
            errors.append(f"Input too long (maximum {self.max_length} characters)")
        
        # Security checks
        for pattern in self.blocked_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                errors.append("Input contains potentially harmful content")
                break
        
        # Content quality checks
        if len(text.split()) < 2 and len(text) > 50:
            warnings.append("Response seems unusually brief for the input length")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "cleaned_text": self.sanitize_input(text)
        }
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_tech_stack(self, tech_stack: str) -> List[str]:
        """Validate and clean tech stack input"""
        if not tech_stack:
            return []
        
        # Split by common separators
        skills = re.split(r'[,;|\n]+', tech_stack)
        
        # Clean and filter
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            if skill and len(skill) > 1:
                cleaned_skills.append(skill.title())
        
        return cleaned_skills[:10]  # Limit to 10 skills

def validate_input(text: str) -> List[str]:
    """Legacy function for backward compatibility"""
    validator = InputValidator()
    result = validator.validate_text_input(text)
    return result.get("errors", [])

def sanitize_input(text: str) -> str:
    """Clean and sanitize input text"""
    if not text:
        return ""
    
    # Remove potential HTML/script tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Trim and return
    return text.strip()
