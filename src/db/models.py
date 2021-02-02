from typing import List, Optional
from datetime import datetime


class Channel:

    channel_id: int
    name: str
    link: str
    description: str
    subscribers_count: int

    def __init__(self, channel_id: int,
                 name: str,
                 link: str,
                 description: str,
                 subscribers_count: int):
        self.channel_id = channel_id
        self.name = name
        self.link = link
        self.description = description
        self.subscribers_count = subscribers_count

    @property
    def db_params(self) -> List[str]:
        return [self.channel_id, self.name, self.name, self.link, self.description, self.subscribers_count]


class Message:

    message_id: int
    is_post: bool
    date: datetime
    views_count: int
    author: Optional[str, None]
    text: str
    channel_id: int

    def __init__(self,
                 message_id: int,
                 is_post: bool,
                 date: datetime,
                 views_count: int,
                 author: Optional[str, None],
                 text: str,
                 channel_id: int):
        self.message_id = message_id
        self.is_post = is_post
        self.date = date
        self.views_count = views_count
        self.author = author
        self.text = text
        self.channel_id = channel_id

    @property
    def db_params(self) -> List[Optional[str, None]]:
        return [self.message_id, self.channel_id, self.date,
                self.text, self.views_count, self.author, self.is_post]
