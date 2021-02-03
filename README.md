# telegram-channels-loader
[![Build Status](https://travis-ci.com/vnkrtv/telegram-channels-loader.svg?branch=main)](https://travis-ci.com/vnkrtv/telegram-channels-loader)
## Description

Service providing loading messages from telegram channels to PostgreSQL DB.

## Usage  

- ```git clone https://github.com/vnkrtv/telegram-channels-loader.git && telegram-channels-loader```
- ```docker build -t tg-channels-loader .```
- Set params in env.cfg file
- Set tracking channels list (more details are described below) 
- ```docker run --env-file env.cfg --name tg-loader -d tg-channels-loader```

## Tracking channels

There are 2 ways to set the list of tracking channels:
- set channels types in channels_types.json file - service will automatically take the 24 most popular channels on the specified types from the [this site](tlgrm.ru/channels) and start monitoring them
- set CUSTOM_CHANNELS_URLS env in env.cfg file and edit channels.json file - service will only monitor the specified channels  

Table of channel types are specified below:

| Subject of the channel    | Type          |
|---------------------------|---------------|
| News and media            | news          |
| Blogs                     | blogs         |
| Technologies              | tech          |
| Humor and entertainment   | entertainment |
| Politics and economics    | economics     |
| Cryptocurrencies          | crypto        |
| Science and education     | education     |
| Music                     | music         |
| Linguistics               | language      |
| Businesses and startups   | business      |
| Psychology                | psychology    |
| Marketing and Advertising | marketing     |
| Career                    | career        |
| Movies and TV series      | video         |
| Literature                | books         |
| Health and sports         | fitness       |
| Travel and emigration     | travel        |
| Art and photography       | art           |
| Fashion and Beauty        | beauty        |
| Medicine                  | health        |
| Games and apps            | gaming        |
| Food and drink            | food          |
| Sales                     | sales         |
| Quotes                    | quotes        |