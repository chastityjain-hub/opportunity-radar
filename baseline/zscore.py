from __future__ import annotations

import logging
import sys
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from signals.rules import fetch_bulk_deals


LOGGER = logging.getLogger(__name__)
DEFAULT_ZSCORE_THRESHOLD = 1.0


def compute_zscores() -> list[dict[str, Any]]:
    """Compute z-scores for each symbol using prior deal-value history."""
    deals = fetch_bulk_deals()
    if not deals:
        LOGGER.info("No bulk deals available for z-score detection")
        return []

    deals_by_symbol: dict[str, list[dict[str, Any]]] = {}
    for deal in deals:
        deals_by_symbol.setdefault(deal["symbol"], []).append(deal)

    computed_scores: list[dict[str, Any]] = []
    for symbol, symbol_deals in deals_by_symbol.items():
        ordered_deals = sorted(symbol_deals, key=lambda item: item["deal_date"])

        for index, deal in enumerate(ordered_deals):
            history = ordered_deals[:index]
            if len(history) < 2:
                continue

            historical_values = [float(item["deal_value"]) for item in history]
            historical_mean = mean(historical_values)
            historical_std = pstdev(historical_values)

            if historical_std == 0:
                continue

            current_value = float(deal["deal_value"])
            zscore = (current_value - historical_mean) / historical_std
            computed_scores.append(
                {
                    "symbol": symbol,
                    "signal_type": "zscore_anomaly",
                    "value": round(zscore, 4),
                    "z_score": round(zscore, 4),
                    "deal_value": current_value,
                    "date": deal["deal_date"],
                }
            )

    return computed_scores


def detect_zscore_signals(
    zscore_threshold: float = DEFAULT_ZSCORE_THRESHOLD,
) -> list[dict[str, Any]]:
    """Calculate per-symbol z-scores for deal value and flag anomalies."""
    signals = [
        score for score in compute_zscores() if float(score["z_score"]) > zscore_threshold
    ]

    LOGGER.info("Z-score detection produced %s signals", len(signals))
    return signals


def print_all_zscores(
    computed_scores: list[dict[str, Any]],
    zscore_threshold: float = DEFAULT_ZSCORE_THRESHOLD,
) -> None:
    """Print every computed z-score and mark threshold hits."""
    if not computed_scores:
        print("No z-scores computed")
        return

    print("All Z-Scores:")
    for score in computed_scores:
        marker = " <-- above threshold" if float(score["z_score"]) > zscore_threshold else ""
        print(
            f"{score['symbol']} | {score['z_score']} | "
            f"{score['deal_value']} | {score['date']}{marker}"
        )


def print_zscore_signals(signals: list[dict[str, Any]]) -> None:
    """Print z-score anomalies in a simple CLI-friendly format."""
    if not signals:
        print("No anomalies detected")
        return

    print("Z-Score Signals:")
    for signal in signals:
        print(
            f"{signal['symbol']} | {signal['z_score']} | "
            f"{signal['deal_value']} | {signal['date']}"
        )


__all__ = [
    "DEFAULT_ZSCORE_THRESHOLD",
    "compute_zscores",
    "detect_zscore_signals",
    "print_all_zscores",
    "print_zscore_signals",
]


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    all_scores = compute_zscores()
    print_all_zscores(all_scores)
    print()
    print_zscore_signals(detect_zscore_signals())
