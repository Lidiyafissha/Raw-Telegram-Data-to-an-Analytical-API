"""
Configuration file for Medical Telegram Warehouse Project
"""

import os
from dotenv import load_dotenv

# -------------------------------------------------------------------
# Load Environment Variables
# -------------------------------------------------------------------

load_dotenv()

# -------------------------------------------------------------------
# Telegram Configuration
# -------------------------------------------------------------------

TELEGRAM_CONFIG = {
    "api_id": int(os.getenv("TELEGRAM_API_ID")),
    "api_hash": os.getenv("TELEGRAM_API_HASH"),
    "session_name": os.getenv("TELEGRAM_SESSION_NAME", "telegram_scraper_session")
}

# -------------------------------------------------------------------
# Channels to Scrape
# -------------------------------------------------------------------

CHANNELS = [
    "lobelia4cosmetics",
    "tikvahpharma",
    "chemed123"
]

# -------------------------------------------------------------------
# Data Paths
# -------------------------------------------------------------------

DATA_PATHS = {
    "raw_base": "data/raw",
    "raw_messages": "data/raw/telegram_messages",
    "raw_images": "data/raw/images"
}
