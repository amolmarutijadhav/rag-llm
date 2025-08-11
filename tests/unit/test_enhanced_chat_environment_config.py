"""
Unit tests for enhanced chat environment variable configuration.
Tests that environment variables properly override default configuration values.
"""

import os
import pytest
from unittest.mock import patch
from app.core.enhanced_chat_config import (
    QUERY_GENERATION_CONFIG,
    MULTI_TURN_STRATEGY_CONFIG,
    CONTEXT_WINDOW_CONFIG,
    CONVERSATION_STATE_CONFIG,
    ENTITY_EXTRACTION_CONFIG,
    TOPIC_EXTRACTION_CONFIG,
    GOAL_DETECTION_CONFIG
)


class TestEnhancedChatEnvironmentConfig:
    """Test cases for enhanced chat environment variable configuration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Clear any existing environment variables
        self.env_vars_to_clear = [
            "ENHANCED_CHAT_MAX_TURNS",
            "ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER",
            "ENHANCED_CHAT_SHORT_MSG_MULTIPLIER",
            "ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE",
            "ENHANCED_CHAT_CONDENSED_MAX_TURNS",
            "ENHANCED_CHAT_SUMMARY_MAX_TURNS",
            "ENHANCED_CHAT_MAX_QUERIES_PER_REQUEST",
            "ENHANCED_CHAT_ENABLE_GOAL_TRACKING",
            "ENHANCED_CHAT_ENABLE_PHASE_DETECTION"
        ]
        
        for var in self.env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
    
    def teardown_method(self):
        """Clean up test fixtures"""
        # Clear environment variables after each test
        for var in self.env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
    
    def test_default_configuration_values(self):
        """Test that default configuration values are set correctly"""
        # Test core conversation context settings
        assert QUERY_GENERATION_CONFIG["max_conversation_turns"] == 5
        assert MULTI_TURN_STRATEGY_CONFIG["condensed_query_max_turns"] == 5
        assert MULTI_TURN_STRATEGY_CONFIG["summary_query_max_turns"] == 5
        
        # Test context window settings
        assert CONTEXT_WINDOW_CONFIG["context_window_multiplier"] == 2
        assert CONTEXT_WINDOW_CONFIG["short_message_multiplier"] == 3
        assert CONTEXT_WINDOW_CONFIG["max_context_window_size"] == 50
        
        # Test feature enablement
        assert QUERY_GENERATION_CONFIG["enable_goal_tracking"] is True
        assert QUERY_GENERATION_CONFIG["enable_phase_detection"] is True
        assert MULTI_TURN_STRATEGY_CONFIG["enable_condensed_queries"] is True
        assert MULTI_TURN_STRATEGY_CONFIG["enable_summary_queries"] is True
    
    def test_environment_variable_override_max_turns(self):
        """Test that ENHANCED_CHAT_MAX_TURNS overrides default value"""
        with patch.dict(os.environ, {"ENHANCED_CHAT_MAX_TURNS": "10"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.enhanced_chat_config
            importlib.reload(app.core.enhanced_chat_config)
            
            assert app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG["max_conversation_turns"] == 10
    
    def test_environment_variable_override_context_window_multiplier(self):
        """Test that ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER overrides default value"""
        with patch.dict(os.environ, {"ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER": "4"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.enhanced_chat_config
            importlib.reload(app.core.enhanced_chat_config)
            
            assert app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["context_window_multiplier"] == 4
    
    def test_environment_variable_override_short_message_multiplier(self):
        """Test that ENHANCED_CHAT_SHORT_MSG_MULTIPLIER overrides default value"""
        with patch.dict(os.environ, {"ENHANCED_CHAT_SHORT_MSG_MULTIPLIER": "5"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.enhanced_chat_config
            importlib.reload(app.core.enhanced_chat_config)
            
            assert app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["short_message_multiplier"] == 5
    
    def test_environment_variable_override_max_context_window_size(self):
        """Test that ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE overrides default value"""
        with patch.dict(os.environ, {"ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE": "100"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.enhanced_chat_config
            importlib.reload(app.core.enhanced_chat_config)
            
            assert app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["max_context_window_size"] == 100
    
    def test_environment_variable_override_condensed_max_turns(self):
        """Test that ENHANCED_CHAT_CONDENSED_MAX_TURNS overrides default value"""
        with patch.dict(os.environ, {"ENHANCED_CHAT_CONDENSED_MAX_TURNS": "8"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.enhanced_chat_config
            importlib.reload(app.core.enhanced_chat_config)
            
            assert app.core.enhanced_chat_config.MULTI_TURN_STRATEGY_CONFIG["condensed_query_max_turns"] == 8
    
    def test_environment_variable_override_summary_max_turns(self):
        """Test that ENHANCED_CHAT_SUMMARY_MAX_TURNS overrides default value"""
        with patch.dict(os.environ, {"ENHANCED_CHAT_SUMMARY_MAX_TURNS": "6"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.enhanced_chat_config
            importlib.reload(app.core.enhanced_chat_config)
            
            assert app.core.enhanced_chat_config.MULTI_TURN_STRATEGY_CONFIG["summary_query_max_turns"] == 6
    
    def test_environment_variable_override_boolean_features(self):
        """Test that boolean environment variables override default values"""
        with patch.dict(os.environ, {
            "ENHANCED_CHAT_ENABLE_GOAL_TRACKING": "false",
            "ENHANCED_CHAT_ENABLE_PHASE_DETECTION": "false"
        }):
            # Re-import to get updated configuration
            import importlib
            import app.core.enhanced_chat_config
            importlib.reload(app.core.enhanced_chat_config)
            
            assert app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG["enable_goal_tracking"] is False
            assert app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG["enable_phase_detection"] is False
    
    def test_environment_variable_override_float_values(self):
        """Test that float environment variables override default values"""
        with patch.dict(os.environ, {
            "ENHANCED_CHAT_CONDENSED_QUERY_WEIGHT": "0.6",
            "ENHANCED_CHAT_SUMMARY_QUERY_WEIGHT": "0.4"
        }):
            # Re-import to get updated configuration
            import importlib
            import app.core.enhanced_chat_config
            importlib.reload(app.core.enhanced_chat_config)
            
            assert app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG["condensed_query_weight"] == 0.6
            assert app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG["summary_query_weight"] == 0.4
    
    def test_invalid_environment_variable_fallback(self):
        """Test that invalid environment variables fall back to defaults"""
        with patch.dict(os.environ, {"ENHANCED_CHAT_MAX_TURNS": "invalid"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.enhanced_chat_config
            importlib.reload(app.core.enhanced_chat_config)
            
            # Should fall back to default value
            assert app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG["max_conversation_turns"] == 5
    
    def test_multiple_environment_variables(self):
        """Test that multiple environment variables work together"""
        with patch.dict(os.environ, {
            "ENHANCED_CHAT_MAX_TURNS": "8",
            "ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER": "3",
            "ENHANCED_CHAT_SHORT_MSG_MULTIPLIER": "4",
            "ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE": "80",
            "ENHANCED_CHAT_CONDENSED_MAX_TURNS": "6",
            "ENHANCED_CHAT_SUMMARY_MAX_TURNS": "7"
        }):
            # Re-import to get updated configuration
            import importlib
            import app.core.enhanced_chat_config
            importlib.reload(app.core.enhanced_chat_config)
            
            # Verify all values are updated
            assert app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG["max_conversation_turns"] == 8
            assert app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["context_window_multiplier"] == 3
            assert app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["short_message_multiplier"] == 4
            assert app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["max_context_window_size"] == 80
            assert app.core.enhanced_chat_config.MULTI_TURN_STRATEGY_CONFIG["condensed_query_max_turns"] == 6
            assert app.core.enhanced_chat_config.MULTI_TURN_STRATEGY_CONFIG["summary_query_max_turns"] == 7
    
    def test_context_window_calculation_with_environment_variables(self):
        """Test that context window calculation uses environment variable values"""
        with patch.dict(os.environ, {
            "ENHANCED_CHAT_MAX_TURNS": "6",
            "ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER": "2",
            "ENHANCED_CHAT_SHORT_MSG_MULTIPLIER": "3"
        }):
            # Re-import to get updated configuration
            import importlib
            import app.core.enhanced_chat_config
            importlib.reload(app.core.enhanced_chat_config)
            
            # Test context window calculations
            max_turns = app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG["max_conversation_turns"]
            context_multiplier = app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["context_window_multiplier"]
            short_multiplier = app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["short_message_multiplier"]
            
            # Standard context window: 6 * 2 = 12 messages
            expected_standard = max_turns * context_multiplier
            assert expected_standard == 12
            
            # Short message context window: 6 * 3 = 18 messages
            expected_short = max_turns * short_multiplier
            assert expected_short == 18


if __name__ == "__main__":
    pytest.main([__file__])
