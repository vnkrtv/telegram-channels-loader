import os
import asyncio

from telethon import TelegramClient

SESSION_NAME = os.getenv('SESSION_NAME', 'tg_grabber')
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')


async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print('Successfully register client')

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
