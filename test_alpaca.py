#!/usr/bin/env python3
"""
Test script for Alpaca trading module.
This script tests the basic functionality without actually placing orders.
"""

from pathlib import Path
from dotenv import load_dotenv

# Load from the same directory as the script
env_path = Path(__file__).parent / '.env'
print(f"Loading .env from: {env_path}")
load_dotenv(dotenv_path=env_path)

# Rest of your imports and code...



import logging
import sys
import os
from dotenv import load_dotenv

# Add current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading.alpaca_client import AlpacaTradingClient

# Load API keys from environment (since settings.py has them commented)
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def test_alpaca_client():
    """Test basic Alpaca client functionality."""
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        logger.error("API keys not found. Please check your .env file.")
        return False

    try:
        # Initialize client
        logger.info("Testing Alpaca client initialization...")
        client = AlpacaTradingClient()
        logger.info("✓ Alpaca client initialized successfully")

        # Test getting account info
        logger.info("Testing account information retrieval...")
        account = client.get_account()
        logger.info(f"✓ Account retrieved: {account['account_type']} - Status: {account['status']}")
        logger.info(".2f")

        # Test getting positions
        logger.info("Testing positions retrieval...")
        positions = client.get_positions()
        logger.info(f"✓ Found {len(positions)} positions")

        # Test getting a quote (if we have any symbols)
        logger.info("Testing quote retrieval...")
        try:
            quote = client.get_latest_quote('AAPL')
            logger.info(f"✓ AAPL quote: Bid ${quote['bid_price']:.2f}, Ask ${quote['ask_price']:.2f}")
        except Exception as e:
            logger.warning(f"Quote test failed (this is normal if market is closed): {e}")

        logger.info("✓ All basic tests passed!")
        return True

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

def test_imports():
    """Test that all imports work correctly."""
    try:
        from trading import AlpacaTradingClient, get_account_balance
        logger.info("✓ Module imports successful")
        return True
    except ImportError as e:
        logger.error(f"Import failed: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    print("Testing Alpaca Trading Module")
    print("=" * 30)

    # Test imports first
    if not test_imports():
        sys.exit(1)

    # Test client functionality
    if not test_alpaca_client():
        sys.exit(1)

    print("\n✓ All tests passed!")
    print("\nThe Alpaca trading module is ready for use.")
