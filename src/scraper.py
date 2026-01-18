"""
Telegram Scraper for Ethiopian Medical Channels
-----------------------------------------------
Extracts recent messages and images from public Telegram channels
and stores them in a raw data lake structure.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from dotenv import load_dotenv

from config import TELEGRAM_CONFIG, DATA_PATHS, CHANNELS

# -------------------------------------------------------------------
# Environment & Logging Setup
# -------------------------------------------------------------------

load_dotenv()

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------------------------------------------------
# Utility Functions
# -------------------------------------------------------------------

def ensure_dir(path: Path) -> None:
    """Create directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def today_partition() -> str:
    """Return today's date as YYYY-MM-DD."""
    return datetime.utcnow().strftime("%Y-%m-%d")


# -------------------------------------------------------------------
# Core Scraping Logic
# -------------------------------------------------------------------

async def scrape_channel(client: TelegramClient, channel: str) -> None:
    """
    Scrape the 100 most recent messages from a Telegram channel.
    """
    logging.info(f"Started scraping channel: {channel}")

    messages_data = []
    date_partition = today_partition()

    json_dir = Path(DATA_PATHS["raw_messages"]) / date_partition
    image_dir = Path(DATA_PATHS["raw_images"]) / channel

    ensure_dir(json_dir)
    ensure_dir(image_dir)

    try:
        async for message in client.iter_messages(channel, limit=100):

            image_path = None
            has_media = bool(message.photo)

            if has_media:
                image_path = image_dir / f"{message.id}.jpg"
                await client.download_media(message.photo, image_path)

            messages_data.append({
                "message_id": message.id,
                "channel_name": channel,
                "message_date": message.date.isoformat() if message.date else None,
                "message_text": message.text,
                "views": message.views,
                "forwards": message.forwards,
                "has_media": has_media,
                "image_path": str(image_path) if image_path else None
            })

        output_file = json_dir / f"{channel}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(messages_data, f, ensure_ascii=False, indent=2, default=str)

        logging.info(
            f"Finished scraping channel: {channel} | Messages: {len(messages_data)}"
        )

    except FloodWaitError as e:
        logging.error(f"Rate limit hit for {channel}: wait {e.seconds}s")
        await asyncio.sleep(e.seconds)

    except Exception as e:
        logging.error(f"Error scraping channel {channel}: {e}")


# -------------------------------------------------------------------
# Entry Point
# -------------------------------------------------------------------

async def main() -> None:
    """
    Initialize Telegram client and scrape all configured channels.
    """
    client = TelegramClient(
        TELEGRAM_CONFIG["session_name"],
        TELEGRAM_CONFIG["api_id"],
        TELEGRAM_CONFIG["api_hash"]
    )

    async with client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)


if __name__ == "__main__":
    asyncio.run(main())
