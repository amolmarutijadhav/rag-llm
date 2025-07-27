"""
OpenAI provider implementations for embedding and LLM services with enhanced logging.
"""

from typing import List, Dict, Any, Union
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider
from .enhanced_base_provider import EnhancedBaseProvider
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class OpenAIEmbeddingProvider(EnhancedBaseProvider, EmbeddingProvider):
    """OpenAI embedding service provider with enhanced logging."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI embedding provider.
        
        Args:
            config: Configuration dictionary containing:
                - api_url: OpenAI embeddings API URL
                - api_key: OpenAI API key
                - model: Embedding model name
                - auth_scheme: Authentication scheme (default: "bearer")
        """
        # Add provider name to config for logging
        config["provider_name"] = "openai_embeddings"
        super().__init__(config)
        self.api_url = config.get("api_url", "https://api.openai.com/v1/embeddings")
        self.api_key = config.get("api_key")
        self.model = config.get("model", "text-embedding-ada-002")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        logger.info("OpenAI Embedding Provider initialized", extra={
            'extra_fields': {
                'event_type': 'provider_initialized',
                'provider': 'openai_embeddings',
                'model': self.model,
                'api_url': self.api_url
            }
        })
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for text chunks using OpenAI API with enhanced logging.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            Exception: If embedding generation fails
        """
        logger.debug(f"Getting embeddings for {len(texts)} texts", extra={
            'extra_fields': {
                'event_type': 'embedding_request_start',
                'provider': 'openai_embeddings',
                'text_count': len(texts),
                'model': self.model
            }
        })
        
        try:
            payload = {
                "input": texts,
                "model": self.model
            }
            
            headers = self._get_headers(self.api_key)
            response = await self._make_request("POST", self.api_url, headers, json_data=payload)
            
            data = response.json()
            embeddings = [item["embedding"] for item in data["data"]]
            
            logger.info(f"Successfully generated embeddings", extra={
                'extra_fields': {
                    'event_type': 'embedding_request_success',
                    'provider': 'openai_embeddings',
                    'text_count': len(texts),
                    'embedding_count': len(embeddings),
                    'model': self.model
                }
            })
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings", extra={
                'extra_fields': {
                    'event_type': 'embedding_request_failure',
                    'provider': 'openai_embeddings',
                    'text_count': len(texts),
                    'model': self.model,
                    'error': str(e)
                }
            })
            raise Exception(f"OpenAI embedding API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the OpenAI embedding model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "provider": "openai",
            "model": self.model,
            "api_url": self.api_url,
            "vector_size": 1536 if "ada-002" in self.model else 3072  # Default sizes
        }


class OpenAILLMProvider(EnhancedBaseProvider, LLMProvider):
    """OpenAI LLM service provider with enhanced logging."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI LLM provider.
        
        Args:
            config: Configuration dictionary containing:
                - api_url: OpenAI chat completions API URL
                - api_key: OpenAI API key
                - default_model: Default model name
                - default_temperature: Default temperature
                - default_max_tokens: Default max tokens
                - auth_scheme: Authentication scheme (default: "bearer")
        """
        # Add provider name to config for logging
        config["provider_name"] = "openai_llm"
        super().__init__(config)
        self.api_url = config.get("api_url", "https://api.openai.com/v1/chat/completions")
        self.api_key = config.get("api_key")
        self.default_model = config.get("default_model", "gpt-3.5-turbo")
        self.default_temperature = config.get("default_temperature", 0.1)
        self.default_max_tokens = config.get("default_max_tokens", 1000)
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        logger.info("OpenAI LLM Provider initialized", extra={
            'extra_fields': {
                'event_type': 'provider_initialized',
                'provider': 'openai_llm',
                'default_model': self.default_model,
                'api_url': self.api_url
            }
        })
    
    async def call_llm(self, messages: List[Dict[str, str]], model: str = None, 
                      temperature: float = None, max_tokens: int = None) -> str:
        """
        Make a simple LLM call and return the content string with enhanced logging.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use (uses default if not provided)
            temperature: Sampling temperature (uses default if not provided)
            max_tokens: Maximum tokens to generate (uses default if not provided)
            
        Returns:
            Generated text content as string
        """
        # Use defaults if not provided
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        
        logger.debug(f"Making LLM call", extra={
            'extra_fields': {
                'event_type': 'llm_request_start',
                'provider': 'openai_llm',
                'model': model,
                'message_count': len(messages),
                'temperature': temperature,
                'max_tokens': max_tokens
            }
        })
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        return await self.call_llm_api(payload, return_full_response=False)
    
    async def call_llm_api(self, request: Dict[str, Any], return_full_response: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Make a flexible LLM API call with enhanced logging.
        
        Args:
            request: Complete request dictionary
            return_full_response: If True, return full response dict; if False, return content string
            
        Returns:
            Either content string or full response dictionary
        """
        logger.debug(f"Making LLM API call", extra={
            'extra_fields': {
                'event_type': 'llm_api_request_start',
                'provider': 'openai_llm',
                'model': request.get('model'),
                'return_full_response': return_full_response
            }
        })
        
        try:
            headers = self._get_headers(self.api_key)
            response = await self._make_request("POST", self.api_url, headers, json_data=request)
            
            data = response.json()
            
            if return_full_response:
                logger.info(f"LLM API call successful (full response)", extra={
                    'extra_fields': {
                        'event_type': 'llm_api_request_success',
                        'provider': 'openai_llm',
                        'model': request.get('model'),
                        'response_type': 'full'
                    }
                })
                return data
            else:
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.info(f"LLM API call successful", extra={
                    'extra_fields': {
                        'event_type': 'llm_api_request_success',
                        'provider': 'openai_llm',
                        'model': request.get('model'),
                        'response_type': 'content',
                        'content_length': len(content)
                    }
                })
                return content
                
        except Exception as e:
            logger.error(f"LLM API call failed", extra={
                'extra_fields': {
                    'event_type': 'llm_api_request_failure',
                    'provider': 'openai_llm',
                    'model': request.get('model'),
                    'error': str(e)
                }
            })
            raise Exception(f"OpenAI LLM API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the OpenAI LLM model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "provider": "openai",
            "default_model": self.default_model,
            "api_url": self.api_url,
            "default_temperature": self.default_temperature,
            "default_max_tokens": self.default_max_tokens
        } 