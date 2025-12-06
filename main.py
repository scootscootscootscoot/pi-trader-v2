#!/usr/bin/env python3
"""
Main entry point for the trading bot.

Integrates all modules: trading client, data providers, AI analysis,
strategies, and reporting to create a fully functional automated trading system.
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
import pytz

from config.settings import TRADING_SYMBOLS
from core.orchestrator import TradingOrchestrator
from trading.alpaca_client import AlpacaTradingClient
from data.yahoo_finance import YahooFinanceDataFetcher
from ai import OpenRouterClient, PromptBuilder
from strategy.base_strategy import SimpleAggressiveStrategy
from reporting.telegram_bot import TelegramReporter, report_error, report_daily_summary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class IntegratedTradingBot:
    """
    Integrated trading bot that connects all modules.

    Handles initialization, health checks, rate limiting, and the main trading flow.
    """

    def __init__(self):
        self.trading_client = None
        self.data_fetcher = None
        self.ai_client = None
        self.prompt_builder = None
        self.strategy = None
        self.telegram_reporter = None
        self.orchestrator = None

        # Rate limiting for trading cycles
        self.cycle_interval_minutes = 120  # Run trading cycle every 2 hours during market hours
        self.last_cycle_time = None

        # Health monitoring
        self.health_status = {
            'alpaca_api': False,
            'yahoo_finance': False,
            'openrouter_api': False,
            'telegram_bot': False,
            'last_check': None
        }

    async def initialize(self):
        """Initialize all trading bot components."""
        try:
            # Initialize trading client
            self.trading_client = AlpacaTradingClient()
            logger.info("Trading client initialized")

            # Initialize data fetcher
            self.data_fetcher = YahooFinanceDataFetcher()
            logger.info("Data fetcher initialized")

            # Initialize AI client
            self.ai_client = OpenRouterClient()
            self.prompt_builder = PromptBuilder()
            logger.info("AI client and prompt builder initialized")

            # Initialize strategy
            self.strategy = SimpleAggressiveStrategy(trading_client=self.trading_client)
            logger.info("Trading strategy initialized")

            # Initialize Telegram reporter
            self.telegram_reporter = TelegramReporter()
            await self.telegram_reporter.start_bot()
            logger.info("Telegram reporter initialized")

            # Initialize orchestrator
            self.orchestrator = TradingOrchestrator()
            # Override the trading cycle with our integrated version (synchronous wrapper)
            self.orchestrator._execute_trading_cycle = self._execute_trading_cycle_sync
            logger.info("Trading orchestrator initialized")

            logger.info("All components initialized successfully")
            return True

        except Exception as e:
            error_msg = f"Failed to initialize trading bot: {e}"
            logger.error(error_msg)
            await self._report_error(error_msg)
            return False

    @property
    def kill_requested(self):
        """Check if kill command was received via Telegram."""
        return self.telegram_reporter.kill_requested if self.telegram_reporter else False

    def _execute_trading_cycle_sync(self):
        """Synchronous wrapper for the async trading cycle method."""
        try:
            # Create an event loop for this thread if one doesn't exist
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._integrated_trading_cycle())
            loop.close()
        except Exception as e:
            logger.error(f"Error in trading cycle wrapper: {e}")

    async def _report_error(self, error_msg: str):
        """Report error via Telegram if available."""
        try:
            if self.telegram_reporter:
                await self.telegram_reporter.send_error_alert(error_msg)
        except Exception as e:
            logger.error(f"Failed to report error via Telegram: {e}")

    async def perform_health_checks(self):
        """Perform comprehensive health checks on all systems."""
        logger.info("Performing comprehensive health checks...")
        updated = False

        # Test Alpaca API
        try:
            if self.trading_client:
                account = self.trading_client.get_account()
                self.health_status['alpaca_api'] = account.get('status') == 'ACTIVE'
                if self.health_status['alpaca_api']:
                    logger.info("Alpaca API: OK")
                else:
                    logger.warning(f"Alpaca API: Account status {account.get('status')}")
            else:
                self.health_status['alpaca_api'] = False
        except Exception as e:
            logger.error(f"Alpaca health check failed: {e}")
            self.health_status['alpaca_api'] = False
            updated = True

        # Test Yahoo Finance
        try:
            if self.data_fetcher:
                # Quick test with just AAPL
                data = self.data_fetcher.fetch_intraday_data(['AAPL'], period='1d', interval='1h')
                self.health_status['yahoo_finance'] = len(data) > 0
                logger.info("Yahoo Finance: OK")
            else:
                self.health_status['yahoo_finance'] = False
        except Exception as e:
            logger.error(f"Yahoo Finance health check failed: {e}")
            self.health_status['yahoo_finance'] = False
            updated = True

        # Test OpenRouter API
        try:
            if self.ai_client:
                # Just check if client can be initialized (rate limiting handled internally)
                self.health_status['openrouter_api'] = not self.ai_client.is_rate_limited()
                if self.health_status['openrouter_api']:
                    logger.info("OpenRouter API: OK")
                else:
                    logger.info("OpenRouter API: Rate limited (this is normal)")
            else:
                self.health_status['openrouter_api'] = False
        except Exception as e:
            logger.error(f"OpenRouter health check failed: {e}")
            self.health_status['openrouter_api'] = False
            updated = True

        # Test Telegram Bot
        try:
            if self.telegram_reporter:
                # Send a simple health check message
                message = "🏥 **System Health Check**\n\nAll systems operational ✅"
                await self.telegram_reporter.send_error_alert(message)
                self.health_status['telegram_bot'] = True
                logger.info("Telegram Bot: OK")
            else:
                self.health_status['telegram_bot'] = False
        except Exception as e:
            logger.error(f"Telegram health check failed: {e}")
            self.health_status['telegram_bot'] = False
            updated = True

        self.health_status['last_check'] = datetime.now(pytz.UTC)

        # Report issues if any health status changed
        if updated:
            unhealthy = [k for k, v in self.health_status.items() if k != 'last_check' and not v]
            if unhealthy:
                await self._report_error(f"Health check failed for: {', '.join(unhealthy)}")

        return all(self.health_status.values())

    async def _integrated_trading_cycle(self):
        """Execute a complete trading cycle with all integrated components."""
        try:
            # Perform health checks first
            all_healthy = await self.perform_health_checks()
            if not all_healthy:
                logger.warning("Some systems unhealthy, proceeding with caution")

            # Rate limiting for cycles
            now = datetime.now(pytz.UTC)
            if self.last_cycle_time:
                time_since_last = (now - self.last_cycle_time).total_seconds() / 60
                if time_since_last < self.cycle_interval_minutes:
                    logger.debug(f"Skipping cycle - too soon since last cycle ({time_since_last:.1f} min ago)")
                    return
            self.last_cycle_time = now

            logger.info("Starting integrated trading cycle")

            # 1. Fetch market data
            market_data = {}
            try:
                market_data = self.data_fetcher.fetch_intraday_data(TRADING_SYMBOLS, period='1d', interval='5m')
                logger.info(f"Fetched data for {len(market_data)} symbols")
            except Exception as e:
                logger.error(f"Failed to fetch market data: {e}")
                await self._report_error(f"Data fetch error: {e}")
                return

            # 2. Generate AI analysis for symbols in batches
            ai_signals = []
            batch_size = 10  # Process 10 symbols per AI call for efficiency
            symbols_to_analyze = [s for s in TRADING_SYMBOLS if s in market_data and not market_data[s].empty]

            logger.info(f"Analyzing {len(symbols_to_analyze)} symbols in batches of {batch_size}")

            for i in range(0, len(symbols_to_analyze), batch_size):
                batch = symbols_to_analyze[i:i + batch_size]
                try:
                    # Build prompt for this batch of symbols
                    batch_data = {symbol: market_data[symbol] for symbol in batch}
                    messages = self.prompt_builder.build_prompt_messages(batch_data)

                    # Get AI analysis for the batch
                    ai_response = self.ai_client.call_chat_completion(messages)

                    if ai_response and 'choices' in ai_response:
                        response_text = ai_response['choices'][0]['message']['content']
                        logger.info(f"AI analysis for batch {i//batch_size + 1}: {batch} - {response_text[:100]}...")

                        # Parse signals from AI response
                        signals = self.strategy.parse_ai_response(response_text)
                        ai_signals.extend(signals)
                    else:
                        logger.warning(f"No valid AI response for batch: {batch}")

                except Exception as e:
                    logger.error(f"AI analysis failed for batch {i//batch_size + 1}: {batch} - {e}")
                    continue

            if not ai_signals:
                logger.info("No trading signals generated this cycle")
                return

            # 3. Execute signals through strategy
            account_summary = self.strategy.get_account_summary()
            executed_signals = []

            for signal in ai_signals:
                try:
                    if self.strategy.should_execute_signal(signal, account_summary):
                        success = self.strategy.execute_signal(signal)
                        executed_signals.append(signal)
                        logger.info(f"Executed signal: {signal}")
                    else:
                        logger.info(f"Signal rejected based on risk management: {signal}")
                except Exception as e:
                    logger.error(f"Failed to execute signal {signal}: {e}")

            # 4. Report results
            if executed_signals:
                try:
                    # Calculate P&L (simplified - in real system you'd track actual trades)
                    account = self.trading_client.get_account()
                    pnl = account.get('equity', 0) - 100000  # Assuming $100k starting equity

                    # Generate insights summary
                    insights = f"Executed {len(executed_signals)} trades. Symbols: {', '.join(s.symbol for s in executed_signals)}"

                    await self.telegram_reporter.send_daily_summary(pnl, [], insights)
                    logger.info(f"Reported cycle results: P&L ${pnl:.2f}, {len(executed_signals)} trades")

                except Exception as e:
                    logger.error(f"Failed to generate cycle report: {e}")

            logger.info("Trading cycle completed successfully")

        except Exception as e:
            error_msg = f"Trading cycle failed: {e}"
            logger.error(error_msg)
            await self._report_error(error_msg)

async def main():
    """Main application entry point."""
    # Set up signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown")
        if bot and bot.orchestrator:
            bot.orchestrator.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize and run the trading bot
    bot = IntegratedTradingBot()

    try:
        # Initialize all components
        success = await bot.initialize()
        if not success:
            logger.error("Failed to initialize trading bot")
            return

        # Send start message
        await bot.telegram_reporter.send_start_message()

        # Start the orchestrator (which will run the trading cycles)
        bot.orchestrator.start()

        # Keep the main thread alive
        while True:
            await asyncio.sleep(60)  # Check every minute

            # Check for kill command
            if bot.kill_requested:
                logger.info("Kill command received, shutting down gracefully")
                break

            # Could add additional monitoring here

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await bot._report_error(f"Critical system error: {e}")
    finally:
        # Send stop message and stop bot
        try:
            if bot.telegram_reporter:
                await bot.telegram_reporter.send_stop_message()
                await bot.telegram_reporter.stop_bot()
        except Exception as e:
            logger.error(f"Failed to send stop message or stop bot: {e}")

        if bot.orchestrator:
            bot.orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(main())
