from typing import List
import json
import logging
import pathlib

import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient

BASE_URL = 'https://tlgrm.ru/channels/'
CHANNELS_URLS_FILE = pathlib.Path(__file__).parent.parent.absolute() / 'channels.json'
CHANNELS_TYPES_FILE = pathlib.Path(__file__).parent.parent.absolute() / 'channels_types.json'


class ChannelType:
    """
    Channels types from unofficial telegram site (tlgrm.ru/channels)
    """

    NEWS = 'news'
    BLOG = 'blogs'
    TECH = 'tech'
    ENTERTAINMENT = 'entertainment'
    POLITICS = 'economics'
    ECONOMICS = 'economics'
    CRYPTO = 'crypto'
    EDUCATION = 'education'
    MUSIC = 'music'
    LANGUAGE = 'language'
    BUSINESS = 'business'
    PSYCHOLOGY = 'psychology'
    MARKETING = 'marketing'
    CAREER = 'career'
    VIDEO = 'video'
    BOOKS = 'books'
    FITNESS = 'fitness'
    TRAVEL = 'travel'
    ART = 'art'
    BEAUTY = 'beauty'
    HEALTH = 'health'
    GAMING = 'gaming'
    FOOD = 'food'
    SALES = 'sales'
    QUOTES = 'quotes'


def get_ref(channel_type: str) -> str:
    return BASE_URL + channel_type


def load_channels(ref: str, ch_type: str) -> List[dict]:
    channels = []
    link = 'https://t.me/{}'
    try:
        page = requests.get(ref).content
        soup = BeautifulSoup(page, 'html.parser')
        for div in soup.find_all('div', attrs={'class': 'channel-card__info'})[1:]:
            name = div.find('a').text
            subs = int(div.find('span', attrs={'class': 'channel-card__subscribers'}).text.strip().replace(' ', ''))
            ch_link = div.find('a', attrs={'class': 'channel-card__username'}).text.strip().replace('&commat', '')
            if ch_type == ChannelType.POLITICS:
                ch_type = 'politics economics'
            channels.append({
                'name': name,
                'subs_count': subs,
                'link': link.format(ch_link),
                'type': ch_type
            })

    except Exception as e:
        logging.error(e)
    return channels


def load_channels_by_types(types_list: List[str]) -> List[dict]:
    all_channels = {}
    for ch_type in types_list:
        channels = load_channels(get_ref(ch_type), ch_type)
        for ch in channels:
            if ch['name'] not in all_channels:
                all_channels[ch['name']] = ch
            else:
                all_channels[ch['name']]['type'] += f' {ch_type}'
    return list(all_channels.values())


def get_channels(use_custom_channels: bool) -> List[dict]:
    if use_custom_channels:
        with open(CHANNELS_URLS_FILE, 'r') as f:
            channels = json.load(f)
    else:
        with open(CHANNELS_TYPES_FILE, 'r') as f:
            types_list = json.load(f)
        channels = load_channels_by_types(types_list)
    logging.info('Got %d channels' % len(channels))
    return channels


async def register_client(session_name: str, api_id: int, api_hash: str):
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()
    await client.disconnect()
    logging.info('Successfully register client')
