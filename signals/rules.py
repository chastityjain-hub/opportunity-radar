from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.models import get_connection


LOGGER = logging.getLogger(__name__)
DEFAULT_DEAL_VALUE_THRESHOLD = 10_000_000.0


def fetch_bulk_deals() -> list[dict[str, Any]]:
    """Fetch bulk deal rows from SQLite with computed deal value."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                symbol,
                quantity,
                price,
                deal_date,
                (quantity * price) AS deal_value
            FROM bulk_deals
            ORDER BY deal_date ASC, id ASC
            """
        )
        rows = cursor.fetchall()

    return [
        {
            "symbol": row["symbol"],
            "quantity": row["quantity"],
            "price": row["price"],
            "deal_date": row["deal_date"],
            "deal_value": row["deal_value"],
        }
        for row in rows
    ]


def detect_rule_signals(
    deal_value_threshold: float = DEFAULT_DEAL_VALUE_THRESHOLD,
) -> list[dict[str, Any]]:
    """Detect high-volume and large-value signals from bulk deals."""
    deals = fetch_bulk_deals()
    if not deals:
        LOGGER.info("No bulk deals available for rule detection")
        return []

    sorted_quantities = sorted(deal["quantity"] for deal in deals)
    percentile_index = max(int(len(sorted_quantities) * 0.9) - 1, 0)
    volume_threshold = sorted_quantities[percentile_index]

    signals: list[dict[str, Any]] = []
    for deal in deals:
        if deal["quantity"] >= volume_threshold:
            signals.append(
                {
                    "symbol": deal["symbol"],
                    "signal_type": "high_volume",
                    "value": float(deal["quantity"]),
                    "date": deal["deal_date"],
                }
            )

        if float(deal["deal_value"]) >= deal_value_threshold:
            signals.append(
                {
                    "symbol": deal["symbol"],
                    "signal_type": "large_deal_value",
                    "value": float(deal["deal_value"]),
                    "date": deal["deal_date"],
                }
            )

    LOGGER.info(
        "Rule detection produced %s signals using volume threshold %s and deal value threshold %s",
        len(signals),
        volume_threshold,
        deal_value_threshold,
    )
    return signals


def print_detected_signals(signals: list[dict[str, Any]]) -> None:
    """Print detected signals in a simple CLI-friendly format."""
    if not signals:
        print("No signals detected")
        return

    print("Detected signals:")
    for signal in signals:
        print(
            f"{signal['symbol']} | {signal['signal_type']} | "
            f"{signal['value']} | {signal['date']}"
        )


__all__ = [
    "DEFAULT_DEAL_VALUE_THRESHOLD",
    "detect_rule_signals",
    "fetch_bulk_deals",
    "print_detected_signals",
]


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    print_detected_signals(detect_rule_signals())
