import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Alpaca API credentials (commented out for alpaca-py, which handles auth per client)
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
ALPACA_PAPER_URL = os.getenv('ALPACA_PAPER_URL', 'https://paper-api.alpaca.markets')

# OpenRouter API
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL')

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Trading symbols
TRADING_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'SPY', 'QQQ', 'DIA']  # Default symbols for day trading plus major indexes
