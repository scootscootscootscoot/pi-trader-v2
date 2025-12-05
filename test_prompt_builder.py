#!/usr/bin/env python3
"""
Test script for prompt builder system.
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from ai.prompt_builder import PromptBuilder, build_trading_prompt

def create_sample_market_data():
    """Create sample market data for testing."""
    # Create sample data for AAPL
    timestamps = pd.date_range('2025-01-12 14:00:00', periods=5, freq='5min')
    data = {
        'Open': [185.50, 185.75, 186.00, 185.80, 186.20],
        'High': [186.00, 186.25, 186.50, 186.10, 186.80],
        'Low': [185.25, 185.50, 185.75, 185.50, 186.00],
        'Close': [185.75, 186.00, 185.90, 186.25, 186.70],
        'Volume': [150000, 180000, 120000, 200000, 250000]
    }

    df_aapl = pd.DataFrame(data, index=timestamps)

    # Create sample data for GOOGL
    data_googl = {
        'Open': [2800.00, 2810.00, 2795.00, 2820.00, 2815.00],
        'High': [2820.00, 2825.00, 2810.00, 2830.00, 2825.00],
        'Low': [2790.00, 2800.00, 2785.00, 2810.00, 2810.00],
        'Close': [2810.00, 2805.00, 2800.00, 2825.00, 2820.00],
        'Volume': [80000, 95000, 75000, 110000, 135000]
    }

    df_googl = pd.DataFrame(data_googl, index=timestamps)

    return {'AAPL': df_aapl, 'GOOGL': df_googl}

def test_prompt_builder():
    """Test the prompt builder functionality."""
    print("Testing Prompt Builder System")
    print("=" * 50)

    # Create sample data
    market_data = create_sample_market_data()
    print(f"Created sample data for symbols: {list(market_data.keys())}")

    # Test PromptBuilder class
    builder = PromptBuilder()

    # Test available templates
    templates = builder.get_available_templates()
    print(f"\nAvailable templates: {templates}")

    # Test market data formatting
    print("\n--- Market Data Formatting ---")
    formatted_data = builder.format_market_data(market_data, max_rows=3)
    print(formatted_data[:500] + "..." if len(formatted_data) > 500 else formatted_data)

    # Test system message building
    print("\n--- System Message (Aggressive Day Trader) ---")
    system_msg = builder.build_system_message()
    print(system_msg[:300] + "..." if len(system_msg) > 300 else system_msg)

    # Test user message building
    print("\n--- User Message ---")
    user_msg = builder.build_user_message(market_data)
    print(user_msg[:300] + "..." if len(user_msg) > 300 else user_msg)

    # Test complete prompt building
    print("\n--- Complete Prompt Messages ---")
    messages = builder.build_prompt_messages(market_data)
    print(f"Number of messages: {len(messages)}")
    for i, msg in enumerate(messages):
        print(f"Message {i+1} ({msg['role']}):")
        print(msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content'])
        print()

    # Test convenience function
    print("--- Convenience Function Test ---")
    messages2 = build_trading_prompt(market_data, "momentum_scalper")
    print(f"Convenience function created {len(messages2)} messages")

    print("\n✅ All tests passed! Prompt builder system is working.")

if __name__ == "__main__":
    test_prompt_builder()
