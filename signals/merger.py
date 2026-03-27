from __future__ import annotations

import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from baseline.zscore import detect_zscore_signals
from signals.rules import detect_rule_signals


LOGGER = logging.getLogger(__name__)


def _get_strength_and_score(condition_count: int) -> tuple[str, int]:
    if condition_count <= 1:
        return "Weak", 3
    if condition_count == 2:
        return "Moderate", 6
    return "Strong", min(10, 3 + (condition_count * 2))


def merge_signals() -> list[dict[str, Any]]:
    """Combine rule and z-score signals for demo-friendly merged output."""
    rule_signals = detect_rule_signals()
    zscore_signals = detect_zscore_signals()
    combined_signals = rule_signals + zscore_signals
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for signal in combined_signals:
        grouped[(signal["symbol"], signal["date"])].append(signal)

    final_signals: list[dict[str, Any]] = []
    for (symbol, date), matches in grouped.items():
        distinct_conditions = {signal["signal_type"] for signal in matches}
        if len(distinct_conditions) < 1:
            continue

        sorted_conditions = sorted(distinct_conditions)
        strength, conviction_score = _get_strength_and_score(len(sorted_conditions))
        final_signals.append(
            {
                "symbol": symbol,
                "signal_type": "merged_signal",
                "signal_types_combined": " + ".join(sorted_conditions),
                "strength": strength,
                "conviction_score": conviction_score,
                "value": {
                    "matched_conditions": sorted_conditions,
                    "source_signals": matches,
                },
                "date": date,
            }
        )

    print(f"Total rule signals: {len(rule_signals)}")
    print(f"Total z-score signals: {len(zscore_signals)}")
    print(f"Merged signals count: {len(final_signals)}")

    LOGGER.info("Signal merger produced %s final signals", len(final_signals))
    return final_signals


def print_final_signals(signals: list[dict[str, Any]]) -> None:
    """Print merged high-confidence signals in a simple CLI-friendly format."""
    if not signals:
        print("No high-confidence signals found")
        return

    print("Final Signals:")
    for signal in signals:
        print(
            f"{signal['symbol']} | {signal['signal_types_combined']} | "
            f"{signal['strength']} | {signal['conviction_score']} | {signal['date']}"
        )


__all__ = ["merge_signals", "print_final_signals"]


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    print_final_signals(merge_signals())
