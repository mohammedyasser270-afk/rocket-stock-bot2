from __future__ import annotations

import os
from dataclasses import dataclass


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    telegram_user_id: str
    alpaca_key: str
    alpaca_secret: str

    min_price: float
    max_price: float
    min_previous_volume: int
    min_dollar_volume: float
    max_history_symbols: int
    max_results: int
    min_score: int
    history_calendar_days: int
    snapshot_batch_size: int
    bar_batch_size: int
    force_run: bool

    @classmethod
    def load(cls) -> "Settings":
        required = {
            "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
            "TELEGRAM_USER_ID": os.getenv("TELEGRAM_USER_ID", "").strip(),
            "ALPACA_API_KEY": os.getenv("ALPACA_API_KEY", "").strip(),
            "ALPACA_SECRET_KEY": os.getenv("ALPACA_SECRET_KEY", "").strip(),
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise RuntimeError("Missing GitHub secrets: " + ", ".join(missing))

        return cls(
            telegram_token=required["TELEGRAM_BOT_TOKEN"],
            telegram_user_id=required["TELEGRAM_USER_ID"],
            alpaca_key=required["ALPACA_API_KEY"],
            alpaca_secret=required["ALPACA_SECRET_KEY"],
            min_price=_float("MIN_PRICE", 2.0),
            max_price=_float("MAX_PRICE", 50.0),
            min_previous_volume=_int("MIN_PREVIOUS_VOLUME", 300_000),
            min_dollar_volume=_float("MIN_DOLLAR_VOLUME", 3_000_000),
            max_history_symbols=_int("MAX_HISTORY_SYMBOLS", 250),
            max_results=_int("MAX_RESULTS", 8),
            min_score=_int("MIN_SCORE", 60),
            history_calendar_days=_int("HISTORY_CALENDAR_DAYS", 150),
            snapshot_batch_size=_int("SNAPSHOT_BATCH_SIZE", 150),
            bar_batch_size=_int("BAR_BATCH_SIZE", 50),
            force_run=_bool("FORCE_RUN", False),
        )
