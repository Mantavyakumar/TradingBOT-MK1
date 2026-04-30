"""
Fetch Polymarket bet/market data from a Polymarket URL.

No account, wallet, private key, or API key is required for this script.

Usage:
    python polymarket_fetch_bets.py "https://polymarket.com/event/..."

Watch live prices every 10 seconds:
    python polymarket_fetch_bets.py "https://polymarket.com/event/..." --watch 10
"""

from __future__ import annotations

import argparse
import json
import time
from typing import Any
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import Request, urlopen


GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"


def get_json(url: str) -> Any:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 PolyMK1/1.0",
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: Any) -> Any:
    data = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=data,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 PolyMK1/1.0",
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


def slugs_from_url(polymarket_url: str) -> tuple[str | None, str | None]:
    parsed = urlparse(polymarket_url)
    query = parse_qs(parsed.query)

    market_slug = query.get("marketSlug", [None])[0]
    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) >= 2 and path_parts[0] == "event":
        return market_slug, path_parts[1]

    return market_slug, None


def fetch_markets(polymarket_url: str) -> list[dict[str, Any]]:
    market_slug, event_slug = slugs_from_url(polymarket_url)

    if market_slug:
        markets = get_json(f"{GAMMA_API}/markets?slug={quote(market_slug)}")
        if not markets:
            raise ValueError(f"No market found for marketSlug: {market_slug}")
        return markets

    if event_slug:
        events = get_json(f"{GAMMA_API}/events?slug={quote(event_slug)}")
        if not events:
            raise ValueError(f"No event found for event slug: {event_slug}")
        markets = events[0].get("markets") or []
        if not markets:
            raise ValueError(f"Event found, but no markets were included: {event_slug}")
        return markets

    raise ValueError("Could not find marketSlug or /event/... slug in the URL.")


def fetch_midpoints(token_ids: list[str]) -> dict[str, str]:
    payload = [{"token_id": token_id} for token_id in token_ids]
    return post_json(f"{CLOB_API}/midpoints", payload)


def print_market_snapshot(market: dict[str, Any]) -> None:
    outcomes = [str(item) for item in parse_json_list(market.get("outcomes"))]
    token_ids = [str(item) for item in parse_json_list(market.get("clobTokenIds"))]
    outcome_prices = [str(item) for item in parse_json_list(market.get("outcomePrices"))]
    midpoints = fetch_midpoints(token_ids) if token_ids else {}

    print("\nMARKET")
    print(f"Question: {market.get('question')}")
    print(f"Slug: {market.get('slug')}")
    print(f"Active: {market.get('active')}")
    print(f"Closed: {market.get('closed')}")
    print(f"Accepting orders: {market.get('acceptingOrders')}")
    print(f"Order book enabled: {market.get('enableOrderBook')}")
    print(f"End date: {market.get('endDate')}")

    print("\nOUTCOMES / BETS")
    for index, outcome in enumerate(outcomes):
        token_id = token_ids[index] if index < len(token_ids) else ""
        gamma_price = outcome_prices[index] if index < len(outcome_prices) else ""
        live_midpoint = midpoints.get(token_id, "")

        print(f"\n[{index}] {outcome}")
        print(f"Token ID: {token_id}")
        print(f"Gamma price: {gamma_price}")
        print(f"Live midpoint: {live_midpoint}")

    print("\nUse one Token ID as POLYMARKET_TOKEN_ID in PolyMK1.py.")


def print_markets_snapshot(markets: list[dict[str, Any]]) -> None:
    print(f"\nFound {len(markets)} market(s).")
    for market_number, market in enumerate(markets, start=1):
        print(f"\n================ MARKET {market_number} ================")
        print_market_snapshot(market)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Polymarket bet data from a market URL.")
    parser.add_argument("url", help="Polymarket market URL")
    parser.add_argument("--watch", type=int, default=0, help="Refresh every N seconds")
    args = parser.parse_args()

    markets = fetch_markets(args.url)

    if args.watch <= 0:
        print_markets_snapshot(markets)
        return

    while True:
        print_markets_snapshot(markets)
        time.sleep(args.watch)


if __name__ == "__main__":
    main()
