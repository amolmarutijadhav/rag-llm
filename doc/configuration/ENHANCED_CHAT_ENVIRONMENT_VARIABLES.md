# Enhanced Chat Environment Variables Configuration

This document describes all environment variables available for configuring the enhanced chat completion service, particularly focusing on conversation context settings.

## Overview

The enhanced chat completion service supports extensive configuration through environment variables, allowing you to customize conversation context handling, query generation, and response processing without code changes.

## Conversation Context Configuration

### Core Context Settings

| Environment Variable | Default | Description | Impact |
|---------------------|---------|-------------|---------|
| `ENHANCED_CHAT_MAX_TURNS` | `5` | Maximum number of conversation turns to consider for context | Controls how many previous user-assistant exchanges are included in context analysis |
| `ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER` | `2` | Multiplier for standard context window size | Standard conversations use `max_turns * multiplier` messages |
| `ENHANCED_CHAT_SHORT_MSG_MULTIPLIER` | `3` | Multiplier for short message context window | Short messages (≤2 words) use `max_turns * multiplier` messages |
| `ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE` | `50` | Maximum number of messages in context window | Prevents excessive memory usage for very long conversations |

### Query Generation Settings

| Environment Variable | Default | Description | Impact |
|---------------------|---------|-------------|---------|
| `ENHANCED_CHAT_CONDENSED_MAX_TURNS` | `5` | Max turns for condensed query generation | Controls context window for standalone question generation |
| `ENHANCED_CHAT_SUMMARY_MAX_TURNS` | `5` | Max turns for summary query generation | Controls context window for context summarization |
| `ENHANCED_CHAT_MAX_QUERIES_PER_REQUEST` | `8` | Maximum number of queries generated per request | Limits query generation for performance |
| `ENHANCED_CHAT_MIN_QUERY_LENGTH` | `10` | Minimum length for generated queries | Filters out very short queries |
| `ENHANCED_CHAT_MAX_QUERY_LENGTH` | `200` | Maximum length for generated queries | Prevents overly long queries |

### Query Weighting

| Environment Variable | Default | Description | Impact |
|---------------------|---------|-------------|---------|
| `ENHANCED_CHAT_CONDENSED_QUERY_WEIGHT` | `0.4` | Weight for condensed queries in ranking | Higher values prioritize standalone questions |
| `ENHANCED_CHAT_SUMMARY_QUERY_WEIGHT` | `0.3` | Weight for summary queries in ranking | Higher values prioritize context summaries |
| `ENHANCED_CHAT_ORIGINAL_QUERY_WEIGHT` | `0.3` | Weight for original queries in ranking | Higher values prioritize user's original question |

## Conversation State Configuration

### Entity and Topic Tracking

| Environment Variable | Default | Description | Impact |
|---------------------|---------|-------------|---------|
| `ENHANCED_CHAT_MAX_ENTITIES_TRACKED` | `10` | Maximum number of entities to track | Limits memory usage for entity tracking |
| `ENHANCED_CHAT_MAX_CONSTRAINTS_TRACKED` | `5` | Maximum number of constraints to track | Limits memory usage for constraint tracking |
| `ENHANCED_CHAT_STATE_PERSISTENCE_TURNS` | `10` | Number of turns to persist conversation state | Controls how long conversation state is maintained |
| `ENHANCED_CHAT_MAX_CONVERSATION_HISTORY_LENGTH` | `50` | Maximum length of conversation history | Prevents memory issues with very long conversations |

### Detection Thresholds

| Environment Variable | Default | Description | Impact |
|---------------------|---------|-------------|---------|
| `ENHANCED_CHAT_GOAL_DETECTION_THRESHOLD` | `0.7` | Confidence threshold for goal detection | Higher values make goal detection more strict |
| `ENHANCED_CHAT_PHASE_DETECTION_CONFIDENCE` | `0.6` | Confidence threshold for phase detection | Higher values make phase detection more strict |
| `ENHANCED_CHAT_GOAL_PHRASE_MAX_LENGTH` | `100` | Maximum length for goal phrases | Limits goal phrase extraction |

## Feature Enablement

### Core Features

| Environment Variable | Default | Description | Impact |
|---------------------|---------|-------------|---------|
| `ENHANCED_CHAT_ENABLE_GOAL_TRACKING` | `true` | Enable conversation goal tracking | Disables goal-oriented query generation if false |
| `ENHANCED_CHAT_ENABLE_PHASE_DETECTION` | `true` | Enable conversation phase detection | Disables phase-specific query generation if false |
| `ENHANCED_CHAT_ENABLE_CONDENSED_QUERIES` | `true` | Enable condensed query generation | Disables standalone question generation if false |
| `ENHANCED_CHAT_ENABLE_SUMMARY_QUERIES` | `true` | Enable summary query generation | Disables context summarization if false |
| `ENHANCED_CHAT_ENABLE_GOAL_ORIENTED_QUERIES` | `true` | Enable goal-oriented query generation | Disables goal-based query expansion if false |
| `ENHANCED_CHAT_ENABLE_PHASE_SPECIFIC_QUERIES` | `true` | Enable phase-specific query generation | Disables phase-based query expansion if false |

### Entity and Topic Features

| Environment Variable | Default | Description | Impact |
|---------------------|---------|-------------|---------|
| `ENHANCED_CHAT_ENABLE_ENTITY_TRACKING` | `true` | Enable entity tracking | Disables entity-based query generation if false |
| `ENHANCED_CHAT_ENABLE_TOPIC_TRACKING` | `true` | Enable topic tracking | Disables topic-based query generation if false |
| `ENHANCED_CHAT_ENABLE_CAPITALIZED_ENTITIES` | `true` | Enable extraction of capitalized entities | Disables detection of proper nouns if false |
| `ENHANCED_CHAT_ENABLE_KEYWORD_ENTITIES` | `true` | Enable extraction of keyword entities | Disables detection of technical terms if false |

## Entity and Topic Extraction

### Entity Extraction Settings

| Environment Variable | Default | Description | Impact |
|---------------------|---------|-------------|---------|
| `ENHANCED_CHAT_MIN_ENTITY_LENGTH` | `3` | Minimum length for entity extraction | Filters out very short entities |
| `ENHANCED_CHAT_MAX_ENTITIES_PER_MESSAGE` | `5` | Maximum entities extracted per message | Limits entity extraction per message |

### Topic Extraction Settings

| Environment Variable | Default | Description | Impact |
|---------------------|---------|-------------|---------|
| `ENHANCED_CHAT_MIN_TOPIC_LENGTH` | `4` | Minimum length for topic extraction | Filters out very short topics |
| `ENHANCED_CHAT_MAX_TOPICS_PER_MESSAGE` | `3` | Maximum topics extracted per message | Limits topic extraction per message |

## Usage Examples

### Basic Configuration

```env
# Standard conversation context (10 messages: 5 turns × 2)
ENHANCED_CHAT_MAX_TURNS=5
ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER=2

# Short message context (15 messages: 5 turns × 3)
ENHANCED_CHAT_SHORT_MSG_MULTIPLIER=3
```

### Extended Context Configuration

```env
# Extended conversation context (20 messages: 10 turns × 2)
ENHANCED_CHAT_MAX_TURNS=10
ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER=2

# Extended short message context (30 messages: 10 turns × 3)
ENHANCED_CHAT_SHORT_MSG_MULTIPLIER=3
```

### Performance-Optimized Configuration

```env
# Reduced context for better performance
ENHANCED_CHAT_MAX_TURNS=3
ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER=2
ENHANCED_CHAT_SHORT_MSG_MULTIPLIER=2
ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE=20

# Reduced query generation
ENHANCED_CHAT_MAX_QUERIES_PER_REQUEST=4
ENHANCED_CHAT_ENABLE_SUMMARY_QUERIES=false
```

### High-Quality Configuration

```env
# Extended context for better quality
ENHANCED_CHAT_MAX_TURNS=8
ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER=3
ENHANCED_CHAT_SHORT_MSG_MULTIPLIER=4

# Enhanced query generation
ENHANCED_CHAT_MAX_QUERIES_PER_REQUEST=12
ENHANCED_CHAT_CONDENSED_QUERY_WEIGHT=0.5
ENHANCED_CHAT_SUMMARY_QUERY_WEIGHT=0.4
```

## Context Window Calculation

The system uses adaptive context windows based on message complexity:

### Standard Messages
```
Context Window = min(max_turns × context_window_multiplier, available_messages, max_context_window_size)
```

### Short Messages (≤2 words)
```
Context Window = min(max_turns × short_message_multiplier, available_messages, max_context_window_size)
```

### Example Calculations

| Configuration | Standard Messages | Short Messages |
|---------------|-------------------|----------------|
| Default (5×2, 5×3) | 10 messages | 15 messages |
| Extended (8×2, 8×3) | 16 messages | 24 messages |
| Performance (3×2, 3×2) | 6 messages | 6 messages |

## Best Practices

### For Production Environments

1. **Start with Defaults**: Use default values initially and adjust based on performance metrics
2. **Monitor Memory Usage**: Higher context windows increase memory usage
3. **Balance Quality vs Performance**: More context improves quality but reduces performance
4. **Test with Real Conversations**: Validate settings with actual user conversations

### For Development Environments

1. **Use Extended Context**: Higher values help with debugging and development
2. **Enable All Features**: Keep all features enabled for comprehensive testing
3. **Monitor Logs**: Check logs for context window calculations and query generation

### For Testing Environments

1. **Use Minimal Context**: Lower values for faster test execution
2. **Disable Non-Essential Features**: Turn off features not being tested
3. **Consistent Settings**: Use the same settings across all test runs

## Troubleshooting

### Common Issues

1. **High Memory Usage**: Reduce `ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE`
2. **Slow Response Times**: Reduce `ENHANCED_CHAT_MAX_TURNS` and multipliers
3. **Poor Context Retention**: Increase `ENHANCED_CHAT_MAX_TURNS`
4. **Too Many Queries**: Reduce `ENHANCED_CHAT_MAX_QUERIES_PER_REQUEST`

### Performance Tuning

1. **Monitor Context Window Sizes**: Check logs for actual context window calculations
2. **Profile Query Generation**: Monitor time spent on query generation
3. **Memory Profiling**: Track memory usage with different settings
4. **Response Time Analysis**: Measure impact of settings on response times

## Migration Guide

### From Hardcoded Values

If you're migrating from hardcoded values, the environment variables map as follows:

| Old Hardcoded Value | New Environment Variable |
|-------------------|-------------------------|
| `max_turns=5` | `ENHANCED_CHAT_MAX_TURNS=5` |
| `max_turns * 2` | `ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER=2` |
| `max_turns * 3` | `ENHANCED_CHAT_SHORT_MSG_MULTIPLIER=3` |

### Validation

After setting environment variables, validate the configuration:

1. Check application logs for configuration loading
2. Verify context window calculations in debug logs
3. Test with known conversation patterns
4. Monitor performance metrics

## Related Documentation

- [Enhanced Chat Completion Implementation](../implementation/ENHANCED_SHORT_MESSAGE_CONTEXT_IMPLEMENTATION.md)
- [Enhanced Chat Configuration](../implementation/ENHANCED_CHAT_CONFIGURATION.md)
- [Performance Optimization Guide](../performance/PERFORMANCE_OPTIMIZATION.md)
