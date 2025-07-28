"""
Enhanced Chat Completion Service using Strategy Pattern and Plugin Architecture.
Maintains external interface compatibility while providing extensible functionality.
"""

from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from app.domain.models.requests import ChatCompletionRequest, ChatMessage
from app.domain.models.responses import ChatCompletionResponse
from app.domain.services.rag_service import RAGService
from app.core.logging_config import get_logger, get_correlation_id
import asyncio
from collections import defaultdict

logger = get_logger(__name__)

class ProcessingPriority(Enum):
    """Processing priority levels for plugins"""
    HIGH = 1
    NORMAL = 2
    LOW = 3

@dataclass
class ProcessingContext:
    """Context object passed between plugins during processing"""
    request: ChatCompletionRequest
    strategy: Optional[str] = None
    conversation_context: Optional[Dict[str, Any]] = None
    enhanced_queries: Optional[List[str]] = None
    rag_results: Optional[List[Dict[str, Any]]] = None
    response_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.conversation_context is None:
            self.conversation_context = {}

class ConversationAnalysisStrategy(ABC):
    """Abstract base class for conversation analysis strategies"""
    
    @abstractmethod
    async def analyze_conversation(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """Analyze conversation and extract context"""
        pass
    
    @abstractmethod
    async def generate_enhanced_queries(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Generate enhanced queries based on conversation context"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy"""
        pass

class TopicTrackingStrategy(ConversationAnalysisStrategy):
    """Strategy that tracks conversation topics and generates topic-aware queries"""
    
    def get_strategy_name(self) -> str:
        return "topic_tracking"
    
    async def analyze_conversation(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """Analyze conversation to extract topics and context"""
        topics = []
        entities = []
        context_clues = []
        
        # Extract topics from system messages
        for message in messages:
            if message.role == "system":
                topics.append("system_instruction")
                context_clues.append(message.content)
            elif message.role == "user":
                # Simple topic extraction (can be enhanced with NLP)
                words = message.content.lower().split()
                topics.extend([word for word in words if len(word) > 3])
            elif message.role == "assistant":
                # Extract entities from assistant responses
                entities.extend(self._extract_entities(message.content))
        
        return {
            "topics": list(set(topics)),
            "entities": list(set(entities)),
            "context_clues": context_clues,
            "conversation_length": len(messages),
            "last_user_message": next((msg.content for msg in reversed(messages) if msg.role == "user"), "")
        }
    
    async def generate_enhanced_queries(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Generate enhanced queries based on conversation context"""
        queries = [question]  # Always include original question
        
        # Add topic-based queries
        for topic in context.get("topics", [])[:3]:  # Limit to top 3 topics
            if topic != "system_instruction":
                queries.append(f"{topic} {question}")
        
        # Add entity-based queries
        for entity in context.get("entities", [])[:2]:  # Limit to top 2 entities
            queries.append(f"{entity} {question}")
        
        # Add context-aware queries
        if context.get("context_clues"):
            context_clue = context["context_clues"][-1]  # Use last context clue
            queries.append(f"{context_clue} {question}")
        
        return list(set(queries))  # Remove duplicates
    
    def _extract_entities(self, text: str) -> List[str]:
        """Simple entity extraction (can be enhanced with NLP)"""
        # Simple implementation - extract capitalized words as entities
        words = text.split()
        entities = [word for word in words if word[0].isupper() and len(word) > 2]
        return entities

class EntityExtractionStrategy(ConversationAnalysisStrategy):
    """Strategy that focuses on entity extraction and entity-aware queries"""
    
    def get_strategy_name(self) -> str:
        return "entity_extraction"
    
    async def analyze_conversation(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """Analyze conversation focusing on entity extraction"""
        entities = []
        relationships = []
        
        for message in messages:
            if message.role in ["user", "assistant"]:
                entities.extend(self._extract_entities(message.content))
                relationships.extend(self._extract_relationships(message.content))
        
        return {
            "entities": list(set(entities)),
            "relationships": list(set(relationships)),
            "conversation_length": len(messages),
            "last_user_message": next((msg.content for msg in reversed(messages) if msg.role == "user"), "")
        }
    
    async def generate_enhanced_queries(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Generate entity-aware queries"""
        queries = [question]
        
        # Add entity-based queries
        for entity in context.get("entities", [])[:3]:
            queries.append(f"{entity} {question}")
            queries.append(f"{question} {entity}")
        
        # Add relationship-based queries
        for relationship in context.get("relationships", [])[:2]:
            queries.append(f"{relationship} {question}")
        
        return list(set(queries))
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        # Enhanced entity extraction
        words = text.split()
        entities = []
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append(word)
            elif word.lower() in ["api", "rag", "llm", "ai", "ml"]:
                entities.append(word.upper())
        return entities
    
    def _extract_relationships(self, text: str) -> List[str]:
        """Extract relationships from text"""
        relationships = []
        text_lower = text.lower()
        
        if "how" in text_lower:
            relationships.append("how")
        if "what" in text_lower:
            relationships.append("what")
        if "why" in text_lower:
            relationships.append("why")
        if "when" in text_lower:
            relationships.append("when")
        if "where" in text_lower:
            relationships.append("where")
        
        return relationships

class ChatCompletionPlugin(ABC):
    """Abstract base class for chat completion plugins"""
    
    @abstractmethod
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        """Process the context and return updated context"""
        pass
    
    @abstractmethod
    def get_priority(self) -> ProcessingPriority:
        """Get the processing priority of this plugin"""
        pass
    
    @abstractmethod
    def get_plugin_name(self) -> str:
        """Get the name of this plugin"""
        pass

class ConversationContextPlugin(ChatCompletionPlugin):
    """Plugin that analyzes conversation context"""
    
    def __init__(self, strategy_factory: 'ConversationStrategyFactory'):
        self.strategy_factory = strategy_factory
    
    def get_priority(self) -> ProcessingPriority:
        return ProcessingPriority.HIGH
    
    def get_plugin_name(self) -> str:
        return "conversation_context"
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        """Analyze conversation context and determine strategy"""
        correlation_id = get_correlation_id()
        
        logger.debug("Processing conversation context", extra={
            'extra_fields': {
                'event_type': 'conversation_context_plugin_start',
                'plugin': self.get_plugin_name(),
                'correlation_id': correlation_id
            }
        })
        
        # Determine strategy based on request characteristics
        strategy = self.strategy_factory.get_strategy(context.request)
        context.strategy = strategy.get_strategy_name()
        
        # Analyze conversation
        conversation_context = await strategy.analyze_conversation(context.request.messages)
        context.conversation_context = conversation_context
        
        logger.info("Conversation context processed", extra={
            'extra_fields': {
                'event_type': 'conversation_context_plugin_complete',
                'plugin': self.get_plugin_name(),
                'strategy': context.strategy,
                'topics_count': len(conversation_context.get('topics', [])),
                'entities_count': len(conversation_context.get('entities', [])),
                'correlation_id': correlation_id
            }
        })
        
        return context

class MultiQueryRAGPlugin(ChatCompletionPlugin):
    """Plugin that performs multi-query RAG processing"""
    
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
    
    def get_priority(self) -> ProcessingPriority:
        return ProcessingPriority.NORMAL
    
    def get_plugin_name(self) -> str:
        return "multi_query_rag"
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        """Perform multi-query RAG processing"""
        correlation_id = get_correlation_id()
        
        logger.debug("Processing multi-query RAG", extra={
            'extra_fields': {
                'event_type': 'multi_query_rag_plugin_start',
                'plugin': self.get_plugin_name(),
                'correlation_id': correlation_id
            }
        })
        
        # Get the last user message
        last_user_message = context.conversation_context.get('last_user_message', '')
        if not last_user_message:
            # Fallback: extract from messages
            for message in reversed(context.request.messages):
                if message.role == "user":
                    last_user_message = message.content
                    break
        
        if not last_user_message:
            logger.warning("No user message found", extra={
                'extra_fields': {
                    'event_type': 'multi_query_rag_no_user_message',
                    'correlation_id': correlation_id
                }
            })
            return context
        
        # Generate enhanced queries using the strategy
        strategy = context.strategy
        if strategy == "topic_tracking":
            analysis_strategy = TopicTrackingStrategy()
        elif strategy == "entity_extraction":
            analysis_strategy = EntityExtractionStrategy()
        else:
            analysis_strategy = TopicTrackingStrategy()  # Default
        
        enhanced_queries = await analysis_strategy.generate_enhanced_queries(
            last_user_message, context.conversation_context
        )
        context.enhanced_queries = enhanced_queries
        
        # Perform multi-query retrieval
        all_results = []
        for query in enhanced_queries:
            try:
                result = await self.rag_service.ask_question(query, top_k=2)
                if result.get('success') and result.get('sources'):
                    all_results.extend(result['sources'])
            except Exception as e:
                logger.warning(f"Query failed: {query}", extra={
                    'extra_fields': {
                        'event_type': 'multi_query_rag_query_failed',
                        'query': query,
                        'error': str(e),
                        'correlation_id': correlation_id
                    }
                })
        
        # Deduplicate and rank results
        unique_results = self._deduplicate_results(all_results)
        context.rag_results = unique_results[:5]  # Limit to top 5 results
        
        logger.info("Multi-query RAG processing completed", extra={
            'extra_fields': {
                'event_type': 'multi_query_rag_plugin_complete',
                'plugin': self.get_plugin_name(),
                'queries_count': len(enhanced_queries),
                'results_count': len(context.rag_results),
                'correlation_id': correlation_id
            }
        })
        
        return context
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate results based on content"""
        seen_contents = set()
        unique_results = []
        
        for result in results:
            content = result.get('content', '')
            content_hash = hash(content)
            
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_results.append(result)
        
        # Sort by score if available
        unique_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return unique_results

class ResponseEnhancementPlugin(ChatCompletionPlugin):
    """Plugin that enhances the final response"""
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
    
    def get_priority(self) -> ProcessingPriority:
        return ProcessingPriority.LOW
    
    def get_plugin_name(self) -> str:
        return "response_enhancement"
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        """Enhance the final response with context and metadata"""
        correlation_id = get_correlation_id()
        
        logger.debug("Enhancing response", extra={
            'extra_fields': {
                'event_type': 'response_enhancement_plugin_start',
                'plugin': self.get_plugin_name(),
                'correlation_id': correlation_id
            }
        })
        
        # Get the last user message
        last_user_message = context.conversation_context.get('last_user_message', '')
        
        # Prepare context for LLM
        context_text = ""
        if context.rag_results:
            context_parts = []
            for result in context.rag_results:
                content = result.get('content', '')
                source = result.get('source', 'Unknown')
                context_parts.append(f"Source: {source}\nContent: {content}")
            context_text = "\n\n".join(context_parts)
        
        # Generate response using LLM
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant. Use the following context to answer the user's question. Consider the conversation context provided.\n\nContext:\n{context_text}"
            },
            {
                "role": "user",
                "content": last_user_message
            }
        ]
        
        # Use call_llm_api for full control
        request = {
            "model": context.request.model,
            "messages": messages,
            "temperature": context.request.temperature,
            "max_tokens": context.request.max_tokens
        }
        
        try:
            response = await self.llm_provider.call_llm_api(request, return_full_response=True)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Prepare response data
            context.response_data = {
                "id": f"chatcmpl-{correlation_id}",
                "object": "chat.completion",
                "created": int(__import__('time').time()),
                "model": context.request.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": response.get("usage", {
                    "prompt_tokens": len(last_user_message.split()),
                    "completion_tokens": len(content.split()),
                    "total_tokens": len(last_user_message.split()) + len(content.split())
                }),
                "sources": context.rag_results or []
            }
            
            # Add enhanced metadata
            context.metadata = {
                "conversation_aware": True,
                "strategy_used": context.strategy,
                "enhanced_queries_count": len(context.enhanced_queries or []),
                "conversation_context": context.conversation_context,
                "processing_plugins": ["conversation_context", "multi_query_rag", "response_enhancement"]
            }
            
            logger.info("Response enhancement completed", extra={
                'extra_fields': {
                    'event_type': 'response_enhancement_plugin_complete',
                    'plugin': self.get_plugin_name(),
                    'content_length': len(content),
                    'sources_count': len(context.rag_results or []),
                    'correlation_id': correlation_id
                }
            })
            
        except Exception as e:
            logger.error("Response enhancement failed", extra={
                'extra_fields': {
                    'event_type': 'response_enhancement_plugin_error',
                    'plugin': self.get_plugin_name(),
                    'error': str(e),
                    'correlation_id': correlation_id
                }
            })
            # Fallback response
            context.response_data = {
                "id": f"chatcmpl-{correlation_id}",
                "object": "chat.completion",
                "created": int(__import__('time').time()),
                "model": context.request.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I'm sorry, I encountered an error while processing your request."
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                "sources": []
            }
        
        return context

class ConversationStrategyFactory:
    """Factory for creating conversation analysis strategies"""
    
    def __init__(self):
        self.strategies = {
            "topic_tracking": TopicTrackingStrategy(),
            "entity_extraction": EntityExtractionStrategy()
        }
    
    def get_strategy(self, request: ChatCompletionRequest) -> ConversationAnalysisStrategy:
        """Determine the best strategy based on request characteristics"""
        
        # Analyze request to determine strategy
        messages = request.messages
        system_messages = [msg for msg in messages if msg.role == "system"]
        user_messages = [msg for msg in messages if msg.role == "user"]
        
        # If there are system messages with specific instructions, use topic tracking
        if system_messages and any("entity" in msg.content.lower() for msg in system_messages):
            return self.strategies["entity_extraction"]
        
        # If conversation is long, use topic tracking
        if len(messages) > 5:
            return self.strategies["topic_tracking"]
        
        # Default to topic tracking
        return self.strategies["topic_tracking"]

class ChatCompletionPluginManager:
    """Manages the execution of chat completion plugins"""
    
    def __init__(self):
        self.plugins: List[ChatCompletionPlugin] = []
    
    def register_plugin(self, plugin: ChatCompletionPlugin):
        """Register a plugin for processing"""
        self.plugins.append(plugin)
        # Sort by priority
        self.plugins.sort(key=lambda p: p.get_priority().value)
    
    async def process_request(self, context: ProcessingContext) -> ProcessingContext:
        """Process the request through all registered plugins"""
        correlation_id = get_correlation_id()
        
        logger.info("Starting plugin processing", extra={
            'extra_fields': {
                'event_type': 'plugin_processing_start',
                'plugins_count': len(self.plugins),
                'correlation_id': correlation_id
            }
        })
        
        for plugin in self.plugins:
            try:
                logger.debug(f"Processing plugin: {plugin.get_plugin_name()}", extra={
                    'extra_fields': {
                        'event_type': 'plugin_processing_step',
                        'plugin': plugin.get_plugin_name(),
                        'priority': plugin.get_priority().value,
                        'correlation_id': correlation_id
                    }
                })
                
                context = await plugin.process(context)
                
            except Exception as e:
                logger.error(f"Plugin {plugin.get_plugin_name()} failed", extra={
                    'extra_fields': {
                        'event_type': 'plugin_processing_error',
                        'plugin': plugin.get_plugin_name(),
                        'error': str(e),
                        'correlation_id': correlation_id
                    }
                })
                # Continue with next plugin
        
        logger.info("Plugin processing completed", extra={
            'extra_fields': {
                'event_type': 'plugin_processing_complete',
                'correlation_id': correlation_id
            }
        })
        
        return context

class EnhancedChatCompletionService:
    """Enhanced chat completion service using Strategy Pattern and Plugin Architecture"""
    
    def __init__(self, rag_service: RAGService, llm_provider):
        self.rag_service = rag_service
        self.llm_provider = llm_provider
        self.strategy_factory = ConversationStrategyFactory()
        self.plugin_manager = ChatCompletionPluginManager()
        
        # Register core plugins
        self.plugin_manager.register_plugin(
            ConversationContextPlugin(self.strategy_factory)
        )
        self.plugin_manager.register_plugin(
            MultiQueryRAGPlugin(self.rag_service)
        )
        self.plugin_manager.register_plugin(
            ResponseEnhancementPlugin(self.llm_provider)
        )
        
        logger.info("Enhanced Chat Completion Service initialized", extra={
            'extra_fields': {
                'event_type': 'enhanced_chat_completion_service_initialized',
                'plugins_count': 3,
                'strategies_count': 2
            }
        })
    
    async def process_request(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Process a chat completion request with enhanced capabilities"""
        correlation_id = get_correlation_id()
        
        logger.info("Enhanced chat completion request received", extra={
            'extra_fields': {
                'event_type': 'enhanced_chat_completion_request_start',
                'model': request.model,
                'messages_count': len(request.messages),
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Create processing context
            context = ProcessingContext(request)
            
            # Process through plugin pipeline
            context = await self.plugin_manager.process_request(context)
            
            # Build response
            response = ChatCompletionResponse(**context.response_data)
            
            # Add enhanced metadata if available
            if context.metadata:
                response.metadata = context.metadata
            
            logger.info("Enhanced chat completion request completed", extra={
                'extra_fields': {
                    'event_type': 'enhanced_chat_completion_request_complete',
                    'model': request.model,
                    'strategy_used': context.strategy,
                    'correlation_id': correlation_id
                }
            })
            
            return response
            
        except Exception as e:
            logger.error("Enhanced chat completion request failed", extra={
                'extra_fields': {
                    'event_type': 'enhanced_chat_completion_request_error',
                    'model': request.model,
                    'error': str(e),
                    'correlation_id': correlation_id
                }
            })
            raise 