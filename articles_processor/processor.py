# FIXME: Testy dla artykułów z kilkoma autorami (np. OKO.press)
# FIXME: parser dla "Więzi"

import logging
import re
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Dict, Optional, Tuple

from articles_processor.parser_types import OutputData
from articles_processor.parsers.agora_parser import WyborczaHTMLParser, WysokieObcasyHTMLParser
from articles_processor.parsers.okopress_parser import OKOPressHTMLParser
from articles_processor.parsers.polityka_parser import PolitykaHTMLParser
from articles_processor.parsers.wiez_parser import WiezHTMLParser
from bibtex.bibtex_key_generator import generate_bibtex_key

# ============================================================================

input_dir: Path = Path('input/')
input_dir: Path = Path('/media/pawel/data/My Downloads/~ DOŚĆ Milczenia/')
input_file_path: Path = input_dir / "gw2.html"
input_file_path: Path = input_dir / """
Karol Wojtyła, Ekke Overbeek, pedofilia i SB - Więź.htm
""".strip()

# TODO: Chyba OK.
input_file_path: Path = Path(
    "./tests/wyborcza1_Jacek Dehnel do Marcina Matczaka Wierzący nie wierzą w niewierzących.html")
# TODO: Dlaczego tyle pustych wierszy?
# input_file_path: Path = Path(
#     "./tests/polityka1_„Franciszkańska 3” Marcina Gutowskiego. Karol Wojtyła wiedział o złu w Kościele. Dorabianie usprawiedliwień jest kolejnym złem.html")
# TODO: Chyba OK.
# input_file_path: Path = Path("./tests/wiez1_Karol Wojtyła, Ekke Overbeek, pedofilia i SB - Więź.htm")
# TODO: Chyba OK.
# input_file_path: Path = Path(
#     "./tests/okopress1_Iustitia Nie daliśmy się złamać przez 8 lat, wygramy. Walczymy o nowoczesne sądy i nową KRS - OKO.press.html")
# TODO: ??
# input_file_path: Path = Path("./tests/wysokieobcasy1_Córka współzałożyciela Oddziału Zamkniętego Czułam, że jestem skazana na uzależnienia.html")

# ============================================================================

root = logging.getLogger()
root.setLevel(logging.DEBUG)


# FIXME: Ładowanie z URL-a; autouzupełnianie formatki nawet gdy
#  artykuły płatne (tj. nie zależy nam na treści).

def load_file(input_file_path: Path, charset: str) -> Optional[str]:
    try:
        with open(input_file_path, encoding=charset) as f:
            file_content = f.readlines()
        parser_input = ''.join(file_content)
        return parser_input
    except UnicodeDecodeError:
        return None


parser_input: Optional[str] = None
charset: Optional[str] = None

charsets = [chset.lower() for chset in ["UTF-8", "ISO-8859-2"]]
for charset in charsets:
    if (parser_input := load_file(input_file_path, charset)) is not None:
        break

if (m_chset := re.search(r"<meta char[sS]et=\"(?P<charset>[a-zA-Z0-9\-]+)\"",
                         parser_input, flags=re.IGNORECASE)) is not None:
    chset = m_chset.group('charset').lower()
    if chset != charset:
        with open(input_file_path, encoding=chset) as f:
            file_content = f.readlines()
            parser_input = ''.join(file_content)
else:
    raise NotImplementedError("Need to extract charset!")
    # FIXME: extract charset from metadata?

if re.search(r"<link rel=\"canonical\" href=\"https://(\w+\.)?wyborcza\.pl/", parser_input):
    parser = WyborczaHTMLParser()
elif re.search(r"<link rel=\"canonical\" href=\"https://www\.wysokieobcasy\.pl/", parser_input):
    parser = WysokieObcasyHTMLParser()
elif re.search(r"<meta name=\"application-name\" content=\"Polityka\"", parser_input):
    parser = PolitykaHTMLParser()
elif re.search(r"<link rel=\"canonical\" href=\"https://oko\.press/", parser_input):
    parser = OKOPressHTMLParser()
elif re.search(r"<link rel=\"canonical\" href=\"https://wiez\.pl/", parser_input):
    parser = WiezHTMLParser()
else:
    raise NotImplementedError("No parser matching the content!")

parser.feed(parser_input)
output: OutputData = parser.output

print(output)


class Publisher(StrEnum):
    WYBORCZA = "Gazeta Wyborcza"
    POLITYKA = "Polityka"
    OKO_PRESS = "OKO.press"
    WIEZ = "Więź"


def get_publisher(url: str) -> Tuple[Publisher, str]:
    if 'wyborcza.pl' in url:
        publisher = Publisher.WYBORCZA

        subtypes: Dict[str, str] = {
            'duzyformat': "Duży Format",
            'torun': "Toruń",
        }

        for url_chunk, subtype in subtypes.items():
            if f"/{url_chunk}/" in url:
                return publisher, f"{publisher} ({subtype})"
        return publisher, str(publisher)

    if 'www.wysokieobcasy.pl' in url:
        return Publisher.WYBORCZA, f"{Publisher.WYBORCZA} (Wysokie Obcasy)"

    if 'www.polityka.pl' in url:
        return Publisher.POLITYKA, str(Publisher.POLITYKA)

    if 'oko.press' in url:
        return Publisher.OKO_PRESS, str(Publisher.OKO_PRESS)

    if 'wiez.pl' in url:
        return Publisher.WIEZ, str(Publisher.WIEZ)

    raise ValueError(f"Undefined publisher for URL: `{url}`")


with open("misc_template.txt") as f:
    template = "".join(f.readlines())

for output_filepath in [
    Path("output") / f"{input_file_path.stem}.txt",
    Path("output") / f"current.txt"
]:
    # output_filepath = Path("output") / f"{input_file_path.stem}.txt"
    with open(output_filepath, "w", encoding="UTF-8") as f:
        publisher_type, publisher_str = get_publisher(output.url)
        publisher_id = {
            Publisher.WYBORCZA: 'gw',
            Publisher.POLITYKA: 'polityka',
            Publisher.OKO_PRESS: 'okopress',
            Publisher.WIEZ: 'wiez',
        }[publisher_type]
        f.write(template.format(
            label=f"{generate_bibtex_key(output.title)}_{publisher_id}_{output.pub_date.strftime('%Y_%m_%d')}",
            author=output.author,
            publisher=publisher_str,
            title=output.title,
            pubdate=output.pub_date.strftime('%Y-%m-%d'),
            url=output.url,
        ))
        f.write("\n------\n")
        f.write(output.print(full=False))
