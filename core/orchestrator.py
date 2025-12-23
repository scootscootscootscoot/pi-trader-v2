import logging
import signal
import sys
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

from config import settings

logger = logging.getLogger(__name__)

def is_market_open():
    """
    Check if the US stock market is currently open.
    Market hours: 9:30 AM - 4:00 PM ET, Monday to Friday.

    Returns:
        bool: True if market is open, False otherwise.
    """
    try:
        et = pytz.timezone('US/Eastern')
        now = datetime.now(et)

        # Check if it's a weekday (Monday=0 to Friday=4)
        if now.weekday() > 4:  # 5=Saturday, 6=Sunday
            return False

        # Market hours
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= now < market_close
    except Exception as e:
        logger.error(f"Error checking market hours: {e}")
        return False

class TradingOrchestrator:
    """
    Main orchestrator for the trading bot.
    Handles scheduling of trading activities during market hours.
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone('US/Eastern'))
        self.running = False
        logger.info("Trading orchestrator initialized")

    def start(self):
        """
        Start the orchestrator and scheduler.
        """
        if self.running:
            logger.warning("Orchestrator is already running")
            return

        try:
            # Add scheduled jobs for market hours (9:30 AM - 4:00 PM ET, weekdays, every 2 hours)
            # Trading cycles at 10:00, 12:00, 14:00 (every 2 hours during market hours)
            self.scheduler.add_job(
                func=self._execute_trading_cycle,
                trigger="cron",
                day_of_week='mon-fri',
                hour='10,12,14',
                minute=0,
                id="trading_cycle_scheduled",
                name="Trading Cycle Execution - Scheduled"
            )

            # TEMPORARY: Add immediate job for testing
            from datetime import datetime
            self.scheduler.add_job(
                func=self._execute_trading_cycle,
                trigger="date",
                run_date=datetime.now(),
                id="trading_cycle_test",
                name="Trading Cycle Test - Immediate"
            )

            self.scheduler.start()
            self.running = True
            logger.info("Trading orchestrator started successfully: scheduling during market hours only (every 2 hours)")

        except Exception as e:
            logger.error(f"Failed to start orchestrator: {e}")
            raise

    def stop(self):
        """
        Stop the orchestrator and scheduler.
        """
        if not self.running:
            return

        try:
            self.scheduler.shutdown(wait=True)
            self.running = False
            logger.info("Trading orchestrator stopped")
        except Exception as e:
            logger.error(f"Error stopping orchestrator: {e}")

    def _execute_trading_cycle(self):
        """
        Execute one cycle of trading activities.
        This is called only during market hours via cron scheduling.
        """
        try:
            # Placeholder for trading logic
            # TODO: Integrate with strategy evaluators, trading client, etc.
            logger.info("Executing trading cycle")

        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")

def signal_handler(signum, frame):
    """
    Handle shutdown signals gracefully.
    """
    logger.info(f"Received signal {signum}, initiating shutdown")
    if 'orchestrator' in globals():
        orchestrator.stop()
    sys.exit(0)

def main():
    """
    Main entry point for the trading orchestrator.
    """
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    global orchestrator
    orchestrator = TradingOrchestrator()

    try:
        orchestrator.start()

        # Keep the main thread alive
        while True:
            signal.pause()

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if 'orchestrator' in globals():
            orchestrator.stop()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    main()
