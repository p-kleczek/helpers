# -*- coding: utf-8 -*-
import copy
import logging
from typing import Dict, List
from urllib.parse import urljoin

import requests

from commons_lib.html_parser import BasicHTMLParser

root = logging.getLogger()
root.setLevel(logging.WARNING)


class SdmHTMLParser(BasicHTMLParser):
    def __init__(self):
        super().__init__()
        self.is_slider_div = False
        self.img_urls: List[str] = []

    def process_starttag(self):
        if self.current_tag.td.tag == 'div':
            self.is_slider_div = self.current_tag.td.attrs.get('class') == 'slider lightbox slider--wide'

        if self.current_tag.td.tag == 'a' and self.is_slider_div:
            self.img_urls.append(self.current_tag.td.attrs['href'])


def get_sdm_imgs_urls(object_id: str):
    sdm_url_root = 'https://sdm.upjp2.edu.pl/obiekty-archiwalne/'
    sdm_url = urljoin(sdm_url_root, object_id)

    session = requests.Session()  # Connection: keep-alive (by default)
    session.head(sdm_url)
    resp = session.get(sdm_url)
    resp_text = resp.text

    parser = SdmHTMLParser()
    parser.feed(resp_text)
    # print(parser.img_urls)

    return parser.img_urls
