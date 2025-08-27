"""
LLM Provider abstractions for TalentScout AI
Support for multiple AI providers (Groq, OpenAI, etc.)
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

@dataclass
class LLMResponse:
    """Standardized LLM response format"""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    cost: float = 0.0
    response_time: float = 0.0
    success: bool = True
    error: Optional[str] = None

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response from messages"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass

class GroqProvider(BaseLLMProvider):
    """Groq LLM provider implementation"""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        super().__init__(api_key, model)
        
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
            self._available = True
            logger.info(f"✅ Groq provider initialized with model: {model}")
        except ImportError:
            logger.error("❌ Groq library not installed. Run: pip install groq")
            self._available = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq provider: {e}")
            self._available = False
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using Groq API"""
        
        if not self._available:
            return LLMResponse(
                content="",
                model=self.model,
                provider="groq",
                success=False,
                error="Groq provider not available"
            )
        
        try:
            import time
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 600),
                top_p=kwargs.get('top_p', 0.9),
                stream=kwargs.get('stream', False)
            )
            
            response_time = time.time() - start_time
            
            content = response.choices[0].message.content.strip()
            tokens_used = getattr(response, 'usage', {}).get('total_tokens', 0)
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider="groq",
                tokens_used=tokens_used,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"❌ Groq API call failed: {e}")
            return LLMResponse(
                content="",
                model=self.model,
                provider="groq",
                success=False,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if Groq provider is available"""
        return self._available

class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model)
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self._available = True
            logger.info(f"✅ OpenAI provider initialized with model: {model}")
        except ImportError:
            logger.error("❌ OpenAI library not installed. Run: pip install openai")
            self._available = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI provider: {e}")
            self._available = False
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using OpenAI API"""
        
        if not self._available:
            return LLMResponse(
                content="",
                model=self.model,
                provider="openai",
                success=False,
                error="OpenAI provider not available"
            )
        
        try:
            import time
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 600),
                top_p=kwargs.get('top_p', 0.9)
            )
            
            response_time = time.time() - start_time
            
            content = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Rough cost calculation (varies by model)
            cost_per_token = 0.002 / 1000  # Approximate
            cost = tokens_used * cost_per_token
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider="openai",
                tokens_used=tokens_used,
                cost=cost,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"❌ OpenAI API call failed: {e}")
            return LLMResponse(
                content="",
                model=self.model,
                provider="openai",
                success=False,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if OpenAI provider is available"""
        return self._available

class LLMManager:
    """Manage multiple LLM providers with fallback support"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.primary_provider: Optional[str] = None
        self.fallback_order: List[str] = []
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers"""
        
        # Initialize Groq provider
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            groq_provider = GroqProvider(groq_key)
            if groq_provider.is_available():
                self.providers['groq'] = groq_provider
                if not self.primary_provider:
                    self.primary_provider = 'groq'
                self.fallback_order.append('groq')
        
        # Initialize OpenAI provider
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            openai_provider = OpenAIProvider(openai_key)
            if openai_provider.is_available():
                self.providers['openai'] = openai_provider
                if not self.primary_provider:
                    self.primary_provider = 'openai'
                self.fallback_order.append('openai')
        
        logger.info(f"✅ Initialized {len(self.providers)} LLM providers")
        logger.info(f"Primary provider: {self.primary_provider}")
        logger.info(f"Fallback order: {self.fallback_order}")
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response with automatic fallback"""
        
        if not self.providers:
            return LLMResponse(
                content="",
                model="none",
                provider="none",
                success=False,
                error="No LLM providers available"
            )
        
        # Try providers in fallback order
        for provider_name in self.fallback_order:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                response = provider.generate_response(messages, **kwargs)
                
                if response.success:
                    logger.info(f"✅ Successfully generated response using {provider_name}")
                    return response
                else:
                    logger.warning(f"⚠️ {provider_name} failed: {response.error}")
        
        # All providers failed
        return LLMResponse(
            content="",
            model="fallback",
            provider="none",
            success=False,
            error="All LLM providers failed"
        )
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def set_primary_provider(self, provider_name: str) -> bool:
        """Set primary provider"""
        if provider_name in self.providers:
            self.primary_provider = provider_name
            # Move to front of fallback order
            if provider_name in self.fallback_order:
                self.fallback_order.remove(provider_name)
            self.fallback_order.insert(0, provider_name)
            logger.info(f"✅ Primary provider set to: {provider_name}")
            return True
        else:
            logger.error(f"❌ Provider {provider_name} not available")
            return False

# Global LLM manager instance
llm_manager = LLMManager()
