"""
Trade logging system for recording and reviewing trading activities.

This module provides comprehensive logging of all trading activities,
including signal generation, order placement, execution, and performance tracking.
"""

import logging
import os
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import pytz

logger = logging.getLogger(__name__)

class TradeLogger:
    """
    Comprehensive trade logging system for recording and reviewing trading activities.

    Features:
    - Daily log files with structured JSON format
    - Trade signal logging with full context
    - Order execution tracking with order IDs
    - Performance metrics and P&L tracking
    - Daily summary reports
    """

    def __init__(self, log_directory: str = "logs"):
        """
        Initialize the trade logger.

        Args:
            log_directory: Directory to store log files
        """
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)

        # Current day's log file
        self.current_date = None
        self.current_log_file = None
        self.daily_trades = []

        # Set up logging
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging configuration for trade activities."""
        # Create a specific logger for trades
        self.trade_logger = logging.getLogger('trading.activity')
        self.trade_logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        self.log_directory.mkdir(exist_ok=True)

        # File handler will be set up daily
        self.file_handler = None

    def _get_daily_log_file(self, target_date: Optional[date] = None) -> Path:
        """
        Get the log file path for a specific date.

        Args:
            target_date: Date for the log file (defaults to today)

        Returns:
            Path to the log file
        """
        if target_date is None:
            target_date = date.today()

        return self.log_directory / f"trading_activity_{target_date.isoformat()}.json"

    def _ensure_daily_log_handler(self):
        """Ensure we have the correct file handler for today's date."""
        today = date.today()

        if self.current_date != today:
            # Remove old handler if it exists
            if self.file_handler and self.trade_logger.hasHandler(self.file_handler):
                self.trade_logger.removeHandler(self.file_handler)

            # Create new handler for today
            self.current_log_file = self._get_daily_log_file(today)
            self.file_handler = logging.FileHandler(self.current_log_file, mode='a', encoding='utf-8')
            self.file_handler.setLevel(logging.INFO)

            # Set formatter for structured logging
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.file_handler.setFormatter(formatter)

            # Add handler to logger
            self.trade_logger.addHandler(self.file_handler)
            self.current_date = today

            # Reset daily trades list for new day
            self.daily_trades = []

    def log_signal_generation(self, symbol: str, signal_data: Dict[str, Any],
                            ai_response: str, confidence: int):
        """
        Log the generation of a trading signal.

        Args:
            symbol: Stock symbol
            signal_data: Signal details (action, price, quantity, etc.)
            ai_response: Raw AI response that generated the signal
            confidence: AI confidence level (0-100)
        """
        self._ensure_daily_log_handler()

        log_entry = {
            'timestamp': datetime.now(pytz.UTC).isoformat(),
            'type': 'signal_generated',
            'symbol': symbol,
            'signal': signal_data,
            'ai_response': ai_response[:500],  # Truncate long responses
            'confidence': confidence,
            'market_conditions': self._get_market_context()
        }

        # Log to file
        self.trade_logger.info(f"SIGNAL_GENERATED: {json.dumps(log_entry)}")

        # Also log to console for immediate visibility
        logger.info(f"Generated signal for {symbol}: {signal_data.get('action', 'unknown')} "
                   f"at ${signal_data.get('price', 0):.2f} (confidence: {confidence}%)")

    def log_signal_execution(self, signal: Dict[str, Any], order_id: str,
                           execution_price: Optional[float] = None,
                           quantity: Optional[int] = None):
        """
        Log the execution of a trading signal.

        Args:
            signal: The executed signal data
            order_id: Alpaca order ID
            execution_price: Actual execution price (if available)
            quantity: Actual quantity executed
        """
        self._ensure_daily_log_handler()

        log_entry = {
            'timestamp': datetime.now(pytz.UTC).isoformat(),
            'type': 'signal_executed',
            'symbol': signal.get('symbol'),
            'action': signal.get('action'),
            'intended_price': signal.get('price'),
            'execution_price': execution_price,
            'quantity': quantity or signal.get('quantity'),
            'order_id': order_id,
            'confidence': signal.get('confidence'),
            'reason': signal.get('reason', ''),
            'stop_loss': signal.get('stop_loss')
        }

        # Add to daily trades for summary
        self.daily_trades.append(log_entry)

        # Log to file
        self.trade_logger.info(f"SIGNAL_EXECUTED: {json.dumps(log_entry)}")

        # Log to console
        price_info = f" at ${execution_price:.2f}" if execution_price else f" (limit: ${signal.get('price', 0):.2f})"
        logger.info(f"Executed {signal.get('action', 'unknown')} order for {quantity or signal.get('quantity')} "
                   f"{signal.get('symbol')}{price_info} (Order ID: {order_id})")

    def log_signal_rejection(self, signal: Dict[str, Any], reason: str):
        """
        Log when a signal is rejected.

        Args:
            signal: The rejected signal data
            reason: Reason for rejection
        """
        self._ensure_daily_log_handler()

        log_entry = {
            'timestamp': datetime.now(pytz.UTC).isoformat(),
            'type': 'signal_rejected',
            'symbol': signal.get('symbol'),
            'action': signal.get('action'),
            'price': signal.get('price'),
            'confidence': signal.get('confidence'),
            'reason': reason
        }

        # Log to file
        self.trade_logger.info(f"SIGNAL_REJECTED: {json.dumps(log_entry)}")

        # Log to console
        logger.info(f"Rejected signal for {signal.get('symbol')}: {reason}")

    def log_order_status_update(self, order_id: str, symbol: str, status: str,
                              filled_qty: Optional[int] = None,
                              filled_price: Optional[float] = None):
        """
        Log order status updates from Alpaca.

        Args:
            order_id: Alpaca order ID
            symbol: Stock symbol
            status: Order status (filled, cancelled, etc.)
            filled_qty: Quantity filled
            filled_price: Average fill price
        """
        self._ensure_daily_log_handler()

        log_entry = {
            'timestamp': datetime.now(pytz.UTC).isoformat(),
            'type': 'order_update',
            'order_id': order_id,
            'symbol': symbol,
            'status': status,
            'filled_quantity': filled_qty,
            'filled_price': filled_price
        }

        # Log to file
        self.trade_logger.info(f"ORDER_UPDATE: {json.dumps(log_entry)}")

        # Log to console
        logger.info(f"Order {order_id} ({symbol}) status: {status}"
                   f"{f' - filled {filled_qty}@{filled_price:.2f}' if filled_qty and filled_price else ''}")

    def log_daily_summary(self, account_equity: float, starting_equity: float = 100000.0):
        """
        Generate and log daily summary statistics.

        Args:
            account_equity: Current account equity
            starting_equity: Starting equity for the day
        """
        self._ensure_daily_log_handler()

        # Calculate daily P&L
        daily_pnl = account_equity - starting_equity
        daily_pnl_percent = (daily_pnl / starting_equity) * 100 if starting_equity > 0 else 0

        # Count trades by type
        buy_trades = [t for t in self.daily_trades if t.get('action') == 'buy']
        sell_trades = [t for t in self.daily_trades if t.get('action') == 'sell']

        summary = {
            'date': date.today().isoformat(),
            'total_trades': len(self.daily_trades),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'symbols_traded': list(set(t.get('symbol') for t in self.daily_trades)),
            'starting_equity': starting_equity,
            'ending_equity': account_equity,
            'daily_pnl': daily_pnl,
            'daily_pnl_percent': daily_pnl_percent,
            'trades': self.daily_trades
        }

        # Log summary to file
        self.trade_logger.info(f"DAILY_SUMMARY: {json.dumps(summary)}")

        # Log to console
        logger.info(f"Daily Summary - Trades: {len(self.daily_trades)}, "
                   f"P&L: ${daily_pnl:.2f} ({daily_pnl_percent:.2f}%), "
                   f"Symbols: {', '.join(summary['symbols_traded'])}")

        return summary

    def get_daily_trades(self, target_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Get all trades for a specific date.

        Args:
            target_date: Date to get trades for (defaults to today)

        Returns:
            List of trade dictionaries
        """
        log_file = self._get_daily_log_file(target_date)

        if not log_file.exists():
            return []

        trades = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'SIGNAL_EXECUTED:' in line:
                        # Extract JSON from log line
                        json_start = line.find('{')
                        if json_start != -1:
                            try:
                                trade_data = json.loads(line[json_start:])
                                trades.append(trade_data)
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Error reading daily trades from {log_file}: {e}")

        return trades

    def get_trading_history(self, days: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get trading history for the last N days.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary with dates as keys and trade lists as values
        """
        history = {}
        today = date.today()

        for i in range(days):
            target_date = today - timedelta(days=i)
            trades = self.get_daily_trades(target_date)
            if trades:  # Only include days with trades
                history[target_date.isoformat()] = trades

        return history

    def _get_market_context(self) -> Dict[str, Any]:
        """
        Get current market context (could be expanded with more data).

        Returns:
            Dictionary with market context information
        """
        # For now, just return basic timestamp info
        # This could be expanded to include market indices, volatility, etc.
        return {
            'timestamp': datetime.now(pytz.UTC).isoformat(),
            'timezone': 'UTC'
        }

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up old log files.

        Args:
            days_to_keep: Number of days of logs to keep
        """
        import glob
        from datetime import timedelta

        cutoff_date = date.today() - timedelta(days=days_to_keep)

        # Find all log files
        log_pattern = str(self.log_directory / "trading_activity_*.json")

        for log_file in glob.glob(log_pattern):
            try:
                # Extract date from filename
                filename = Path(log_file).name
                date_str = filename.replace('trading_activity_', '').replace('.json', '')

                file_date = date.fromisoformat(date_str)

                if file_date < cutoff_date:
                    os.remove(log_file)
                    logger.info(f"Removed old log file: {log_file}")

            except (ValueError, OSError) as e:
                logger.warning(f"Error processing log file {log_file}: {e}")

# Global instance for easy access
_trade_logger = None

def get_trade_logger() -> TradeLogger:
    """Get the global trade logger instance."""
    global _trade_logger
    if _trade_logger is None:
        _trade_logger = TradeLogger()
    return _trade_logger
