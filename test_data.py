#!/usr/bin/env python3
"""
Test script for Yahoo Finance data module.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from config.settings import TRADING_SYMBOLS
from data.yahoo_finance import get_yahoo_finance_data
import logging

logging.basicConfig(level=logging.INFO)

def test_yahoo_finance():
    """Test fetching Yahoo Finance data."""
    symbols = TRADING_SYMBOLS[:2]  # Test with first 2 symbols
    print(f"Fetching data for symbols: {symbols}")

    data = get_yahoo_finance_data(symbols, period='1d', interval='5m')

    if data:
        print("Data fetching successful!")
        for symbol, df in data.items():
            print(f"Symbol: {symbol}")
            print(f"Data shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            if not df.empty:
                print("Sample data:")
                print(df.head())
            print("-" * 40)
    else:
        print("No data fetched.")

if __name__ == "__main__":
    test_yahoo_finance()
