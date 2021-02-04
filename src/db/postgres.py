from typing import List, Any, Tuple
import logging
import asyncio

import asyncpg

from .db_schema import DB_SCHEMA
from .models import Channel, Message


class PostgresStorage:
    """
    Base class for working with PostgreSQL
    """

    pool: asyncpg.pool.Pool

    def __init__(self,
                 host: str,
                 port: int = 5432,
                 user: str = 'postgres',
                 password: str = 'password',
                 dbname: str = 'postgres'):
        uri = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        self.pool = loop.run_until_complete(asyncpg.create_pool(dsn=uri))
        logging.info('Opened connection pool to PostgreSQL DB(%s)' % uri)

    async def exec_query(self, sql: str, params: List[Any]) -> List[Tuple]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            return rows

    async def exec(self, sql: str, params: List[Any]):
        async with self.pool.acquire() as conn:
            await conn.execute(sql, *params)

    async def exec_ddl(self, sql: str):
        async with self.pool.acquire() as conn:
            await conn.execute(sql)


class TelegramStorage(PostgresStorage):
    """
    Class for working with Telegram data stored in PostgreSQL
    """

    async def create_schema(self):
        await self.exec_ddl(sql=DB_SCHEMA)
        logging.info('Created DB schema')

    async def add_channel(self, channel: Channel):
        sql = '''
            INSERT INTO 
                channels (channel_id, name, link, description, subscribers_count, type) 
            VALUES 
                ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (channel_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    link = EXCLUDED.link,
                    description=EXCLUDED.description,
                    subscribers_count=EXCLUDED.subscribers_count'''
        await self.exec(sql=sql, params=channel.db_params)

    async def add_message(self, message: Message):
        sql = '''
            INSERT INTO 
                messages (message_id, channel_id, date, text, views_count, author, is_post) 
            VALUES 
                ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (message_id)
                DO UPDATE SET
                    text = EXCLUDED.text,
                    views_count = EXCLUDED.views_count'''
        await self.exec(sql=sql, params=message.db_params)

    async def get_channel(self, channel_id: int) -> Any:
        sql = 'SELECT * FROM channels WHERE channel_id=$1'
        row = await self.exec_query(sql=sql, params=[channel_id])
        if not row:
            return None
        row = row[0]
        channel = Channel(
            channel_id=channel_id,
            name=row[1],
            link=row[2],
            description=row[3],
            subscribers_count=row[4],
            channel_type=row[5])
        return channel

    async def get_messages(self, channel_id: int = 0, message_ids: List[int] = None) -> List[Message]:
        sql = f'SELECT * FROM messages'
        params = []
        if channel_id:
            sql += ' WHERE channel_id=$1'
            params = [channel_id]
        elif message_ids:
            sql += ' WHERE message_id IN $1'
            params = [tuple(message_ids)]
        messages = []
        for row in await self.exec_query(sql=sql, params=params):
            message = Message(
                message_id=row[0],
                channel_id=row[1],
                date=row[2],
                text=row[3],
                views_count=row[4],
                author=row[5],
                is_post=row[6])
            messages.append(message)
        return messages
