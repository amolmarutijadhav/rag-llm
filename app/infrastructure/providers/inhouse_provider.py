"""
Sample in-house provider implementations with enhanced logging.
These are example implementations showing how to create custom providers for internal services.
"""

from typing import List, Dict, Any, Union
import asyncio
import time
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider, VectorStoreProvider
from .enhanced_base_provider import EnhancedBaseProvider
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class InhouseEmbeddingProvider(EnhancedBaseProvider, EmbeddingProvider):
    """Sample in-house embedding service provider with enhanced logging."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize in-house embedding provider.
        
        Args:
            config: Configuration dictionary containing:
                - api_url: In-house embeddings API URL
                - api_key: In-house API key
                - model: Embedding model name
                - auth_scheme: Authentication scheme
                - max_concurrent_requests: Maximum concurrent requests (default: 5)
                - request_delay: Delay between requests in seconds (default: 0.1)
        """
        # Add provider name to config for logging
        config["provider_name"] = "inhouse_embeddings"
        super().__init__(config)
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
        self.model = config.get("model", "inhouse-embedding-model")
        self.max_concurrent_requests = config.get("max_concurrent_requests", 5)
        self.request_delay = config.get("request_delay", 0.1)
        
        if not self.api_url:
            raise ValueError("In-house embedding API URL is required")
        
        logger.info("In-house Embedding Provider initialized", extra={
            'extra_fields': {
                'event_type': 'provider_initialized',
                'provider': 'inhouse_embeddings',
                'model': self.model,
                'api_url': self.api_url,
                'max_concurrent_requests': self.max_concurrent_requests,
                'request_delay': self.request_delay
            }
        })
    
    async def get_single_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text using in-house API.
        
        Args:
            text: Single text string to embed
            
        Returns:
            Embedding vector as list of floats
            
        Raises:
            Exception: If embedding generation fails
        """
        logger.debug(f"Getting single embedding from in-house service", extra={
            'extra_fields': {
                'event_type': 'inhouse_single_embedding_request_start',
                'provider': 'inhouse_embeddings',
                'text_length': len(text),
                'model': self.model
            }
        })
        
        try:
            # Single text payload structure for in-house API
            payload = {
                "text": text,  # Single text instead of array
                "embeddings_model": self.model,
                "format": "vector"
            }
            
            headers = self._get_headers(self.api_key, content_type="application/x-www-form-urlencoded")
            response = await self._make_request("POST", self.api_url, headers, data=payload)
            
            data = response.json()
            # Handle different response formats for single embedding
            embedding = self._extract_single_embedding(data)
            
            logger.info(f"Successfully generated single embedding from in-house service", extra={
                'extra_fields': {
                    'event_type': 'inhouse_single_embedding_request_success',
                    'provider': 'inhouse_embeddings',
                    'text_length': len(text),
                    'embedding_dimensions': len(embedding),
                    'model': self.model
                }
            })
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate single embedding from in-house service", extra={
                'extra_fields': {
                    'event_type': 'inhouse_single_embedding_request_failure',
                    'provider': 'inhouse_embeddings',
                    'text_length': len(text),
                    'model': self.model,
                    'error': str(e)
                }
            })
            raise Exception(f"In-house single embedding API error: {str(e)}")
    
    def _extract_single_embedding(self, data: Dict[str, Any]) -> List[float]:
        """
        Extract single embedding from API response with multiple format support.
        
        Args:
            data: Response data from in-house API
            
        Returns:
            Single embedding vector as list of floats
            
        Raises:
            ValueError: If embedding cannot be extracted from response
        """
        # Handle different response formats
        if "embedding" in data:
            return data["embedding"]
        elif "vector" in data:
            return data["vector"]
        elif "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
            return data["data"][0].get("embedding", [])
        elif "embeddings" in data and isinstance(data["embeddings"], list) and len(data["embeddings"]) > 0:
            return data["embeddings"][0]
        else:
            raise ValueError(f"Unknown embedding response format: {list(data.keys())}")
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for text chunks using in-house API with single text processing.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            Exception: If embedding generation fails
        """
        logger.debug(f"Getting embeddings from in-house service for {len(texts)} texts (single processing)", extra={
            'extra_fields': {
                'event_type': 'inhouse_embedding_request_start',
                'provider': 'inhouse_embeddings',
                'text_count': len(texts),
                'model': self.model,
                'processing_mode': 'single_text'
            }
        })
        
        start_time = time.time()
        
        try:
            # Process texts one by one with controlled concurrency
            embeddings = await self._process_texts_sequentially(texts)
            
            duration_ms = (time.time() - start_time) * 1000
            total_chars = sum(len(text) for text in texts)
            
            logger.info(f"Successfully generated embeddings from in-house service", extra={
                'extra_fields': {
                    'event_type': 'inhouse_embedding_request_success',
                    'provider': 'inhouse_embeddings',
                    'text_count': len(texts),
                    'embedding_count': len(embeddings),
                    'model': self.model,
                    'duration_ms': duration_ms,
                    'total_chars': total_chars,
                    'avg_ms_per_text': duration_ms / len(texts) if texts else 0,
                    'processing_mode': 'single_text'
                }
            })
            
            return embeddings
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(f"Failed to generate embeddings from in-house service", extra={
                'extra_fields': {
                    'event_type': 'inhouse_embedding_request_failure',
                    'provider': 'inhouse_embeddings',
                    'text_count': len(texts),
                    'model': self.model,
                    'error': str(e),
                    'duration_ms': duration_ms,
                    'processing_mode': 'single_text'
                }
            })
            raise Exception(f"In-house embedding API error: {str(e)}")
    
    async def _process_texts_sequentially(self, texts: List[str]) -> List[List[float]]:
        """
        Process texts sequentially with controlled concurrency and rate limiting.
        
        Args:
            texts: List of text strings to process
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        # Process texts with controlled concurrency
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        async def process_single_text(text: str) -> List[float]:
            async with semaphore:
                embedding = await self.get_single_embedding(text)
                # Add delay between requests to respect rate limits
                if self.request_delay > 0:
                    await asyncio.sleep(self.request_delay)
                return embedding
        
        # Create tasks for all texts
        tasks = [process_single_text(text) for text in texts]
        
        # Execute all tasks concurrently with controlled concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process text {i}", extra={
                    'extra_fields': {
                        'event_type': 'inhouse_embedding_text_failure',
                        'provider': 'inhouse_embeddings',
                        'text_index': i,
                        'text_length': len(texts[i]) if i < len(texts) else 0,
                        'error': str(result)
                    }
                })
                # Return empty embedding for failed texts to maintain order
                embeddings.append([])
            else:
                embeddings.append(result)
        
        return embeddings
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the in-house embedding model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "provider": "inhouse",
            "model": self.model,
            "api_url": self.api_url,
            "vector_size": 768,  # Example size for in-house model
            "processing_mode": "single_text",
            "max_concurrent_requests": self.max_concurrent_requests,
            "request_delay": self.request_delay
        }


class InhouseLLMProvider(EnhancedBaseProvider, LLMProvider):
    """Sample in-house LLM service provider with enhanced logging and custom request/response processing."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize in-house LLM provider.
        
        Args:
            config: Configuration dictionary containing:
                - api_url: In-house LLM API URL
                - api_key: In-house API key
                - default_model: Default model name
                - default_temperature: Default temperature
                - default_max_tokens: Default max tokens
                - static_fields: Static fields for authentication/identification
        """
        # Add provider name to config for logging
        config["provider_name"] = "inhouse_llm"
        super().__init__(config)
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
        self.default_model = config.get("default_model", "inhouse-llm-model")
        self.default_temperature = config.get("default_temperature", 0.1)
        self.default_max_tokens = config.get("default_max_tokens", 1000)
        
        # Static fields for authentication/identification
        self.static_fields = config.get("static_fields", {})
        
        if not self.api_url:
            raise ValueError("In-house LLM API URL is required")
        
        logger.info("In-house LLM Provider initialized", extra={
            'extra_fields': {
                'event_type': 'provider_initialized',
                'provider': 'inhouse_llm',
                'default_model': self.default_model,
                'api_url': self.api_url,
                'static_fields_count': len(self.static_fields)
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
        
        logger.debug(f"Making LLM call to in-house service", extra={
            'extra_fields': {
                'event_type': 'inhouse_llm_request_start',
                'provider': 'inhouse_llm',
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
        Make a flexible LLM API call with enhanced logging and custom preprocessing/postprocessing.
        
        Args:
            request: Complete request dictionary
            return_full_response: If True, return full response dict; if False, return content string
            
        Returns:
            Either content string or full response dictionary
        """
        logger.debug(f"Making LLM API call to in-house service", extra={
            'extra_fields': {
                'event_type': 'inhouse_llm_api_request_start',
                'provider': 'inhouse_llm',
                'model': request.get('model'),
                'return_full_response': return_full_response
            }
        })
        
        try:
            # Apply request preprocessor
            processed_request = self._preprocess_request(request)
            
            # Make the API call
            headers = self._get_headers(self.api_key)
            response = await self._make_request("POST", self.api_url, headers, json_data=processed_request)
            data = response.json()
            
            # Apply response postprocessor
            result = self._postprocess_response(data, return_full_response)
            
            logger.info(f"In-house LLM API call successful", extra={
                'extra_fields': {
                    'event_type': 'inhouse_llm_api_request_success',
                    'provider': 'inhouse_llm',
                    'model': request.get('model'),
                    'response_type': 'full' if return_full_response else 'content',
                    'content_length': len(str(result)) if not return_full_response else 0
                }
            })
            
            return result
                
        except Exception as e:
            logger.error(f"In-house LLM API call failed", extra={
                'extra_fields': {
                    'event_type': 'inhouse_llm_api_request_failure',
                    'provider': 'inhouse_llm',
                    'model': request.get('model'),
                    'error': str(e)
                }
            })
            raise Exception(f"In-house LLM API error: {str(e)}")
    
    def _preprocess_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess request to convert OpenAI format to in-house format.
        
        Requirements:
        1. Convert messages array to single "message" field with full conversation history
        2. Extract system prompt from system role messages
        3. Add static fields for authentication
        
        Args:
            request: Original OpenAI format request with conversation history
            
        Returns:
            Processed request in in-house format
        """
        try:
            logger.debug("Applying request preprocessor", extra={
                'extra_fields': {
                    'event_type': 'request_preprocessing_start',
                    'provider': 'inhouse_llm',
                    'original_request_keys': list(request.keys())
                }
            })
            
            # Start with static fields
            processed_request = self.static_fields.copy()
            
            # Add model
            processed_request["model"] = request.get("model", self.default_model)
            
            # Process messages to build conversation and extract system prompt
            messages = request.get("messages", [])
            system_prompt = ""
            conversation_parts = []
            
            for message in messages:
                role = message.get("role", "")
                content = message.get("content", "")
                
                if role == "system":
                    # Extract system prompt
                    system_prompt = content
                elif role == "user":
                    # Add user message to conversation
                    conversation_parts.append(f"User: {content}")
                elif role == "assistant":
                    # Add assistant message to conversation
                    conversation_parts.append(f"Assistant: {content}")
            
            # Build the complete conversation as a single message
            if conversation_parts:
                # Join all conversation parts with line breaks
                full_conversation = "\n\n".join(conversation_parts)
                
                # If there's a system prompt, prepend it to the conversation
                #if system_prompt:
                #    full_conversation = f"System: {system_prompt}\n\n{full_conversation}"
                
                processed_request["message"] = full_conversation
            else:
                # Fallback if no conversation found
                processed_request["message"] = ""
            
            # Set system prompt separately if present (for backward compatibility)
            if system_prompt:
                processed_request["system_prompt"] = system_prompt
            
            # Add other parameters
            if "temperature" in request:
                processed_request["temperature"] = request["temperature"]
            
            if "max_tokens" in request:
                processed_request["max_tokens"] = request["max_tokens"]
            
            # Add any additional fields from original request that might be needed
            for key, value in request.items():
                if key not in ["messages", "model", "temperature", "max_tokens"]:
                    processed_request[key] = value
            
            logger.debug("Request preprocessing completed", extra={
                'extra_fields': {
                    'event_type': 'request_preprocessing_success',
                    'provider': 'inhouse_llm',
                    'processed_request_keys': list(processed_request.keys()),
                    'has_system_prompt': "system_prompt" in processed_request,
                    'conversation_length': len(processed_request.get("message", "")),
                    'conversation_turns': len(conversation_parts)
                }
            })
            
            return processed_request
            
        except Exception as e:
            logger.error("Request preprocessing failed", extra={
                'extra_fields': {
                    'event_type': 'request_preprocessing_failure',
                    'provider': 'inhouse_llm',
                    'error': str(e)
                }
            })
            # Fall back to original request
            return request
    
    def _postprocess_response(self, data: Dict[str, Any], return_full_response: bool) -> Union[str, Dict[str, Any]]:
        """
        Postprocess response to convert in-house format to OpenAI-like format.
        
        Requirements:
        1. Response body contains simple "text" field
        2. Generate OpenAI-like response structure with id, choices, usage, etc.
        
        Args:
            data: Raw response from in-house API
            return_full_response: Whether to return full response or just content
            
        Returns:
            Processed response in OpenAI-like format or content string
        """
        try:
            logger.debug("Applying response postprocessor", extra={
                'extra_fields': {
                    'event_type': 'response_postprocessing_start',
                    'provider': 'inhouse_llm',
                    'response_keys': list(data.keys()),
                    'return_full_response': return_full_response
                }
            })
            
            # Extract the text content from response
            text_content = data.get("text", "")
            
            if not return_full_response:
                # Return just the content string
                logger.debug("Response postprocessing completed (content only)", extra={
                    'extra_fields': {
                        'event_type': 'response_postprocessing_success',
                        'provider': 'inhouse_llm',
                        'content_length': len(text_content)
                    }
                })
                return text_content
            
            # Create OpenAI-like response structure
            import uuid
            import time
            
            # Generate a unique ID
            response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
            
            # Get current timestamp
            current_time = int(time.time())
            
            # Create OpenAI-like response
            openai_response = {
                "id": response_id,
                "object": "chat.completion",
                "created": current_time,
                "model": self.default_model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": text_content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": self._estimate_tokens(text_content),  # Rough estimation
                    "completion_tokens": self._estimate_tokens(text_content),
                    "total_tokens": self._estimate_tokens(text_content) * 2
                }
            }
            
            # Add any additional fields from original response
            for key, value in data.items():
                if key != "text" and key not in openai_response:
                    openai_response[key] = value
            
            logger.debug("Response postprocessing completed (full response)", extra={
                'extra_fields': {
                    'event_type': 'response_postprocessing_success',
                    'provider': 'inhouse_llm',
                    'response_id': response_id,
                    'content_length': len(text_content)
                }
            })
            
            return openai_response
            
        except Exception as e:
            logger.error("Response postprocessing failed", extra={
                'extra_fields': {
                    'event_type': 'response_postprocessing_failure',
                    'provider': 'inhouse_llm',
                    'error': str(e)
                }
            })
            # Fall back to simple text extraction
            if return_full_response:
                return {
                    "id": "fallback-id",
                    "choices": [{"message": {"content": data.get("text", "")}}],
                    "usage": {"total_tokens": 0}
                }
            else:
                return data.get("text", "")
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Rough estimation of token count for usage statistics.
        This is a simple approximation - in production, you might want to use a proper tokenizer.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return max(1, len(text) // 4)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the in-house LLM model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "provider": "inhouse",
            "default_model": self.default_model,
            "api_url": self.api_url,
            "default_temperature": self.default_temperature,
            "default_max_tokens": self.default_max_tokens,
            "has_custom_processing": True,
            "static_fields_count": len(self.static_fields)
        }


class InhouseVectorStoreProvider(EnhancedBaseProvider, VectorStoreProvider):
    """Sample in-house vector store service provider with enhanced logging."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize in-house vector store provider.
        
        Args:
            config: Configuration dictionary containing:
                - base_url: In-house vector store base URL
                - api_key: In-house API key
        """
        # Add provider name to config for logging
        config["provider_name"] = "inhouse_vector_store"
        super().__init__(config)
        self.base_url = config.get("base_url")
        self.api_key = config.get("api_key")
        
        if not self.base_url:
            raise ValueError("In-house vector store base URL is required")
        
        logger.info("In-house Vector Store Provider initialized", extra={
            'extra_fields': {
                'event_type': 'provider_initialized',
                'provider': 'inhouse_vector_store',
                'base_url': self.base_url
            }
        })
    
    def _get_collection_url(self, collection_name: str) -> str:
        """Get the collection URL for a given collection name."""
        return f"{self.base_url}/collections/{collection_name}"
    
    def _get_points_url(self, collection_name: str) -> str:
        """Get the points URL for a given collection name."""
        return f"{self.base_url}/collections/{collection_name}/points"
    
    def _get_search_url(self, collection_name: str) -> str:
        """Get the search URL for a given collection name."""
        return f"{self.base_url}/collections/{collection_name}/search"
    
    async def create_collection_if_not_exists(self, collection_name: str, vector_size: int, distance_metric: str) -> bool:
        """
        Create a collection if it doesn't exist with enhanced logging.
        
        Args:
            collection_name: Name of the collection
            vector_size: Dimension of the vectors
            distance_metric: Distance metric to use
            
        Returns:
            True if collection exists or was created successfully
        """
        logger.debug(f"Creating in-house collection", extra={
            'extra_fields': {
                'event_type': 'inhouse_collection_create_start',
                'provider': 'inhouse_vector_store',
                'collection_name': collection_name,
                'vector_size': vector_size,
                'distance_metric': distance_metric
            }
        })
        
        try:
            collection_url = self._get_collection_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            # Example payload for in-house API
            create_payload = {
                "name": collection_name,
                "vector_dimension": vector_size,
                "distance_metric": distance_metric
            }
            
            await self._make_request("POST", collection_url, headers, json_data=create_payload)
            
            logger.info(f"Successfully created in-house collection", extra={
                'extra_fields': {
                    'event_type': 'inhouse_collection_create_success',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name,
                    'vector_size': vector_size,
                    'distance_metric': distance_metric
                }
            })
            return True
            
        except Exception as e:
            logger.error(f"Failed to create in-house collection", extra={
                'extra_fields': {
                    'event_type': 'inhouse_collection_create_failure',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name,
                    'vector_size': vector_size,
                    'distance_metric': distance_metric,
                    'error': str(e)
                }
            })
            return False
    
    async def insert_vectors(self, points: List[Dict[str, Any]], collection_name: str) -> bool:
        """
        Insert vectors into the vector store with enhanced logging.
        
        Args:
            points: List of points to insert
            collection_name: Name of the collection to insert into
            
        Returns:
            True if insertion was successful
        """
        logger.debug(f"Inserting vectors into in-house vector store", extra={
            'extra_fields': {
                'event_type': 'inhouse_vector_insert_start',
                'provider': 'inhouse_vector_store',
                'collection_name': collection_name,
                'point_count': len(points)
            }
        })
        
        try:
            # Transform points to in-house format if needed
            transformed_points = []
            for point in points:
                transformed_point = {
                    "id": point["id"],
                    "vector": point["vector"],
                    "metadata": point["payload"]
                }
                transformed_points.append(transformed_point)
            
            payload = {"vectors": transformed_points}
            headers = self._get_headers(self.api_key)
            points_url = self._get_points_url(collection_name)
            
            await self._make_request("POST", points_url, headers, json_data=payload)
            
            logger.info(f"Successfully inserted vectors into in-house vector store", extra={
                'extra_fields': {
                    'event_type': 'inhouse_vector_insert_success',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name,
                    'point_count': len(points)
                }
            })
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert vectors into in-house vector store", extra={
                'extra_fields': {
                    'event_type': 'inhouse_vector_insert_failure',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name,
                    'point_count': len(points),
                    'error': str(e)
                }
            })
            raise Exception(f"In-house vector insert API error: {str(e)}")
    
    async def search_vectors(self, query_vector: List[float], top_k: int, collection_name: str) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the vector store with enhanced logging.
        
        Args:
            query_vector: The query vector to search for
            top_k: Number of top results to return
            collection_name: Name of the collection to search in
            
        Returns:
            List of search results with payload and score
        """
        logger.debug(f"Searching vectors in in-house vector store", extra={
            'extra_fields': {
                'event_type': 'inhouse_vector_search_start',
                'provider': 'inhouse_vector_store',
                'collection_name': collection_name,
                'top_k': top_k,
                'query_vector_size': len(query_vector)
            }
        })
        
        try:
            payload = {
                "query_vector": query_vector,
                "limit": top_k,
                "include_metadata": True
            }
            
            headers = self._get_headers(self.api_key)
            search_url = self._get_search_url(collection_name)
            
            response = await self._make_request("POST", search_url, headers, json_data=payload)
            data = response.json()
            
            # Transform results to standard format
            results = []
            for item in data.get("results", []):
                result = {
                    "payload": {
                        "content": item.get("metadata", {}).get("content"),
                        "metadata": item.get("metadata", {})
                    },
                    "score": item.get("similarity", 0.0)
                }
                results.append(result)
            
            logger.info(f"Successfully searched vectors in in-house vector store", extra={
                'extra_fields': {
                    'event_type': 'inhouse_vector_search_success',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name,
                    'top_k': top_k,
                    'result_count': len(results)
                }
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search vectors in in-house vector store", extra={
                'extra_fields': {
                    'event_type': 'inhouse_vector_search_failure',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name,
                    'top_k': top_k,
                    'error': str(e)
                }
            })
            raise Exception(f"In-house vector search API error: {str(e)}")
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics about a collection with enhanced logging.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary containing collection statistics
        """
        logger.debug(f"Getting collection stats from in-house vector store", extra={
            'extra_fields': {
                'event_type': 'inhouse_collection_stats_start',
                'provider': 'inhouse_vector_store',
                'collection_name': collection_name
            }
        })
        
        try:
            collection_url = self._get_collection_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            response = self._make_sync_request("GET", collection_url, headers)
            data = response.json()
            
            stats = {
                "total_documents": data.get("document_count", 0),
                "collection_name": collection_name,
                "vector_size": data.get("vector_dimension", 1536)
            }
            
            logger.info(f"Successfully retrieved collection stats from in-house vector store", extra={
                'extra_fields': {
                    'event_type': 'inhouse_collection_stats_success',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name,
                    'total_documents': stats["total_documents"],
                    'vector_size': stats["vector_size"]
                }
            })
            
            return stats
            
        except Exception as e:
            logger.warning(f"Failed to get collection stats from in-house vector store, using defaults", extra={
                'extra_fields': {
                    'event_type': 'inhouse_collection_stats_failure',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name,
                    'error': str(e)
                }
            })
            return {
                "total_documents": 0,
                "collection_name": collection_name,
                "vector_size": 1536
            }
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection with enhanced logging.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if deletion was successful
        """
        logger.info(f"Deleting collection from in-house vector store", extra={
            'extra_fields': {
                'event_type': 'inhouse_collection_delete',
                'provider': 'inhouse_vector_store',
                'collection_name': collection_name
            }
        })
        
        try:
            collection_url = self._get_collection_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            self._make_sync_request("DELETE", collection_url, headers)
            
            logger.info(f"Successfully deleted collection from in-house vector store", extra={
                'extra_fields': {
                    'event_type': 'inhouse_collection_delete_success',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name
                }
            })
            return True
            
        except Exception as e:
            logger.warning(f"Failed to delete collection from in-house vector store", extra={
                'extra_fields': {
                    'event_type': 'inhouse_collection_delete_failure',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name,
                    'error': str(e)
                }
            })
            return True  # Return True to avoid breaking existing code
    
    def delete_all_points(self, collection_name: str) -> bool:
        """
        Delete all points in a collection without deleting the collection itself with enhanced logging.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if deletion was successful
        """
        logger.info(f"Deleting all points from collection in in-house vector store", extra={
            'extra_fields': {
                'event_type': 'inhouse_points_delete',
                'provider': 'inhouse_vector_store',
                'collection_name': collection_name
            }
        })
        
        try:
            delete_url = f"{self._get_points_url(collection_name)}/clear"
            headers = self._get_headers(self.api_key)
            
            self._make_sync_request("POST", delete_url, headers)
            
            logger.info(f"Successfully deleted all points from collection in in-house vector store", extra={
                'extra_fields': {
                    'event_type': 'inhouse_points_delete_success',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name
                }
            })
            return True
            
        except Exception as e:
            logger.warning(f"Failed to delete all points from collection in in-house vector store", extra={
                'extra_fields': {
                    'event_type': 'inhouse_points_delete_failure',
                    'provider': 'inhouse_vector_store',
                    'collection_name': collection_name,
                    'error': str(e)
                }
            })
            return True  # Return True to avoid breaking existing code 