"""
Prompt engineering system for trading bot.

This module provides prompt templates and utilities for building prompts
to interact with LLMs for trading analysis and decision making.
"""

import logging
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptBuilder:
    """
    Builds prompts using strategy templates for trading analysis.

    Supports multiple strategy templates and formats market data
    for LLM consumption.
    """

    def __init__(self, default_template: str = "aggressive_day_trader"):
        """
        Initialize PromptBuilder with default template.

        Args:
            default_template: Default strategy template to use
        """
        self.default_template = default_template
        self.templates = {}
        self._load_templates()

    def _load_templates(self):
        """Load available strategy templates."""
        self.templates.update({
            "aggressive_day_trader": self._aggressive_day_trader_template(),
            "conservative_swing": self._conservative_swing_template(),
            "momentum_scalper": self._momentum_scalper_template()
        })
        logger.info(f"Loaded {len(self.templates)} strategy templates")

    def _aggressive_day_trader_template(self) -> str:
        """Template for aggressive day trading strategy."""
        return """You are an expert aggressive day trader specializing in high-frequency momentum plays.
Your goal is to identify short-term trading opportunities that can be captured within minutes to hours.

TRADING PHILOSOPHY:
- Focus on high-volatility moves with clear momentum
- Use technical analysis to identify entry/exit points
- Risk management: Maximum 2% per trade, stop losses mandatory
- Target 3:1 reward-to-risk ratio minimum
- Time frame: 5-15 minute charts, hold 3-60 minutes maximum

MARKET ANALYSIS:
{market_data}

TRADING RULES:
1. Look for strong volume surges with price momentum
2. Identify support/resistance levels and breakout patterns
3. Use RSI, MACD, and volume indicators for confirmation
4. Enter on pullbacks during strong trends
5. Exit quickly on profit targets or early warning signs

Please analyze the current market data and provide:
1. SHORT-TERM TRADING SIGNALS (next 5-30 minutes)
2. SPECIFIC ENTRY/EXIT PRICES for each symbol
3. RISK MANAGEMENT recommendations
4. CONFIDENCE LEVEL (0-100) for each signal

Format your response as:
SYMBOL: [SIGNAL] at $[PRICE] - Confidence: X% - Reason: [brief explanation]"""

    def _conservative_swing_template(self) -> str:
        """Template for conservative swing trading strategy."""
        return """You are a conservative swing trader focusing on higher-probability setups.
Your approach emphasizes risk management and longer-term price swings.

TRADING PHILOSOPHY:
- Identify clear trend continuation patterns
- Wait for optimal risk-reward setups
- Hold positions 1-5 days during strong trends
- Risk management: Maximum 1% per trade
- Target 2:1 reward-to-risk ratio minimum

MARKET ANALYSIS:
{market_data}

Please analyze and provide swing trading opportunities."""

    def _momentum_scalper_template(self) -> str:
        """Template for momentum scalping strategy."""
        return """You are a momentum scalper seeking quick intraday moves.
Focus on rapid price movements with high volume confirmation.

MARKET ANALYSIS:
{market_data}

TRADING RULES:
- Enter on momentum bursts
- Exit within 5-15 minutes
- Risk 0.5% per trade maximum

Please provide scalping signals."""

    def format_market_data(self, market_data: Dict[str, pd.DataFrame],
                          max_rows: int = 20) -> str:
        """
        Format market data dictionary into readable text for LLM.

        Args:
            market_data: Dict with symbols as keys and DataFrames as values
            max_rows: Maximum number of recent rows to include per symbol

        Returns:
            Formatted string representation of market data
        """
        if not market_data:
            return "NO MARKET DATA AVAILABLE"

        formatted_sections = []

        for symbol, df in market_data.items():
            if df.empty:
                continue

            # Take most recent rows
            recent_df = df.tail(max_rows).copy()

            # Calculate current price change before formatting columns
            current_info = "Current price data unavailable"
            if 'Close' in recent_df.columns and len(recent_df) > 0:
                latest_price = recent_df['Close'].iloc[-1]
                prev_price = recent_df['Close'].iloc[-2] if len(recent_df) > 1 else latest_price
                try:
                    change_pct = ((latest_price - prev_price) / prev_price) * 100
                    change_symbol = "+" if change_pct >= 0 else ""
                    formatted_price = f"{latest_price:.2f}"
                    current_info = f"Current: ${formatted_price} ({change_symbol}{change_pct:+.2f}%)"
                except (ZeroDivisionError, TypeError):
                    formatted_price = f"{latest_price:.2f}"
                    current_info = f"Current: ${formatted_price}"

            # Format timestamp column
            if 'Datetime' in recent_df.columns:
                recent_df['Datetime'] = recent_df['Datetime'].dt.strftime('%H:%M:%S')
            elif isinstance(recent_df.index, pd.DatetimeIndex):
                recent_df['Time'] = recent_df.index.strftime('%H:%M:%S')
                if 'Time' not in recent_df.columns:
                    recent_df = recent_df.reset_index().rename(columns={'index': 'Time'})
                    recent_df['Time'] = pd.to_datetime(recent_df['Time']).dt.strftime('%H:%M:%S')

            # Format numeric columns
            numeric_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            for col in numeric_cols:
                if col in recent_df.columns:
                    if col == 'Volume':
                        recent_df[col] = recent_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
                    else:
                        recent_df[col] = recent_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")

            # Create section
            section = f"""
SYMBOL: {symbol}
{current_info}

Recent {len(recent_df)} data points:
{recent_df.to_string(index=False, justify='left', max_rows=None)}
"""
            formatted_sections.append(section.strip())

        return "\n\n".join(formatted_sections)

    def build_system_message(self, template: Optional[str] = None) -> str:
        """
        Build system message using specified template.

        Args:
            template: Template name (uses default if None)

        Returns:
            System message string
        """
        template_name = template or self.default_template
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found. Available: {list(self.templates.keys())}")

        return self.templates[template_name]

    def build_user_message(self, market_data: Dict[str, pd.DataFrame],
                          additional_context: Optional[str] = None) -> str:
        """
        Build user message with market data and optional context.

        Args:
            market_data: Dictionary of market data
            additional_context: Additional context to include

        Returns:
            User message string
        """
        formatted_data = self.format_market_data(market_data)

        message = f"Current market conditions:\n\n{formatted_data}"

        if additional_context:
            message += f"\n\nAdditional context:\n{additional_context}"

        return message

    def build_prompt_messages(self, market_data: Dict[str, pd.DataFrame],
                            template: Optional[str] = None,
                            additional_context: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Build complete prompt as list of message dictionaries.

        Args:
            market_data: Market data dictionary
            template: Template name (uses default if None)
            additional_context: Additional context string

        Returns:
            List of message dicts for LLM API
        """
        system_msg = self.build_system_message(template)
        user_msg = self.build_user_message(market_data, additional_context)

        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]

    def get_available_templates(self) -> List[str]:
        """Get list of available template names."""
        return list(self.templates.keys())

    def add_template(self, name: str, template: str):
        """
        Add a custom template.

        Args:
            name: Template name
            template: Template string with {market_data} placeholder
        """
        if "{market_data}" not in template:
            raise ValueError("Template must contain {market_data} placeholder")
        self.templates[name] = template
        logger.info(f"Added custom template: {name}")

# Convenience functions
def build_trading_prompt(market_data: Dict[str, pd.DataFrame],
                        template: str = "aggressive_day_trader",
                        additional_context: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Convenience function to build trading prompt.

    Args:
        market_data: Market data dictionary
        template: Template name
        additional_context: Additional context

    Returns:
        List of message dictionaries
    """
    builder = PromptBuilder()
    return builder.build_prompt_messages(market_data, template, additional_context)
