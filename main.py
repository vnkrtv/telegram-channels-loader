import os
import asyncio
import logging

import nest_asyncio

from src import TelegramLoader, TelegramStorage, get_channels, set_logging_level

SESSION_NAME = os.getenv('SESSION_NAME', 'tg_grabber')
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
PG_HOST = os.getenv('PG_HOST', '172.17.0.2')
PG_PORT = os.getenv('PG_PORT', 5432)
PG_NAME = os.getenv('PG_NAME', 'telegram')
PG_USER = os.getenv('PG_USER', 'vnkrtv')
PG_PASS = os.getenv('PG_PASS', 'password')
TIMEOUT = float(os.getenv('TIMEOUT', 60 * 60))
MESSAGES_LIMIT = int(os.getenv('MESSAGES_LIMIT', 1000))
CUSTOM_CHANNELS_URLS = bool(os.getenv('CUSTOM_CHANNELS_URLS'))


async def main():
    channels = get_channels(CUSTOM_CHANNELS_URLS)

    db = TelegramStorage(host=PG_HOST,
                         port=PG_PORT,
                         dbname=PG_NAME,
                         user=PG_USER,
                         password=PG_PASS)
    await db.create_schema()

    loader = TelegramLoader(db=db,
                            session_name=SESSION_NAME,
                            api_id=API_ID,
                            api_hash=API_HASH,
                            timeout=TIMEOUT)
    await loader.run_client()
    await loader.add_channels(channels)
    await loader.start_loading(total_count_limit=MESSAGES_LIMIT)


if __name__ == '__main__':
    set_logging_level(logging.INFO)
    nest_asyncio.apply()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
