import asyncio
import logging
from typing import List, Dict, Any

from telegram import Bot
from telegram.error import TelegramError

from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# Configure logging
logger = logging.getLogger(__name__)

class TelegramReporter:
    """Async Telegram bot for reporting trading data and alerts."""

    def __init__(self):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            raise ValueError("Telegram bot token and chat ID must be configured in settings.")
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.chat_id = TELEGRAM_CHAT_ID

    async def send_daily_summary(self, pnl: float, trades: List[Dict[str, Any]], insights: str) -> bool:
        """
        Send daily summary report to Telegram.

        Args:
            pnl: Profit and loss amount
            trades: List of trade dictionaries
            insights: AI-generated insights

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Format the summary message
            trade_count = len(trades)
            insights_formatted = insights[:4000]  # Limit message length

            message = f"� **Daily Trading Summary**\n\n💰 P&L: ${pnl:.2f}\n📈 Trades: {trade_count}\n\n🔍 **Insights:**\n{insights_formatted}"

            await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='Markdown')
            logger.info("Daily summary sent to Telegram")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send daily summary: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending daily summary: {e}")
            return False

    async def send_error_alert(self, error_message: str) -> bool:
        """
        Send error alert to Telegram.

        Args:
            error_message: Error message to send

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            message = f"🚨 **Error Alert**\n\n{error_message}"
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            logger.warning(f"Error alert sent to Telegram: {error_message}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send error alert: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending error alert: {e}")
            return False

# Global instance for easy access
_telegram_reporter = None

def get_telegram_reporter() -> TelegramReporter:
    """Get the global Telegram reporter instance."""
    global _telegram_reporter
    if _telegram_reporter is None:
        try:
            _telegram_reporter = TelegramReporter()
        except ValueError as e:
            logger.error(f"Failed to initialize Telegram reporter: {e}")
            raise
    return _telegram_reporter

# Convenience functions for async reporting
async def report_daily_summary(pnl: float, trades: List[Dict[str, Any]], insights: str) -> bool:
    """Convenience function to send daily summary."""
    return await get_telegram_reporter().send_daily_summary(pnl, trades, insights)

async def report_error(error_message: str) -> bool:
    """Convenience function to send error alert."""
    return await get_telegram_reporter().send_error_alert(error_message)
