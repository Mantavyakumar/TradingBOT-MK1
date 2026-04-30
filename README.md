GoldBetAdvisor

GoldBetAdvisor is a command-line tool that analyzes real-time gold market data using your trading strategies and compares it against Polymarket prediction markets.

It helps you decide whether a market is worth betting on — and if so, which side aligns with your strategy.

⚠️ This tool provides analysis only. It does NOT execute trades or place bets.

🚀 Quick Start

Run the script with a Polymarket URL:

python filename.py "POLYMARKET_EVENT_OR_MARKET_URL"
✅ Example
python GoldBetAdvisor.py "https://polymarket.com/event/gc-hit-jun-2026?marketSlug=..."

or:

python GoldBetAdvisor.py "https://polymarket.com/event/gc-hit-jun-2026"
⚙️ Command-Line Options
Option	Description	Default
url	Polymarket event or market URL	Required
--strategy	Strategy to use: trend or blackbox	trend
--window	Lookback window (blackbox only)	20
--symbol	Gold symbol (Yahoo Finance)	XAUUSD=X
--interval	Candle timeframe (1m, 5m, 1h, etc.)	5m
--range	Historical data range	30d
--fresh-bars	How recent a signal must be	3
--watch	Auto-refresh interval (seconds)	0 (off)
🧠 Strategies Explained
🔹 Trend Confirmation (Default)

A structured trend-following system using:

📈 EMA 20 / 50 / 200
⚡ RSI (14) momentum filter
🔼 Breakout confirmation

Bullish signal requires:

Price above EMA 200 (long-term strength)
EMA 20 > EMA 50 (short-term trend)
RSI between 50–72 (healthy momentum)
Break above previous candle high
Recent pullback to EMA 20
🔹 Blackbox Strategy

Your custom price-action logic:

🚀 Breakout detection
🎯 Trap identification
🔁 Re-cross confirmation

Designed to catch:

Fake breakouts
Smart-money traps
Re-entry opportunities
📊 What the Script Outputs

For every run, you’ll see:

🟡 Market Data
Latest gold price
Candle timestamp
Resistance levels
📉 Indicators
EMA 20 / 50 / 200
RSI (14)
🧭 Strategy Status
Current state (SEARCHING / WAITING / BULLISH, etc.)
Signal price (if any)
Whether the signal is fresh
🎯 Market Analysis

Each Polymarket market is classified as:

HIGH (price expected to go above target)
LOW (price expected to stay below target)
💡 Betting Advice Logic
Situation	Output
Bullish signal + HIGH market	✅ CONSIDER YES
Bullish signal + LOW market	❌ CONSIDER NO
No fresh signal	⛔ NO BET
🔄 Live Monitoring Mode

Continuously refresh data:

python GoldBetAdvisor.py "URL" --watch 60

⏱ Updates every 60 seconds.

⚠️ Important Disclaimer
This tool is for research and analysis only
It does not guarantee profit
Financial markets are unpredictable
Always test strategies before using real money
🛠️ Future Improvements (Ideas)
Multi-timeframe confirmation
Bearish strategy support
GUI dashboard
Backtesting module
Alert system (Telegram/Discord)
