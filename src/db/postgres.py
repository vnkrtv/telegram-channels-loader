from typing import Generator

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

    def exec_query(self, query: str, params: list) -> Generator:
        cursor = self.conn.cursor()
        cursor.execute(query, params)
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
                tiktoks (tiktok_id, create_time, description, author_id, video_id, music_id, 
                          digg_count, share_count, comment_count, play_count, is_ad) 
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (tiktok_id)
                DO UPDATE SET
                    digg_count = EXCLUDED.digg_count,
                    share_count = EXCLUDED.share_count,
                    comment_count = EXCLUDED.comment_count,
                    play_count = EXCLUDED.play_count'''
        self.exec(sql=sql, params=message.db_params)

    def __get_all(self, table_name: str, count: int = 0) -> Generator:
        sql = f'SELECT * FROM {table_name}'
        if count != 0:
            sql += f' LIMIT {count}'
        return self.exec(sql=sql, params=[])

    def get_all_tiktokers(self, count: int = 0) -> Generator:
        return self.__get_all(table_name='tiktokers', count=count)

    def get_all_tiktoks(self, count: int = 0) -> Generator:
        return self.__get_all(table_name='tiktoks', count=count)

    def get_ticktoker(self, ticktoker_id: int = None, nickname: str = None) -> tuple:
        sql = f'SELECT * FROM tiktokers'
        if ticktoker_id:
            sql += f' WHERE tiktoker_id={ticktoker_id}'
        elif nickname:
            sql += f' WHERE nickname={nickname}'
        return next(self.exec(sql=sql, params=[]))

    def get_ticktoks(self, ticktok_id: int = None, author_id: int = None) -> Generator:
        sql = f'SELECT * FROM tiktoks'
        if ticktok_id:
            sql += f' WHERE tiktok_id={ticktok_id}'
        elif author_id:
            sql += f' WHERE author_id={author_id}'
        return self.exec(sql=sql, params=[])
