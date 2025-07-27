"""
Base provider class with common functionality for all external service providers.
"""

import httpx
from typing import Dict, Any
from app.core.config import Config


class BaseProvider:
    """Base class for all external service providers with common HTTP functionality."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize base provider with configuration.
        
        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config
        self.timeout = config.get("timeout", Config.REQUEST_TIMEOUT)
        self.max_retries = config.get("max_retries", Config.MAX_RETRIES)
        self.ssl_config = Config.get_ssl_config()
    
    def _get_client_kwargs(self) -> Dict[str, Any]:
        """Get common client configuration for HTTP requests."""
        return {
            "timeout": self.timeout,
            **self.ssl_config
        }
    
    def _get_headers(self, api_key: str, content_type: str = "application/json") -> Dict[str, str]:
        """Get common headers for API requests."""
        headers = {"Content-Type": content_type}
        
        if api_key:
            # Handle different authentication schemes
            if self.config.get("auth_scheme") == "bearer":
                headers["Authorization"] = f"Bearer {api_key}"
            elif self.config.get("auth_scheme") == "api_key":
                headers["api-key"] = api_key
            else:
                # Default to Bearer token
                headers["Authorization"] = f"Bearer {api_key}"
        
        return headers
    
    async def _make_request(self, method: str, url: str, headers: Dict[str, str], 
                           json_data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> httpx.Response:
        """
        Make an HTTP request with common error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: Request URL
            headers: Request headers
            json_data: JSON data for request body
            params: Query parameters
            
        Returns:
            HTTP response
            
        Raises:
            Exception: If request fails
        """
        try:
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=params
                )
                response.raise_for_status()
                return response
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Request error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def _make_sync_request(self, method: str, url: str, headers: Dict[str, str],
                          json_data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> httpx.Response:
        """
        Make a synchronous HTTP request with common error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: Request URL
            headers: Request headers
            json_data: JSON data for request body
            params: Query parameters
            
        Returns:
            HTTP response
            
        Raises:
            Exception: If request fails
        """
        try:
            with httpx.Client(**self._get_client_kwargs()) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=params
                )
                response.raise_for_status()
                return response
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Request error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}") 