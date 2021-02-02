from typing import Generator, Optional, List

import psycopg2

from .db_schema import DB_SCHEMA
from .models import Channel, Message


class PostgresStorage:
    """
    Base class for working with PostgreSQL
    """

    conn: psycopg2.extensions.connection

    def __init__(self, conn):
        self.conn = conn

    @classmethod
    def connect(cls,
                host: str,
                port: int = 5432,
                user: str = 'postgres',
                password: str = 'password',
                dbname: str = 'postgres'):
        return cls(conn=psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=dbname)
        )

    def exec_query(self, sql: str, params: list) -> Generator:
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

    def exec(self, sql: str, params: list):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params)
        except psycopg2.Error as e:
            self.conn.rollback()
            raise e
        self.conn.commit()


class TelegramStorage(PostgresStorage):
    """
    Class for working with Telegram
    """

    def create_schema(self):
        self.exec(sql=DB_SCHEMA, params=[])

    def add_channel(self, channel: Channel):
        sql = '''
            INSERT INTO 
                channels (channel_id, name, link, description, subscribers_count) 
            VALUES 
                (%s, %s, %s, %s, %s)
            ON CONFLICT (channel_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    link = EXCLUDED.link,
                    description=EXCLUDED.description,
                    subscribers_count=EXCLUDED.subscribers_count'''
        self.exec(sql=sql, params=channel.db_params)

    def add_message(self, message: Message):
        sql = '''
            INSERT INTO 
                tiktoks (message_id, channel_id, date, text, views_count, author, is_post) 
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (message_id)
                DO UPDATE SET
                    text = EXCLUDED.text,
                    views_count = EXCLUDED.views_count'''
        self.exec(sql=sql, params=message.db_params)

    def __get_all(self, table_name: str, count: int = 0) -> Generator:
        sql = f'SELECT * FROM {table_name}'
        if count != 0:
            sql += f' LIMIT {count}'
        return self.exec_query(sql=sql, params=[])

    def get_all_channels(self, count: int = 0) -> Generator:
        return self.__get_all(table_name='channels', count=count)

    def get_all_messages(self, count: int = 0) -> Generator:
        return self.__get_all(table_name='messages', count=count)

    def get_channel(self, channel_id: int) -> Optional[Channel, None]:
        sql = 'SELECT * FROM channels WHERE channel_id=%s'
        row = next(self.exec_query(sql=sql, params=[channel_id]))
        if not row:
            return None
        channel = Channel(
            channel_id=channel_id,
            name=row[1],
            link=row[2],
            description=row[3],
            subscribers_count=row[4])
        return channel

    def get_messages(self, channel_id: int = 0, message_ids: List[int] = None) -> List[Message]:
        sql = f'SELECT * FROM messages'
        params = []
        if channel_id:
            sql += ' WHERE channel_id=%s'
            params = [channel_id]
        elif message_ids:
            sql += ' WHERE message_id IN %s'
            params = [tuple(message_ids)]
        messages = []
        for row in self.exec_query(sql=sql, params=params):
            message = Message(
                message_id=row[0],
                channel_id=row[1],
                date=row[2],
                description=row[3],
                text=row[4],
                views_count=row[5],
                author=row[6],
                is_post=row[7])
            messages.append(message)
        return messages
