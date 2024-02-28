import json
import logging
import re
from time import sleep
from typing import Optional

import requests
from bs4 import BeautifulSoup
from django.utils.timezone import now
from retry import retry

from main.models import Game

logger = logging.getLogger(__name__)


BGG_SEARCH_URL = 'https://boardgamegeek.com/search/boardgame?q={}&nosession=1&showcount=50'
BGG_GAME_URL = r'https://www.boardgamegeek.com/boardgame/{}'


class TooManyRequestsError(Exception):
    """Too many http requests."""


class RequestsError(Exception):
    """SSL error from BGG."""


sleep_time = 0
last_url = None


def to_int(val: str) -> Optional[int]:
    try:
        new_val = int(val) or None
    except ValueError:
        new_val = None
    return new_val


@retry((TooManyRequestsError, RequestsError), delay=5, jitter=1, max_delay=60, tries=10)
def get(url: str, custom_headers: dict = None) -> requests.Response:
    global sleep_time
    global last_url
    if last_url == url:
        sleep_time = round(sleep_time + 0.5, 3)
        logger.info(f'Increased sleep time to {sleep_time}')
    elif sleep_time:
        sleep_time = round(sleep_time - 0.005, 3)
    last_url = url
    sleep(sleep_time)

    headers = {
        'Accept': 'application/json',
        'Referer': 'https://boardgamegeek.com/',
    }
    if custom_headers:
        headers.update(custom_headers)
    try:
        res = requests.get(url, headers=headers)
    except Exception as exc:
        logger.warning(f'Connection error! url={url}')
        logger.warning(f'Connection error! exc={exc}')
        raise RequestsError() from exc
    if res.status_code in [429, 430]:
        logger.warning(f'Too many requests! {url}')
        raise TooManyRequestsError()
    elif res.status_code >= 500:
        logger.warning(f'Server error! {url}')
        raise TooManyRequestsError()
    res.raise_for_status()
    return res


def bgg_search_name(name: str) -> list:
    raw = get(BGG_SEARCH_URL.format(name))
    res = raw.json()
    data = [{
        'id': i['id'],
        'name': i['name'],
        'year': i['yearpublished'],
    } for i in res['items']]
    return data


def scrape_game_by_id(id: int) -> dict:
    logger.info(f'Scraping {id}')
    res = get(BGG_GAME_URL.format(id))
    matches = re.search(
        r'GEEK\.geekitemPreload\s=\s(.*)GEEK\.geekitemSettings', res.text, re.S)
    json_match = matches.groups()[0]
    preload = json.loads(json_match.strip().rstrip(';'))
    item = {'scraped_at': now()}

    item['id'] = to_int(preload['item']['id'])
    item['name'] = preload['item']['name']
    item['subtype'] = preload['item']['subtype']
    item['year'] = to_int(preload['item']['yearpublished'])
    item['url'] = preload['item']['canonical_link']

    # rank
    for info in preload['item']['rankinfo']:
        if info['veryshortprettyname'] == 'Overall':
            item['rank'] = to_int(info['rank'])
    item['rating'] = float(preload['item']['stats']['average'])

    # basic details
    item['min_players'] = to_int(preload['item']['minplayers'])
    item['max_players'] = to_int(preload['item']['maxplayers'])
    item['min_play_time'] = to_int(preload['item']['minplaytime'])
    item['max_play_time'] = to_int(preload['item']['maxplaytime'])
    item['pitch'] = preload['item']['short_description']
    description_html = preload['item']['description'].replace('\\', '').replace('\n', ' ')
    description = BeautifulSoup(description_html, 'html.parser').text
    item['description'] = description.replace('  ', ' ').strip()
    item['img'] = preload['item']['imageurl'].replace('\\', '')

    # polls
    polls = preload['item']['polls']
    if polls['userplayers']['recommended']:
        item['rec_min_players'] = to_int(polls['userplayers']['recommended'][0]['min'])
        item['rec_max_players'] = to_int(polls['userplayers']['recommended'][0]['max'])
    if polls['userplayers']['best']:
        item['best_min_players'] = to_int(polls['userplayers']['best'][0]['min'])
        item['best_max_players'] = to_int(polls['userplayers']['best'][0]['max'])
    item['weight_avg'] = to_int(polls['boardgameweight']['averageweight'])

    logger.info(f'Scraped game {id}')
    return item
