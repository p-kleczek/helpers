# -*- coding: utf-8 -*-
import copy
import logging
from dataclasses import dataclass
from typing import Dict, List

import requests

from commons_lib.html_parser import BasicHTMLParser
from genealogia.commons import compose_url, Region

root = logging.getLogger()
root.setLevel(logging.DEBUG)

regions_encoding: Dict[Region, str] = {
    Region.Dolnoslaskie: 'dolnośląskie',
    Region.KujawskoPomorskie: 'kujawsko-pomorskie',
    Region.Lubelskie: 'lubelskie',
    Region.Lubuskie: 'lubuskie',
    Region.Lodzkie: 'łódzkie',
    Region.Malopolskie: 'małopolskie',
    Region.Mazowieckie: 'mazowieckie',
    Region.Opolskie: 'opolskie',
    Region.Podkarpackie: 'podkarpackie',
    Region.Podlaskie: 'podlaskie',
    Region.Pomorskie: 'pomorskie',
    Region.Slaskie: 'śląskie',
    Region.Swietokrzyskie: 'świętokrzyskie',
    Region.WarminskoMazurskie: 'warmińsko-mazurskie',
    Region.Wielkopolskie: 'wielkopolskie',
    Region.Zachodniopomorskie: 'zachodniopomorskie',
}

sample_query_params = {
    'imie': 'Jan',
    'nazw': 'Nowak',
    'wojewodztwo': '',
    'miasto': '',
}

grobonet_url = "https://grobonet.com/index.php"


def query_graves(common_params: Dict):
    this_common_params = copy.copy(common_params)

    aggregated_data = []

    for region, region_param_value in regions_encoding.items():
        this_common_params['wojewodztwo'] = region_param_value
        region_results = query_region(this_common_params)
        aggregated_data.extend(region_results)
        exit(-2)

    return aggregated_data


@dataclass
class CemeteryEntry:
    settlement: str = None
    cemetery: str = None
    url: str = None
    n_entries: int = None


class RegionGravesHTMLParser(BasicHTMLParser):
    """
    Parse e.g., https://grobonet.com/index.php?page=wyszukiwanie&imie=Jan&nazw=Nowak&wojewodztwo=dolno%C5%9Bl%C4%85skie&p=1
    """

    def __init__(self):
        super().__init__()
        self.output: List[CemeteryEntry] = []

    def process_starttag(self):
        if self.current_tag.td.tag == 'a' and self.current_tag.td.attrs.get('class') == 'boxWoj':
            cemetery_entry = CemeteryEntry(url=self.current_tag.td.attrs['href'])
            self.output.append(cemetery_entry)

    def process_data(self):
        if self.current_tag.td.tag == 'span' and self.current_tag.td.attrs.get('class') == 'nameOfState':
            self.output[-1].settlement = self.current_tag.td.data
            return

        if self.current_tag.td.tag == 'div' and self.current_tag.td.attrs.get('class') == '' \
                and len(self.tag_hierarchy) > 1 and self.tag_hierarchy[-2].td.attrs.get('class') == "boxWoj":
            if self.current_tag.td.data.strip():
                self.output[-1].cemetery = self.current_tag.td.data
            return

        if self.current_tag.td.tag == 'span' and self.current_tag.td.attrs.get('class') == 'numbers':
            self.output[-1].n_entries = int(self.current_tag.td.data)
            return


def query_region(common_params: Dict, page_inx: int = 1):
    """
    :param common_params:
    :param page_inx:
    :return:
    """
    this_common_params = copy.copy(common_params)
    this_common_params['p'] = page_inx

    session = requests.Session()  # Connection: keep-alive (by default)
    session.head(grobonet_url)

    # GET / HTTP/1.1
    # Host: grobonet.com
    # User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0
    # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    # Accept-Language: en-US,en;q=0.5
    # Accept-Encoding: gzip, deflate, br
    # DNT: 1
    # Connection: keep-alive
    # Upgrade-Insecure-Requests: 1
    # Sec-Fetch-Dest: document
    # Sec-Fetch-Mode: navigate
    # Sec-Fetch-Site: none
    # Sec-Fetch-User: ?1
    # Pragma: no-cache
    # Cache-Control: no-cache
    resp = session.get(grobonet_url)
    # HTTP/1.1 200 OK
    # Server: nginx
    # Date: Tue, 28 Nov 2023 08:00:10 GMT
    # Content-Type: text/html; charset=UTF-8
    # Transfer-Encoding: chunked
    # Connection: keep-alive
    # Vary: Accept-Encoding
    # Set-Cookie: PHPSESSID=a4vjvqmij5j337nf7gjvrfff2b; path=/
    # Expires: Thu, 19 Nov 1981 08:52:00 GMT
    # Cache-Control: no-store, no-cache, must-revalidate
    # Pragma: no-cache
    # Content-Encoding: gzip

    url = compose_url(url=grobonet_url, params=this_common_params)
    referer = compose_url(url=grobonet_url, params={})

    # session.cookies.set("PHPSESSID", "oia6ajlishjv9g035i6523bd0u", domain="grobonet.com")
    session.cookies.set("_ga", "GA1.1.88282952.1701156823", domain="grobonet.com")
    session.cookies.set("_ga_2YEB54LF7N", "GS1.1.1701156823.1.0.1701156823.0.0.0", domain="grobonet.com")

    resp = session.get(
        url,
        headers={
            # 'Host': "grobonet.com",
            'User-Agent': "Magic Browser",
            # 'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            'Accept-Language': "en-US,en;q=0.5",
            'Accept-Encoding': "gzip, deflate, br",
            'DNT': "1",
            'Connection': "keep-alive",
            # 'Referer': referer,
            'Upgrade-Insecure-Requests': "1",
            'Sec-Fetch-Dest': "document",
            'Sec-Fetch-Mode': "navigate",
            # 'Sec-Fetch-Site': "cross-site" | "same-origin" | "same-site" | "none",
            'Sec-Fetch-Site': "none",
            'Sec-Fetch-User': "?1",
            'Pragma': "no-cache",
            'Cache-Control': "no-cache",
        })
    resp_text = resp.text

    parser = RegionGravesHTMLParser()
    parser.feed(resp_text)
    print(parser.output)

    # FIXME: Obsłużyć wiele stron -> wysyłać zapytania dla kolejnych numerów, aż do momentu uzyskania błędu 404.
    # <ul class="pagination">

    return parser.output


query_graves(common_params=sample_query_params)
exit(-1)

# with open('/mnt/data/My Documents/Domowe/Genealogia/GEN_Szperacz/Grobonet/grobonet_region_sample.html') as f:
#     html_sample = "\n".join(f.readlines())

parser = RegionGravesHTMLParser()
parser.feed(html_sample)
print(parser.output)
exit(-1)

json_out = query_acts(sample_query_params, event_type=EventType.Marriage)

print(len(json_out))
if json_out:
    print(json_out[0])
