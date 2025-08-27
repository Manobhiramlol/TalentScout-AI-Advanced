"""
Rate limiting utilities for TalentScout AI API calls
"""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter for API calls"""
    
    def __init__(self, max_calls: int = 60, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(deque)  # user_id -> deque of timestamps
    
    def is_allowed(self, user_id: str = "default") -> bool:
        """Check if user is allowed to make a call"""
        current_time = time.time()
        user_calls = self.calls[user_id]
        
        # Remove old calls outside time window
        while user_calls and current_time - user_calls[0] > self.time_window:
            user_calls.popleft()
        
        # Check if under limit
        if len(user_calls) < self.max_calls:
            user_calls.append(current_time)
            return True
        
        return False
    
    def get_reset_time(self, user_id: str = "default") -> Optional[float]:
        """Get time until rate limit resets"""
        user_calls = self.calls[user_id]
        if not user_calls:
            return None
        
        oldest_call = user_calls[0]
        reset_time = oldest_call + self.time_window
        return max(0, reset_time - time.time())

class APIRateLimiter:
    """Specific rate limiter for external API calls"""
    
    def __init__(self):
        # Different limits for different APIs
        self.limiters = {
            'groq': RateLimiter(max_calls=30, time_window=60),  # 30 calls per minute
            'openai': RateLimiter(max_calls=20, time_window=60),  # 20 calls per minute
            'general': RateLimiter(max_calls=100, time_window=60)  # General limit
        }
    
    def check_limit(self, api_name: str, user_id: str = "default") -> Dict[str, any]:
        """Check rate limit for specific API"""
        limiter = self.limiters.get(api_name, self.limiters['general'])
        
        allowed = limiter.is_allowed(user_id)
        reset_time = limiter.get_reset_time(user_id)
        
        return {
            "allowed": allowed,
            "reset_time": reset_time,
            "api": api_name
        }
    
    def wait_if_needed(self, api_name: str, user_id: str = "default") -> bool:
        """Wait if rate limit exceeded (blocking)"""
        result = self.check_limit(api_name, user_id)
        
        if not result["allowed"] and result["reset_time"]:
            wait_time = min(result["reset_time"], 60)  # Max wait 60 seconds
            logger.info(f"Rate limit exceeded for {api_name}. Waiting {wait_time:.1f} seconds.")
            time.sleep(wait_time)
            return True
        
        return False

# Global instances
api_rate_limiter = APIRateLimiter()
general_rate_limiter = RateLimiter()
