from __future__ import annotations


def score(metrics: dict) -> tuple[int, list[str]]:
    total = 0
    reasons: list[str] = []

    price = metrics["last_close"]
    ema9 = metrics["ema9"]
    ema20 = metrics["ema20"]
    ema50 = metrics["ema50"]
    rsi = metrics["rsi"]
    relative_volume = metrics["relative_volume"]
    distance = metrics["breakout_distance_pct"]

    if price > ema20:
        total += 12
        reasons.append("فوق EMA20")

    if ema9 > ema20:
        total += 8
        reasons.append("EMA9 فوق EMA20")

    if ema20 > ema50:
        total += 15
        reasons.append("اتجاه متوسط صاعد")

    if 50 <= rsi <= 68:
        total += 15
        reasons.append(f"RSI مناسب {rsi:.1f}")
    elif 45 <= rsi < 50 or 68 < rsi <= 72:
        total += 7

    if metrics["macd"] > metrics["macd_signal"]:
        total += 12
        reasons.append("MACD إيجابي")

    if relative_volume >= 1.5:
        total += 18
        reasons.append(f"RVOL قوي {relative_volume:.2f}")
    elif relative_volume >= 1.1:
        total += 10
        reasons.append(f"RVOL جيد {relative_volume:.2f}")

    if 0 <= distance <= 3:
        total += 20
        reasons.append(f"قريب من الاختراق {distance:.1f}%")
    elif -2 <= distance < 0:
        total += 14
        reasons.append("اختراق مبكر")
    elif 3 < distance <= 6:
        total += 8

    return min(total, 100), reasons


def levels(metrics: dict) -> dict:
    price = metrics["last_close"]
    atr = max(metrics["atr"], price * 0.015)
    support = metrics["support"]
    resistance = metrics["resistance"]

    entry_low = max(metrics["ema20"], price - 0.30 * atr)
    entry_high = price + 0.10 * atr

    structural_stop = entry_low - 1.15 * atr
    stop = max(support, structural_stop)
    if stop >= entry_low:
        stop = entry_low - 0.90 * atr

    risk = max(entry_high - stop, price * 0.01)

    return {
        "entry_low": entry_low,
        "entry_high": entry_high,
        "breakout": resistance,
        "stop": stop,
        "target1": entry_high + 2.0 * risk,
        "target2": entry_high + 3.0 * risk,
    }
