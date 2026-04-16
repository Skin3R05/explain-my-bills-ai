import sqlite3
import os
from datetime import datetime
import pandas as pd

# ── Config ────────────────────────────────────────────────────────────────────
DB_PATH = "data/bills.db"


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database, creating dirs if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Create the bill_history table if it does not already exist."""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bill_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT    NOT NULL,
                charge_name TEXT    NOT NULL,
                value       REAL    NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_charges(charges: dict) -> None:
    """Persist a bill's charges to the database with the current timestamp."""
    if not charges:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        conn.executemany(
            "INSERT INTO bill_history (timestamp, charge_name, value) VALUES (?, ?, ?)",
            [(timestamp, name, value) for name, value in charges.items()]
        )
        conn.commit()
    finally:
        conn.close()


def load_history() -> list:
    """
    Load all bill records and return them grouped by timestamp.

    Returns:
        List of dicts: [{"timestamp": str, "charges": {name: value, ...}}, ...]
    """
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT timestamp, charge_name, value
            FROM bill_history
            ORDER BY timestamp
        """)
        rows = cursor.fetchall()
    finally:
        conn.close()

    history: dict = {}
    for timestamp, charge, value in rows:
        history.setdefault(timestamp, {})[charge] = value

    return [
        {"timestamp": ts, "charges": charges}
        for ts, charges in history.items()
    ]


def load_df() -> pd.DataFrame:
    """
    Load the full bill_history table as a flat, ML-ready DataFrame.

    Returns:
        DataFrame with columns: timestamp (datetime), charge (str), value (float)
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            """
            SELECT
                timestamp,
                charge_name AS charge,
                value
            FROM bill_history
            ORDER BY timestamp
            """,
            conn
        )
    finally:
        conn.close()

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df