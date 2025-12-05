# Pi Trader V2 - AI-Powered Automated Trading Bot

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/your-repo/pi-trader-v2)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive automated trading bot that combines AI-powered market analysis, real-time data fetching, risk management, and automated execution through the Alpaca trading platform. Designed for traders who want to leverage artificial intelligence for market analysis while maintaining control over risk parameters.

## 🚀 Features

- **AI-Powered Trading Signals**: Uses OpenRouter API for advanced market analysis and trading decision generation
- **Real-Time Data Integration**: Fetches live market data from Yahoo Finance with 5-minute intervals
- **Automated Order Execution**: Seamless integration with Alpaca for placing market, limit, and stop orders
- **Risk Management**: Built-in position sizing, stop-loss calculations, and configurable risk parameters
- **Telegram Notifications**: Real-time alerts and daily summary reports via Telegram bot
- **Paper Trading Support**: Test strategies in Alpaca's paper trading environment
- **Modular Architecture**: Easily extensible strategy system and component-based design
- **Health Monitoring**: Comprehensive system health checks for all integrated services
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## 📋 Prerequisites

Before running Pi Trader V2, ensure you have:

- **Python 3.8+** installed on your system
- **Trading Account**: Alpaca account (with API keys) - supports both live and paper trading
- **AI API Access**: OpenRouter API key for AI-powered analysis
- **Telegram Bot**: Telegram bot token for notifications (optional but recommended)

## 🛠 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/pi-trader-v2.git
   cd pi-trader-v2
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:

   Copy the example environment file and fill in your credentials:
   ```
   cp .env.example .env
   ```

   Edit `.env` with your API credentials:
   ```env
   # Alpaca API Credentials (paper trading)
   ALPACA_API_KEY=your_alpaca_api_key_here
   ALPACA_SECRET_KEY=your_alpaca_secret_key_here
   ALPACA_PAPER_URL=https://paper-api.alpaca.markets

   # OpenRouter API (for AI analysis)
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free

   # Telegram Bot (for notifications)
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
   ```

   **Note**: Never commit your `.env` file to version control. It contains sensitive API keys.

## ⚙️ Configuration

### API Keys Setup

#### Alpaca Trading
1. Sign up for an Alpaca account at [alpaca.markets](https://alpaca.markets)
2. Generate API keys in your Alpaca dashboard
3. Use paper trading keys for testing (`ALPACA_PAPER_URL=https://paper-api.alpaca.markets`)

#### OpenRouter AI
1. Visit [OpenRouter.ai](https://openrouter.ai) and sign up
2. Generate an API key
3. Free tier includes 1 request per 15 minutes (sufficient for typical trading cycles)

#### Telegram Notifications
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot` and follow the instructions
3. Get your bot token from BotFather
4. Send a message to your bot (or create a group/channel)
5. Use `@userinfobot` or check bot logs to get your chat ID

### Trading Symbols

Modify `config/settings.py` to customize trading symbols:
```python
TRADING_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'SPY', 'QQQ', 'DIA']
```

### Risk Management

Adjust risk parameters in `strategy/base_strategy.py`:
- `risk_per_trade`: Maximum percentage of equity per trade (default: 2%)
- `max_confidence_threshold`: Minimum AI confidence level to execute trades (default: 80%)

## 🚀 Usage

### Running the Bot

**Start the automated trading bot**:
```bash
python main.py
```

The bot will:
1. Initialize all components (Alpaca, Yahoo Finance, OpenRouter, Telegram)
2. Perform comprehensive health checks
3. Begin trading cycles every 5 minutes during market hours
4. Send notifications via Telegram for important events

### Testing Components

**Test Alpaca connection**:
```bash
python test_alpaca.py
```

**Test Yahoo Finance data fetching**:
```bash
python test_data.py
```

**Test prompt building**:
```bash
python test_prompt_builder.py
```

### Manual Testing

You can also test individual components:
```python
from config.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY
from trading.alpaca_client import AlpacaTradingClient

# Test Alpaca connection
client = AlpacaTradingClient()
account = client.get_account()
print(f"Account equity: ${account.get('equity', 0)}")
```

## 🏗 How It Works

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Yahoo Finance │───▶│   AI Analysis   │───▶│   Strategy      │
│   Data Fetcher  │    │   (OpenRouter)  │    │   Engine        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Risk Manager  │───▶│  Order          │───▶│   Alpaca API    │
│                 │    │  Execution     │    │   (Trading)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐    ┌─────────────────┐
│  Telegram       │    │   Health        │
│  Notifications  │    │   Monitoring    │
└─────────────────┘    └─────────────────┘
```

### Trading Cycle

1. **Data Collection**: Fetch 5-minute interval data for configured symbols
2. **AI Analysis**: Send market data to OpenRouter API for analysis
3. **Signal Generation**: Parse AI responses into structured trading signals
4. **Risk Assessment**: Evaluate signals against account equity and risk limits
5. **Order Execution**: Place orders through Alpaca API with appropriate position sizing
6. **Reporting**: Send trade confirmations and daily summaries via Telegram

### AI Prompt Format

The AI receives prompts containing recent market data and generates responses in this format:

```
SYMBOL: AAPL: [BUY] at $185.42 - Confidence: 85% - Reason: Strong upward momentum with high volume

SYMBOL: TSLA: [SELL] at $248.50 - Confidence: 92% - Reason: Profit taking after earnings gap

SYMBOL: MSFT: [HOLD] - Confidence: 60% - Reason: Consolidation phase, wait for clearer direction
```

## ⚠️ Risk Warnings

**This software is for educational and research purposes only. Trading cryptocurrencies and stocks carries significant risk of loss.**

- **Start with Paper Trading**: Always test strategies in Alpaca's paper trading environment
- **Set Appropriate Risk Limits**: Default 2% risk per trade is conservative - adjust based on your risk tolerance
- **Monitor System Health**: Use Telegram notifications to stay informed of system status
- **Regular Backtesting**: Test strategies against historical data before live deployment
- **Never Invest More Than You Can Afford to Lose**

## 🔧 Troubleshooting

### Common Issues

**Alpaca API Connection Failed**:
- Verify API keys are correct in `.env`
- Ensure you're using paper trading URLs for testing
- Check Alpaca account status and permissions

**Rate Limiting Errors**:
- OpenRouter free tier: 1 request per 15 minutes
- Upgrade to paid tier or implement caching for testing
- Consider using alternative AI providers

**Telegram Notifications Not Working**:
- Verify bot token and chat ID
- Ensure bot is added to the chat/group
- Check bot permissions (especially in groups)

**No Trading Signals Generated**:
- Check AI API key and credits
- Verify market data fetching (test with `test_data.py`)
- Ensure trading symbols are valid and actively traded

### Health Checks

The bot performs automatic health checks for all services. Monitor the logs for:

- Alpaca API connectivity and account status
- Yahoo Finance data availability
- OpenRouter API rate limiting status
- Telegram bot functionality

### Logs

View application logs:
```bash
tail -f trading_bot.log
```

Log levels: DEBUG, INFO, WARNING, ERROR

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for API changes
- Ensure all health checks pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Bug Reports**: Open an issue on GitHub with detailed reproduction steps
- **Feature Requests**: Use GitHub issues to suggest enhancements
- **General Questions**: Check existing issues and discussions first

## 📊 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

**Disclaimer**: This software is provided as-is without warranty. Use at your own risk. Always perform thorough testing before deploying trading strategies with real money.
