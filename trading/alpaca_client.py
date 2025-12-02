from alpaca_trade_api import REST
import logging
import os

logger = logging.getLogger(__name__)

class AlpacaTradingClient:
    """
    Alpaca trading client for placing orders and managing account.
    Uses paper trading by default for safety.
    """

    def __init__(self, api_key=None, secret_key=None, base_url=None):
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        self.base_url = base_url or os.getenv('ALPACA_PAPER_URL', 'https://paper-api.alpaca.markets')

        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API key and secret key are required")

        try:
            self.api = REST(
                key_id=self.api_key,
                secret_key=self.secret_key,
                base_url=self.base_url,
                api_version='v2'
            )
            logger.info("Alpaca client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca client: {str(e)}")
            raise

    def get_account(self):
        """
        Get account information.

        Returns:
            dict: Account details including balance, buying power, etc.
        """
        try:
            account = self.api.get_account()
            return {
                'account_id': account.id,
                'account_type': account.status,
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'equity': float(account.equity),
                'status': account.status,
                'created_at': account.created_at.isoformat() if account.created_at else None
            }
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            raise

    def get_positions(self):
        """
        Get current positions.

        Returns:
            list: List of position dictionaries
        """
        try:
            positions = self.api.list_positions()
            return [{
                'symbol': pos.symbol,
                'qty': pos.qty,
                'avg_entry_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price),
                'market_value': float(pos.market_value),
                'unrealized_pl': float(pos.unrealized_pl),
                'unrealized_plpc': float(pos.unrealized_plpc)
            } for pos in positions]
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            raise

    def place_market_order(self, symbol, qty, side='buy', time_in_force='day'):
        """
        Place a market order.

        Args:
            symbol (str): Stock symbol
            qty (int): Quantity to trade
            side (str): Order side ('buy' or 'sell')
            time_in_force (str): Time in force ('day', 'gtc', etc.)

        Returns:
            str: Order ID
        """
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force=time_in_force
            )
            logger.info(f"Placed {side} market order for {qty} {symbol}")
            return order.id
        except Exception as e:
            logger.error(f"Error placing market order: {str(e)}")
            raise

    def place_limit_order(self, symbol, qty, limit_price, side='buy', time_in_force='day'):
        """
        Place a limit order.

        Args:
            symbol (str): Stock symbol
            qty (int): Quantity to trade
            limit_price (float): Limit price
            side (str): Order side ('buy' or 'sell')
            time_in_force (str): Time in force ('day', 'gtc', etc.)

        Returns:
            str: Order ID
        """
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='limit',
                limit_price=limit_price,
                time_in_force=time_in_force
            )
            logger.info(f"Placed {side} limit order for {qty} {symbol} at {limit_price}")
            return order.id
        except Exception as e:
            logger.error(f"Error placing limit order: {str(e)}")
            raise

    def place_stop_order(self, symbol, qty, stop_price, side='sell', time_in_force='day'):
        """
        Place a stop order (typically for selling to limit losses).

        Args:
            symbol (str): Stock symbol
            qty (int): Quantity to trade
            stop_price (float): Stop price
            side (str): Order side ('sell' for stop loss)
            time_in_force (str): Time in force ('day', 'gtc', etc.)

        Returns:
            str: Order ID
        """
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='stop',
                stop_price=stop_price,
                time_in_force=time_in_force
            )
            logger.info(f"Placed {side} stop order for {qty} {symbol} at {stop_price}")
            return order.id
        except Exception as e:
            logger.error(f"Error placing stop order: {str(e)}")
            raise

    def cancel_order(self, order_id):
        """
        Cancel a specific order.

        Args:
            order_id (str): Order ID to cancel

        Returns:
            bool: True if successful
        """
        try:
            self.api.cancel_order(order_id)
            logger.info(f"Cancelled order {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {str(e)}")
            raise

    def cancel_all_orders(self):
        """
        Cancel all open orders.

        Returns:
            int: Number of orders cancelled
        """
        try:
            result = self.api.cancel_all_orders()
            logger.info("Cancelled all open orders")
            return len(result) if hasattr(result, '__len__') else 0
        except Exception as e:
            logger.error(f"Error cancelling all orders: {str(e)}")
            raise

    def get_orders(self, status='open', symbols=None, limit=50):
        """
        Get order history.

        Args:
            status (str): Order status ('open', 'closed', 'all')
            symbols (list): Filter by symbols
            limit (int): Maximum orders to retrieve

        Returns:
            list: List of order dictionaries
        """
        try:
            orders = self.api.list_orders(
                status=status,
                symbols=symbols,
                limit=limit
            )
            return [{
                'id': order.id,
                'symbol': order.symbol,
                'qty': order.qty,
                'filled_qty': order.filled_qty,
                'side': order.side,
                'type': order.type,
                'status': order.status,
                'submission_time': order.submitted_at.isoformat() if order.submitted_at else None,
                'filled_at': order.filled_at.isoformat() if order.filled_at else None
            } for order in orders]
        except Exception as e:
            logger.error(f"Error getting orders: {str(e)}")
            raise

    def get_latest_quote(self, symbol):
        """
        Get the latest quote for a symbol.

        Args:
            symbol (str): Stock symbol

        Returns:
            dict: Quote information
        """
        try:
            quote = self.api.get_latest_quote(symbol)
            return {
                'symbol': symbol,
                'ask_price': float(quote.askprice),
                'ask_size': quote.asksize,
                'bid_price': float(quote.bidprice),
                'bid_size': quote.bidsize,
                'timestamp': quote.timestamp.isoformat() if quote.timestamp else None
            }
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {str(e)}")
            raise

    def get_bars(self, symbol, timeframe='5Min', start=None, end=None, limit=100):
        """
        Get historical bars for a symbol.

        Args:
            symbol (str): Stock symbol
            timeframe (str): Timeframe ('1Min', '5Min', etc.)
            start (str or datetime): Start date/datetime
            end (str or datetime): End date/datetime
            limit (int): Maximum bars to retrieve

        Returns:
            list: List of bar dictionaries
        """
        try:
            # Map string timeframes to TimeFrame objects
            tf_map = {
                '1Min': '1Min',
                '5Min': '5Min',
                '15Min': '15Min',
                '1H': '1Hour',
                '1D': '1Day'
            }

            tf = tf_map.get(timeframe, '5Min')

            bars = self.api.get_barset(
                symbol,
                tf,
                start=start,
                end=end,
                limit=limit
            )

            return [{
                'symbol': symbol,
                'timestamp': bar.t.isoformat() if bar.t else None,
                'open': float(bar.o),
                'high': float(bar.h),
                'low': float(bar.l),
                'close': float(bar.c),
                'volume': bar.v,
                'trade_count': bar.vw or 0,
                'vwap': bar.vw or 0.0
            } for bar in bars[symbol]]
        except Exception as e:
            logger.error(f"Error getting bars for {symbol}: {str(e)}")
            raise

# Convenience functions
def get_account_balance():
    """Get account balance using default settings."""
    client = AlpacaTradingClient()
    return client.get_account()

def get_current_positions():
    """Get current positions using default settings."""
    client = AlpacaTradingClient()
    return client.get_positions()

def place_buy_order(symbol, qty, order_type='market', **kwargs):
    """
    Place a buy order.

    Args:
        symbol (str): Stock symbol
        qty (int): Quantity
        order_type (str): 'market', 'limit', or 'stop'

    Returns:
        str: Order ID
    """
    client = AlpacaTradingClient()
    if order_type == 'market':
        return client.place_market_order(symbol, qty, side='buy', **kwargs)
    elif order_type == 'limit':
        return client.place_limit_order(symbol, qty, side='buy', **kwargs)
    else:
        raise ValueError(f"Unsupported order type: {order_type}")

def place_sell_order(symbol, qty, order_type='market', **kwargs):
    """
    Place a sell order.

    Args:
        symbol (str): Stock symbol
        qty (int): Quantity
        order_type (str): 'market', 'limit', or 'stop'

    Returns:
        str: Order ID
    """
    client = AlpacaTradingClient()
    if order_type == 'market':
        return client.place_market_order(symbol, qty, side='sell', **kwargs)
    elif order_type == 'limit':
        return client.place_limit_order(symbol, qty, side='sell', **kwargs)
    elif order_type == 'stop':
        return client.place_stop_order(symbol, qty, side='sell', **kwargs)
    else:
        raise ValueError(f"Unsupported order type: {order_type}")
