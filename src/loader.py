import asyncio
import json
import os
from typing import List

from telethon.sync import TelegramClient
from telethon import connection

# для корректного переноса времени сообщений в json
from datetime import date, datetime

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

from .db import TelegramStorage, Channel, Message


class TelegramLoader:

    client: TelegramClient
    storage: TelegramStorage
    channels: list

    def __init__(self, client: TelegramClient, storage: TelegramStorage):
        self.storage = storage
        self.client = client
        self.client.start()

    @classmethod
    def create(cls, storage: TelegramStorage, api_id: int, api_hash: str):
        client = TelegramClient(None, api_id, api_hash)
        return cls(client=client, storage=storage)

    async def add_channels(self, channels_urls: List[str]):
        for channel_url in channels_urls:
            channel = await self.client.get_entity(channel_url)
            self.channels.append(channel)

    async def start_loading(self):
        with self.client:
            self.client.loop.run_until_complete(main())

    async def dump_all_participants(self, channel):
        offset_user = 0    # номер участника, с которого начинается считывание
        limit_user = 100   # максимальное число записей, передаваемых за один раз

        all_participants = []   # список всех участников канала
        filter_user = ChannelParticipantsSearch('')

        while True:
            participants = await self.client(GetParticipantsRequest(channel,
                filter_user, offset_user, limit_user, hash=0))
            if not participants.users:
                break
            all_participants.extend(participants.users)
            offset_user += len(participants.users)

        all_users_details = []   # список словарей с интересующими параметрами участников канала

        for participant in all_participants:
            all_users_details.append({"id": participant.id,
                "first_name": participant.first_name,
                "last_name": participant.last_name,
                "user": participant.username,
                "phone": participant.phone,
                "is_bot": participant.bot})

        with open('channel_users.json', 'w', encoding='utf8') as outfile:
            json.dump(all_users_details, outfile, ensure_ascii=False)


    async def dump_all_messages(self, channel: Channel, total_count_limit: int = 500):
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

        for message_json in all_messages:
            message = Message(
                message_id=message_json['id'],
                is_post=message_json['post'],
                text=message_json['message'],
                views_count=message_json['views'],
                date=datetime.fromisoformat(message_json['date']),
                channel_id=channel.channel_id,
                author=message_json['post_author'])
            self.storage.add_message(message)
