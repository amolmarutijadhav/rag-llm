"""
SRE-optimized base provider with comprehensive observability and debugging.
"""

import httpx
import time
import json
import asyncio
from typing import Dict, Any, Optional
from dataclasses import asdict
from app.core.config import Config
from app.core.logging_config import (
    get_logger, get_correlation_id, ExternalAPICall, 
    sanitize_for_logging, logging_config, api_logger
)

logger = get_logger(__name__)

class EnhancedBaseProvider:
    """Production-ready base provider with SRE features and connection pooling"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get("timeout", Config.REQUEST_TIMEOUT)
        self.max_retries = config.get("max_retries", Config.MAX_RETRIES)
        self.ssl_config = Config.get_ssl_config()
        self.provider_name = config.get("provider_name", "unknown")
        self.retry_delay = config.get("retry_delay", 1.0)
        
        # Connection pooling configuration
        self.max_keepalive_connections = config.get("max_keepalive_connections", 20)
        self.max_connections = config.get("max_connections", 100)
        self.keepalive_expiry = config.get("keepalive_expiry", 30.0)
        
        # Client instances for connection pooling
        self._async_client: Optional[httpx.AsyncClient] = None
        self._sync_client: Optional[httpx.Client] = None
        self._client_lock = asyncio.Lock()
        self._sync_client_lock = asyncio.Lock()
        self._is_closing = False
    
    def _get_client_kwargs(self) -> Dict[str, Any]:
        """Get client configuration with connection pooling settings"""
        return {
            "timeout": self.timeout,
            "limits": httpx.Limits(
                max_keepalive_connections=self.max_keepalive_connections,
                max_connections=self.max_connections,
                keepalive_expiry=self.keepalive_expiry
            ),
            **self.ssl_config
        }
    
    async def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client with connection pooling"""
        if self._is_closing:
            raise RuntimeError("Provider is being closed")
            
        # Check if client exists and is still valid
        if self._async_client is not None:
            try:
                # More comprehensive validation
                if (hasattr(self._async_client, '_transport') and 
                    self._async_client._transport is not None and
                    hasattr(self._async_client._transport, 'pool') and
                    self._async_client._transport.pool is not None):
                    return self._async_client
                else:
                    # Client exists but transport is invalid
                    logger.warning("Async client transport is invalid, recreating", extra={
                        'extra_fields': {
                            'event_type': 'connection_pool_recreation',
                            'provider': self.provider_name,
                            'reason': 'invalid_transport'
                        }
                    })
                    self._async_client = None
            except (AttributeError, RuntimeError, Exception) as e:
                logger.warning("Async client validation failed, recreating", extra={
                    'extra_fields': {
                        'event_type': 'connection_pool_recreation',
                        'provider': self.provider_name,
                        'reason': 'client_validation_failed',
                        'error': str(e)
                    }
                })
                self._async_client = None
        
        # Create new client if needed
        async with self._client_lock:
            if self._async_client is None and not self._is_closing:
                self._async_client = httpx.AsyncClient(**self._get_client_kwargs())
                logger.info(f"Created async HTTP client with connection pooling", extra={
                    'extra_fields': {
                        'event_type': 'connection_pool_created',
                        'provider': self.provider_name,
                        'max_keepalive_connections': self.max_keepalive_connections,
                        'max_connections': self.max_connections,
                        'keepalive_expiry': self.keepalive_expiry
                    }
                })
        
        return self._async_client
    
    def _get_sync_client(self) -> httpx.Client:
        """Get or create sync HTTP client with connection pooling"""
        # Check if client exists and is still valid
        if self._sync_client is not None:
            try:
                # More comprehensive validation
                if (hasattr(self._sync_client, '_transport') and 
                    self._sync_client._transport is not None and
                    hasattr(self._sync_client._transport, 'pool') and
                    self._sync_client._transport.pool is not None):
                    return self._sync_client
                else:
                    # Client exists but transport is invalid
                    logger.warning("Sync client transport is invalid, recreating", extra={
                        'extra_fields': {
                            'event_type': 'sync_connection_pool_recreation',
                            'provider': self.provider_name,
                            'reason': 'invalid_transport'
                        }
                    })
                    self._sync_client = None
            except (AttributeError, RuntimeError, Exception) as e:
                logger.warning("Sync client validation failed, recreating", extra={
                    'extra_fields': {
                        'event_type': 'sync_connection_pool_recreation',
                        'provider': self.provider_name,
                        'reason': 'client_validation_failed',
                        'error': str(e)
                    }
                })
                self._sync_client = None
        
        # Create new client if needed
        with self._sync_client_lock:
            if self._sync_client is None:
                self._sync_client = httpx.Client(**self._get_client_kwargs())
                logger.info(f"Created sync HTTP client with connection pooling", extra={
                    'extra_fields': {
                        'event_type': 'sync_connection_pool_created',
                        'provider': self.provider_name,
                        'max_keepalive_connections': self.max_keepalive_connections,
                        'max_connections': self.max_connections,
                        'keepalive_expiry': self.keepalive_expiry
                    }
                })
        
        return self._sync_client
    
    async def _close_async_client(self):
        """Close async HTTP client"""
        if self._async_client is not None:
            async with self._client_lock:
                if self._async_client is not None:
                    await self._async_client.aclose()
                    self._async_client = None
                    logger.info(f"Closed async HTTP client", extra={
                        'extra_fields': {
                            'event_type': 'connection_pool_closed',
                            'provider': self.provider_name
                        }
                    })
    
    def _close_sync_client(self):
        """Close sync HTTP client"""
        if self._sync_client is not None:
            with self._sync_client_lock:
                if self._sync_client is not None:
                    self._sync_client.close()
                    self._sync_client = None
                    logger.info(f"Closed sync HTTP client", extra={
                        'extra_fields': {
                            'event_type': 'sync_connection_pool_closed',
                            'provider': self.provider_name
                        }
                    })
    
    async def close(self):
        """Close all HTTP clients and cleanup resources"""
        self._is_closing = True
        await self._close_async_client()
        self._close_sync_client()
        logger.info(f"Provider closed and resources cleaned up", extra={
            'extra_fields': {
                'event_type': 'provider_closed',
                'provider': self.provider_name
            }
        })
    
    def _get_headers(self, api_key: str, content_type: str = "application/json") -> Dict[str, str]:
        headers = {"Content-Type": content_type}
        
        if api_key:
            auth_scheme = self.config.get("auth_scheme", "bearer")
            if auth_scheme == "bearer":
                headers["Authorization"] = f"Bearer {api_key}"
            elif auth_scheme == "api_key":
                headers["api-key"] = api_key
            else:
                headers["Authorization"] = f"Bearer {api_key}"
        
        return headers
    
    def _generate_curl_command(self, method: str, url: str, headers: Dict[str, str], 
                             body: Optional[Dict[str, Any]] = None) -> str:
        """Generate curl command for debugging external API issues"""
        return api_logger.generate_curl_command(method, url, headers, body)
    
    async def _make_request_with_retries(self, method: str, url: str, headers: Dict[str, str], 
                                      json_data: Optional[Dict[str, Any]] = None, 
                                      data: Optional[Dict[str, Any]] = None,
                                      params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make HTTP request with retries and comprehensive logging using connection pooling"""
        start_time = time.time()
        correlation_id = get_correlation_id()
        retry_count = 0
        
        # Log request start
        logger.debug(f"External API request started", extra={
            'extra_fields': {
                'event_type': 'external_api_request_start',
                'provider': self.provider_name,
                'method': method,
                'url': url,
                'correlation_id': correlation_id,
                'retry_count': retry_count
            }
        })
        
        while retry_count <= self.max_retries:
            try:
                # Get pooled client
                client = await self._get_async_client()
                
                request_kwargs = {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "params": params
                }
                
                if json_data is not None:
                    request_kwargs["json"] = json_data
                if data is not None:
                    request_kwargs["data"] = data
                    
                response = await client.request(**request_kwargs)
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Calculate request/response sizes
                request_size = len(json.dumps(json_data or {}).encode('utf-8'))
                response_size = len(response.content)
                
                # Create API call log
                api_call = ExternalAPICall(
                    correlation_id=correlation_id,
                    provider=self.provider_name,
                    endpoint=url,
                    method=method,
                    request_size_bytes=request_size,
                    response_size_bytes=response_size,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    success=response.status_code < 400,
                    error_type=None,
                    error_message=None,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    curl_command=self._generate_curl_command(method, url, headers, json_data),
                    retry_count=retry_count
                )
                
                # Log success
                if response.status_code < 400:
                    logger.info(f"External API call successful", extra={
                        'extra_fields': {
                            'event_type': 'external_api_success',
                            'api_call': asdict(api_call)
                        }
                    })
                    response.raise_for_status()
                    return response
                else:
                    # Log HTTP error
                    api_call.success = False
                    api_call.error_type = "HTTP_ERROR"
                    api_call.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
                    
                    logger.warning(f"External API returned error status", extra={
                        'extra_fields': {
                            'event_type': 'external_api_http_error',
                            'api_call': asdict(api_call)
                        }
                    })
                    
                    response.raise_for_status()
                    
            except httpx.HTTPStatusError as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Create error API call log
                api_call = ExternalAPICall(
                    correlation_id=correlation_id,
                    provider=self.provider_name,
                    endpoint=url,
                    method=method,
                    request_size_bytes=len(json.dumps(json_data or {}).encode('utf-8')),
                    response_size_bytes=len(e.response.content) if e.response else 0,
                    status_code=e.response.status_code if e.response else None,
                    duration_ms=duration_ms,
                    success=False,
                    error_type="HTTP_ERROR",
                    error_message=f"HTTP {e.response.status_code}: {e.response.text[:500]}" if e.response else str(e),
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    curl_command=self._generate_curl_command(method, url, headers, json_data),
                    retry_count=retry_count
                )
                
                # Check if we should retry
                if retry_count < self.max_retries and e.response.status_code >= 500:
                    retry_count += 1
                    logger.warning(f"Retrying external API call ({retry_count}/{self.max_retries})", extra={
                        'extra_fields': {
                            'event_type': 'external_api_retry',
                            'api_call': asdict(api_call)
                        }
                    })
                    await asyncio.sleep(self.retry_delay * retry_count)  # Exponential backoff
                    continue
                else:
                    # Log final failure
                    logger.error(f"External API call failed permanently", extra={
                        'extra_fields': {
                            'event_type': 'external_api_failure',
                            'api_call': asdict(api_call)
                        }
                    })
                    raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
                    
            except httpx.RequestError as e:
                duration_ms = (time.time() - start_time) * 1000
                
                api_call = ExternalAPICall(
                    correlation_id=correlation_id,
                    provider=self.provider_name,
                    endpoint=url,
                    method=method,
                    request_size_bytes=len(json.dumps(json_data or {}).encode('utf-8')),
                    response_size_bytes=0,
                    status_code=None,
                    duration_ms=duration_ms,
                    success=False,
                    error_type="NETWORK_ERROR",
                    error_message=str(e),
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    curl_command=self._generate_curl_command(method, url, headers, json_data),
                    retry_count=retry_count
                )
                
                # Retry network errors
                if retry_count < self.max_retries:
                    retry_count += 1
                    logger.warning(f"Retrying network error ({retry_count}/{self.max_retries})", extra={
                        'extra_fields': {
                            'event_type': 'external_api_network_retry',
                            'api_call': asdict(api_call)
                        }
                    })
                    await asyncio.sleep(self.retry_delay * retry_count)
                    continue
                else:
                    logger.error(f"External API network error after retries", extra={
                        'extra_fields': {
                            'event_type': 'external_api_network_failure',
                            'api_call': asdict(api_call)
                        }
                    })
                    raise Exception(f"Network error: {str(e)}")
                    
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                logger.error(f"Unexpected error in external API call", extra={
                    'extra_fields': {
                        'event_type': 'external_api_unexpected_error',
                        'provider': self.provider_name,
                        'method': method,
                        'url': url,
                        'error': str(e),
                        'duration_ms': duration_ms,
                        'correlation_id': correlation_id,
                        'retry_count': retry_count
                    }
                })
                raise Exception(f"Unexpected error: {str(e)}")
    
    async def _make_request(self, method: str, url: str, headers: Dict[str, str], 
                           json_data: Optional[Dict[str, Any]] = None, 
                           data: Optional[Dict[str, Any]] = None,
                           params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make HTTP request with enhanced logging and retries using connection pooling"""
        return await self._make_request_with_retries(method, url, headers, json_data, data, params)
    
    def _make_sync_request(self, method: str, url: str, headers: Dict[str, str],
                          json_data: Optional[Dict[str, Any]] = None, 
                          data: Optional[Dict[str, Any]] = None,
                          params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make synchronous HTTP request with enhanced logging using connection pooling"""
        start_time = time.time()
        correlation_id = get_correlation_id()
        
        logger.debug(f"Sync external API request started", extra={
            'extra_fields': {
                'event_type': 'sync_external_api_request_start',
                'provider': self.provider_name,
                'method': method,
                'url': url,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Get pooled sync client
            client = self._get_sync_client()
            
            request_kwargs = {
                "method": method,
                "url": url,
                "headers": headers,
                "params": params
            }
            
            if json_data is not None:
                request_kwargs["json"] = json_data
            if data is not None:
                request_kwargs["data"] = data
                
            response = client.request(**request_kwargs)
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful response
            logger.debug(f"Sync external API request completed", extra={
                'extra_fields': {
                    'event_type': 'sync_external_api_success',
                    'provider': self.provider_name,
                    'method': method,
                    'url': url,
                    'status_code': response.status_code,
                    'duration_ms': duration_ms,
                    'correlation_id': correlation_id
                }
            })
            
            response.raise_for_status()
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(f"Sync external API request failed", extra={
                'extra_fields': {
                    'event_type': 'sync_external_api_failure',
                    'provider': self.provider_name,
                    'method': method,
                    'url': url,
                    'error': str(e),
                    'duration_ms': duration_ms,
                    'correlation_id': correlation_id,
                    'curl_command': self._generate_curl_command(method, url, headers, json_data)
                }
            })
            raise Exception(f"Sync request error: {str(e)}") 