from enum import StrEnum
from typing import Dict
import urllib.parse


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


def compose_url(url: str, params: Dict) -> str:
    def encode_brackets(s: str) -> str:
        # FIXME: Maybe it is already performed automatically?
        return s.replace('[', '%5B').replace(']', '%5D')

    params_str = ('?' + '&'.join(f"{encode_brackets(k)}={urllib.parse.quote(str(v).encode('utf-8'))}"
                                 for k, v in params.items())) if params else ''

    url_with_params = f"{url}{params_str}"
    return url_with_params
