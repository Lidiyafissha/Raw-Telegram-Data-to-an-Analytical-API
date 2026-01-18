import os
import json
from pathlib import Path
from dotenv import load_dotenv

import importlib
import importlib.util

# Prefer psycopg2 but fall back to psycopg (psycopg3) if psycopg2 is not installed.
psycopg2 = None
if importlib.util.find_spec("psycopg2") is not None:
    psycopg2 = importlib.import_module("psycopg2")
elif importlib.util.find_spec("psycopg") is not None:
    psycopg2 = importlib.import_module("psycopg")
else:
    raise ImportError(
        "neither 'psycopg2' nor 'psycopg' is installed; install one with "
        "'pip install psycopg2-binary' or 'pip install psycopg'"
    )

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("medical_warehouse"),
    "user": os.getenv("PostgresQL 16"),
    "password": os.getenv("postgres"),
}

RAW_DATA_PATH = Path("data/raw/telegram_messages")

CREATE_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.telegram_messages (
    message_id BIGINT,
    channel_name TEXT,
    message_date TIMESTAMP,
    message_text TEXT,
    views INTEGER,
    forwards INTEGER,
    has_media BOOLEAN,
    image_path TEXT
);
"""

INSERT_SQL = """
INSERT INTO raw.telegram_messages (
    message_id, channel_name, message_date,
    message_text, views, forwards, has_media, image_path
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(CREATE_TABLE_SQL)
    conn.commit()

    for json_file in RAW_DATA_PATH.rglob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            records = json.load(f)

        for r in records:
            cur.execute(
                INSERT_SQL,
                (
                    r["message_id"],
                    r["channel_name"],
                    r["message_date"],
                    r["message_text"],
                    r["views"],
                    r["forwards"],
                    r["has_media"],
                    r["image_path"],
                )
            )

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    load_data()
