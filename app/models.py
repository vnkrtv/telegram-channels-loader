from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .db import Base


class Channel(Base):
    __tablename__ = "channels"

    channel_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    link = Column(String, index=True)
    description = Column(String, default='')
    subscribers_count = Column(Integer)

    messages = relationship('Message', back_populates="channel")


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now)
    description = Column(String, index=True)
    views_count = Column(Integer)
    author = Column(String, nullable=True)
    text = Column(String)
    channel_id = Column(Integer, ForeignKey("channels.id"))

    channel = relationship("Chanel", back_populates="messages")
