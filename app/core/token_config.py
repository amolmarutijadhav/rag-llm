"""
Centralized Token Configuration Service
Eliminates hardcoding and provides clean token management
"""

import os
from dataclasses import dataclass
from typing import Optional
from app.core.config import Config


@dataclass
class TokenConfig:
    """Simplified token configuration with validation"""
    
    # Response generation limits
    max_response_tokens: int = 4000
    min_response_tokens: int = 100
    
    # Context limits
    max_context_tokens: int = 8000
    max_total_tokens: int = 16000
    
    # Validation ranges
    MAX_RESPONSE_TOKENS = 8000
    MIN_RESPONSE_TOKENS = 50
    MAX_CONTEXT_TOKENS = 32000
    MIN_CONTEXT_TOKENS = 1000
    MAX_TOTAL_TOKENS = 128000
    MIN_TOTAL_TOKENS = 2000
    
    def __post_init__(self):
        """Validate token limits after initialization"""
        self._validate_limits()
    
    def _validate_limits(self):
        """Validate all token limits are within reasonable ranges"""
        if not self.MIN_RESPONSE_TOKENS <= self.max_response_tokens <= self.MAX_RESPONSE_TOKENS:
            raise ValueError(
                f"max_response_tokens ({self.max_response_tokens}) must be between "
                f"{self.MIN_RESPONSE_TOKENS} and {self.MAX_RESPONSE_TOKENS}"
            )
        
        if not self.MIN_CONTEXT_TOKENS <= self.max_context_tokens <= self.MAX_CONTEXT_TOKENS:
            raise ValueError(
                f"max_context_tokens ({self.max_context_tokens}) must be between "
                f"{self.MIN_CONTEXT_TOKENS} and {self.MAX_CONTEXT_TOKENS}"
            )
        
        if not self.MIN_TOTAL_TOKENS <= self.max_total_tokens <= self.MAX_TOTAL_TOKENS:
            raise ValueError(
                f"max_total_tokens ({self.max_total_tokens}) must be between "
                f"{self.MIN_TOTAL_TOKENS} and {self.MAX_TOTAL_TOKENS}"
            )
        
        # Ensure total tokens can accommodate context + response
        if self.max_context_tokens + self.max_response_tokens > self.max_total_tokens:
            raise ValueError(
                f"max_context_tokens ({self.max_context_tokens}) + max_response_tokens "
                f"({self.max_response_tokens}) cannot exceed max_total_tokens ({self.max_total_tokens})"
            )
    
    def get_response_tokens(self, requested_tokens: Optional[int] = None) -> int:
        """Get validated response token limit"""
        if requested_tokens is None:
            return self.max_response_tokens
        
        return min(requested_tokens, self.max_response_tokens)
    
    def get_context_tokens(self, requested_tokens: Optional[int] = None) -> int:
        """Get validated context token limit"""
        if requested_tokens is None:
            return self.max_context_tokens
        
        return min(requested_tokens, self.max_context_tokens)
    
    def calculate_available_tokens(self, prompt_tokens: int) -> int:
        """Calculate available tokens for response given prompt size"""
        available = self.max_total_tokens - prompt_tokens
        return max(available, self.min_response_tokens)


class TokenConfigService:
    """Service for managing token configuration"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> TokenConfig:
        """Load token configuration from environment variables"""
        return TokenConfig(
            max_response_tokens=int(os.getenv("MAX_RESPONSE_TOKENS", "4000")),
            min_response_tokens=int(os.getenv("MIN_RESPONSE_TOKENS", "100")),
            max_context_tokens=int(os.getenv("MAX_CONTEXT_TOKENS", "8000")),
            max_total_tokens=int(os.getenv("MAX_TOTAL_TOKENS", "16000"))
        )
    
    def get_config(self) -> TokenConfig:
        """Get current token configuration"""
        return self.config
    
    def update_config(self, **kwargs) -> TokenConfig:
        """Update token configuration with new values"""
        current_config = self.config.__dict__.copy()
        current_config.update(kwargs)
        self.config = TokenConfig(**current_config)
        return self.config


# Global instance for dependency injection
token_config_service = TokenConfigService() 