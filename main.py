import os
import json
import asyncio

import nest_asyncio

from src import TelegramLoader, TelegramStorage

TG_USERNAME = os.getenv('TG_USERNAME', '')
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
PG_HOST = os.getenv('PG_HOST', '172.17.0.2')
PG_PORT = os.getenv('PG_PORT', 5432)
PG_NAME = os.getenv('PG_NAME', 'telegram')
PG_USER = os.getenv('PG_USER', 'vnkrtv')
PG_PASS = os.getenv('PG_PASS', 'password')
TIMEOUT = float(os.getenv('TIMEOUT', 60 * 60))
CHANNELS_FILE = os.getenv('CHANNELS_FILE', './channels.json')
MESSAGES_LIMIT = int(os.getenv('MESSAGES_LIMIT', 500))


async def main():
    with open(CHANNELS_FILE, 'r') as f:
        channels_urls = json.load(f)

    db = TelegramStorage(host=PG_HOST,
                         port=PG_PORT,
                         dbname=PG_NAME,
                         user=PG_USER,
                         password=PG_PASS)
    await db.create_schema()

    loader = TelegramLoader.create(db=db, api_id=API_ID, api_hash=API_HASH, timeout=TIMEOUT)
    await loader.start_client()
    await loader.add_channels(channels_urls)
    await loader.start_loading(total_count_limit=MESSAGES_LIMIT)


if __name__ == '__main__':
    nest_asyncio.apply()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
