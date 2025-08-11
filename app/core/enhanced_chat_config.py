"""
Configuration for Enhanced Chat Completion Service
"""

from typing import Dict, Any
from app.core.config import Config

# Query Generation Configuration
QUERY_GENERATION_CONFIG = {
    "max_conversation_turns": 5,
    "condensed_query_weight": 0.4,
    "summary_query_weight": 0.3,
    "original_query_weight": 0.3,
    "enable_goal_tracking": True,
    "enable_phase_detection": True,
    "max_queries_per_request": 8,
    "min_query_length": 10,
    "max_query_length": 200
}

# Conversation State Configuration
CONVERSATION_STATE_CONFIG = {
    "max_entities_tracked": 10,
    "max_constraints_tracked": 5,
    "state_persistence_turns": 10,
    "goal_detection_threshold": 0.7,
    "phase_detection_confidence": 0.6,
    "max_conversation_history_length": 50
}

# Multi-Turn Strategy Configuration
MULTI_TURN_STRATEGY_CONFIG = {
    "enable_condensed_queries": True,
    "enable_summary_queries": True,
    "enable_goal_oriented_queries": True,
    "enable_phase_specific_queries": True,
    "enable_entity_tracking": True,
    "enable_topic_tracking": True,
    "condensed_query_max_turns": 5,
    "summary_query_max_turns": 5
}

# Entity Extraction Configuration
ENTITY_EXTRACTION_CONFIG = {
    "min_entity_length": 3,
    "max_entities_per_message": 5,
    "entity_keywords": [
        "api", "rag", "llm", "ai", "ml", "brd", "basel", "sme",
        "compliance", "risk", "policy", "document", "requirement"
    ],
    "enable_capitalized_entities": True,
    "enable_keyword_entities": True
}

# Topic Extraction Configuration
TOPIC_EXTRACTION_CONFIG = {
    "min_topic_length": 4,
    "max_topics_per_message": 3,
    "topic_keywords": [
        "compliance", "risk", "policy", "document", "requirement",
        "implementation", "migration", "assessment", "analysis",
        "development", "testing", "deployment", "maintenance"
    ]
}

# Goal Detection Configuration
GOAL_DETECTION_CONFIG = {
    "goal_indicators": [
        "need to", "want to", "must", "should", "goal", "objective",
        "prepare", "create", "develop", "implement", "achieve",
        "complete", "finish", "build", "design", "plan"
    ],
    "goal_phrase_max_length": 100,
    "goal_detection_confidence": 0.7
}

# Phase Detection Configuration
PHASE_DETECTION_CONFIG = {
    "phases": {
        "planning": {
            "indicators": ["plan", "structure", "outline", "framework", "approach"],
            "confidence_threshold": 0.6
        },
        "drafting": {
            "indicators": ["draft", "write", "create", "develop", "prepare"],
            "confidence_threshold": 0.6
        },
        "reviewing": {
            "indicators": ["review", "check", "validate", "verify", "assess"],
            "confidence_threshold": 0.6
        },
        "finalizing": {
            "indicators": ["finalize", "complete", "finish", "submit", "approve"],
            "confidence_threshold": 0.6
        }
    },
    "default_phase": "planning"
}

# Constraint Detection Configuration
CONSTRAINT_DETECTION_CONFIG = {
    "constraint_indicators": [
        "must", "should", "required", "mandatory", "compliance",
        "deadline", "budget", "scope", "limitation", "constraint"
    ],
    "max_constraints_per_message": 3
}

# Action Detection Configuration
ACTION_DETECTION_CONFIG = {
    "action_words": [
        "draft", "write", "review", "check", "validate",
        "update", "modify", "change", "improve", "enhance",
        "implement", "deploy", "test", "analyze", "assess"
    ],
    "max_actions_per_message": 2
}

# Logging Configuration
LOGGING_CONFIG = {
    "enable_detailed_logging": True,
    "log_query_generation": True,
    "log_conversation_state": True,
    "log_entity_extraction": True,
    "log_goal_detection": True,
    "log_phase_detection": True,
    "log_performance_metrics": True
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "max_processing_time_ms": 5000,
    "enable_query_caching": True,
    "cache_ttl_seconds": 300,
    "enable_parallel_processing": True,
    "max_concurrent_queries": 4
}

# Quality Assurance Configuration
QUALITY_CONFIG = {
    "enable_query_validation": True,
    "min_query_quality_score": 0.5,
    "enable_duplicate_detection": True,
    "enable_relevance_scoring": True,
    "relevance_threshold": 0.6
}

# Enhanced Chat Configuration
# Configuration for enhanced chat completion and progressive context relaxation

class EnhancedChatConfig:
    """Configuration for enhanced chat completion features"""
    
    # Progressive Context Relaxation Configuration
    PROGRESSIVE_CONTEXT_RELAXATION = {
        'initial_stage': 'moderate',  # 'moderate', 'relaxed', 'broad', 'very_broad'
        'enable_initial_context_boost': True,
        'initial_boost_turns': 3,  # Number of turns to apply initial boost
        'boost_top_k_increase': 2,  # Additional top_k for initial turns
        'boost_threshold_reduction': 0.05,  # Threshold reduction for initial turns
        'boost_context_weight_increase': 0.1,  # Context weight increase for initial turns
        'stage_transition_threshold': 0.6,  # Confidence threshold for stage transitions
        'max_top_k': 15,  # Maximum top_k value
        'min_similarity_threshold': 0.3,  # Minimum similarity threshold
        'max_context_weight': 1.0,  # Maximum context weight
    }
    
    # Adaptive Confidence Management Configuration
    ADAPTIVE_CONFIDENCE = {
        'base_threshold': 0.7,
        'min_threshold': 0.3,
        'max_threshold': 0.95,
        'turn_decay_factor': 0.05,
        'context_boost_factor': 0.1,
    }
    
    # Conversation Turn Tracking Configuration
    TURN_TRACKING = {
        'max_turn_history': 20,
        'confidence_trend_window': 5,  # Turns to consider for trend analysis
    }
    
    # Strategy Selection Configuration
    STRATEGY_SELECTION = {
        'complexity_threshold': 0.7,  # Threshold for high complexity conversations
        'technical_terms': ['api', 'code', 'function', 'error', 'debug', 'technical', 'implementation', 'algorithm'],
        'creative_terms': ['creative', 'design', 'art', 'story', 'narrative', 'imagine', 'brainstorm', 'idea'],
    }
    
    @classmethod
    def get_progressive_context_config(cls) -> Dict[str, Any]:
        """Get progressive context relaxation configuration"""
        return cls.PROGRESSIVE_CONTEXT_RELAXATION.copy()
    
    @classmethod
    def get_adaptive_confidence_config(cls) -> Dict[str, Any]:
        """Get adaptive confidence management configuration"""
        return cls.ADAPTIVE_CONFIDENCE.copy()
    
    @classmethod
    def get_turn_tracking_config(cls) -> Dict[str, Any]:
        """Get conversation turn tracking configuration"""
        return cls.TURN_TRACKING.copy()
    
    @classmethod
    def get_strategy_selection_config(cls) -> Dict[str, Any]:
        """Get strategy selection configuration"""
        return cls.STRATEGY_SELECTION.copy()
    
    @classmethod
    def update_progressive_context_config(cls, **kwargs):
        """Update progressive context relaxation configuration"""
        cls.PROGRESSIVE_CONTEXT_RELAXATION.update(kwargs)
    
    @classmethod
    def update_adaptive_confidence_config(cls, **kwargs):
        """Update adaptive confidence management configuration"""
        cls.ADAPTIVE_CONFIDENCE.update(kwargs)
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Get all enhanced chat configuration"""
        return {
            'progressive_context_relaxation': cls.get_progressive_context_config(),
            'adaptive_confidence': cls.get_adaptive_confidence_config(),
            'turn_tracking': cls.get_turn_tracking_config(),
            'strategy_selection': cls.get_strategy_selection_config(),
        }

def get_config() -> Dict[str, Any]:
    """Get the complete configuration for enhanced chat completion"""
    return {
        "query_generation": QUERY_GENERATION_CONFIG,
        "conversation_state": CONVERSATION_STATE_CONFIG,
        "multi_turn_strategy": MULTI_TURN_STRATEGY_CONFIG,
        "entity_extraction": ENTITY_EXTRACTION_CONFIG,
        "topic_extraction": TOPIC_EXTRACTION_CONFIG,
        "goal_detection": GOAL_DETECTION_CONFIG,
        "phase_detection": PHASE_DETECTION_CONFIG,
        "constraint_detection": CONSTRAINT_DETECTION_CONFIG,
        "action_detection": ACTION_DETECTION_CONFIG,
        "logging": LOGGING_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "quality": QUALITY_CONFIG
    }

def get_query_generation_config() -> Dict[str, Any]:
    """Get query generation configuration"""
    return QUERY_GENERATION_CONFIG

def get_conversation_state_config() -> Dict[str, Any]:
    """Get conversation state configuration"""
    return CONVERSATION_STATE_CONFIG

def get_multi_turn_strategy_config() -> Dict[str, Any]:
    """Get multi-turn strategy configuration"""
    return MULTI_TURN_STRATEGY_CONFIG

def get_entity_extraction_config() -> Dict[str, Any]:
    """Get entity extraction configuration"""
    return ENTITY_EXTRACTION_CONFIG

def get_topic_extraction_config() -> Dict[str, Any]:
    """Get topic extraction configuration"""
    return TOPIC_EXTRACTION_CONFIG

def get_goal_detection_config() -> Dict[str, Any]:
    """Get goal detection configuration"""
    return GOAL_DETECTION_CONFIG

def get_phase_detection_config() -> Dict[str, Any]:
    """Get phase detection configuration"""
    return PHASE_DETECTION_CONFIG

def get_constraint_detection_config() -> Dict[str, Any]:
    """Get constraint detection configuration"""
    return CONSTRAINT_DETECTION_CONFIG

def get_action_detection_config() -> Dict[str, Any]:
    """Get action detection configuration"""
    return ACTION_DETECTION_CONFIG

def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration"""
    return LOGGING_CONFIG

def get_performance_config() -> Dict[str, Any]:
    """Get performance configuration"""
    return PERFORMANCE_CONFIG

def get_quality_config() -> Dict[str, Any]:
    """Get quality assurance configuration"""
    return QUALITY_CONFIG
