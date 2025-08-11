"""
Unit tests for inhouse LLM memory configuration.
Tests that the INHOUSE_LLM_ENABLE_MEMORY environment variable is properly loaded.
"""

import os
import pytest
from unittest.mock import patch
from app.core.config import Config


class TestInhouseLLMMemoryConfig:
    """Test cases for inhouse LLM memory configuration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Clear any existing environment variables
        if "INHOUSE_LLM_ENABLE_MEMORY" in os.environ:
            del os.environ["INHOUSE_LLM_ENABLE_MEMORY"]
    
    def teardown_method(self):
        """Clean up test fixtures"""
        # Clear environment variables after each test
        if "INHOUSE_LLM_ENABLE_MEMORY" in os.environ:
            del os.environ["INHOUSE_LLM_ENABLE_MEMORY"]
    
    def test_default_memory_configuration(self):
        """Test that default memory configuration is set correctly"""
        # Default should be False
        assert Config.INHOUSE_LLM_ENABLE_MEMORY is False
    
    def test_environment_variable_enable_memory_true(self):
        """Test that INHOUSE_LLM_ENABLE_MEMORY=true sets the value correctly"""
        with patch.dict(os.environ, {"INHOUSE_LLM_ENABLE_MEMORY": "true"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.config
            importlib.reload(app.core.config)
            
            assert app.core.config.Config.INHOUSE_LLM_ENABLE_MEMORY is True
    
    def test_environment_variable_enable_memory_false(self):
        """Test that INHOUSE_LLM_ENABLE_MEMORY=false sets the value correctly"""
        with patch.dict(os.environ, {"INHOUSE_LLM_ENABLE_MEMORY": "false"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.config
            importlib.reload(app.core.config)
            
            assert app.core.config.Config.INHOUSE_LLM_ENABLE_MEMORY is False
    
    def test_environment_variable_case_insensitive(self):
        """Test that INHOUSE_LLM_ENABLE_MEMORY is case insensitive"""
        with patch.dict(os.environ, {"INHOUSE_LLM_ENABLE_MEMORY": "TRUE"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.config
            importlib.reload(app.core.config)
            
            assert app.core.config.Config.INHOUSE_LLM_ENABLE_MEMORY is True
    
    def test_environment_variable_invalid_value_fallback(self):
        """Test that invalid environment variable values fall back to default"""
        with patch.dict(os.environ, {"INHOUSE_LLM_ENABLE_MEMORY": "invalid"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.config
            importlib.reload(app.core.config)
            
            # Should fall back to default value (False)
            assert app.core.config.Config.INHOUSE_LLM_ENABLE_MEMORY is False
    
    def test_llm_provider_config_includes_memory_setting(self):
        """Test that get_llm_provider_config includes the memory setting for inhouse provider"""
        with patch.dict(os.environ, {"PROVIDER_LLM_TYPE": "inhouse", "INHOUSE_LLM_ENABLE_MEMORY": "true"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.config
            importlib.reload(app.core.config)
            
            config = app.core.config.Config.get_llm_provider_config()
            assert config["type"] == "inhouse"
            assert config["enable_memory"] is True
    
    def test_llm_provider_config_memory_disabled(self):
        """Test that get_llm_provider_config includes memory setting when disabled"""
        with patch.dict(os.environ, {"PROVIDER_LLM_TYPE": "inhouse", "INHOUSE_LLM_ENABLE_MEMORY": "false"}):
            # Re-import to get updated configuration
            import importlib
            import app.core.config
            importlib.reload(app.core.config)
            
            config = app.core.config.Config.get_llm_provider_config()
            assert config["type"] == "inhouse"
            assert config["enable_memory"] is False


if __name__ == "__main__":
    pytest.main([__file__])
