from __future__ import annotations

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "radar.db"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection to the Opportunity Radar database."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the database and required tables if they do not already exist."""
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bulk_deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                client_name TEXT NOT NULL,
                deal_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                deal_date TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS insider_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                person TEXT NOT NULL,
                category TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                value REAL NOT NULL,
                trade_date TEXT NOT NULL
            )
            """
        )

        connection.commit()


__all__ = ["DB_DIR", "DB_PATH", "get_connection", "init_db"]
