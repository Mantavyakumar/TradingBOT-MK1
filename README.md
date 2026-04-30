🥇 GoldBetAdvisor

A command-line tool that analyzes real-time gold market data using your trading strategies and compares it with Polymarket prediction markets.

It helps you decide:

Whether a bet is worth taking
Which side (YES / NO) aligns with your strategy

⚠️ Analysis only — this tool does NOT place trades.

🚀 Quick Start

Run the script with a Polymarket URL:

python GoldBetAdvisor.py "POLYMARKET_URL"                                            

✅ Example
python GoldBetAdvisor.py "https://polymarket.com/event/gc-hit-jun-2026?marketSlug=..."

or




python GoldBetAdvisor.py "https://polymarket.com/event/gc-hit-jun-2026"





⚙️ Command-Line Options
--strategy     Choose strategy: trend | blackbox
--window       Lookback window (blackbox only)
--symbol       Gold symbol (default: XAUUSD=X)
--interval     Candle timeframe (default: 5m)
--range        Data range (default: 30d)
--fresh-bars   Signal freshness threshold
--watch        Auto-refresh interval (seconds)
🧠 Strategies
🔹 Trend Confirmation (Default)

Uses:

EMA 20 / 50 / 200
RSI (14)
Breakout confirmation

✔ Best for structured trend-following setups

🔹 Blackbox Strategy

Uses:

Breakout
Trap
Re-cross logic

✔ Best for catching fakeouts and smart-money moves

📊 Output

The script prints:

📈 Gold price + indicators
🧭 Strategy state
🔔 Signal freshness
🎯 Market classification (HIGH / LOW)
💡 Betting advice:
✅ CONSIDER YES
❌ CONSIDER NO
⛔ NO BET
🔄 Live Mode

Run continuously:

python GoldBetAdvisor.py "URL" --watch 60
⚠️ Disclaimer
Not financial advice
No guarantee of profit
Use at your own risk

📊 PolyMarket Fetch Bets

A lightweight command-line tool that fetches and displays live Polymarket market data directly from a URL.

It shows:

Market details
All outcomes / bet options
Token IDs
Live midpoint prices (CLOB data)

⚠️ No API key, wallet, or login required.

🚀 Quick Start

Run the script with a Polymarket URL:

python polymarket_fetch_bets.py "POLYMARKET_URL"
✅ Example
python polymarket_fetch_bets.py "https://polymarket.com/event/gc-hit-jun-2026"
🔄 Live Mode (Auto Refresh)

Watch live market updates:

python polymarket_fetch_bets.py "POLYMARKET_URL" --watch 10

Updates every 10 seconds.

📌 What It Shows
🧾 Market Info
Question / prediction
Market slug
Active / closed status
Order book availability
End date
🎯 Outcomes (Bet Options)

For each outcome, it displays:

Outcome name (YES / NO or similar)
Token ID
Gamma price (API price)
Live midpoint price (CLOB liquidity price)
🧠 How It Works

The script pulls data from:

🟡 Gamma API → Market structure & metadata
🔵 CLOB API → Live pricing (midpoints)

It automatically:

Detects event or market URLs
Extracts all associated markets
Fetches live pricing per token
📥 Command Options
url        Polymarket event or market URL (required)
--watch    Refresh interval in seconds (default: off)
💡 Output Example
MARKET
Question: Will gold hit $2500 by June 2026?
Active: true
Closed: false

OUTCOMES / BETS

[0] YES
Token ID: 123456
Gamma price: 0.62
Live midpoint: 0.64

[1] NO
Token ID: 789101
Gamma price: 0.38
Live midpoint: 0.36
⚠️ Disclaimer
This tool is for data analysis only
It does not place trades or execute bets
Market prices may change rapidly
