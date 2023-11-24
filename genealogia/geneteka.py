# -*- coding: utf-8 -*-
import json
import logging
import urllib.request
import urllib.parse
from enum import StrEnum
from pathlib import Path
from random import randint
from typing import Dict

import requests


# FIXME: Parametry rpp1 i rpp2 w _GET (https://geneteka.genealodzy.pl/js/main.js?ver=1.71)

#     sUrl = updateURL(sUrl, 'rpp1', page * length);
#     sUrl = updateURL(sUrl, 'rpp2', length);

class Region(StrEnum):
    Dolnoslaskie = "dolnośląskie"
    KujawskoPomorskie = "kujawsko-pomorskie"
    Lubelskie = "lubelskie"
    Lubuskie = "lubuskie"
    Lodzkie = "łódzkie"
    Malopolskie = "małopolskie"
    Mazowieckie = "mazowieckie"
    Warszawa = "Warszawa"
    Opolskie = "opolskie"
    Podkarpackie = "podkarpackie"
    Podlaskie = "podlaskie"
    Pomorskie = "pomorskie"
    Slaskie = "śląskie"
    Swietokrzyskie = "świętokrzyskie"
    WarminskoMazurskie = "warmińsko-mazurskie"
    Wielkopolskie = "wielkopolskie"
    Zachodniopomorskie = "zachodniopomorskie"
    Ukraina = "Ukraina"
    Bialorus = "Białoruś"
    Litwa = "Litwa"
    POZOSTALE = "(pozostałe)"


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
    'bdm': 'B',
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


# FIXME: Handle multiple pages.

def query_births(common_params: Dict):
    url = "https://geneteka.genealodzy.pl/api/getAct.php"
    charset: str = "UTF-8"

    params = {}

    params['draw'] = 1

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

    params['start'] = 0  # FIXME: To pewnie podział na strony.
    params['length'] = 50  # FIXME: Czy można dać więcej (niż 50)? Żeby nie było podziału na strony?

    params['search[value]'] = ""
    params['search[regex]'] = 'false'

    for k, v in common_params.items():
        params[k] = v

    # def random_with_n_digits(n):
    #     range_start = 10 ** (n - 1)
    #     range_end = (10 ** n) - 1
    #     return randint(range_start, range_end)
    #
    # # See: https://api.jquery.com/jquery.ajax/ (`cache` param)
    # unserscore = '1700816545053'
    #
    # # params['_'] = str(random_with_n_digits(13))  # "1700816545053"  # FIXME: Generate random number
    # # params['_'] = unserscore  # Anti-cache parameter.

    def compose_url(url: str, params: Dict) -> str:
        def encode_brackets(s: str) -> str:
            return s.replace('[', '%5B').replace(']', '%5D')

        params_str = '&'.join(f"{encode_brackets(k)}={urllib.parse.quote(str(v).encode('utf-8'))}"
                              for k, v in params.items())

        url_with_params = f"{url}?{params_str}"
        return url_with_params

    session = requests.Session()  # Connection: keep-alive (by default)
    session.head(geneteka_url)

    resp = session.get(
        compose_url(url=url, params=params),
        headers={
            'Host': "geneteka.genealodzy.pl",
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Accept-Language': "en-US,en;q=0.5",
            'Accept-Encoding': "gzip, deflate, br",
            'Content-Type': "application/json; charset=UTF-8",
            'X-Requested-With': "XMLHttpRequest",
            'Connection': "keep-alive",
            'Referer': compose_url(url=geneteka_url, params=common_params),
            'Sec-Fetch-Dest': "empty",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Site': "same-origin",
            'Pragma': "no-cache",
            'Cache-Control': "no-cache",
            'TE': "trailers",
        })
    json_out = resp.json()

    print('Total: ', json_out['recordsTotal'])
    print('Current batch: ', len(json_out['data']))

    return json_out


def load_url(url: str = "https://geneteka.genealodzy.pl/index.php", charset: str = "UTF-8"):
    params = {
        'op': 'gt',
        'lang': 'pol',
        'bdm': 'B',
        'w': '01ds',
        'rid': 'B',
        'search_lastname': 'gadomski',
        'search_name': 'Józef',
        'search_lastname2': '',
        'search_name2': '',
        'from_date': '1820',
        'to_date': '1885',
        'exac': '1',
        'pair': '1',
        'parents': '1',
    }

    # FIXME: Encode values
    # data = urllib.parse.urlencode('Józef').encode(encoding='utf-8', errors='ignore')

    params_str = '&'.join(f"{k}={urllib.parse.quote(v.encode('utf-8'))}" for k, v in params.items())
    url_with_params = f"{url}?{params_str}"

    req = urllib.request.Request(url_with_params, headers={'User-Agent': "Magic Browser"})
    parser_input = None
    with urllib.request.urlopen(req) as response:
        html_reponse = response.read()
        parser_input = html_reponse.decode(charset)

    return parser_input


# parser_input = load_url()
parser_input = query_births(sample_query_params)

# x = 1
# print(parser_input)

# output_filepath = Path("out/out.html")
# with open(output_filepath, "w", encoding="UTF-8") as f:
#     f.write(parser_input)
