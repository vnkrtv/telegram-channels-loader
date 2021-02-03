import asyncio
import logging
from typing import List

from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest

from .db import TelegramStorage, Channel, Message


class TelegramLoader:

    client: TelegramClient
    db: TelegramStorage
    channels: List[Channel]
    timeout: float

    def __init__(self,
                 db: TelegramStorage,
                 session_name: str,
                 api_id: int,
                 api_hash: str,
                 timeout: float):
        self.db = db
        self.timeout = timeout
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.channels = []

    async def run_client(self):
        await self.client.start()

    async def add_channels(self, channels: List[str]):
        self.client.loop.run_until_complete(self.__add_channels(channels))

    async def __add_channels(self, channels: List[dict]):
        for channel_dict in channels:
            channel_entity = await self.client.get_entity(channel_dict['link'])
            tg_channel = await self.client(GetFullChannelRequest(
                channel=channel_entity
            ))
            channel = Channel.from_dict(name=channel_entity.to_dict()['title'],
                                        channel_dict=tg_channel.full_chat.to_dict(),
                                        link=channel_dict['link'],
                                        channel_type=channel_dict['type'])
            await self.db.add_channel(channel)
            logging.info('Loaded %s(%s) channel info' % (channel.name, channel.link))
            self.channels.append(channel)

    async def start_loading(self, total_count_limit: int):
        self.client.loop.run_until_complete(self.__start_loading(total_count_limit=total_count_limit))

    async def __start_loading(self, total_count_limit: int):
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
        logging.info('Loaded %d messages from %s(%s) channel' % (len(all_messages), channel.name, channel.link))

    async def load_all_channels_messages(self, total_count_limit: int):
        for channel in self.channels:
            await self.load_channel_messages(channel, total_count_limit)
