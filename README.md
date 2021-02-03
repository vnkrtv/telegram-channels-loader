# telegram-channels-loader
[![Build Status](https://travis-ci.com/vnkrtv/telegram-channels-loader.svg?branch=main)](https://travis-ci.com/vnkrtv/telegram-channels-loader)
## Description

Service providing loading messages from telegram channels to PostgreSQL DB.

## Usage  

- ```git clone https://github.com/vnkrtv/telegram-channels-loader.git && telegram-channels-loader```
- ```docker build -t tg-channels-loader .```
- Set params in env.cfg file
- Set channels links list in channels.json file  
- ```docker run --env-file env.cfg --name tg-loader -d tg-channels-loader```