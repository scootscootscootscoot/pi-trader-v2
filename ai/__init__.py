"""
AI module for trading bot.

Provides prompt engineering, LLM integration, and AI-powered analysis
for trading strategies and market data processing.
"""

from .openrouter_client import OpenRouterClient, chat_completion, get_default_client, set_default_model
from .prompt_builder import PromptBuilder, build_trading_prompt

__all__ = [
    'OpenRouterClient',
    'chat_completion',
    'get_default_client',
    'set_default_model',
    'PromptBuilder',
    'build_trading_prompt'
]
