"""
GoldBetAdvisor

Runs your breakout / trap / re-cross strategy on real gold futures data, then
checks a Polymarket gold bet and prints advice for which side to consider.

This script does not place orders.

Usage:
    python GoldBetAdvisor.py "https://polymarket.com/event/gc-hit-jun-2026?marketSlug=..."

You can also pass the event URL:
    python GoldBetAdvisor.py "https://polymarket.com/event/gc-hit-jun-2026"
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, quote, urlparse
from urllib.error import HTTPError
from urllib.request import Request, urlopen


GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
YAHOO_CHART_API = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


@dataclass
class Candle:
    timestamp: int
    high: float
    close: float


@dataclass
class StrategyResult:
    name: str
    state: str
    zone: float | None
    latest_close: float
    latest_candle_time: int
    latest_resistance: float | None
    latest_signal_index: int | None
    latest_signal_price: float | None
    bullish: bool
    reason: str
    ema20: float | None = None
    ema50: float | None = None
    ema200: float | None = None
    rsi14: float | None = None


def get_json(url: str) -> Any:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 GoldBetAdvisor/1.0",
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: Any) -> Any:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 GoldBetAdvisor/1.0",
        },
        method="POST",
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_json_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if not value:
        return []
    return json.loads(value)


def slugs_from_url(polymarket_url: str) -> tuple[str | None, str | None, int]:
    parsed = urlparse(polymarket_url)
    query = parse_qs(parsed.query)
    market_slug = query.get("marketSlug", [None])[0]
    outcome_index = int(query.get("outcomeIndex", ["0"])[0])

    path_parts = [part for part in parsed.path.split("/") if part]
    event_slug = path_parts[1] if len(path_parts) >= 2 and path_parts[0] == "event" else None
    return market_slug, event_slug, outcome_index


def fetch_markets(polymarket_url: str) -> tuple[list[dict[str, Any]], int]:
    market_slug, event_slug, outcome_index = slugs_from_url(polymarket_url)

    if market_slug:
        markets = get_json(f"{GAMMA_API}/markets?slug={quote(market_slug)}")
        if not markets:
            raise ValueError(f"No Polymarket market found for marketSlug={market_slug}")
        return markets, outcome_index

    if event_slug:
        events = get_json(f"{GAMMA_API}/events?slug={quote(event_slug)}")
        if not events:
            raise ValueError(f"No Polymarket event found for slug={event_slug}")
        return events[0].get("markets") or [], outcome_index

    raise ValueError("Use a Polymarket event URL or a URL with marketSlug=...")


def fetch_midpoints(token_ids: list[str]) -> dict[str, str]:
    if not token_ids:
        return {}
    return post_json(f"{CLOB_API}/midpoints", [{"token_id": token_id} for token_id in token_ids])


def fetch_gold_candles_for_symbol(symbol: str, interval: str, lookback_range: str) -> list[Candle]:
    yahoo_symbol = quote(symbol, safe="=")
    url = f"{YAHOO_CHART_API.format(symbol=yahoo_symbol)}?interval={quote(interval)}&range={quote(lookback_range)}"
    payload = get_json(url)
    result = payload["chart"]["result"][0]
    timestamps = result["timestamp"]
    quote_data = result["indicators"]["quote"][0]
    highs = quote_data["high"]
    closes = quote_data["close"]

    candles = []
    for timestamp, high, close in zip(timestamps, highs, closes):
        if high is None or close is None:
            continue
        candles.append(Candle(timestamp=timestamp, high=float(high), close=float(close)))

    if not candles:
        raise ValueError(f"No candles received from Yahoo Finance for {symbol}.")

    return candles


def fetch_gold_candles(symbol: str, interval: str, lookback_range: str) -> tuple[list[Candle], str]:
    symbols_to_try = [symbol]

    if symbol == "XAUUSD=X":
        # Yahoo does not always expose direct XAUUSD spot candles. XAUT-USD is
        # tokenized gold and usually tracks spot more closely than many ETFs.
        symbols_to_try.extend(["XAUT-USD", "GC=F"])

    last_error: Exception | None = None
    for candidate in symbols_to_try:
        try:
            return fetch_gold_candles_for_symbol(candidate, interval, lookback_range), candidate
        except HTTPError as exc:
            last_error = exc
            if exc.code != 404:
                raise
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"Could not fetch candles for {', '.join(symbols_to_try)}. Last error: {last_error}")


def run_blackbox_strategy(candles: list[Candle], window: int) -> StrategyResult:
    zone: float | None = None
    state = "SEARCHING"
    latest_signal_index: int | None = None
    latest_signal_price: float | None = None
    latest_resistance: float | None = None

    for index, candle in enumerate(candles):
        if index < window:
            continue

        previous_resistance = max(item.high for item in candles[index - window : index])
        latest_resistance = previous_resistance
        breakout = candle.close > previous_resistance
        re_cross = zone is not None and candle.close > zone

        if state == "SEARCHING" and breakout:
            zone = previous_resistance
            state = "TRAPPED"

        if state == "TRAPPED" and zone is not None and candle.close < zone:
            state = "WAITING"

        if state == "WAITING" and re_cross:
            latest_signal_index = index
            latest_signal_price = candle.close
            state = "SEARCHING"
            zone = None

    return StrategyResult(
        name="blackbox",
        state=state,
        zone=zone,
        latest_close=candles[-1].close,
        latest_candle_time=candles[-1].timestamp,
        latest_resistance=latest_resistance,
        latest_signal_index=latest_signal_index,
        latest_signal_price=latest_signal_price,
        bullish=latest_signal_index == len(candles) - 1,
        reason="Fresh breakout/trap/re-cross signal required.",
    )


def ema(values: list[float], period: int) -> list[float | None]:
    if len(values) < period:
        return [None] * len(values)

    result: list[float | None] = [None] * len(values)
    seed = sum(values[:period]) / period
    result[period - 1] = seed
    multiplier = 2 / (period + 1)

    previous = seed
    for index in range(period, len(values)):
        previous = (values[index] - previous) * multiplier + previous
        result[index] = previous

    return result


def rsi(values: list[float], period: int = 14) -> list[float | None]:
    if len(values) <= period:
        return [None] * len(values)

    result: list[float | None] = [None] * len(values)
    gains: list[float] = []
    losses: list[float] = []

    for index in range(1, period + 1):
        change = values[index] - values[index - 1]
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))

    average_gain = sum(gains) / period
    average_loss = sum(losses) / period
    result[period] = 100 if average_loss == 0 else 100 - (100 / (1 + average_gain / average_loss))

    for index in range(period + 1, len(values)):
        change = values[index] - values[index - 1]
        gain = max(change, 0)
        loss = abs(min(change, 0))
        average_gain = ((average_gain * (period - 1)) + gain) / period
        average_loss = ((average_loss * (period - 1)) + loss) / period
        result[index] = 100 if average_loss == 0 else 100 - (100 / (1 + average_gain / average_loss))

    return result


def run_trend_confirmation_strategy(candles: list[Candle]) -> StrategyResult:
    closes = [candle.close for candle in candles]
    ema20_values = ema(closes, 20)
    ema50_values = ema(closes, 50)
    ema200_values = ema(closes, 200)
    rsi14_values = rsi(closes, 14)

    latest = candles[-1]
    previous = candles[-2]
    ema20_latest = ema20_values[-1]
    ema50_latest = ema50_values[-1]
    ema200_latest = ema200_values[-1]
    rsi14_latest = rsi14_values[-1]

    if None in {ema20_latest, ema50_latest, ema200_latest, rsi14_latest}:
        return StrategyResult(
            name="trend",
            state="INSUFFICIENT_DATA",
            zone=None,
            latest_close=latest.close,
            latest_candle_time=latest.timestamp,
            latest_resistance=previous.high,
            latest_signal_index=None,
            latest_signal_price=None,
            bullish=False,
            reason="Need at least 200 candles for EMA-200 trend confirmation.",
            ema20=ema20_latest,
            ema50=ema50_latest,
            ema200=ema200_latest,
            rsi14=rsi14_latest,
        )

    long_term_uptrend = latest.close > ema200_latest
    short_term_uptrend = ema20_latest > ema50_latest
    constructive_momentum = 50 <= rsi14_latest <= 72
    confirmation_break = latest.close > previous.high
    recently_pulled_back = any(candle.close <= ema20_values[index] for index, candle in enumerate(candles[-6:], start=len(candles) - 6) if ema20_values[index] is not None)

    checks = {
        "close > EMA200": long_term_uptrend,
        "EMA20 > EMA50": short_term_uptrend,
        "RSI14 between 50 and 72": constructive_momentum,
        "close > previous high": confirmation_break,
        "recent pullback to EMA20": recently_pulled_back,
    }
    bullish = all(checks.values())
    failed = [name for name, passed in checks.items() if not passed]
    reason = "Bullish trend-continuation setup confirmed." if bullish else "Failed checks: " + ", ".join(failed)

    return StrategyResult(
        name="trend",
        state="BULLISH" if bullish else "WAITING",
        zone=ema20_latest,
        latest_close=latest.close,
        latest_candle_time=latest.timestamp,
        latest_resistance=previous.high,
        latest_signal_index=len(candles) - 1 if bullish else None,
        latest_signal_price=latest.close if bullish else None,
        bullish=bullish,
        reason=reason,
        ema20=ema20_latest,
        ema50=ema50_latest,
        ema200=ema200_latest,
        rsi14=rsi14_latest,
    )


def classify_market(question: str) -> str:
    text = question.lower()
    if "high" in text or "above" in text or "over" in text:
        return "HIGH"
    if "low" in text or "below" in text or "under" in text:
        return "LOW"
    return "UNKNOWN"


def extract_target(question: str) -> str:
    match = re.search(r"\$[\d,]+(?:\.\d+)?", question)
    return match.group(0) if match else "unknown target"


def advice_for_market(market: dict[str, Any], strategy: StrategyResult, signal_is_fresh: bool) -> str:
    market_type = classify_market(str(market.get("question", "")))

    if not signal_is_fresh:
        return f"NO BET - no confirmed bullish gold signal. {strategy.reason}"

    if market_type == "HIGH":
        return "CONSIDER YES - gold strategy is bullish and this is a HIGH target market."

    if market_type == "LOW":
        return "CONSIDER NO - gold strategy is bullish, which works against a LOW target market."

    return "NO BET - market direction could not be classified as HIGH or LOW."


def print_market_advice(market: dict[str, Any], strategy: StrategyResult, signal_is_fresh: bool) -> None:
    outcomes = [str(item) for item in parse_json_list(market.get("outcomes"))]
    token_ids = [str(item) for item in parse_json_list(market.get("clobTokenIds"))]
    gamma_prices = [str(item) for item in parse_json_list(market.get("outcomePrices"))]
    midpoints = fetch_midpoints(token_ids)

    print("\n============================================================")
    print(f"Question: {market.get('question')}")
    print(f"Target: {extract_target(str(market.get('question', '')))}")
    print(f"Type: {classify_market(str(market.get('question', '')))}")
    print(f"Active: {market.get('active')} | Closed: {market.get('closed')} | Accepting orders: {market.get('acceptingOrders')}")
    print(f"Advice: {advice_for_market(market, strategy, signal_is_fresh)}")

    print("\nOutcomes:")
    for index, outcome in enumerate(outcomes):
        token_id = token_ids[index] if index < len(token_ids) else ""
        gamma_price = gamma_prices[index] if index < len(gamma_prices) else ""
        midpoint = midpoints.get(token_id, "")
        print(f"  [{index}] {outcome}")
        print(f"      Token ID: {token_id}")
        print(f"      Gamma price: {gamma_price}")
        print(f"      Live midpoint: {midpoint}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Advise on Polymarket gold bets using your gold strategy.")
    parser.add_argument("url", help="Polymarket market URL or event URL")
    parser.add_argument("--window", type=int, default=20, help="Lookback window from your Pine strategy")
    parser.add_argument("--strategy", choices=["blackbox", "trend"], default="trend", help="Strategy to apply to real gold candles")
    parser.add_argument("--symbol", default="XAUUSD=X", help="Yahoo Finance symbol. Default is spot gold vs USD: XAUUSD=X")
    parser.add_argument("--interval", default="5m", help="Yahoo Finance candle interval, e.g. 1m, 5m, 15m, 1h")
    parser.add_argument("--range", default="30d", help="Yahoo Finance lookback range, e.g. 5d, 1mo, 3mo")
    parser.add_argument("--fresh-bars", type=int, default=3, help="Signal is fresh if it happened within this many candles")
    parser.add_argument("--watch", type=int, default=0, help="Refresh every N seconds")
    args = parser.parse_args()

    while True:
        candles, data_symbol = fetch_gold_candles(symbol=args.symbol, interval=args.interval, lookback_range=args.range)
        if args.strategy == "blackbox":
            strategy = run_blackbox_strategy(candles, window=args.window)
        else:
            strategy = run_trend_confirmation_strategy(candles)
        markets, _ = fetch_markets(args.url)

        signal_is_fresh = strategy.bullish or (
            strategy.latest_signal_index is not None
            and len(candles) - 1 - strategy.latest_signal_index <= args.fresh_bars
        )

        print("\nGOLD STRATEGY STATUS")
        print(f"Requested symbol: {args.symbol}")
        print(f"Data symbol used: {data_symbol}")
        print(f"Strategy: {strategy.name}")
        candle_time = datetime.fromtimestamp(strategy.latest_candle_time, tz=timezone.utc)
        print(f"Latest candle time UTC: {candle_time:%Y-%m-%d %H:%M:%S}")
        print(f"Latest gold close: {strategy.latest_close:.2f}")
        print(f"Current resistance: {strategy.latest_resistance}")
        print(f"EMA20: {strategy.ema20}")
        print(f"EMA50: {strategy.ema50}")
        print(f"EMA200: {strategy.ema200}")
        print(f"RSI14: {strategy.rsi14}")
        print(f"Strategy state: {strategy.state}")
        print(f"Zone: {strategy.zone}")
        print(f"Latest bullish signal price: {strategy.latest_signal_price}")
        print(f"Fresh signal: {signal_is_fresh}")
        print(f"Reason: {strategy.reason}")

        for market in markets:
            print_market_advice(market, strategy, signal_is_fresh)

        print("\nReminder: this is analysis, not guaranteed profit. Test before placing real bets.")

        if args.watch <= 0:
            break

        time.sleep(args.watch)


if __name__ == "__main__":
    main()
