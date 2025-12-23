# Enhanced Trading Logging System

This document describes the enhanced logging functionality added to track and review trading activities.

## Overview

The trading bot now includes comprehensive logging that captures:
- Signal generation from AI analysis
- Trade execution with full details
- Signal rejections and reasons
- Order status updates
- Daily performance summaries

## Log Files

Logs are stored in the `logs/` directory with daily files named `trading_activity_YYYY-MM-DD.json`.

Each log file contains structured JSON entries for different types of events.

## Event Types

### SIGNAL_GENERATED
Logged when AI generates a trading signal.
```json
{
  "timestamp": "2025-12-22T18:29:21.224372+00:00",
  "type": "signal_generated",
  "symbol": "AAPL",
  "signal": {
    "symbol": "AAPL",
    "action": "buy",
    "price": 150.0,
    "quantity": 10,
    "confidence": 85,
    "reason": "Strong upward momentum detected",
    "stop_loss": 145.0
  },
  "ai_response": "AI response text (truncated)",
  "confidence": 85
}
```

### SIGNAL_EXECUTED
Logged when a trading signal is successfully executed.
```json
{
  "timestamp": "2025-12-22T18:29:21.225113+00:00",
  "type": "signal_executed",
  "symbol": "AAPL",
  "action": "buy",
  "intended_price": 150.0,
  "execution_price": 150.25,
  "quantity": 10,
  "order_id": "order_12345",
  "confidence": 85,
  "reason": "Strong upward momentum detected",
  "stop_loss": 145.0
}
```

### SIGNAL_REJECTED
Logged when a signal is rejected (e.g., due to risk management).
```json
{
  "timestamp": "2025-12-22T18:29:21.225502+00:00",
  "type": "signal_rejected",
  "symbol": "TSLA",
  "action": "buy",
  "price": 200.0,
  "confidence": 65,
  "reason": "Confidence below threshold"
}
```

### ORDER_UPDATE
Logged when order status changes.
```json
{
  "timestamp": "2025-12-22T18:29:21.225905+00:00",
  "type": "order_update",
  "order_id": "order_12345",
  "symbol": "AAPL",
  "status": "filled",
  "filled_quantity": 10,
  "filled_price": 150.25
}
```

### DAILY_SUMMARY
Logged at the end of each trading day with performance metrics.
```json
{
  "date": "2025-12-22",
  "total_trades": 1,
  "buy_trades": 1,
  "sell_trades": 0,
  "symbols_traded": ["AAPL"],
  "starting_equity": 100000.0,
  "ending_equity": 102500.0,
  "daily_pnl": 2500.0,
  "daily_pnl_percent": 2.5,
  "trades": [...]
}
```

## Review Script

Use the `review_trades.py` script to easily review trading activity:

```bash
# Review today's trades
python review_trades.py

# Review a specific date
python review_trades.py 2025-12-21

# Review last 7 days
python review_trades.py --last 7
```

## Features

- **Daily Log Rotation**: Automatic creation of new log files each day
- **Structured Data**: All logs are in JSON format for easy parsing
- **Comprehensive Tracking**: Captures the complete trade lifecycle
- **Performance Metrics**: Daily P&L and trade statistics
- **Easy Review**: User-friendly scripts for reviewing activity
- **Git Ignored**: Log files are excluded from version control

## Integration

The logging system is automatically integrated into:
- Signal generation in `main.py`
- Trade execution in `strategy/base_strategy.py`
- Daily summaries on bot shutdown

No additional configuration is needed - logging happens automatically during normal bot operation.
