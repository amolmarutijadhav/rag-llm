"""
OpenAI provider implementations for embedding and LLM services.
"""

from typing import List, Dict, Any, Union
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider
from .base_provider import BaseProvider


class OpenAIEmbeddingProvider(BaseProvider, EmbeddingProvider):
    """OpenAI embedding service provider."""
    
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
        super().__init__(config)
        self.api_url = config.get("api_url", "https://api.openai.com/v1/embeddings")
        self.api_key = config.get("api_key")
        self.model = config.get("model", "text-embedding-ada-002")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for text chunks using OpenAI API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            Exception: If embedding generation fails
        """
        try:
            payload = {
                "input": texts,
                "model": self.model
            }
            
            headers = self._get_headers(self.api_key)
            response = await self._make_request("POST", self.api_url, headers, json_data=payload)
            
            data = response.json()
            return [item["embedding"] for item in data["data"]]
            
        except Exception as e:
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


class OpenAILLMProvider(BaseProvider, LLMProvider):
    """OpenAI LLM service provider."""
    
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
        super().__init__(config)
        self.api_url = config.get("api_url", "https://api.openai.com/v1/chat/completions")
        self.api_key = config.get("api_key")
        self.default_model = config.get("default_model", "gpt-3.5-turbo")
        self.default_temperature = config.get("default_temperature", 0.1)
        self.default_max_tokens = config.get("default_max_tokens", 1000)
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
    
    async def call_llm(self, messages: List[Dict[str, str]], model: str = None, 
                      temperature: float = None, max_tokens: int = None) -> str:
        """
        Make a simple LLM call and return the content string.
        
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
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        return await self.call_llm_api(payload, return_full_response=False)
    
    async def call_llm_api(self, request: Dict[str, Any], return_full_response: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Make a flexible LLM API call.
        
        Args:
            request: Complete request dictionary
            return_full_response: If True, return full response dict; if False, return content string
            
        Returns:
            Either content string or full response dictionary
        """
        try:
            headers = self._get_headers(self.api_key)
            response = await self._make_request("POST", self.api_url, headers, json_data=request)
            
            data = response.json()
            
            if return_full_response:
                return data
            else:
                return data["choices"][0]["message"]["content"]
                
        except Exception as e:
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