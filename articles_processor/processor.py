# FIXME: Testy dla artykułów z kilkoma autorami (np. OKO.press)
import logging
import re
import sys
import urllib.request
from enum import StrEnum, Enum, auto
from pathlib import Path
from time import sleep
from typing import Dict, Optional, Tuple

from articles_processor.parser_types import OutputData
from articles_processor.parsers.agora_parser import WyborczaHTMLParser, WysokieObcasyHTMLParser
from articles_processor.parsers.default_parser import DefaultHTMLParser
from articles_processor.parsers.okopress_parser import OKOPressHTMLParser
from articles_processor.parsers.onet_parser import OnetHTMLParser
from articles_processor.parsers.pap_parser import PapHTMLParser
from articles_processor.parsers.polityka_parser import PolitykaHTMLParser
from articles_processor.parsers.rzeczpospolita_parser import RzeczpospolitaHTMLParser
from articles_processor.parsers.wiez_parser import WiezHTMLParser
from bibtex.bibtex_key_generator import generate_bibtex_key


class InputMode(Enum):
    FILE = auto()
    URL = auto()


# ============================================================================

input_mode: InputMode = InputMode.FILE

url = """
https://www.archidiecezja.lodz.pl/aktualnosci/2023/03/abp-rys-o-zarzutach-przeciw-janowi-pawlowi-ii-nie-mam-cienia-watpliwosci-ze-papiez-sie-obroni
""".strip()

# input_dir: Path = Path('input/')
input_dir: Path = Path('/media/pawel/data/My Downloads/~ DOŚĆ Milczenia/')
input_dir: Path = Path('/media/pawel/data/My Downloads/~ Dobra zmiana/')
# input_dir = Path("/media/pawel/data/My Downloads/~ Dobra zmiana/jp2/")
input_dir: Path = Path('/media/pawel/data/My Downloads/~ DOŚĆ Milczenia/jp2')
# input_file_path: Path = input_dir / "gw2.html"
input_file_path: Path = input_dir / """
Jan Paweł II. Kto przynosi złe wieści, musi stracić głowę.html
""".strip()

# # TODO: Chyba OK.
# input_file_path: Path = Path(
#     "./tests/wyborcza1_Jacek Dehnel do Marcina Matczaka Wierzący nie wierzą w niewierzących.html")
# # TODO: Dlaczego tyle pustych wierszy?
# # input_file_path: Path = Path(
# #     "./tests/polityka1_„Franciszkańska 3” Marcina Gutowskiego. Karol Wojtyła wiedział o złu w Kościele. Dorabianie usprawiedliwień jest kolejnym złem.html")
# # TODO: Chyba OK.
# # input_file_path: Path = Path("./tests/wiez1_Karol Wojtyła, Ekke Overbeek, pedofilia i SB - Więź.htm")
# # TODO: Chyba OK.
# # input_file_path: Path = Path(
# #     "./tests/okopress1_Iustitia Nie daliśmy się złamać przez 8 lat, wygramy. Walczymy o nowoczesne sądy i nową KRS - OKO.press.html")
# # TODO: ??
# # input_file_path: Path = Path("./tests/wysokieobcasy1_Córka współzałożyciela Oddziału Zamkniętego Czułam, że jestem skazana na uzależnienia.html")

# input_file_path: Path = Path(
#     "./tests/rp1_Wojtyła do księdza-pedofila Każde przestępstwo winno być ukarane - rp.pl.html")

# ============================================================================

root = logging.getLogger()
root.setLevel(logging.DEBUG)


# FIXME: Ładowanie z URL-a; autouzupełnianie formatki nawet gdy
#  artykuły płatne (tj. nie zależy nam na treści).

def gather_input() -> str:
    def load_file(input_file_path: Path, charset: str) -> Optional[str]:
        try:
            with open(input_file_path, encoding=charset) as f:
                file_content = f.readlines()
            parser_input = ''.join(file_content)
            return parser_input
        except UnicodeDecodeError:
            return None

    def load_url(url, charset: str):
        req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
        with urllib.request.urlopen(req) as response:
            html_reponse = response.read()
            parser_input = html_reponse.decode(charset)
            return parser_input

    parser_input: Optional[str] = None

    charset: Optional[str] = None

    charsets = [chset.lower() for chset in ["UTF-8", "ISO-8859-2"]]
    for charset in charsets:
        if input_mode == InputMode.FILE:
            parser_input = load_file(input_file_path, charset=charset)
        elif input_mode == InputMode.URL:
            parser_input = load_url(url, charset=charset)
        else:
            raise NotImplementedError

        if parser_input is not None:
            break

    meta_search_input = re.sub(r"\n", " ", parser_input)
    meta_search_input = re.sub(r" +", " ", meta_search_input)

    m_chset = re.search(r"<meta char[sS]et=\"(?P<charset>[a-zA-Z0-9\-]+)\"",
                        meta_search_input, flags=re.IGNORECASE)
    if m_chset is None:
        m_chset = re.search(
            r'<meta http-equiv="Content-Type" content="text\/html; charset="?(?P<charset>[a-zA-Z0-9\-]+)"?',
            meta_search_input, flags=re.IGNORECASE)

    if m_chset is not None:
        chset = m_chset.group('charset').lower()
        if chset != charset:
            if input_mode == InputMode.FILE:
                parser_input = load_file(input_file_path, charset=chset)
            elif input_mode == InputMode.URL:
                parser_input = load_url(url, charset=chset)
    else:
        raise NotImplementedError("Need to extract charset!")
        # FIXME: extract charset from metadata?

    def fix_meta_charset(parser_input: str) -> str:
        """<meta> tag with `charset` attr should be a start-end tag."""

        if (m := re.search(r"<meta charset=\"(?P<charset>[\w\-]+)\"\s*>", parser_input)) is not None:
            parser_input = re.sub(r"<meta charset=\"[\w\-]+\"\s*>",
                                  f"<meta charset=\"{m.group('charset')}\" />",
                                  parser_input)
        return parser_input

    parser_input = fix_meta_charset(parser_input)
    return parser_input


parser_input = gather_input()


def get_parser(parser_input):
    if re.search(r"<link rel=\"canonical\" href=\"https://(?:\w+\.)?wyborcza\.pl/", parser_input) \
            or re.search(r"<meta http-equiv=\"Refresh\" content=\"0; URL=https://wyborcza\.pl/", parser_input):
        return WyborczaHTMLParser()
    elif re.search(r"<link rel=\"canonical\" href=\"https://www\.wysokieobcasy\.pl/", parser_input):
        return WysokieObcasyHTMLParser()
    elif re.search(r"<meta name=\"application-name\" content=\"Polityka\"", parser_input):
        return PolitykaHTMLParser()
    elif re.search(r"<link rel=\"canonical\" href=\"https://oko\.press/", parser_input):
        return OKOPressHTMLParser()
    elif re.search(r"<link rel=\"canonical\" href=\"https://wiez\.pl/", parser_input):
        return WiezHTMLParser()
    elif re.search(r"<link rel=\"canonical\" href=\"https://www\.rp\.pl/", parser_input):
        return RzeczpospolitaHTMLParser()
    elif re.search(r"<link rel=\"canonical\" href=\"https://www\.pap\.pl/", parser_input):
        return PapHTMLParser()
    elif re.search(r"<link rel=\"canonical\" href=\"https://(?:\w+\.)?onet\.pl/", parser_input):
        return OnetHTMLParser()
    else:
        raise NotImplementedError("No parser matching the content!")


if input_mode == InputMode.URL:
    parser = DefaultHTMLParser()
else:
    parser = get_parser(parser_input)

parser.feed(parser_input)
output: OutputData = parser.output


class Publisher(StrEnum):
    GENERIC = "PUBLISHER"

    WYBORCZA = "Gazeta Wyborcza"
    POLITYKA = "Polityka"
    OKO_PRESS = "OKO.press"
    WIEZ = "Więź"
    RZECZPOSPOLITA = "Rzeczpospolita"
    EKAI = "eKAI"
    GOSC = "Gość Niedzielny"
    ONET = "Onet"
    RADIO_ZET = "Radio ZET"
    TVN24 = "TVN24"
    DZIENNIK = "Dziennik"
    PAP = "Polska Agencja Prasowa (PAP)"


def get_publisher(url: str) -> Tuple[Publisher, str]:
    if 'wyborcza.pl' in url:
        publisher = Publisher.WYBORCZA

        subtypes: Dict[str, str] = {
            'duzyformat': "Duży Format",
            'alehistoria': "Ale Historia",
            'magazyn': "Wolna Sobota",

            'torun': "Toruń",
            'zakopane': "Zakopane",
            'wroclaw': "Wrocław",
            'krakow': "Kraków",
            'warszawa': "Warszawa",
            'trojmiasto': "Trójmiasto",
        }

        m = re.search(r"wyborcza\.pl/(?P<chunk>[^/]+)(?:/|$)", url)
        if (chunk := m.group('chunk')).isalpha():
            # if m := re.search(r"https://(?P<city>\w+)\.wyborcza\.pl/", url):
            #     if (city := m.group('city')) not in subtypes:
            #         raise ValueError(f"GW city not handled: {city}")
            if chunk not in subtypes:
                raise ValueError(f"GW chunk `{chunk}` not handled in {url}")
            return publisher, f"{publisher} ({subtypes[chunk]})"
        else:
            return publisher, str(publisher)

    if 'www.wysokieobcasy.pl' in url:
        return Publisher.WYBORCZA, f"{Publisher.WYBORCZA} (Wysokie Obcasy)"

    if 'www.polityka.pl' in url:
        return Publisher.POLITYKA, str(Publisher.POLITYKA)

    if 'oko.press' in url:
        return Publisher.OKO_PRESS, str(Publisher.OKO_PRESS)

    if 'wiez.pl' in url:
        return Publisher.WIEZ, str(Publisher.WIEZ)

    if 'rp.pl' in url:
        return Publisher.RZECZPOSPOLITA, str(Publisher.RZECZPOSPOLITA)

    if 'ekai.pl' in url:
        return Publisher.EKAI, str(Publisher.EKAI)

    if 'gosc.pl' in url:
        return Publisher.GOSC, str(Publisher.GOSC)

    if 'onet.pl' in url:
        return Publisher.ONET, str(Publisher.ONET)

    if 'radiozet.pl' in url:
        return Publisher.RADIO_ZET, str(Publisher.RADIO_ZET)

    if 'tvn24.pl' in url:
        return Publisher.TVN24, str(Publisher.TVN24)

    if 'wiadomosci.dziennik.pl' in url:
        return Publisher.DZIENNIK, str(Publisher.DZIENNIK)

    if 'www.pap.pl' in url:
        return Publisher.PAP, str(Publisher.PAP)

    return Publisher.GENERIC, Publisher.GENERIC
    # raise ValueError(f"Undefined publisher for URL: `{url}`")


with open("misc_template.txt") as f:
    template = "".join(f.readlines())

output_filepaths = [
    Path("output") / f"current.txt"
]

if input_mode == InputMode.FILE:
    output_filepaths.append(Path("output") / f"{input_file_path.stem}.txt")

for output_filepath in output_filepaths:
    # output_filepath = Path("output") / f"{input_file_path.stem}.txt"
    with open(output_filepath, "w", encoding="UTF-8") as f:
        publisher_type, publisher_str = get_publisher(output.url)

        known_publisher_ids = {
            Publisher.WYBORCZA: 'gw',
            # Publisher.POLITYKA: 'polityka',
            Publisher.OKO_PRESS: 'okopress',
            # Publisher.WIEZ: 'wiez',
            Publisher.RZECZPOSPOLITA: 'rp',
            # Publisher.EKAI: 'ekai',
            # Publisher.GOSC: 'gosc',
            # Publisher.ONET: 'onet',
            Publisher.RADIO_ZET: 'radiozet',
            # Publisher.TVN24: 'tvn24',
            # Publisher.DZIENNIK: 'dziennik',
            # Publisher.PAP: 'pap',
        }
        publisher_id = known_publisher_ids.get(publisher_type) or publisher_type

        f.write(template.format(
            label=f"{generate_bibtex_key(output.title)}_{publisher_id}_{output.pub_date.strftime('%Y_%m_%d')}",
            author=output.author,
            publisher=publisher_str,
            title=output.title,
            pubdate=output.pub_date.strftime('%Y-%m-%d'),
            url=output.url,
        ))

        if publisher_type == Publisher.GOSC:
            f.write("\nUWAGA: Uzupełnij informację o numerze 'Gościa' oraz ew. o diecezji!\n")

        f.write("\n------\n")
        f.write(output.print(full=False))

print(output, flush=True)

sleep(0.1)

if output.errors:
    print(f"ERRORS:  {[e.name for e in output.errors]}", file=sys.stderr)
