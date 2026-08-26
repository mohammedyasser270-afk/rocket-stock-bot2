from __future__ import annotations

import pandas as pd


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    average_gain = gain.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False,
    ).mean()
    average_loss = loss.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False,
    ).mean()

    relative_strength = average_gain / average_loss.replace(0, float("nan"))
    result = 100 - (100 / (1 + relative_strength))
    return result.fillna(50)


def analyze(frame: pd.DataFrame) -> dict | None:
    if frame is None or len(frame) < 55:
        return None

    data = frame.copy()
    for column in ("open", "high", "low", "close", "volume"):
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["high", "low", "close", "volume"])
    if len(data) < 55:
        return None

    close = data["close"]
    high = data["high"]
    low = data["low"]
    volume = data["volume"]

    ema9 = close.ewm(span=9, adjust=False).mean()
    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()

    rsi14 = rsi(close, 14)

    average_volume20 = volume.rolling(20).mean()
    relative_volume = (
        float(volume.iloc[-1] / average_volume20.iloc[-1])
        if average_volume20.iloc[-1] > 0
        else 0.0
    )

    resistance20 = float(high.shift(1).rolling(20).max().iloc[-1])
    support20 = float(low.shift(1).rolling(20).min().iloc[-1])

    previous_close = close.shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr14 = float(true_range.rolling(14).mean().iloc[-1])

    last_close = float(close.iloc[-1])
    breakout_distance = (
        (resistance20 - last_close) / last_close * 100
        if last_close > 0
        else 999.0
    )

    return {
        "last_close": last_close,
        "ema9": float(ema9.iloc[-1]),
        "ema20": float(ema20.iloc[-1]),
        "ema50": float(ema50.iloc[-1]),
        "rsi": float(rsi14.iloc[-1]),
        "macd": float(macd.iloc[-1]),
        "macd_signal": float(macd_signal.iloc[-1]),
        "relative_volume": relative_volume,
        "average_volume20": float(average_volume20.iloc[-1]),
        "support": support20,
        "resistance": resistance20,
        "atr": atr14,
        "breakout_distance_pct": breakout_distance,
    }
