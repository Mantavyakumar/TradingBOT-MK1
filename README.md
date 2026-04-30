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
