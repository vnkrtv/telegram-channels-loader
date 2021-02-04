from typing import List, Dict, Any, AnyStr
from datetime import datetime


class Channel:
    channel_id: int
    name: str
    link: str
    description: str
    subscribers_count: int
    channel_type: str

    def __init__(self, channel_id: int,
                 name: str,
                 link: str,
                 description: str,
                 subscribers_count: int,
                 channel_type: str):
        self.channel_id = channel_id
        self.name = name
        self.link = link
        self.description = description
        self.subscribers_count = subscribers_count
        self.channel_type = channel_type

    @property
    def db_params(self) -> List[AnyStr]:
        return [self.channel_id, self.name, self.link, self.description, self.subscribers_count, self.channel_type]

    @classmethod
    def from_dict(cls, name: str, channel_dict: Dict[AnyStr, Any], link: str, channel_type: str):
        return cls(
            channel_id=channel_dict['id'],
            name=name,
            link=link,
            description=channel_dict['about'],
            subscribers_count=channel_dict['participants_count'],
            channel_type=channel_type)


class Message:
    message_id: int
    is_post: bool
    date: datetime
    views_count: int
    author: Any
    text: str
    channel_id: int

    def __init__(self,
                 message_id: int,
                 is_post: bool,
                 date: datetime,
                 views_count: int,
                 author: Any,
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
    def db_params(self) -> List[Any]:
        return [self.message_id, self.channel_id, self.date,
                self.text, self.views_count, self.author, self.is_post]

    @classmethod
    def from_dict(cls, message_dict: Dict[AnyStr, Any], channel_id: int):
        return cls(
            message_id=message_dict['id'],
            is_post=message_dict['post'],
            text=message_dict['message'],
            views_count=message_dict['views'],
            date=datetime.strptime(str(message_dict['date'])[:-6], "%Y-%m-%d %H:%M:%S"),
            channel_id=channel_id,
            author=message_dict['post_author'])
