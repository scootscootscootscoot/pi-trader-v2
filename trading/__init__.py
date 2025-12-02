"""
Trading module for Alpaca integration.

This module provides functionality for:
- Account management
- Order placement (market, limit, stop orders)
- Position tracking
- Market data retrieval
"""

from .alpaca_client import (
    AlpacaTradingClient,
    get_account_balance,
    get_current_positions,
    place_buy_order,
    place_sell_order
)

__all__ = [
    'AlpacaTradingClient',
    'get_account_balance',
    'get_current_positions',
    'place_buy_order',
    'place_sell_order'
]
