import os

from src import TelegramLoader

TG_USERNAME = os.getenv('TG_USERNAME', '')
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')

if __name__ == '__main__':
    loader = TelegramLoader.create(api_id=API_ID, api_hash=API_HASH)
