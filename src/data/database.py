import sqlite3
from datetime import datetime
import pandas as pd

# =========================
# DATABASE CONFIG
# =========================
DB_PATH = "data/bills.db"


# =========================
# CONNECTION
# =========================
def get_connection():
    return sqlite3.connect(DB_PATH)


# =========================
# INIT DATABASE
# =========================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bill_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            charge_name TEXT,
            value REAL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# SAVE BILL CHARGES
# =========================
def save_charges(charges: dict):
    conn = get_connection()
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for name, value in charges.items():
        cursor.execute("""
            INSERT INTO bill_history (timestamp, charge_name, value)
            VALUES (?, ?, ?)
        """, (timestamp, name, value))

    conn.commit()
    conn.close()


# =========================
# LOAD HISTORY (STRUCTURED)
# =========================
def load_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, charge_name, value
        FROM bill_history
        ORDER BY timestamp
    """)

    rows = cursor.fetchall()
    conn.close()

    history = {}

    for timestamp, charge, value in rows:
        if timestamp not in history:
            history[timestamp] = {}

        history[timestamp][charge] = value

    return [
        {"timestamp": ts, "charges": charges}
        for ts, charges in history.items()
    ]


# =========================
# LOAD FLAT DATAFRAME (ML READY)
# =========================
def load_df():
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            timestamp,
            charge_name AS charge,
            value
        FROM bill_history
        ORDER BY timestamp
    """, conn)

    conn.close()

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df