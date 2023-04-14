import re
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Dict

from articles_processor.parsers import WysokieObcasyHTMLParser, WyborczaHTMLParser
from articles_processor.types import OutputData
from bibtex.bibtex_key_generator import generate_bibtex_key

# ============================================================================

input_dir: Path = Path('input/')
input_dir: Path = Path('/media/pawel/data/My Downloads/~ DOŚĆ Milczenia/')
input_file_path: Path = input_dir / "gw2.html"
input_file_path: Path = input_dir / "Czy mnie dziwi, że na rekolekcjach w Toruniu gość jak patostreamer bije kobietę Ani trochę.html"

# ============================================================================

output: OutputData = OutputData()

charsets = ["UTF-8", "ISO-8859-2"]

for charset in charsets:
    try:
        with open(input_file_path, encoding=charset) as f:
            file_content = f.readlines()
    except UnicodeDecodeError:
        continue
parser_input = ''.join(file_content)


def remove_extra_metadata():
    for tag in ['@context', '@type', 'articleSection', 'hasPart',
                'image', 'publisher', 'isAccessibleForFree',
                'mainEntityOfPage']:
        output.metadata.pop(tag)

    for author in output.metadata['author']:
        author.pop('url')


if re.search(r"<link rel=\"canonical\" href=\"https://(\w+\.)?wyborcza\.pl/", parser_input):
    parser = WyborczaHTMLParser(output)
elif re.search(r"<link rel=\"canonical\" href=\"https://www\.wysokieobcasy\.pl/", parser_input):
    parser = WysokieObcasyHTMLParser(output)
else:
    raise NotImplementedError("No parser matching the content!")

parser.feed(parser_input)

output.title = output.title.strip()
output.author = ", ".join(author['name'] for author in output.metadata['author'])
output.url = output.metadata['mainEntityOfPage']['url']

pub_date_meta_str = output.metadata['datePublished']
pub_date_meta = datetime.fromisoformat(pub_date_meta_str)
if output.pub_date:
    assert output.pub_date.date() == pub_date_meta.date()
else:
    output.pub_date = pub_date_meta

mod_date_meta_str = output.metadata['dateModified']
mod_date_meta = datetime.fromisoformat(mod_date_meta_str)
if output.last_updated:
    assert output.last_updated.date() == mod_date_meta.date()
else:
    output.last_updated = mod_date_meta

remove_extra_metadata()

print(output)


def remove_nbsps(s: str) -> str:
    return s.replace("\u00a0", " ")


output.content = remove_nbsps(output.content)
output.content = output.content.replace("„", '"')
output.content = output.content.rstrip()


class Publishers(StrEnum):
    WYBORCZA = "Gazeta Wyborcza"


def get_publisher(url: str) -> str:
    publisher: str = ""
    if 'wyborcza.pl' in url:
        publisher = Publishers.WYBORCZA

        subtypes: Dict[str, str] = {
            'duzyformat': "Duży Format",
            'torun': "Toruń",
        }

        for url_chunk, subtype in subtypes.items():
            if f"/{url_chunk}/" in url:
                return f"{publisher} ({subtype})"
        return publisher

    if 'wysokieobcasy.pl' in url:
        return f"{Publishers.WYBORCZA} (Wysokie Obcasy)"

    raise ValueError(f"Undefined publisher for URL: {url}")


with open("misc_template.txt") as f:
    template = "".join(f.readlines())

for output_filepath in [
    Path("output") / f"{input_file_path.stem}.txt",
    Path("output") / f"current.txt"
]:
    # output_filepath = Path("output") / f"{input_file_path.stem}.txt"
    with open(output_filepath, "w", encoding="UTF-8") as f:
        publisher_id = 'gw'
        f.write(template.format(
            label=f"{generate_bibtex_key(output.title)}_{publisher_id}_{output.pub_date.strftime('%Y_%m_%d')}",
            author=output.author,
            publisher=get_publisher(output.url),
            title=output.title,
            pubdate=output.pub_date.strftime('%Y-%m-%d'),
            url=output.url,
        ))
        f.write("\n------\n")
        f.write(str(output))
