# -*- coding: utf-8 -*-
import copy
import json
import logging
import math
import urllib.request
import urllib.parse
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from random import randint
from typing import Dict, List

import requests

from genealogia.commons import compose_url, Region

# FIXME: Parametry rpp1 i rpp2 w _GET (https://geneteka.genealodzy.pl/js/main.js?ver=1.71)

#     sUrl = updateURL(sUrl, 'rpp1', page * length);
#     sUrl = updateURL(sUrl, 'rpp2', length);


regions_encoding: Dict[Region, str] = {
    Region.Dolnoslaskie: '01ds',
    Region.KujawskoPomorskie: '02kp',
    Region.Lubelskie: '03lb',
    Region.Lubuskie: '04ls',
    Region.Lodzkie: '05ld',
    Region.Malopolskie: '06mp',
    Region.Mazowieckie: '07mz',
    Region.Warszawa: '71wa',
    Region.Opolskie: '08op',
    Region.Podkarpackie: '09pk',
    Region.Podlaskie: '10pl',
    Region.Pomorskie: '11pm',
    Region.Slaskie: '12sl',
    Region.Swietokrzyskie: '13sk',
    Region.WarminskoMazurskie: '14wm',
    Region.Wielkopolskie: '15wp',
    Region.Zachodniopomorskie: '16zp',
    Region.Ukraina: '21uk',
    Region.Bialorus: '22br',
    Region.Litwa: '23lt',
    Region.POZOSTALE: '25po',
}


class EventType(StrEnum):
    Birth = "B"
    Marriage = "S"
    Death = "D"


root = logging.getLogger()
root.setLevel(logging.DEBUG)

# def load_file(input_file_path: Path, charset: str) -> Optional[str]:
#     try:
#         with open(input_file_path, encoding=charset) as f:
#             file_content = f.readlines()
#         parser_input = ''.join(file_content)
#         return parser_input
#     except UnicodeDecodeError:
#         return None


sample_query_params = {
    'op': 'gt',
    'lang': 'pol',
    # 'bdm': 'B',
    'w': regions_encoding[Region.Warszawa],
    'rid': 'B',
    'search_lastname': 'gadomski',
    'search_name': '',  # 'Józef',
    'search_lastname2': '',
    'search_name2': '',
    'from_date': '',  # '1820',
    'to_date': '',  # '1885',
    # 'exac': '1',
    # 'pair': '1',
    # 'parents': '1',
}

geneteka_url = "https://geneteka.genealodzy.pl/index.php"
acts_url = "https://geneteka.genealodzy.pl/api/getAct.php"

MAX_ENTRIES_PER_REQUEST = 50


def query_acts(common_params: Dict, event_type: EventType):
    this_common_params = copy.copy(common_params)
    this_common_params['bdm'] = str(event_type)

    init_results = query_acts_page(this_common_params)
    total_results = int(init_results['recordsTotal'])

    aggregated_data = init_results['data']

    for page_inx in range(1, int(math.ceil(total_results / MAX_ENTRIES_PER_REQUEST))):
        subsequent_results = query_acts_page(this_common_params, page_inx=page_inx)
        aggregated_data.extend(subsequent_results['data'])

    return aggregated_data


def query_acts_page(common_params: Dict, page_inx: int = 0):
    """
    Query a single page with results (up to 50 entries).
    :param common_params:
    :param page_inx:
    :return:
    """
    this_common_params = copy.copy(common_params)
    if page_inx > 0:
        this_common_params['rpp1'] = page_inx * MAX_ENTRIES_PER_REQUEST
        this_common_params['rpp2'] = MAX_ENTRIES_PER_REQUEST
        this_common_params['ordertable'] = '[[0,"asc"],[1,"asc"],[2,"asc"]]'
        this_common_params['searchtable'] = ""

    params = {}

    params['draw'] = 1  # Licznik zwiększany o 1 wraz z każdym przeklikiwaniem się między stronami tabeli.

    for column_inx in range(10):
        column_data = {
            '[data]': column_inx,
            '[name]': "",
            '[searchable]': 'true' if column_inx != 9 else 'false',
            '[orderable]': 'true' if column_inx != 9 else 'false',
            '[search][value]': '',
            '[search][regex]': 'false',
        }
        for k, v in column_data.items():
            params[f'columns[{column_inx}]{k}'] = v

    for order_inx in range(3):
        order_data = {
            '[column]': order_inx,
            '[dir]': 'asc',
        }
        for k, v in order_data.items():
            params[f'order[{order_inx}]{k}'] = v

    params['start'] = page_inx * MAX_ENTRIES_PER_REQUEST
    params['length'] = MAX_ENTRIES_PER_REQUEST

    params['search[value]'] = ""
    params['search[regex]'] = 'false'

    for k, v in this_common_params.items():
        params[k] = v

    session = requests.Session()  # Connection: keep-alive (by default)
    session.head(geneteka_url)

    url = compose_url(url=acts_url, params=params)
    referer = compose_url(url=geneteka_url, params=this_common_params)

    resp = session.get(
        url,
        headers={
            'Host': "geneteka.genealodzy.pl",
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Accept-Language': "en-US,en;q=0.5",
            'Accept-Encoding': "gzip, deflate, br",
            'Content-Type': "application/json; charset=UTF-8",
            'X-Requested-With': "XMLHttpRequest",
            'Connection': "keep-alive",
            'Referer': referer,
            'Sec-Fetch-Dest': "empty",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Site': "same-origin",
            'Pragma': "no-cache",
            'Cache-Control': "no-cache",
            'TE': "trailers",
        })
    json_out = resp.json()

    return json_out


# def load_url(url: str = "https://geneteka.genealodzy.pl/index.php", charset: str = "UTF-8"):
#     params = {
#         'op': 'gt',
#         'lang': 'pol',
#         'bdm': 'B',
#         'w': '01ds',
#         'rid': 'B',
#         'search_lastname': 'gadomski',
#         'search_name': 'Józef',
#         'search_lastname2': '',
#         'search_name2': '',
#         'from_date': '1820',
#         'to_date': '1885',
#         'exac': '1',
#         'pair': '1',
#         'parents': '1',
#     }
#
#     params_str = '&'.join(f"{k}={urllib.parse.quote(v.encode('utf-8'))}" for k, v in params.items())
#     url_with_params = f"{url}?{params_str}"
#
#     req = urllib.request.Request(url_with_params, headers={'User-Agent': "Magic Browser"})
#     parser_input = None
#     with urllib.request.urlopen(req) as response:
#         html_reponse = response.read()
#         parser_input = html_reponse.decode(charset)
#
#     return parser_input


# init_results = query_births_page(sample_query_params, page_inx=1)

# json_out = load_url()

json_out = query_acts(sample_query_params, event_type=EventType.Marriage)


@dataclass
class Marriage:
    year: str
    act_no: str
    male_name: str
    male_surname: str
    male_parents: str
    female_name: str
    female_surname: str
    female_parents: str
    parish: str
    remarks: str

    @classmethod
    def from_json_entry(cls, entry):
        raise NotImplementedError


def query_marriages() -> List[Marriage]:
    json_out = query_acts(sample_query_params, event_type=EventType.Marriage)
    return [Marriage.from_json_entry(entry) for entry in json_out]

    raise NotImplementedError


print(len(json_out))
if json_out:
    print(json_out[0])

# print('Total: ', json_out['recordsTotal'])
# print('Current batch: ', len(json_out['data']))

# x = 1
# print(parser_input)

# output_filepath = Path("out/out.html")
# with open(output_filepath, "w", encoding="UTF-8") as f:
#     f.write(parser_input)
