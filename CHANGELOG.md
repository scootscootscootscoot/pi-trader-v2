# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v/1.0.0/).

## [Unreleased]

## [2.1.0] - 2025-12-04

### Added

- **Strategy Evolution System**: Automatic strategy improvement based on performance metrics with version control for prompt and parameter adjustments
- **Multiple Trading Strategy Templates**: Pre-built templates for aggressive day trading, conservative swing trading, and momentum scalping strategies
- **Trading Orchestrator**: Scheduled execution during market hours (9:30 AM - 4:00 PM ET) with automated trading cycles
- **Advanced Prompt Builder**: Sophisticated prompt engineering system for optimal AI trading analysis and decision making
- **Integrated Trading Bot**: Unified system with health monitoring, comprehensive logging, and modular architecture
- **Health Monitoring System**: Real-time monitoring of all integrated services (Alpaca API, Yahoo Finance, OpenRouter, Telegram)
- **Rate Limiting & Safety Controls**: Built-in protections against excessive API calls and risk management thresholds
- **Dependencies Added**: `apscheduler` for trading cycle scheduling

## [2.0.0] - 2025-12-01

### Added

- **Initial release of Pi Trader V2 trading bot** with comprehensive trading functionality
- **Alpaca Trading Integration**: Full client for placing market, limit, and stop orders; managing account balance, positions, and order history
- **Yahoo Finance Data**: Module for fetching intraday and historical market data with 5-minute intervals
- **Configuration Management**: Settings module with environment variable support for API keys and trading symbols
- **Telegram Bot Support**: Integration for notifications and potential bot control
- **OpenRouter AI Support**: Added for advanced trading strategies or analysis
- **Paper Trading Support**: Default to paper trading for safety and testing
- **Test Scripts**: Unit tests for Alpaca client and data fetching functionality
- **Dependencies Added**:
  - `alpaca-trade-api>=3.0.0` for Alpaca API access
  - `yfinance` for Yahoo Finance data
  - `python-telegram-bot` for Telegram integration
  - `python-dotenv` for environment variable management
  - `requests` for HTTP operations
- **Default Trading Symbols**: Pre-configured list including AAPL, GOOGL, MSFT, TSLA, NVDA, and major indices (SPY, QQQ, DIA)

### Changed

- N/A (Initial release)

### Deprecated

- N/A (Initial release)

### Removed

- N/A (Initial release)

### Fixed

- N/A (Initial release)

### Security

- N/A (Initial release)
