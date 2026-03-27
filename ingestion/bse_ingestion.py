from __future__ import annotations

import logging
import math
from typing import Any

import yfinance as yf

from ingestion.models import get_connection, init_db


SAMPLE_STOCKS = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
HISTORY_PERIOD = "7d"
HISTORY_INTERVAL = "1d"
MAX_ROWS_PER_SYMBOL = 5
MARKET_CLIENT_NAME = "MARKET"
MARKET_DEAL_TYPE = "BUY"

LOGGER = logging.getLogger(__name__)


def _to_int(value: Any) -> int | None:
    if value is None:
        return None

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _to_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _validate_record(record: dict[str, Any]) -> tuple[bool, str | None]:
    symbol = record.get("symbol")
    quantity = record.get("quantity")
    price = record.get("price")
    deal_date = record.get("deal_date")

    if not symbol:
        return False, "missing symbol"
    if quantity is None:
        return False, "quantity is None"
    if quantity == 0:
        return False, "quantity is 0"
    if price is None:
        return False, "price is None"
    if math.isnan(price):
        return False, "price is NaN"
    if not deal_date:
        return False, "missing deal_date"

    return True, None


def _bulk_deal_exists(cursor: Any, symbol: str, deal_date: str, quantity: int, price: float) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM bulk_deals
        WHERE symbol = ?
          AND deal_date = ?
          AND quantity = ?
          AND ABS(price - ?) < 0.0001
        LIMIT 1
        """,
        (symbol, deal_date, quantity, price),
    )
    return cursor.fetchone() is not None


def _fetch_symbol_history(symbol: str) -> list[dict[str, Any]]:
    try:
        history = yf.Ticker(symbol).history(period=HISTORY_PERIOD, interval=HISTORY_INTERVAL)
    except Exception as exc:
        LOGGER.exception("Failed to fetch yfinance history for %s: %s", symbol, exc)
        return []

    if history.empty:
        LOGGER.warning("No market history returned for %s", symbol)
        return []

    rows: list[dict[str, Any]] = []
    history = history.tail(MAX_ROWS_PER_SYMBOL)

    for timestamp, row in history.iterrows():
        raw_close = row.get("Close")
        close_price = float(raw_close) if raw_close else None
        volume = _to_int(row.get("Volume"))
        record = {
            "symbol": symbol,
            "client_name": MARKET_CLIENT_NAME,
            "deal_type": MARKET_DEAL_TYPE,
            "quantity": volume,
            "price": close_price,
            "deal_date": timestamp.date().isoformat(),
        }
        is_valid, reason = _validate_record(record)
        if not is_valid:
            LOGGER.warning(
                "Skipping invalid market row for %s on %s: %s | close=%s volume=%s",
                symbol,
                timestamp,
                reason,
                raw_close,
                row.get("Volume"),
            )
            continue

        rows.append(record)

    return rows


def ingest_bulk_deals(symbols: list[str] | None = None) -> int:
    init_db()
    symbols = symbols or SAMPLE_STOCKS
    inserted = 0

    with get_connection() as connection:
        cursor = connection.cursor()

        for symbol in symbols:
            records = _fetch_symbol_history(symbol)

            for record in records:
                is_valid, reason = _validate_record(record)
                if not is_valid:
                    LOGGER.warning(
                        "Skipping invalid bulk deal record for %s on %s: %s",
                        record.get("symbol"),
                        record.get("deal_date"),
                        reason,
                    )
                    continue

                if _bulk_deal_exists(
                    cursor,
                    record["symbol"],
                    record["deal_date"],
                    record["quantity"],
                    record["price"],
                ):
                    continue

                cursor.execute(
                    """
                    INSERT INTO bulk_deals
                        (symbol, client_name, deal_type, quantity, price, deal_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record["symbol"],
                        record["client_name"],
                        record["deal_type"],
                        record["quantity"],
                        record["price"],
                        record["deal_date"],
                    ),
                )
                inserted += 1

        connection.commit()

    LOGGER.info("Inserted %s simulated bulk deal records from yfinance", inserted)
    return inserted


def run_ingestion(symbols: list[str] | None = None) -> dict[str, int]:
    bulk_inserted = ingest_bulk_deals(symbols=symbols)
    return {"bulk_deals_inserted": bulk_inserted}


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    LOGGER.info("Ingestion completed: %s", run_ingestion())
