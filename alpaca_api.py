from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

import pandas as pd

from http_client import JsonHttpClient


TRADING_BASE = "https://api.alpaca.markets"
DATA_BASE = "https://data.alpaca.markets"

EXCLUDED_NAME_TERMS = (
    " ETF",
    " ETN",
    " FUND",
    " TRUST",
    " WARRANT",
    " WTS",
    " UNIT",
    " UNITS",
    " PREFERRED",
    " DEPOSITARY",
    " ACQUISITION CORP",
    " ACQUISITION CORPORATION",
    " RIGHTS",
)


def batches(items: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(items), size):
        yield items[index:index + size]


class AlpacaApi:
    def __init__(self, api_key: str, secret_key: str) -> None:
        headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key,
        }
        self.http = JsonHttpClient(headers)

    def get_clock(self) -> dict:
        return self.http.get(f"{TRADING_BASE}/v2/clock")

    def get_active_symbols(self) -> list[str]:
        assets = self.http.get(
            f"{TRADING_BASE}/v2/assets",
            params={"status": "active", "asset_class": "us_equity"},
        )

        symbols: list[str] = []
        for asset in assets:
            symbol = str(asset.get("symbol", "")).upper().strip()
            name = str(asset.get("name", "")).upper()
            exchange = str(asset.get("exchange", "")).upper()

            if not symbol or not asset.get("tradable", False):
                continue
            if exchange not in {"NASDAQ", "NYSE", "AMEX"}:
                continue
            if any(term in name for term in EXCLUDED_NAME_TERMS):
                continue
            if "." in symbol or "/" in symbol:
                continue

            symbols.append(symbol)

        return sorted(set(symbols))

    def get_snapshot_candidates(
        self,
        symbols: list[str],
        *,
        min_price: float,
        max_price: float,
        min_previous_volume: int,
        min_dollar_volume: float,
        batch_size: int,
    ) -> list[dict]:
        candidates: list[dict] = []

        for batch in batches(symbols, batch_size):
            payload = self.http.get(
                f"{DATA_BASE}/v2/stocks/snapshots",
                params={"symbols": ",".join(batch), "feed": "iex"},
            )

            snapshots = payload.get("snapshots", payload)
            for symbol, snapshot in snapshots.items():
                latest_trade = snapshot.get("latestTrade") or {}
                daily_bar = snapshot.get("dailyBar") or {}
                previous_bar = snapshot.get("prevDailyBar") or {}

                price = latest_trade.get("p")
                previous_volume = previous_bar.get("v")
                previous_close = previous_bar.get("c")

                if price is None or previous_volume is None or previous_close is None:
                    continue

                price = float(price)
                previous_volume = int(previous_volume)
                previous_close = float(previous_close)
                dollar_volume = previous_volume * previous_close
                current_volume = int(daily_bar.get("v") or 0)

                if not min_price <= price <= max_price:
                    continue
                if previous_volume < min_previous_volume:
                    continue
                if dollar_volume < min_dollar_volume:
                    continue

                candidates.append(
                    {
                        "symbol": symbol,
                        "live_price": price,
                        "previous_volume": previous_volume,
                        "current_volume": current_volume,
                        "dollar_volume": dollar_volume,
                    }
                )

        candidates.sort(
            key=lambda row: max(row["previous_volume"], row["current_volume"]),
            reverse=True,
        )
        return candidates

    def get_daily_bars(
        self,
        symbols: list[str],
        *,
        calendar_days: int,
        batch_size: int,
    ) -> dict[str, pd.DataFrame]:
        start = (
            datetime.now(timezone.utc) - timedelta(days=calendar_days)
        ).isoformat().replace("+00:00", "Z")

        output: dict[str, list[dict]] = {symbol: [] for symbol in symbols}

        for batch in batches(symbols, batch_size):
            page_token: str | None = None

            while True:
                params = {
                    "symbols": ",".join(batch),
                    "timeframe": "1Day",
                    "start": start,
                    "adjustment": "raw",
                    "feed": "iex",
                    "sort": "asc",
                    "limit": 10000,
                }
                if page_token:
                    params["page_token"] = page_token

                payload = self.http.get(
                    f"{DATA_BASE}/v2/stocks/bars",
                    params=params,
                )

                for symbol, bars in (payload.get("bars") or {}).items():
                    output.setdefault(symbol, []).extend(bars)

                page_token = payload.get("next_page_token")
                if not page_token:
                    break

        frames: dict[str, pd.DataFrame] = {}
        for symbol, bars in output.items():
            if not bars:
                continue

            frame = pd.DataFrame(bars).rename(
                columns={
                    "t": "timestamp",
                    "o": "open",
                    "h": "high",
                    "l": "low",
                    "c": "close",
                    "v": "volume",
                }
            )
            required = ["timestamp", "open", "high", "low", "close", "volume"]
            if not all(column in frame.columns for column in required):
                continue

            frame = frame[required].sort_values("timestamp").reset_index(drop=True)
            frames[symbol] = frame

        return frames
