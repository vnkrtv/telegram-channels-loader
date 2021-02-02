import asyncio
from typing import List

from telethon.sync import TelegramClient
from telethon import events
from telethon import types

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

from .db import TelegramStorage, Channel, Message


class TelegramLoader:

    client: TelegramClient
    db: TelegramStorage
    channels: List[Channel]
    timeout: float

    def __init__(self, client: TelegramClient, db: TelegramStorage, timeout: float):
        self.db = db
        self.timeout = timeout
        self.client = client
        self.client.start()

    async def start_client(self):
        await self.client.run_until_disconnected()

    @classmethod
    def create(cls, db: TelegramStorage, api_id: int, api_hash: str, timeout: float):
        client = TelegramClient(None, api_id, api_hash)
        return cls(client=client, db=db, timeout=timeout)

    async def add_channels(self, channels_urls: List[str]):
        for channel_url in channels_urls:
            tg_channel = await self.client.get_entity(channel_url)
            channel = Channel.from_dict(tg_channel.to_dict())
            await self.db.add_channel(channel)
            self.channels.append(channel)

    async def start_loading(self, total_count_limit: int):
        while True:
            await self.load_all_channels_messages(total_count_limit)
            await asyncio.sleep(self.timeout)

    async def load_channel_messages(self, channel: Channel, total_count_limit: int):
        offset_msg = 0    # номер записи, с которой начинается считывание
        limit_msg = 100   # максимальное число записей, передаваемых за один раз

        all_messages = []   # список всех сообщений

        while True:
            history = await self.client(GetHistoryRequest(
                peer=channel.link,
                offset_id=offset_msg,
                offset_date=None, add_offset=0,
                limit=limit_msg, max_id=0, min_id=0,
                hash=0))
            if not history.messages:
                break
            messages = history.messages
            for message in messages:
                all_messages.append(message.to_dict())
            offset_msg = messages[len(messages) - 1].id
            total_messages = len(all_messages)
            if total_count_limit != 0 and total_messages >= total_count_limit:
                break
        for message_dict in all_messages:
            message = Message.from_dict(message_dict, channel.channel_id)
            await self.db.add_message(message)

    async def load_all_channels_messages(self, total_count_limit: int):
        for channel in self.channels:
            await self.load_channel_messages(channel, total_count_limit)
