#!/usr/bin/env python3
"""
Example script demonstrating how to configure enhanced chat conversation context
using environment variables.

This script shows different configuration scenarios and their impact on context window sizes.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.enhanced_chat_config import (
    QUERY_GENERATION_CONFIG,
    MULTI_TURN_STRATEGY_CONFIG,
    CONTEXT_WINDOW_CONFIG,
    CONVERSATION_STATE_CONFIG
)


def print_configuration_summary(title: str, config: dict):
    """Print a formatted configuration summary"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print(f"{'='*60}")


def calculate_context_windows(max_turns: int, context_multiplier: int, short_multiplier: int):
    """Calculate and display context window sizes"""
    standard_window = max_turns * context_multiplier
    short_window = max_turns * short_multiplier
    
    print(f"\n📊 Context Window Calculations:")
    print(f"  Max Turns: {max_turns}")
    print(f"  Context Multiplier: {context_multiplier}")
    print(f"  Short Message Multiplier: {short_multiplier}")
    print(f"  Standard Context Window: {standard_window} messages")
    print(f"  Short Message Context Window: {short_window} messages")


def demonstrate_default_configuration():
    """Demonstrate the default configuration"""
    print("\n🎯 DEFAULT CONFIGURATION")
    print("This is the configuration when no environment variables are set.")
    
    print_configuration_summary("Query Generation Config", QUERY_GENERATION_CONFIG)
    print_configuration_summary("Multi-Turn Strategy Config", MULTI_TURN_STRATEGY_CONFIG)
    print_configuration_summary("Context Window Config", CONTEXT_WINDOW_CONFIG)
    
    max_turns = QUERY_GENERATION_CONFIG["max_conversation_turns"]
    context_multiplier = CONTEXT_WINDOW_CONFIG["context_window_multiplier"]
    short_multiplier = CONTEXT_WINDOW_CONFIG["short_message_multiplier"]
    
    calculate_context_windows(max_turns, context_multiplier, short_multiplier)


def demonstrate_extended_configuration():
    """Demonstrate extended context configuration"""
    print("\n🚀 EXTENDED CONTEXT CONFIGURATION")
    print("This configuration provides more context for better conversation quality.")
    
    # Set environment variables for extended configuration
    os.environ["ENHANCED_CHAT_MAX_TURNS"] = "8"
    os.environ["ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER"] = "3"
    os.environ["ENHANCED_CHAT_SHORT_MSG_MULTIPLIER"] = "4"
    os.environ["ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE"] = "80"
    os.environ["ENHANCED_CHAT_CONDENSED_MAX_TURNS"] = "6"
    os.environ["ENHANCED_CHAT_SUMMARY_MAX_TURNS"] = "7"
    
    # Re-import to get updated configuration
    import importlib
    import app.core.enhanced_chat_config
    importlib.reload(app.core.enhanced_chat_config)
    
    print_configuration_summary("Query Generation Config", app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG)
    print_configuration_summary("Multi-Turn Strategy Config", app.core.enhanced_chat_config.MULTI_TURN_STRATEGY_CONFIG)
    print_configuration_summary("Context Window Config", app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG)
    
    max_turns = app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG["max_conversation_turns"]
    context_multiplier = app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["context_window_multiplier"]
    short_multiplier = app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["short_message_multiplier"]
    
    calculate_context_windows(max_turns, context_multiplier, short_multiplier)


def demonstrate_performance_configuration():
    """Demonstrate performance-optimized configuration"""
    print("\n⚡ PERFORMANCE-OPTIMIZED CONFIGURATION")
    print("This configuration prioritizes performance over context depth.")
    
    # Clear previous environment variables
    for var in ["ENHANCED_CHAT_MAX_TURNS", "ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER", 
                "ENHANCED_CHAT_SHORT_MSG_MULTIPLIER", "ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE",
                "ENHANCED_CHAT_CONDENSED_MAX_TURNS", "ENHANCED_CHAT_SUMMARY_MAX_TURNS"]:
        if var in os.environ:
            del os.environ[var]
    
    # Set environment variables for performance configuration
    os.environ["ENHANCED_CHAT_MAX_TURNS"] = "3"
    os.environ["ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER"] = "2"
    os.environ["ENHANCED_CHAT_SHORT_MSG_MULTIPLIER"] = "2"
    os.environ["ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE"] = "20"
    os.environ["ENHANCED_CHAT_CONDENSED_MAX_TURNS"] = "3"
    os.environ["ENHANCED_CHAT_SUMMARY_MAX_TURNS"] = "3"
    os.environ["ENHANCED_CHAT_MAX_QUERIES_PER_REQUEST"] = "4"
    os.environ["ENHANCED_CHAT_ENABLE_SUMMARY_QUERIES"] = "false"
    
    # Re-import to get updated configuration
    import importlib
    import app.core.enhanced_chat_config
    importlib.reload(app.core.enhanced_chat_config)
    
    print_configuration_summary("Query Generation Config", app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG)
    print_configuration_summary("Multi-Turn Strategy Config", app.core.enhanced_chat_config.MULTI_TURN_STRATEGY_CONFIG)
    print_configuration_summary("Context Window Config", app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG)
    
    max_turns = app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG["max_conversation_turns"]
    context_multiplier = app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["context_window_multiplier"]
    short_multiplier = app.core.enhanced_chat_config.CONTEXT_WINDOW_CONFIG["short_message_multiplier"]
    
    calculate_context_windows(max_turns, context_multiplier, short_multiplier)


def demonstrate_feature_toggles():
    """Demonstrate feature toggle configuration"""
    print("\n🔧 FEATURE TOGGLE CONFIGURATION")
    print("This configuration shows how to enable/disable specific features.")
    
    # Clear previous environment variables
    for var in ["ENHANCED_CHAT_MAX_TURNS", "ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER", 
                "ENHANCED_CHAT_SHORT_MSG_MULTIPLIER", "ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE",
                "ENHANCED_CHAT_CONDENSED_MAX_TURNS", "ENHANCED_CHAT_SUMMARY_MAX_TURNS",
                "ENHANCED_CHAT_MAX_QUERIES_PER_REQUEST", "ENHANCED_CHAT_ENABLE_SUMMARY_QUERIES"]:
        if var in os.environ:
            del os.environ[var]
    
    # Set environment variables for feature toggles
    os.environ["ENHANCED_CHAT_ENABLE_GOAL_TRACKING"] = "false"
    os.environ["ENHANCED_CHAT_ENABLE_PHASE_DETECTION"] = "false"
    os.environ["ENHANCED_CHAT_ENABLE_CONDENSED_QUERIES"] = "false"
    os.environ["ENHANCED_CHAT_ENABLE_SUMMARY_QUERIES"] = "false"
    os.environ["ENHANCED_CHAT_ENABLE_ENTITY_TRACKING"] = "true"
    os.environ["ENHANCED_CHAT_ENABLE_TOPIC_TRACKING"] = "true"
    
    # Re-import to get updated configuration
    import importlib
    import app.core.enhanced_chat_config
    importlib.reload(app.core.enhanced_chat_config)
    
    print_configuration_summary("Query Generation Config", app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG)
    print_configuration_summary("Multi-Turn Strategy Config", app.core.enhanced_chat_config.MULTI_TURN_STRATEGY_CONFIG)
    
    print("\n🔍 Feature Status:")
    print(f"  Goal Tracking: {app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG['enable_goal_tracking']}")
    print(f"  Phase Detection: {app.core.enhanced_chat_config.QUERY_GENERATION_CONFIG['enable_phase_detection']}")
    print(f"  Condensed Queries: {app.core.enhanced_chat_config.MULTI_TURN_STRATEGY_CONFIG['enable_condensed_queries']}")
    print(f"  Summary Queries: {app.core.enhanced_chat_config.MULTI_TURN_STRATEGY_CONFIG['enable_summary_queries']}")
    print(f"  Entity Tracking: {app.core.enhanced_chat_config.MULTI_TURN_STRATEGY_CONFIG['enable_entity_tracking']}")
    print(f"  Topic Tracking: {app.core.enhanced_chat_config.MULTI_TURN_STRATEGY_CONFIG['enable_topic_tracking']}")


def show_usage_examples():
    """Show practical usage examples"""
    print("\n📖 USAGE EXAMPLES")
    print("Here are some practical examples of how to use environment variables:")
    
    examples = [
        {
            "name": "Basic Configuration",
            "description": "Standard conversation context (10 messages: 5 turns × 2)",
            "env_vars": {
                "ENHANCED_CHAT_MAX_TURNS": "5",
                "ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER": "2",
                "ENHANCED_CHAT_SHORT_MSG_MULTIPLIER": "3"
            }
        },
        {
            "name": "Extended Context",
            "description": "Extended conversation context (20 messages: 10 turns × 2)",
            "env_vars": {
                "ENHANCED_CHAT_MAX_TURNS": "10",
                "ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER": "2",
                "ENHANCED_CHAT_SHORT_MSG_MULTIPLIER": "3"
            }
        },
        {
            "name": "Performance Optimized",
            "description": "Reduced context for better performance",
            "env_vars": {
                "ENHANCED_CHAT_MAX_TURNS": "3",
                "ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER": "2",
                "ENHANCED_CHAT_SHORT_MSG_MULTIPLIER": "2",
                "ENHANCED_CHAT_MAX_CONTEXT_WINDOW_SIZE": "20",
                "ENHANCED_CHAT_MAX_QUERIES_PER_REQUEST": "4"
            }
        },
        {
            "name": "High Quality",
            "description": "Extended context for better quality",
            "env_vars": {
                "ENHANCED_CHAT_MAX_TURNS": "8",
                "ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER": "3",
                "ENHANCED_CHAT_SHORT_MSG_MULTIPLIER": "4",
                "ENHANCED_CHAT_MAX_QUERIES_PER_REQUEST": "12"
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}")
        print(f"   {example['description']}")
        print("   Environment Variables:")
        for key, value in example['env_vars'].items():
            print(f"   export {key}={value}")
        
        # Calculate context windows
        max_turns = int(example['env_vars'].get('ENHANCED_CHAT_MAX_TURNS', 5))
        context_multiplier = int(example['env_vars'].get('ENHANCED_CHAT_CONTEXT_WINDOW_MULTIPLIER', 2))
        short_multiplier = int(example['env_vars'].get('ENHANCED_CHAT_SHORT_MSG_MULTIPLIER', 3))
        
        standard_window = max_turns * context_multiplier
        short_window = max_turns * short_multiplier
        
        print(f"   Context Windows: Standard={standard_window}, Short={short_window}")


def main():
    """Main function to demonstrate all configurations"""
    print("🎯 Enhanced Chat Environment Variables Configuration Demo")
    print("This script demonstrates how to configure conversation context using environment variables.")
    
    try:
        # Demonstrate different configurations
        demonstrate_default_configuration()
        demonstrate_extended_configuration()
        demonstrate_performance_configuration()
        demonstrate_feature_toggles()
        show_usage_examples()
        
        print("\n✅ Configuration demonstration completed successfully!")
        print("\n💡 Tips:")
        print("  - Use environment variables to configure without code changes")
        print("  - Start with defaults and adjust based on performance metrics")
        print("  - Monitor memory usage with higher context windows")
        print("  - Test configurations with real conversations")
        print("  - Use feature toggles to enable/disable specific functionality")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
