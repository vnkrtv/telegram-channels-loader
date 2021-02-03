from typing import List
import json
import logging

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://tlgrm.ru/channels/'
CHANNELS_URLS_FILE = 'channels.json'
CHANNELS_TYPES_FILE = 'channels_types.json'


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
    all_channels = []
    for ch_type in types_list:
        channels = load_channels(get_ref(ch_type), ch_type)
        for ch in channels:
            if ch not in all_channels:
                all_channels.append(ch)
    return all_channels


def get_channels(custom_channels: bool) -> List[dict]:
    if custom_channels:
        with open(CHANNELS_URLS_FILE, 'r') as f:
            return json.load(f)
    else:
        with open(CHANNELS_TYPES_FILE, 'r') as f:
            types_list = json.load(f)
        return load_channels_by_types(types_list)
