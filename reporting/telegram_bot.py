import asyncio
import logging
from typing import List, Dict, Any

from telegram import Bot, Update
from telegram.error import TelegramError, Conflict
from telegram.ext import Application, CommandHandler

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
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.kill_requested = False

        # Add command handlers
        self.application.add_handler(CommandHandler("kill", self._kill_command))
        # Add error handler to handle polling conflicts
        self.application.add_error_handler(self._error_handler)

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

    async def send_start_message(self) -> bool:
        """
        Send notification when the trading bot starts.

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            message = "🤖 **Trading Bot Started**\n\nBot is now active and monitoring markets."
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            logger.info("Start message sent to Telegram")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send start message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending start message: {e}")
            return False

    async def send_stop_message(self) -> bool:
        """
        Send notification when the trading bot stops.

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            message = "🛑 **Trading Bot Stopped**\n\nBot has been shutdown."
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            logger.info("Stop message sent to Telegram")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send stop message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending stop message: {e}")
            return False

    async def start_bot(self) -> None:
        """Start the Telegram bot polling for messages."""
        try:
            await self.application.initialize()
            await self.application.start()
            # Temporarily disable polling due to persistent conflicts
            # await self.application.updater.start_polling(drop_pending_updates=True)
            logger.warning("Telegram polling DISABLED due to conflicts - commands won't work, but messages will")
            logger.info("To re-enable polling, remove the conflict source or use webhooks")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            # Don't raise exception to avoid crashing the whole system
            logger.warning("Telegram bot may not be able to receive commands, but sending messages will still work")

    async def stop_bot(self) -> None:
        """Stop the Telegram bot."""
        try:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Failed to stop Telegram bot: {e}")

    async def _kill_command(self, update: Update, context) -> None:
        """Handle the /kill command to stop the bot."""
        try:
            self.kill_requested = True
            await update.message.reply_text("💀 Kill command received. Shutting down bot...")
            logger.info("Kill command received, shutdown initiated")
        except Exception as e:
            logger.error(f"Error handling kill command: {e}")

    async def _error_handler(self, update: Update, context) -> bool:
        """Handle errors during bot polling."""
        try:
            if isinstance(context.error, Conflict):
                logger.error("Telegram polling conflict detected - another bot instance is running")
                logger.warning("Cannot receive commands due to polling conflict, but sending messages will work")
                # Try to stop polling for this instance to avoid repeated errors
                await self.application.updater.stop()
                return True  # Stop processing this error
            else:
                logger.error(f"Telegram bot error: {context.error}")
                return False  # Continue processing other errors
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
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
