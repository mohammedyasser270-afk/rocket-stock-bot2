from __future__ import annotations

from datetime import datetime, timezone


def build_report(
    *,
    total_assets: int,
    snapshot_candidates: int,
    analyzed: int,
    opportunities: list[dict],
    min_score: int,
) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "🚀 Rocket Stock Scanner V1",
        f"🕒 {timestamp}",
        "",
        f"الأسهم النشطة المفحوصة: {total_assets}",
        f"بعد فلتر السعر والسيولة: {snapshot_candidates}",
        f"الشارتات المحللة: {analyzed}",
        "السعر المسموح: $2–$50",
        "مصدر البيانات: Alpaca IEX",
        "التوافق الشرعي: غير متحقق تلقائيًا",
        "",
    ]

    if not opportunities:
        lines.extend(
            [
                "⚪ لا توجد فرصة تجاوزت الشروط حاليًا.",
                f"Minimum Score: {min_score}",
            ]
        )
        return "\n".join(lines)

    lines.append("🏆 أفضل الفرص الفنية:")
    lines.append("")

    for index, item in enumerate(opportunities, start=1):
        metrics = item["metrics"]
        trade = item["levels"]
        reason = "، ".join(item["reasons"][:4]) or "تجميع نقاط فنية"

        lines.extend(
            [
                f"{index}) {item['symbol']} — Score {item['score']}/100",
                f"السعر اليومي: ${metrics['last_close']:.2f}",
                f"الدخول التقديري: ${trade['entry_low']:.2f}–${trade['entry_high']:.2f}",
                f"Breakout: ${trade['breakout']:.2f}",
                f"Stop: ${trade['stop']:.2f}",
                f"T1: ${trade['target1']:.2f} | T2: ${trade['target2']:.2f}",
                f"RSI: {metrics['rsi']:.1f} | RVOL: {metrics['relative_volume']:.2f}",
                f"السبب: {reason}",
                "",
            ]
        )

    lines.extend(
        [
            "⚠️ النتائج فنية آلية وليست توصية شراء.",
            "تحقق من الخبر، التوافق الشرعي، والسيولة قبل أي قرار.",
        ]
    )
    return "\n".join(lines)
