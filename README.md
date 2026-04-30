GoldBetAdvisor

GoldBetAdvisor runs your breakout / trap / re-cross or trend-confirmation strategy on real gold market data and compares it against a Polymarket gold prediction market.

It then prints actionable advice on whether to consider betting YES / NO / NO BET.

⚠️ This tool is for analysis only — it does NOT place trades.

🚀 How to Run
python filename.py "URL_OF_THE_POLYMARKET_BET"
Example
python GoldBetAdvisor.py "https://polymarket.com/event/gc-hit-jun-2026?marketSlug=..."

or

python GoldBetAdvisor.py "https://polymarket.com/event/gc-hit-jun-2026"
⚙️ Arguments
Argument	Description	Default
url	Polymarket event or market URL	required
--strategy	Strategy to use (blackbox or trend)	trend
--window	Lookback window (for blackbox strategy)	20
--symbol	Yahoo Finance symbol for gold	XAUUSD=X
--interval	Candle timeframe	5m
--range	Historical data range	30d
--fresh-bars	Signal freshness threshold	3
--watch	Auto-refresh interval (seconds)	0
📊 Strategies
1. Trend Confirmation (default)

Uses:

EMA 20 / 50 / 200
RSI (14)
Breakout confirmation

Generates signals when:

Long-term uptrend is intact
Momentum is healthy
Price confirms breakout
2. Blackbox Strategy

Your custom:

Breakout
Trap
Re-cross logic

Detects:

Fake breakouts
Re-entry opportunities
📈 Output

For each run, the script shows:

Gold price + indicators
Strategy state
Whether signal is fresh
Market classification (HIGH / LOW)
Suggested action:
✅ CONSIDER YES
❌ CONSIDER NO
⛔ NO BET
⚠️ Disclaimer

This is a research/analysis tool — not financial advice.

Markets can behave unpredictably. Always test and validate before risking real money.
