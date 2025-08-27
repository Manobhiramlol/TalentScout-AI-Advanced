"""
Security manager for TalentScout AI
Input validation, rate limiting, and security controls
"""

import hashlib
import hmac
import logging
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import secrets
import json

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Security event for logging and monitoring"""
    event_type: str
    session_id: str
    description: str
    severity: str  # low, medium, high, critical
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RateLimitInfo:
    """Rate limiting information"""
    requests: deque = field(default_factory=deque)
    blocked_until: Optional[datetime] = None
    total_requests: int = 0
    blocked_count: int = 0

class SecurityManager:
    """Comprehensive security manager for TalentScout AI"""
    
    def __init__(self):
        # Rate limiting configuration
        self.rate_limits = {
            "message": {"max_requests": 30, "time_window": 60},  # 30 messages per minute
            "api": {"max_requests": 100, "time_window": 3600},   # 100 API calls per hour
            "login": {"max_requests": 5, "time_window": 300}     # 5 login attempts per 5 minutes
        }
        
        # Rate limiting storage
        self.rate_limit_data: Dict[str, RateLimitInfo] = defaultdict(RateLimitInfo)
        
        # Security patterns
        self.malicious_patterns = [
            # Script injection
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            
            # SQL injection
            r'union\s+select',
            r'drop\s+table',
            r'insert\s+into',
            r'delete\s+from',
            
            # Command injection
            r'[;&|`]',
            r'\$\(',
            r'eval\s*\(',
            
            # Path traversal
            r'\.\./',
            r'\.\.\\',
            
            # Suspicious content
            r'<iframe',
            r'<object',
            r'<embed',
        ]
        
        # Compiled patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.malicious_patterns]
        
        # Session tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        
        # Security events log
        self.security_events: List[SecurityEvent] = []
        
        logger.info("✅ SecurityManager initialized with comprehensive protection")
    
    def validate_input(self, text: str, input_type: str = "message") -> Tuple[bool, List[str]]:
        """
        Comprehensive input validation
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        
        issues = []
        
        # Basic validation
        if not text or not isinstance(text, str):
            issues.append("Input must be a non-empty string")
            return False, issues
        
        # Length validation
        max_lengths = {
            "message": 5000,
            "name": 100,
            "email": 254,
            "position": 200,
            "skill": 50
        }
        
        max_length = max_lengths.get(input_type, 1000)
        if len(text) > max_length:
            issues.append(f"Input too long (max {max_length} characters)")
        
        # Minimum length check
        if input_type == "message" and len(text.strip()) < 2:
            issues.append("Message too short (minimum 2 characters)")
        
        # Security pattern check
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                issues.append("Input contains potentially harmful content")
                self._log_security_event(
                    "malicious_input_detected",
                    "unknown",
                    f"Detected malicious pattern in {input_type}",
                    "high",
                    {"input_type": input_type, "pattern_found": True}
                )
                break
        
        # Content quality checks
        if input_type == "message":
            # Check for excessive repetition
            if self._has_excessive_repetition(text):
                issues.append("Input contains excessive repetition")
            
            # Check for nonsensical content
            if self._is_nonsensical_content(text):
                issues.append("Input appears to be nonsensical")
        
        # Email-specific validation
        if input_type == "email":
            if not self._validate_email_format(text):
                issues.append("Invalid email format")
        
        is_valid = len(issues) == 0
        
        if not is_valid:
            logger.warning(f"Input validation failed: {issues}")
        
        return is_valid, issues
    
    def check_rate_limit(self, identifier: str, limit_type: str = "message") -> Tuple[bool, Dict[str, Any]]:
        """
        Check rate limiting for user actions
        
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        
        current_time = datetime.now()
        limit_config = self.rate_limits.get(limit_type, self.rate_limits["message"])
        
        # Get or create rate limit info
        rate_info = self.rate_limit_data[f"{identifier}_{limit_type}"]
        
        # Clean old requests
        time_window = timedelta(seconds=limit_config["time_window"])
        cutoff_time = current_time - time_window
        
        while rate_info.requests and rate_info.requests[0] < cutoff_time:
            rate_info.requests.popleft()
        
        # Check if currently blocked
        if rate_info.blocked_until and current_time < rate_info.blocked_until:
            return False, {
                "allowed": False,
                "reason": "rate_limit_blocked",
                "blocked_until": rate_info.blocked_until,
                "requests_count": len(rate_info.requests)
            }
        
        # Check rate limit
        max_requests = limit_config["max_requests"]
        current_requests = len(rate_info.requests)
        
        if current_requests >= max_requests:
            # Block for increasing duration based on violations
            block_duration = min(300, 60 * (rate_info.blocked_count + 1))  # Max 5 minutes
            rate_info.blocked_until = current_time + timedelta(seconds=block_duration)
            rate_info.blocked_count += 1
            
            self._log_security_event(
                "rate_limit_exceeded",
                identifier,
                f"Rate limit exceeded for {limit_type}",
                "medium",
                {
                    "limit_type": limit_type,
                    "requests_count": current_requests,
                    "max_requests": max_requests,
                    "block_duration": block_duration
                }
            )
            
            return False, {
                "allowed": False,
                "reason": "rate_limit_exceeded",
                "blocked_until": rate_info.blocked_until,
                "requests_count": current_requests,
                "max_requests": max_requests
            }
        
        # Allow request and record it
        rate_info.requests.append(current_time)
        rate_info.total_requests += 1
        
        return True, {
            "allowed": True,
            "requests_count": current_requests + 1,
            "max_requests": max_requests,
            "reset_time": current_time + time_window
        }
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize input text by removing potentially harmful content"""
        
        if not text:
            return ""
        
        # Remove potential HTML/script tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove potential SQL injection patterns
        text = re.sub(r'[\'";]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        return text.strip()
    
    def generate_session_token(self, user_data: Dict[str, Any]) -> str:
        """Generate secure session token"""
        
        # Create payload
        payload = {
            "timestamp": datetime.now().isoformat(),
            "user_data": user_data,
            "nonce": secrets.token_hex(16)
        }
        
        # Create signature
        payload_string = json.dumps(payload, sort_keys=True)
        token = secrets.token_urlsafe(32)
        
        # Store session
        self.active_sessions[token] = {
            "created_at": datetime.now(),
            "user_data": user_data,
            "last_activity": datetime.now(),
            "request_count": 0
        }
        
        logger.info(f"Generated session token for user")
        return token
    
    def validate_session_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate session token and return user data if valid"""
        
        if not token or token not in self.active_sessions:
            return False, None
        
        session_data = self.active_sessions[token]
        
        # Check session age (24 hours max)
        if datetime.now() - session_data["created_at"] > timedelta(hours=24):
            del self.active_sessions[token]
            return False, None
        
        # Check inactivity (2 hours max)
        if datetime.now() - session_data["last_activity"] > timedelta(hours=2):
            del self.active_sessions[token]
            return False, None
        
        # Update last activity
        session_data["last_activity"] = datetime.now()
        session_data["request_count"] += 1
        
        return True, session_data["user_data"]
    
    def check_content_policy(self, text: str) -> Tuple[bool, List[str]]:
        """Check if content violates content policy"""
        
        violations = []
        
        # Check for inappropriate content
        inappropriate_patterns = [
            r'\b(hate|violence|harassment)\b',
            r'\b(personal|private|confidential)\s+information\b',
            r'\b(password|credit card|ssn|social security)\b'
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append("Content may violate community guidelines")
                break
        
        # Check for spam-like content
        if self._is_spam_like(text):
            violations.append("Content appears to be spam")
        
        is_compliant = len(violations) == 0
        
        if not is_compliant:
            self._log_security_event(
                "content_policy_violation",
                "unknown",
                "Content policy violation detected",
                "medium",
                {"violations": violations}
            )
        
        return is_compliant, violations
    
    def get_security_report(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate security report for monitoring"""
        
        current_time = datetime.now()
        
        # Filter events
        if session_id:
            events = [e for e in self.security_events if e.session_id == session_id]
        else:
            events = self.security_events[-100:]  # Last 100 events
        
        # Count events by type
        event_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for event in events:
            event_counts[event.event_type] += 1
            severity_counts[event.severity] += 1
        
        # Rate limiting stats
        total_blocked = sum(info.blocked_count for info in self.rate_limit_data.values())
        active_blocks = sum(1 for info in self.rate_limit_data.values() 
                          if info.blocked_until and current_time < info.blocked_until)
        
        return {
            "timestamp": current_time.isoformat(),
            "session_id": session_id,
            "total_events": len(events),
            "event_types": dict(event_counts),
            "severity_distribution": dict(severity_counts),
            "rate_limiting": {
                "total_blocked": total_blocked,
                "currently_blocked": active_blocks,
                "active_sessions": len(self.active_sessions)
            },
            "recent_events": [
                {
                    "type": e.event_type,
                    "severity": e.severity,
                    "description": e.description,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in events[-10:]  # Last 10 events
            ]
        }
    
    def _validate_email_format(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _has_excessive_repetition(self, text: str) -> bool:
        """Check for excessive character or word repetition"""
        
        # Character repetition (more than 5 consecutive same characters)
        if re.search(r'(.)\1{5,}', text):
            return True
        
        # Word repetition (same word more than 3 times)
        words = text.lower().split()
        word_counts = defaultdict(int)
        for word in words:
            if len(word) > 2:  # Only check words longer than 2 characters
                word_counts[word] += 1
                if word_counts[word] > 3:
                    return True
        
        return False
    
    def _is_nonsensical_content(self, text: str) -> bool:
        """Basic check for nonsensical content"""
        
        # Very high ratio of numbers/symbols to letters
        alpha_count = sum(1 for c in text if c.isalpha())
        total_count = len(text)
        
        if total_count > 10 and alpha_count / total_count < 0.3:
            return True
        
        # Random character sequences
        if re.search(r'[a-zA-Z]{20,}[0-9]{10,}', text):
            return True
        
        return False
    
    def _is_spam_like(self, text: str) -> bool:
        """Check for spam-like characteristics"""
        
        # Excessive caps
        caps_count = sum(1 for c in text if c.isupper())
        if caps_count > len(text) * 0.7 and len(text) > 20:
            return True
        
        # Excessive punctuation
        punct_count = sum(1 for c in text if c in '!?.,;:')
        if punct_count > len(text) * 0.3:
            return True
        
        return False
    
    def _log_security_event(self, event_type: str, session_id: str, description: str, 
                          severity: str, metadata: Optional[Dict[str, Any]] = None):
        """Log security event"""
        
        event = SecurityEvent(
            event_type=event_type,
            session_id=session_id,
            description=description,
            severity=severity,
            metadata=metadata or {}
        )
        
        self.security_events.append(event)
        
        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
        
        # Log to system logger based on severity
        log_message = f"Security Event [{severity.upper()}]: {event_type} - {description}"
        
        if severity == "critical":
            logger.critical(log_message)
        elif severity == "high":
            logger.error(log_message)
        elif severity == "medium":
            logger.warning(log_message)
        else:
            logger.info(log_message)

# Global security manager instance
security_manager = SecurityManager()
