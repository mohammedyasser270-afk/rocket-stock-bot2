from __future__ import annotations

from alpaca_api import AlpacaApi
from config import Settings
from indicators import analyze
from report import build_report
from scoring import levels, score
from telegram_client import TelegramClient


def main() -> None:
    settings = Settings.load()
    telegram = TelegramClient(
        settings.telegram_token,
        settings.telegram_user_id,
    )
    alpaca = AlpacaApi(
        settings.alpaca_key,
        settings.alpaca_secret,
    )

    try:
        clock = alpaca.get_clock()
        is_open = bool(clock.get("is_open", False))

        if not is_open and not settings.force_run:
            print("Market is closed. Scheduled scan skipped.")
            return

        symbols = alpaca.get_active_symbols()
        print(f"Active eligible symbols: {len(symbols)}")

        candidates = alpaca.get_snapshot_candidates(
            symbols,
            min_price=settings.min_price,
            max_price=settings.max_price,
            min_previous_volume=settings.min_previous_volume,
            min_dollar_volume=settings.min_dollar_volume,
            batch_size=settings.snapshot_batch_size,
        )
        print(f"Snapshot candidates: {len(candidates)}")

        selected = candidates[: settings.max_history_symbols]
        selected_symbols = [item["symbol"] for item in selected]

        bars = alpaca.get_daily_bars(
            selected_symbols,
            calendar_days=settings.history_calendar_days,
            batch_size=settings.bar_batch_size,
        )

        opportunities: list[dict] = []
        analyzed_count = 0

        for symbol in selected_symbols:
            metrics = analyze(bars.get(symbol))
            if metrics is None:
                continue

            analyzed_count += 1
            setup_score, reasons = score(metrics)

            if setup_score < settings.min_score:
                continue

            opportunities.append(
                {
                    "symbol": symbol,
                    "score": setup_score,
                    "reasons": reasons,
                    "metrics": metrics,
                    "levels": levels(metrics),
                }
            )

        opportunities.sort(
            key=lambda item: (
                item["score"],
                item["metrics"]["relative_volume"],
            ),
            reverse=True,
        )
        opportunities = opportunities[: settings.max_results]

        telegram.send(
            build_report(
                total_assets=len(symbols),
                snapshot_candidates=len(candidates),
                analyzed=analyzed_count,
                opportunities=opportunities,
                min_score=settings.min_score,
            )
        )

    except Exception as exc:
        error_message = (
            "🔴 Rocket Scanner Error\n\n"
            f"{type(exc).__name__}: {exc}"
        )
        try:
            telegram.send(error_message)
        finally:
            raise


if __name__ == "__main__":
    main()
