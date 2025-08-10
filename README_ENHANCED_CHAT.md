# Enhanced Chat Completion Service

## Overview

The Enhanced Chat Completion Service provides advanced multi-turn conversation support with goal-oriented RAG (Retrieval-Augmented Generation) capabilities. This service is designed to handle complex, multi-step conversations like Business Requirement Document (BRD) preparation, technical consultations, and other goal-oriented tasks.

## Key Features

### 1. Multi-Turn Conversation Support
- **Condensed Query Generation**: Converts recent conversation turns into self-contained queries that resolve pronouns and include key context
- **Summary Query Generation**: Creates 1-2 sentence summaries of recent conversation context
- **Conversation State Tracking**: Monitors goals, phases, entities, and constraints across conversation turns

### 2. Goal-Oriented RAG
- **Goal Detection**: Automatically identifies user goals from conversation context
- **Phase Detection**: Tracks conversation phases (planning, drafting, reviewing, finalizing)
- **Entity Tracking**: Maintains awareness of key entities across conversation turns
- **Constraint Recognition**: Identifies and tracks constraints and requirements

### 3. Enhanced Query Strategies
- **Multi-Query Retrieval**: Generates multiple queries from a single user message
- **Context-Aware Queries**: Incorporates conversation history and state into retrieval
- **Goal-Oriented Queries**: Focuses retrieval on current task objectives
- **Phase-Specific Queries**: Adapts queries based on conversation phase

### 4. Conversation State Management
- **Current Goal Tracking**: Maintains awareness of the user's primary objective
- **Progress Markers**: Tracks completion of conversation milestones
- **Next Steps**: Suggests logical next actions based on conversation state
- **Entity Persistence**: Maintains key entities across conversation turns

## Architecture

### Core Components

1. **MultiTurnConversationStrategy**: Main strategy for multi-turn conversations
2. **ConversationState**: Data structure for tracking conversation state
3. **ProcessingContext**: Context object passed between processing plugins
4. **EnhancedChatCompletionService**: Main service orchestrating the pipeline

### Processing Pipeline

1. **Conversation Analysis**: Analyzes conversation to extract context, goals, and state
2. **Enhanced Query Generation**: Generates multiple queries including condensed and summary queries
3. **Multi-Query RAG**: Performs retrieval using multiple queries for better context coverage
4. **Response Enhancement**: Enhances responses with retrieved context while preserving persona

## Usage Examples

### BRD Preparation Scenario

```python
from app.domain.services.enhanced_chat_completion_service import EnhancedChatCompletionService

# Initialize service
service = EnhancedChatCompletionService(rag_service, llm_provider)

# Multi-turn conversation
messages = [
    ChatMessage(role="system", content="You are a Credit Officer specializing in regulatory compliance."),
    ChatMessage(role="user", content="I need to prepare a BRD for Basel III compliance"),
    ChatMessage(role="assistant", content="I'll help you create a comprehensive BRD. Let me gather relevant information about Basel III requirements."),
    ChatMessage(role="user", content="What sections should I include?"),
    ChatMessage(role="assistant", content="Based on Basel III compliance requirements, your BRD should include: Executive Summary, Risk Assessment, Implementation Plan, and Compliance Framework."),
    ChatMessage(role="user", content="Can you help me draft the executive summary?")
]

request = ChatCompletionRequest(
    model="gpt-4",
    messages=messages,
    temperature=0.7,
    max_tokens=1000
)

response = await service.process_request(request)
```

### Multi-Turn Context Handling

```python
# The service automatically:
# 1. Detects the goal: "Prepare BRD for Basel III compliance"
# 2. Identifies the phase: "drafting" (based on "draft the executive summary")
# 3. Tracks entities: ["Basel", "BRD", "SME", "compliance"]
# 4. Generates enhanced queries including:
#    - Original: "Can you help me draft the executive summary?"
#    - Condensed: "Basel III BRD compliance executive summary draft"
#    - Summary: "Goal: Prepare BRD for Basel III compliance, Entities: Basel, BRD, Actions: draft"
#    - Goal-oriented: "Prepare BRD for Basel III compliance Can you help me draft the executive summary?"
```

## Configuration

### Query Generation Settings

```python
from app.core.enhanced_chat_config import get_query_generation_config

config = get_query_generation_config()
# {
#     "max_conversation_turns": 5,
#     "condensed_query_weight": 0.4,
#     "summary_query_weight": 0.3,
#     "original_query_weight": 0.3,
#     "enable_goal_tracking": True,
#     "enable_phase_detection": True,
#     "max_queries_per_request": 8
# }
```

### Conversation State Settings

```python
from app.core.enhanced_chat_config import get_conversation_state_config

config = get_conversation_state_config()
# {
#     "max_entities_tracked": 10,
#     "max_constraints_tracked": 5,
#     "state_persistence_turns": 10,
#     "goal_detection_threshold": 0.7
# }
```

## API Response Format

### Enhanced Metadata

The service returns enhanced metadata in the response:

```json
{
  "id": "chatcmpl-123",
  "choices": [...],
  "metadata": {
    "conversation_aware": true,
    "multi_turn_enabled": true,
    "strategy_used": "multi_turn_conversation",
    "enhanced_queries_count": 6,
    "conversation_state": {
      "current_goal": "Prepare BRD for Basel III compliance",
      "conversation_phase": "drafting",
      "key_entities_count": 4,
      "constraints_count": 2
    },
    "processing_plugins": [
      "conversation_context",
      "multi_query_rag", 
      "response_enhancement"
    ],
    "persona_preserved": true,
    "rag_context_added": true
  }
}
```

## Testing

Run the test suite to validate the enhanced functionality:

```bash
# Run all tests
pytest tests/test_enhanced_chat_completion.py -v

# Run specific test class
pytest tests/test_enhanced_chat_completion.py::TestMultiTurnConversationStrategy -v

# Run specific test
pytest tests/test_enhanced_chat_completion.py::TestMultiTurnConversationStrategy::test_analyze_conversation -v
```

## Performance Considerations

### Query Generation Limits
- Maximum 8 queries per request (configurable)
- Query length limits: 10-200 characters
- Conversation turn limits: 5 turns for analysis

### Processing Pipeline
- Parallel query processing for better performance
- Caching of conversation analysis results
- Optimized entity and topic extraction

### Memory Management
- Conversation history limited to 50 messages
- Entity tracking limited to 10 entities
- Constraint tracking limited to 5 constraints

## Monitoring and Metrics

### Key Metrics
- **Context Retention**: How well context is maintained across turns
- **Query Relevance**: Relevance scores of generated queries
- **Response Quality**: User satisfaction with responses
- **Conversation Flow**: Natural progression of conversations
- **Goal Achievement**: Success rate of goal-oriented tasks

### Logging
The service provides detailed logging for monitoring and debugging:

```python
# Example log entries
logger.info("Multi-turn conversation processed", extra={
    'extra_fields': {
        'conversation_length': 6,
        'condensed_query': 'Basel III BRD compliance executive summary draft',
        'summary_query': 'Goal: Prepare BRD for Basel III compliance, Entities: Basel, BRD',
        'goal_detected': 'Prepare BRD for Basel III compliance',
        'phase': 'drafting',
        'entities_tracked': 4
    }
})
```

## Future Enhancements

### Planned Features
1. **Adaptive Query Generation**: Learn from user feedback to improve query strategies
2. **Multi-Modal Context**: Support for document uploads during conversation
3. **Advanced Goal Tracking**: Hierarchical goal decomposition and progress tracking
4. **Conversation Memory**: Long-term conversation memory and user preference learning

### Performance Optimizations
1. **Query Caching**: Cache frequently used queries and results
2. **Parallel Processing**: Enhanced parallel processing for multiple queries
3. **Token Optimization**: Better token usage and context window management
4. **Response Streaming**: Stream responses for better user experience

## Integration with Agentic-Credit-Scribe

The enhanced chat completion service can be integrated with the agentic-credit-scribe project to provide:

1. **Goal-Oriented Agent Behavior**: Agents can track and work towards specific goals
2. **Multi-Turn Context Awareness**: Better handling of complex credit analysis conversations
3. **Enhanced RAG Integration**: More relevant context retrieval for credit-related queries
4. **Conversation State Management**: Track progress through credit analysis workflows

### Integration Points
- **System Message Enhancement**: Use conversation state to enhance agent personas
- **Context-Aware Prompts**: Incorporate conversation state into prompt generation
- **Goal Tracking**: Track credit analysis goals and progress
- **Entity Persistence**: Maintain awareness of key entities (borrowers, products, regulations)

## Contributing

When contributing to the enhanced chat completion service:

1. **Follow the Strategy Pattern**: Add new strategies by implementing `ConversationAnalysisStrategy`
2. **Extend Plugin Architecture**: Add new plugins by implementing `ChatCompletionPlugin`
3. **Update Configuration**: Add new configuration options to `enhanced_chat_config.py`
4. **Add Tests**: Include comprehensive tests for new functionality
5. **Update Documentation**: Keep documentation current with new features

## License

This enhanced chat completion service is part of the RAG-LLM project and follows the same licensing terms.
