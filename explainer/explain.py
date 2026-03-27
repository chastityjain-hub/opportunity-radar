from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llm import get_llm_explanation


def _normalize_signal_types(signal_types_combined: Any) -> str:
    if isinstance(signal_types_combined, list):
        return " + ".join(str(item) for item in signal_types_combined)
    return str(signal_types_combined or "market_activity")


def _build_fallback_explanation(
    symbol: str,
    signal_types_combined: str,
    score: int | float,
    date: str,
) -> str:
    lower_signals = signal_types_combined.lower()

    if "zscore" in lower_signals:
        core_view = (
            f"{symbol} is showing abnormal trading activity, with {signal_types_combined} aligning on {date}."
        )
        why_it_matters = (
            "That mix suggests institutional-style positioning or accumulation rather than routine market noise."
        )
    elif "high_volume" in lower_signals and "large_deal" in lower_signals:
        core_view = (
            f"{symbol} recorded heavy participation and outsized traded value on {date}."
        )
        why_it_matters = (
            "This can indicate stronger conviction from larger participants and raises the odds of a meaningful follow-through move."
        )
    elif "high_volume" in lower_signals:
        core_view = f"{symbol} saw unusually strong volume on {date}."
        why_it_matters = (
            "That kind of participation often signals rising market attention and can precede a break in trend."
        )
    else:
        core_view = f"{symbol} showed outsized transaction value on {date}."
        why_it_matters = (
            "Large value concentration can reflect strategic buying interest and may become relevant if momentum starts to build."
        )

    what_to_watch = (
        "Watch upcoming disclosures, price follow-through, and whether elevated volume persists over the next few sessions."
    )

    return f"{core_view} {why_it_matters} {what_to_watch}"


def generate_signal_explanation(
    symbol: str,
    signal_types_combined: str,
    score: int | float,
    date: str,
) -> str:
    """Generate a short plain-English explanation for a merged signal."""
    signal_types_text = _normalize_signal_types(signal_types_combined)
    fallback = _build_fallback_explanation(symbol, signal_types_text, score, date)

    prompt = f"""
You are a financial market analyst for an Indian stock intelligence product.
Write a sharp financial insight in plain English in 2 to 3 lines maximum.
It must clearly cover:
- what happened
- why it matters
- what to watch next

Signal details:
- Symbol: {symbol}
- Signal types: {signal_types_text}
- Conviction score: {score}/10
- Date: {date}

Avoid repetition, avoid hype, sound like an analyst note, and do not use bullet points.
"""

    response = get_llm_explanation(prompt).strip()
    if not response:
        return fallback

    lowered = response.lower()
    if lowered.startswith("explanation unavailable:") or lowered.startswith(
        "error generating explanation:"
    ):
        return fallback

    return response


def generate_signal_explanation_from_dict(signal: dict[str, Any]) -> str:
    """Generate an explanation from a merged signal dictionary."""
    return generate_signal_explanation(
        symbol=str(signal.get("symbol", "UNKNOWN")),
        signal_types_combined=_normalize_signal_types(
            signal.get("signal_types_combined", "market_activity")
        ),
        score=signal.get("conviction_score", signal.get("score", 1)),
        date=str(signal.get("date", "unknown-date")),
    )


def format_signal_explanation(signal: dict[str, Any]) -> str:
    """Format a merged signal and its explanation into a presentation block."""
    symbol = str(signal.get("symbol", "UNKNOWN"))
    signal_types = _normalize_signal_types(signal.get("signal_types_combined", "market_activity"))
    strength = str(signal.get("strength", "Unknown"))
    score = signal.get("conviction_score", signal.get("score", 1))
    date = str(signal.get("date", "unknown-date"))
    explanation = generate_signal_explanation(
        symbol=symbol,
        signal_types_combined=signal_types,
        score=score,
        date=date,
    )

    return (
        "----------------------------------------\n"
        f"Stock: {symbol}\n"
        f"Signal: {signal_types}\n"
        f"Conviction: {strength} ({score}/10)\n"
        f"Date: {date}\n\n"
        "Insight:\n"
        f"{explanation}\n"
        "----------------------------------------"
    )


if __name__ == "__main__":
    sample_signals = [
        {
            "symbol": "TCS.NS",
            "signal_types_combined": "large_deal_value + zscore_anomaly",
            "conviction_score": 6,
            "date": "2026-03-25",
        },
        {
            "symbol": "RELIANCE.NS",
            "signal_types_combined": "high_volume + large_deal_value",
            "conviction_score": 6,
            "date": "2026-03-20",
        },
    ]

    for signal in sample_signals:
        signal["strength"] = "Moderate"
        print(format_signal_explanation(signal))
        print()
