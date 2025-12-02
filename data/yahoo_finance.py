import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class YahooFinanceDataFetcher:
    def __init__(self):
        pass

    def fetch_intraday_data(self, symbols, period='1d', interval='5m'):
        """
        Fetch intraday data for given symbols.

        Args:
            symbols (list): List of stock symbols (e.g., ['AAPL', 'GOOGL'])
            period (str): Period to fetch (e.g., '1d' for 1 day)
            interval (str): Data interval (e.g., '5m' for 5 minutes)

        Returns:
            dict: Dictionary with symbols as keys and DataFrames as values
        """
        try:
            data = yf.download(
                tickers=symbols,
                period=period,
                interval=interval,
                group_by='ticker'
            )

            # If single symbol, convert to dict format
            if isinstance(data, dict):
                return data
            else:
                # Multiple symbols, already grouped
                return data

        except Exception as e:
            logger.error(f"Error fetching data for symbols {symbols}: {str(e)}")
            return {}

    def fetch_last_day_5min_bars(self, symbols):
        """
        Fetch last day's worth of 5-minute bars for given symbols.

        Args:
            symbols (list): List of stock symbols

        Returns:
            dict: Dictionary with symbols as keys and DataFrames as values
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)

        try:
            data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                df = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval='5m',
                    auto_adjust=True
                )
                if not df.empty:
                    data[symbol] = df

            return data

        except Exception as e:
            logger.error(f"Error fetching last day 5min data for symbols {symbols}: {str(e)}")
            return {}

# Convenience function
def get_yahoo_finance_data(symbols, period='1d', interval='5m'):
    """
    Convenience function to get Yahoo Finance data.

    Args:
        symbols (list or str): Stock symbol(s)
        period (str): Period to fetch
        interval (str): Data interval

    Returns:
        dict: Fetched data
    """
    fetcher = YahooFinanceDataFetcher()

    if isinstance(symbols, str):
        symbols = [symbols]

    if period == '1d' and interval == '5m':
        return fetcher.fetch_last_day_5min_bars(symbols)
    else:
        return fetcher.fetch_intraday_data(symbols, period, interval)
