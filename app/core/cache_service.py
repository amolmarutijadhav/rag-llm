"""
Simple In-Memory Cache Service for Enhanced Chat Completion
Provides fast caching for embeddings, search results, and query responses.
"""

import time
import hashlib
import json
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from collections import OrderedDict
import asyncio
from app.core.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    timestamp: float
    ttl: float
    access_count: int = 0
    last_accessed: float = 0.0

class InMemoryCache:
    """Thread-safe in-memory cache with TTL and LRU eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        """
        Initialize in-memory cache
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = asyncio.Lock()
        
        logger.info("In-memory cache initialized", extra={
            'extra_fields': {
                'event_type': 'cache_initialized',
                'max_size': max_size,
                'default_ttl': default_ttl
            }
        })
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create a deterministic string representation
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        async with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            current_time = time.time()
            
            # Check if expired
            if current_time - entry.timestamp > entry.ttl:
                del self.cache[key]
                logger.debug(f"Cache entry expired: {key}", extra={
                    'extra_fields': {
                        'event_type': 'cache_entry_expired',
                        'key': key,
                        'age_seconds': current_time - entry.timestamp
                    }
                })
                return None
            
            # Update access metadata
            entry.access_count += 1
            entry.last_accessed = current_time
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            
            logger.debug(f"Cache hit: {key}", extra={
                'extra_fields': {
                    'event_type': 'cache_hit',
                    'key': key,
                    'access_count': entry.access_count
                }
            })
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful
        """
        async with self.lock:
            # Evict if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            ttl = ttl or self.default_ttl
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl
            )
            
            self.cache[key] = entry
            
            logger.debug(f"Cache set: {key}", extra={
                'extra_fields': {
                    'event_type': 'cache_set',
                    'key': key,
                    'ttl': ttl,
                    'cache_size': len(self.cache)
                }
            })
            
            return True
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"LRU eviction: {oldest_key}", extra={
                'extra_fields': {
                    'event_type': 'cache_lru_eviction',
                    'evicted_key': oldest_key
                }
            })
    
    async def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Cache delete: {key}", extra={
                    'extra_fields': {
                        'event_type': 'cache_delete',
                        'key': key
                    }
                })
                return True
            return False
    
    async def clear(self) -> int:
        """Clear all cache entries"""
        async with self.lock:
            count = len(self.cache)
            self.cache.clear()
            logger.info(f"Cache cleared: {count} entries", extra={
                'extra_fields': {
                    'event_type': 'cache_clear',
                    'entries_cleared': count
                }
            })
            return count
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self.lock:
            current_time = time.time()
            total_entries = len(self.cache)
            expired_entries = 0
            total_access_count = 0
            
            for entry in self.cache.values():
                if current_time - entry.timestamp > entry.ttl:
                    expired_entries += 1
                total_access_count += entry.access_count
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'valid_entries': total_entries - expired_entries,
                'total_access_count': total_access_count,
                'max_size': self.max_size,
                'default_ttl': self.default_ttl,
                'memory_usage_mb': self._estimate_memory_usage()
            }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        # Rough estimation: each entry ~1KB
        return len(self.cache) * 0.001

class CacheService:
    """High-level cache service with multiple cache types"""
    
    def __init__(self):
        """Initialize cache service with different cache types"""
        # Embedding cache: store embedding vectors
        self.embedding_cache = InMemoryCache(
            max_size=500,  # Store up to 500 embeddings
            default_ttl=3600.0  # 1 hour TTL
        )
        
        # Search cache: store vector search results
        self.search_cache = InMemoryCache(
            max_size=1000,  # Store up to 1000 search results
            default_ttl=1800.0  # 30 minutes TTL
        )
        
        # Query cache: store full query responses
        self.query_cache = InMemoryCache(
            max_size=200,  # Store up to 200 query responses
            default_ttl=900.0  # 15 minutes TTL
        )
        
        logger.info("Cache service initialized", extra={
            'extra_fields': {
                'event_type': 'cache_service_initialized',
                'embedding_cache_size': 500,
                'search_cache_size': 1000,
                'query_cache_size': 200
            }
        })
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text"""
        key = self.embedding_cache._generate_key(text)
        return await self.embedding_cache.get(key)
    
    async def set_embedding(self, text: str, embedding: List[float], ttl: Optional[float] = None) -> bool:
        """Cache embedding for text"""
        key = self.embedding_cache._generate_key(text)
        return await self.embedding_cache.set(key, embedding, ttl)
    
    async def get_search_results(self, query_vector: List[float], top_k: int, collection_name: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results"""
        key = self.search_cache._generate_key(query_vector, top_k, collection_name)
        return await self.search_cache.get(key)
    
    async def set_search_results(self, query_vector: List[float], top_k: int, collection_name: str, results: List[Dict[str, Any]], ttl: Optional[float] = None) -> bool:
        """Cache search results"""
        key = self.search_cache._generate_key(query_vector, top_k, collection_name)
        return await self.search_cache.set(key, results, ttl)
    
    async def get_query_response(self, query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached query response"""
        key = self.query_cache._generate_key(query, context)
        return await self.query_cache.get(key)
    
    async def set_query_response(self, query: str, context: Dict[str, Any], response: Dict[str, Any], ttl: Optional[float] = None) -> bool:
        """Cache query response"""
        key = self.query_cache._generate_key(query, context)
        return await self.query_cache.set(key, response, ttl)
    
    async def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches"""
        return {
            'embedding_cache': await self.embedding_cache.get_stats(),
            'search_cache': await self.search_cache.get_stats(),
            'query_cache': await self.query_cache.get_stats()
        }
    
    async def clear_all(self) -> Dict[str, int]:
        """Clear all caches"""
        return {
            'embedding_cache': await self.embedding_cache.clear(),
            'search_cache': await self.search_cache.clear(),
            'query_cache': await self.query_cache.clear()
        }

# Global cache service instance
cache_service = CacheService()
