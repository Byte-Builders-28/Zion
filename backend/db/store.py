import sqlite3
from datetime import datetime

DB_PATH = "zion.db"


def init_chain_table():
    "Run once at startup — creates chain_log table if not exists"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chain_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id  TEXT NOT NULL,
            tx_id        TEXT NOT NULL,
            explorer_url TEXT NOT NULL,
            threat_type  TEXT,
            risk         REAL,
            endpoint     TEXT,
            logged_at    TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_chain_record(record: dict):
    "Called after Algorand confirms TX — saves to local SQLite"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO chain_log
            (incident_id, tx_id, explorer_url, threat_type, risk, endpoint)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        record["incident_id"],
        record["tx_id"],
        record["explorer_url"],
        record.get("threat_type", "unknown"),
        record.get("risk", 0.0),
        record.get("endpoint", "/"),
    ))
    conn.commit()
    conn.close()


def fetch_chain_records(limit=20) -> list:
    "Returns last N chain records for the frontend Chain Log page"
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT incident_id, tx_id, explorer_url,
               threat_type, risk, endpoint, logged_at
        FROM chain_log
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()

    return [
        {
            "incident_id": r[0],
            "tx_id": r[1],
            "tx_short": r[1][:8] + "..." + r[1][-4:],
            "explorer_url": r[2],
            "threat_type": r[3],
            "risk": r[4],
            "endpoint": r[5],
            "logged_at": r[6],
        }
        for r in rows
    ]
