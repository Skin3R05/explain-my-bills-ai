import sqlite3
from datetime import datetime
import pandas as pd

# DATABASE LAYER

DB_PATH = "data/bills.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

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

# SAVE DATA TO DB

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

# LOAD DATA FROM DB

def load_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT timestamp, charge_name, value FROM bill_history")

    rows = cursor.fetchall()
    conn.close()

    history = {}

    for timestamp, charge, value in rows:
        if timestamp not in history:
            history[timestamp] = {}

        history[timestamp][charge] = value

    # convert to your original format
    return [
        {"timestamp": ts, "charges": charges}
        for ts, charges in history.items()
    ]



def load_df():
    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM bill_history",
        conn
    )

    conn.close()
    return df