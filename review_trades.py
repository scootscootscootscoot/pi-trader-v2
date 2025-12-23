#!/usr/bin/env python3
"""
Script to review daily trading activity and performance.

Usage:
    python review_trades.py                    # Review today's trades
    python review_trades.py 2025-12-21        # Review specific date
    python review_trades.py --last 7          # Review last 7 days
"""

import sys
import os
from datetime import datetime, date, timedelta
from pathlib import Path
import json
import argparse

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reporting.trade_logger import get_trade_logger

def format_trade_summary(trade):
    """Format a single trade for display."""
    timestamp = datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00'))
    time_str = timestamp.strftime('%H:%M:%S')

    if trade['action'] == 'buy':
        action_emoji = '🟢'
    elif trade['action'] == 'sell':
        action_emoji = '🔴'
    else:
        action_emoji = '⚪'

    price_info = f"${trade.get('execution_price', trade.get('intended_price', 0)):.2f}"
    if trade.get('execution_price') and trade.get('intended_price'):
        if abs(trade['execution_price'] - trade['intended_price']) > 0.01:
            price_info += f" (target: ${trade['intended_price']:.2f})"

    return f"{time_str} {action_emoji} {trade['action'].upper()} {trade['quantity']} {trade['symbol']} @ {price_info} (ID: {trade['order_id']})"

def review_daily_trades(target_date=None):
    """Review trades for a specific date."""
    trade_logger = get_trade_logger()

    if target_date is None:
        target_date = date.today()

    print(f"📊 Trading Activity Review - {target_date}")
    print("=" * 60)

    # Get trades for the date
    trades = trade_logger.get_daily_trades(target_date)

    if not trades:
        print("❌ No trades found for this date.")
        return

    # Group trades by symbol
    trades_by_symbol = {}
    for trade in trades:
        symbol = trade['symbol']
        if symbol not in trades_by_symbol:
            trades_by_symbol[symbol] = []
        trades_by_symbol[symbol].append(trade)

    # Display trades
    total_trades = len(trades)
    buy_trades = len([t for t in trades if t['action'] == 'buy'])
    sell_trades = len([t for t in trades if t['action'] == 'sell'])

    print(f"📈 Total Trades: {total_trades} (Buy: {buy_trades}, Sell: {sell_trades})")
    print(f"🏷️  Symbols Traded: {', '.join(trades_by_symbol.keys())}")
    print()

    for symbol, symbol_trades in trades_by_symbol.items():
        print(f"📊 {symbol} Trades:")
        for trade in sorted(symbol_trades, key=lambda x: x['timestamp']):
            print(f"  {format_trade_summary(trade)}")
            if trade.get('reason'):
                print(f"    💬 {trade['reason']}")
            if trade.get('stop_loss'):
                print(f"    🛡️  Stop Loss: ${trade['stop_loss']:.2f}")
            if trade.get('confidence'):
                confidence_emoji = '🟢' if trade['confidence'] >= 80 else '🟡' if trade['confidence'] >= 60 else '🔴'
                print(f"    🎯 Confidence: {trade['confidence']}% {confidence_emoji}")
        print()

def review_multiple_days(days):
    """Review trading activity for the last N days."""
    trade_logger = get_trade_logger()
    today = date.today()

    print(f"📊 Trading Activity Review - Last {days} Days")
    print("=" * 60)

    total_trades_all = 0
    total_pnl = 0

    for i in range(days):
        target_date = today - timedelta(days=i)
        trades = trade_logger.get_daily_trades(target_date)

        if trades:
            buy_trades = len([t for t in trades if t['action'] == 'buy'])
            sell_trades = len([t for t in trades if t['action'] == 'sell'])
            symbols = list(set(t['symbol'] for t in trades))

            print(f"📅 {target_date}: {len(trades)} trades (Buy: {buy_trades}, Sell: {sell_trades}) - Symbols: {', '.join(symbols)}")
            total_trades_all += len(trades)
        else:
            print(f"📅 {target_date}: No trades")

    print()
    print(f"📈 Summary: {total_trades_all} total trades across {days} days")

def main():
    parser = argparse.ArgumentParser(description='Review trading activity')
    parser.add_argument('date', nargs='?', help='Specific date to review (YYYY-MM-DD)')
    parser.add_argument('--last', type=int, help='Review last N days')

    args = parser.parse_args()

    try:
        if args.last:
            review_multiple_days(args.last)
        elif args.date:
            target_date = date.fromisoformat(args.date)
            review_daily_trades(target_date)
        else:
            review_daily_trades()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
